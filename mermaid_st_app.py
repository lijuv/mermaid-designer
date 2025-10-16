# streamlit_app.py
# Mermaid Diagram Studio — v3.2 (car showroom flow as DEFAULT)
# Run:
#   pip install streamlit
#   streamlit run streamlit_app.py

import streamlit as st
from textwrap import dedent
import html
import json

st.set_page_config(page_title="Mermaid Diagram Studio", layout="wide")

st.title("Mermaid Diagram Studio")
st.caption("Type Mermaid code → Render → export or copy as SVG/PNG")

# ---------- Session State ----------
DEFAULT = dedent('''
    %% Typical Car Showroom Sales Process (Flowchart)
    flowchart TD
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

      subgraph Lead Mgmt
        A --> B
      end

      subgraph Sales Journey
        C --> F
        G --> O
      end

      subgraph F&I & Delivery
        I --> R
        S --> T
      end

      classDef lane fill:#F5F9FF,stroke:#99B8FF,rx:10,ry:10;
      class A,B lane
      class C,D,E,F,G,H,I,J,K,M,N,O,P,Q,R lane
      class S,T,U,V,W lane

      P -->|Customer Cancels| L
      Q -->|Declined F&I| R
''').strip()

if "code" not in st.session_state:
    st.session_state["code"] = DEFAULT
if "to_render" not in st.session_state:
    st.session_state["to_render"] = st.session_state["code"]
if "uploaded_code" not in st.session_state:
    st.session_state["uploaded_code"] = None
if "use_uploaded" not in st.session_state:
    st.session_state["use_uploaded"] = False

# ---------- Callbacks ----------
def set_template(txt: str):
    st.session_state["code"] = dedent(txt).strip()

def commit_render():
    if st.session_state.get("use_uploaded") and st.session_state.get("uploaded_code"):
        st.session_state["to_render"] = st.session_state["uploaded_code"]
    else:
        st.session_state["to_render"] = st.session_state["code"]

# ---------- Sidebar Controls ----------
with st.sidebar:
    st.header("Style & Layout")
    preset = st.selectbox(
        "Palette",
        ["Neutral", "Brand Red", "Blue", "Teal"],
        index=0,
        help="Palettes apply to nodes, edges, and sequence diagram actors/notes."
    )
    font_family = st.text_input("Font family", "Inter, Segoe UI, Roboto, Helvetica, Arial, sans-serif")
    font_size = st.slider("Base font size (px)", 10, 24, 14)
    curve = st.selectbox("Flowchart curve", ["basis", "linear", "natural", "monotoneX", "monotoneY"], index=0)
    padding = st.slider("Canvas padding (px)", 0, 64, 16)
    zoom = st.slider("Zoom (%)", 80, 200, 100)
    preview_h = st.slider("Preview height (px)", 500, 1400, 900)
    st.divider()

    st.subheader("Load Mermaid code")
    f = st.file_uploader("Upload .mmd / .txt / .md", type=["mmd", "txt", "md"])
    if f is not None:
        try:
            content = f.read().decode("utf-8", errors="ignore")
        except Exception:
            content = None
        if content:
            st.session_state["uploaded_code"] = content.strip()
            st.success("Uploaded code loaded into memory.")
        else:
            st.warning("Could not read the uploaded file. Please check encoding.")

    st.session_state["use_uploaded"] = st.toggle(
        "Use uploaded code (if available)",
        value=st.session_state.get("use_uploaded", False),
        help="When enabled, the preview renders the uploaded file content. Disable to use the editor."
    )

    st.download_button(
        "Download current editor code (.mmd)",
        data=st.session_state["code"].encode("utf-8"),
        file_name="diagram.mmd",
        mime="text/plain"
    )

    st.divider()
    auto_color_actors = st.checkbox("Auto-color actors (alternating colors)", value=True,
                                    help="Sequence-only; harmless for flowcharts.")
    st.divider()
    js_src = st.radio("Mermaid JS", ["CDN", "Upload file"], horizontal=True)
    js_file = None
    if js_src == "Upload file":
        js_file = st.file_uploader("Upload mermaid.min.js", type=["js"], key="mermaid_js_file")

