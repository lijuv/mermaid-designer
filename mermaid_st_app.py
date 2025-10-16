# streamlit_app_min.py
# Minimal Mermaid viewer (robust against $ in code)
# Run:  pip install streamlit
#       streamlit run streamlit_app_min.py

import streamlit as st
from textwrap import dedent
from string import Template
import html, json

st.set_page_config(page_title="Mermaid Minimal", layout="wide")
st.title("Mermaid Minimal")
st.caption("Paste Mermaid code → Render → export/copy SVG/PNG")

DEFAULT = dedent('''
flowchart TD
  %% Typical Car Showroom Sales Process
  A[Lead / Walk-in] --> B{Capture & Qualify}
  B -->|Warm| C[Test Drive Booking]
  B -->|Cold/No Fit| L[Exit / Nurture CRM]
  C --> D[Needs Analysis<br/>(Use-case, budget, timeline)]
  D --> E[Test Drive & Demo]
  E --> F{Interest Confirmed?}
  F -->|No| L
  F -->|Yes| G[Vehicle Selection<br/>(Model/Trim/Color)]
  G --> H{Trade-in?}
  H -->|Yes| I[Trade-in Appraisal<br/>(Condition, KMs, history)]
  H -->|No| J[Financing Options]
  I --> J
  J --> K[Credit Check & Pre-approval]
  K --> M{Approved?}
  M -->|No| L
  M -->|Yes| N[Quote & Offer<br/>(OTR price, trade value, fees)]
  N --> O{Negotiation}
  O --> P[Final Agreement<br/>(Price, terms, delivery)]
  P --> Q[F&I Products<br/>(Warranties, Insurance, Accessories)]
  Q --> R[Contract & Compliance<br/>(Docs, IDs, signatures)]
  R --> S[Vehicle Preparation<br/>(PDI, detailing, rego)]
  S --> T[Handover & Delivery<br/>(Walkthrough, keys, gifts)]
  T --> U[Follow-up & CSI Call]
  U --> V[Service Booking & Retention]
  V --> W[Loyalty / Referral Programs]
''').strip()

code = st.text_area("Mermaid code", value=DEFAULT, height=420)
padding = st.slider("Canvas padding (px)", 0, 64, 16)
zoom = st.slider("Zoom (%)", 80, 200, 100)
preview_h = st.slider("Preview height (px)", 500, 1400, 900)
font = st.text_input("Font family", "Inter, Segoe UI, Roboto, Helvetica, Arial, sans-serif")

# Mermaid config
m_config = {
    "startOnLoad": False,
    "securityLevel": "loose",
    "theme": "base",
    "themeVariables": {"fontFamily": font, "fontSize": "14"}
}

# Escape for HTML, then escape $ for Template to avoid KeyError
escaped_html = html.escape(code)
escaped_for_template = escaped_html.replace("$", "$$")

tpl = Template(r'''
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    :root { --bg: #ffffff; --border: #e6e8eb; }
    * { box-sizing: border-box; }
    body { margin: 0; padding: 0; background: var(--bg); font-family: $FONT; }
    .wrap { background:#fff; padding: $PADDINGpx; border:1px solid var(--border); border-radius:14px; }
    .holder { width: 100%; background: #fff; }
    .holder svg { display:block; width:100% !important; height:auto !important; max-width:100% !important; }
    .actions { display:flex; gap:8px; margin:10px 0 0 0; flex-wrap:wrap; }
    .btn { font:13px $FONT; padding:6px 10px; border:1px solid var(--border); border-radius:8px; background:#fff; cursor:pointer; }
    .zoom { transform: scale($ZOOM); transform-origin: top left; }
  </style>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
</head>
<body>
  <div class="wrap">
    <div id="holder" class="holder zoom">
      <div class="mermaid" id="mm">$ESCAPED</div>
    </div>
    <div class="actions">
      <button class="btn" onclick="downloadSVG()">Download SVG</button>
      <button class="btn" onclick="downloadPNG()">Download PNG</button>
      <button class="btn" onclick="openPNG()">Open PNG</button>
      <button class="btn" onclick="copySVG()">Copy SVG</button>
      <button class="btn" onclick="fitNow()">Fit to width</button>
    </div>
  </div>

  <script>
    const config = $CONFIG;
    function fitSVG(){
      const svg = document.querySelector('#holder svg'); if(!svg) return;
      svg.removeAttribute('width'); svg.removeAttribute('height');
      svg.style.width = '100%'; svg.style.height = 'auto';
      svg.setAttribute('preserveAspectRatio','xMinYMin meet');
    }
    function runMermaid(){
      mermaid.initialize(config);
      mermaid.run({ nodes: [document.getElementById('mm')] })
        .then(()=>{ fitSVG(); })
        .catch(e => {
          document.getElementById('mm').innerHTML =
            '<pre style="color:#b00020;">'+ e.toString() +'</pre>';
        });
    }
    function getSVGEl(){ return document.querySelector('#holder svg'); }
    function getSVGBlobAndXML(){
      const svg = getSVGEl(); if(!svg) return null;
      const clone = svg.cloneNode(true); clone.removeAttribute('style');
      const xml = new XMLSerializer().serializeToString(clone);
      return { xml, blob: new Blob([xml], {type:'image/svg+xml;charset=utf-8'}) };
    }
    function svgToCanvas(cb){
      const svg = getSVGEl(); if(!svg) return;
      const vb = svg.viewBox.baseVal;
      const s = getSVGBlobAndXML();
      const url = URL.createObjectURL(s.blob);
      const img = new Image();
      img.onload = function(){
        const scale = 3, c = document.createElement('canvas');
        c.width = Math.max(1, Math.floor(vb.width * scale));
        c.height = Math.max(1, Math.floor(vb.height * scale));
        const g = c.getContext('2d'); g.fillStyle='#fff'; g.fillRect(0,0,c.width,c.height);
        g.drawImage(img,0,0,c.width,c.height); URL.revokeObjectURL(url); cb(c);
      };
      img.onerror = function(e){ console.error('SVG->img failed', e); URL.revokeObjectURL(url); };
      img.src = url;
    }
    function downloadSVG(){
      const s = getSVGBlobAndXML(); if(!s) return;
      const a = document.createElement('a'); a.href = URL.createObjectURL(s.blob);
      a.download = 'diagram.svg'; document.body.appendChild(a); a.click(); a.remove();
    }
    function downloadPNG(){ svgToCanvas(c=>{ const a=document.createElement('a'); a.href=c.toDataURL('image/png'); a.download='diagram.png'; a.click(); }); }
    function openPNG(){ svgToCanvas(c=>{ const url=c.toDataURL('image/png'); window.open(url,'_blank'); }); }
    async function copySVG(){ const s=getSVGBlobAndXML(); if(!s) return; try{ await navigator.clipboard.writeText(s.xml); alert('SVG XML copied'); }catch(e){ alert('Copy failed: '+e); } }
    function fitNow(){ fitSVG(); }
    window.addEventListener('load', runMermaid);
    new ResizeObserver(()=>fitSVG()).observe(document.getElementById('holder'));
  </script>
</body>
</html>
''')

html_str = tpl.safe_substitute(  # <-- safe_substitute avoids KeyError on stray $ in template
    FONT=font,
    PADDING=str(padding),
    ZOOM=str(zoom/100.0),
    ESCAPED=escaped_for_template,  # <-- our Mermaid HTML with $ escaped for Template
    CONFIG=json.dumps(m_config)
)

st.components.v1.html(html_str, height=preview_h, scrolling=True)