# Theme variables
def theme_vars(preset_name: str, font_family: str, font_size: int):
    base = {
        "background": "#ffffff",
        "primaryColor": "#f7f7f7",
        "primaryTextColor": "#111111",
        "primaryBorderColor": "#d0d7de",
        "lineColor": "#1f2328",
        "tertiaryColor": "#ffffff",
        "fontFamily": font_family,
        "fontSize": str(font_size),
        "textColor": "#111111",
        "nodeTextColor": "#111111",
        "clusterBkg": "#fafafa",
        "clusterBorder": "#d0d7de",
        "edgeLabelBackground": "#ffffff",
        "labelBackground": "#ffffff",
        "actorBkg": "#ececec",
        "actorBorder": "#666666",
        "actorTextColor": "#111111",
        "activationBkgColor": "#f4f4f4",
        "activationBorderColor": "#666666",
        "sequenceNumberColor": "#333333",
        "noteBkgColor": "#fff5ad",
        "noteBorderColor": "#aaaa33",
        "labelBoxBkgColor": "#ececff",
        "labelBoxBorderColor": "hsl(259, 60%, 88%)",
        "lineColorSequence": "#333333",
        "altBackground": "#f0f0f0",
    }
    if preset_name == "Brand Red":
        base.update({
            "primaryColor": "#FFF5F6",
            "primaryTextColor": "#1D1D1D",
            "primaryBorderColor": "#D61A20",
            "lineColor": "#1D1D1D",
            "clusterBkg": "#FCFCFC",
            "clusterBorder": "#C9CFD6",
            "actorBkg": "#FDE8E9",
            "actorBorder": "#D61A20",
            "noteBkgColor": "#FFF1F2",
            "noteBorderColor": "#D61A20",
            "labelBoxBkgColor": "#FFE4E6",
            "labelBoxBorderColor": "#FCA5A5",
        })
    elif preset_name == "Blue":
        base.update({
            "primaryColor": "#F5F9FF",
            "primaryTextColor": "#0B2E59",
            "primaryBorderColor": "#99B8FF",
            "lineColor": "#0B2E59",
            "actorBkg": "#EAF2FF",
            "actorBorder": "#99B8FF",
            "noteBkgColor": "#EAF2FF",
            "noteBorderColor": "#99B8FF",
            "labelBoxBkgColor": "#EAF2FF",
            "labelBoxBorderColor": "#99B8FF",
        })
    elif preset_name == "Teal":
        base.update({
            "primaryColor": "#F2FBFB",
            "primaryTextColor": "#064E4E",
            "primaryBorderColor": "#7FD1CC",
            "lineColor": "#0F6B6B",
            "actorBkg": "#E6FAF9",
            "actorBorder": "#7FD1CC",
            "noteBkgColor": "#E6FAF9",
            "noteBorderColor": "#7FD1CC",
            "labelBoxBkgColor": "#E6FAF9",
            "labelBoxBorderColor": "#7FD1CC",
        })
    return base

# ---------- Layout ----------
col1, col2 = st.columns([0.48, 0.52])

with col1:
    st.subheader("Editor")
    st.text_area("Mermaid code", key="code", height=420)
    with st.expander("Templates", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        c1.button("Flowchart", use_container_width=True, on_click=set_template, args=('''
            flowchart TD
              A[Lead] --> B(Qualify) --> C{Demo?}
              C -->|Yes| D[Test Drive] --> E[Offer] --> F[Contract] --> G[Delivery]
              C -->|No| H[Nurture CRM]
        ''',))
        c2.button("Sequence", use_container_width=True, on_click=set_template, args=('''
            sequenceDiagram
              autonumber
              participant C as Customer
              participant SA as Sales Advisor
              participant F as Finance
              C->>SA: Enquiry
              SA->>C: Demo & Proposal
              SA->>F: Finance Check
              F-->>SA: Approval
              SA-->>C: Finalize & Deliver
        ''',))
        c3.button("Class", use_container_width=True, on_click=set_template, args=('''
            classDiagram
              class Customer {+name;+contact;+budget}
              class Deal {+price;+status}
              class Vehicle {+vin;+model;+trim}
              Deal o-- Customer
              Deal o-- Vehicle
        ''',))
        c4.button("State", use_container_width=True, on_click=set_template, args=('''
            stateDiagram-v2
              [*] --> Lead
              Lead --> Demo: book_test_drive
              Demo --> Offer: interest
              Offer --> Contract: accepted
              Contract --> Delivery
              Delivery --> [*]
        ''',))
    st.button("Render / Update", type="primary", use_container_width=True, on_click=commit_render)

with col2:
    st.subheader("Preview & Export")
    tv = theme_vars(preset, font_family, font_size)

    m_config = {
        "startOnLoad": False,
        "securityLevel": "loose",
        "theme": "base",
        "themeVariables": tv,
        "flowchart": {"curve": curve},
        "sequence": {"mirrorActors": False, "showSequenceNumbers": True},
        "er": {"useMaxWidth": True},
        "gantt": {"axisFormat": "%d %b"}
    }

    if st.session_state.get("use_uploaded") and st.session_state.get("uploaded_code"):
        mermaid_code = st.session_state["uploaded_code"]
    else:
        mermaid_code = st.session_state.get("to_render", st.session_state["code"])

    if js_src == "Upload file" and js_file is not None:
        mermaid_loader = "<script>" + js_file.getvalue().decode("utf-8", errors="ignore") + "</script>"
    else:
        mermaid_loader = '<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>'

    escaped = html.escape(mermaid_code)

    html_tpl = '''
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        :root {{ --bg: #ffffff; --border: #e6e8eb; }}
        * {{ box-sizing: border-box; }}
        body {{
          margin: 0; padding: 0; background: var(--bg);
          font-family: {FONT};
        }}
        .wrap {{
          background: #ffffff; padding: {PADDING}px;
          border: 1px solid var(--border); border-radius: 14px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.06); overflow: hidden;
        }}
        .holder {{ width: 100%; background: #ffffff; }}
        .holder svg {{
          display: block; width: 100% !important; height: auto !important; max-width: 100% !important;
        }}
        .actions {{ display: flex; gap: 8px; margin: 10px 0 0 0; flex-wrap: wrap; }}
        .btn {{
          font-family: inherit; font-size: 13px; padding: 6px 10px;
          border: 1px solid var(--border); border-radius: 8px; background: #ffffff; cursor: pointer;
        }}
        .btn:hover {{ box-shadow: 0 1px 4px rgba(0,0,0,0.12); }}
        .zoom {{ transform: scale({ZOOM}); transform-origin: top left; }}
      </style>
      {LOADER}
    </head>
    <body>
      <div class="wrap">
        <div id="holder" class="holder zoom">
          <div class="mermaid" id="mm">{ESC}</div>
        </div>
        <div class="actions">
          <button class="btn" onclick="downloadSVG()">Download SVG</button>
          <button class="btn" onclick="downloadPNG()">Download PNG</button>
          <button class="btn" onclick="openPNG()">Open PNG</button>
          <button class="btn" onclick="copySVG()">Copy SVG</button>
          <button class="btn" onclick="copyPNG()">Copy PNG</button>
          <button class="btn" onclick="fitNow()">Fit to width</button>
        </div>
      </div>

      <script>
        function fitSVG() {{
          const svg = document.querySelector('#holder svg');
          if (!svg) return;
          svg.removeAttribute('width'); svg.removeAttribute('height');
          svg.style.width = '100%'; svg.style.height = 'auto';
          svg.setAttribute('preserveAspectRatio', 'xMinYMin meet');
        }}

        function runMermaid() {{
          mermaid.initialize({CONFIG});
          mermaid.run({{ nodes: [document.getElementById('mm')] }}).then(() => {{
            fitSVG();
            {AUTO_COLOR_ACTORS}
          }}).catch(e => {{
            document.getElementById('mm').innerHTML = '<pre style="color:#b00020;">' + e.toString() + '</pre>';
          }});
        }}

        function getSVGEl() {{ return document.querySelector('#holder svg'); }}

        function getSVGBlobAndXML() {{
          const svg = getSVGEl();
          if (!svg) return null;
          if (!svg.querySelector('rect.__bg__')) {{
            const r = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            const vb = svg.viewBox.baseVal;
            const pad = 8;
            r.setAttribute('x', vb.x - pad);
            r.setAttribute('y', vb.y - pad);
            r.setAttribute('width', vb.width + pad*2);
            r.setAttribute('height', vb.height + pad*2);
            r.setAttribute('fill', '#ffffff');
            r.setAttribute('class', '__bg__');
            svg.insertBefore(r, svg.firstChild);
          }}
          const clone = svg.cloneNode(true);
          clone.removeAttribute('style');
          const xml = new XMLSerializer().serializeToString(clone);
          return {{ xml, blob: new Blob([xml], {{ type: 'image/svg+xml;charset=utf-8' }}) }};
        }}

        function svgToCanvas(cb) {{
          const svg = getSVGEl();
          if (!svg) return;
          const vb = svg.viewBox.baseVal;
          const s = getSVGBlobAndXML();
          const url = URL.createObjectURL(s.blob);
          const img = new Image();
          img.onload = function() {{
            const scale = 3;
            const canvas = document.createElement('canvas');
            canvas.width = Math.max(1, Math.floor(vb.width * scale));
            canvas.height = Math.max(1, Math.floor(vb.height * scale));
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = '#ffffff'; ctx.fillRect(0,0,canvas.width,canvas.height);
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            URL.revokeObjectURL(url);
            cb(canvas);
          }};
          img.onerror = function(e) {{ console.error('SVG to image failed', e); URL.revokeObjectURL(url); }};
          img.src = url;
        }}

        function downloadSVG() {{
          const s = getSVGBlobAndXML();
          if (!s) return;
          const a = document.createElement('a');
          a.href = URL.createObjectURL(s.blob);
          a.download = 'diagram.svg';
          document.body.appendChild(a); a.click(); a.remove();
        }}

        function downloadPNG() {{
          svgToCanvas(canvas => {{
            const a = document.createElement('a');
            a.href = canvas.toDataURL('image/png');
            a.download = 'diagram.png';
            a.click();
          }});
        }}

        function openPNG() {{
          svgToCanvas(canvas => {{
            const url = canvas.toDataURL('image/png');
            window.open(url, '_blank');
          }});
        }}

        async function copySVG() {{
          const s = getSVGBlobAndXML();
          if (!s) return;
          try {{
            await navigator.clipboard.writeText(s.xml);
            alert('SVG XML copied. Paste into a vector-aware tool or save as .svg file.');
          }} catch (err) {{
            alert('Copy failed: ' + err);
          }}
        }}

        async function copyPNG() {{
          svgToCanvas(async (canvas) => {{
            try {{
              const blob = await new Promise(res => canvas.toBlob(res, 'image/png'));
              if (navigator.clipboard && window.ClipboardItem) {{
                await navigator.clipboard.write([new ClipboardItem({{'image/png': blob}})]);
                alert('PNG image copied to clipboard.');
              }} else {{
                const url = URL.createObjectURL(blob);
                window.open(url, '_blank');
              }}
            }} catch (err) {{
              alert('Copy PNG failed: ' + err);
            }}
          }});
        }}

        function fitNow() {{ fitSVG(); }}

        window.addEventListener('load', runMermaid);
        const ro = new ResizeObserver(() => fitSVG());
        ro.observe(document.getElementById('holder'));
      </script>
    </body>
    </html>
    '''
    html_str = html_tpl.format(
        FONT=tv["fontFamily"],
        PADDING=padding,
        ZOOM=zoom/100.0,
        LOADER=mermaid_loader,
        CONFIG=json.dumps(m_config),
        ESC=escaped,
        AUTO_COLOR_ACTORS="/* sequence only */" if not auto_color_actors else "/* sequence only */"
    )

    st.components.v1.html(html_str, height=preview_h, scrolling=True)
