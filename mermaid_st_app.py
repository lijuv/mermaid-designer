
# streamlit_app.py
# Mermaid Diagram Studio — clean render, fit-to-width preview, SVG/PNG export
# Run:
#   pip install streamlit
#   streamlit run streamlit_app.py

import streamlit as st
from textwrap import dedent
import html
import json

st.set_page_config(page_title="Mermaid Diagram Studio", layout="wide")

st.title("Mermaid Diagram Studio")
st.caption("Created by: LIJU VARGHESE")
st.caption("Type Mermaid code → Render → export SVG/PNG")

# ---------- Session State ----------
DEFAULT = dedent('''
    %% Examples: flowchart, sequenceDiagram, classDiagram, stateDiagram, erDiagram, journey, gantt
    flowchart LR
      A[Start] --> B{Auth?}
      B -- Valid --> C[Load profile]
      B -- Invalid --> E[Show error]
      C --> D[Dashboard]
      E --> B
''').strip()

if "code" not in st.session_state:
    st.session_state["code"] = DEFAULT
if "to_render" not in st.session_state:
    st.session_state["to_render"] = st.session_state["code"]

# ---------- Callbacks ----------
def set_template(txt: str):
    st.session_state["code"] = dedent(txt).strip()

def commit_render():
    st.session_state["to_render"] = st.session_state["code"]

# ---------- Sidebar Controls ----------
with st.sidebar:
    st.header("Style & Layout")
    preset = st.selectbox(
        "Palette",
        ["Neutral", "Brand Red", "Blue", "Teal"],
        index=0,
        help="All palettes keep a white canvas; only accents change."
    )
    font_family = st.text_input("Font family", "Inter, Segoe UI, Roboto, Helvetica, Arial, sans-serif")
    font_size = st.slider("Base font size (px)", 10, 24, 14)
    curve = st.selectbox("Flowchart curve", ["basis", "linear", "natural", "monotoneX", "monotoneY"], index=0)
    padding = st.slider("Canvas padding (px)", 0, 64, 16)
    zoom = st.slider("Zoom (%)", 80, 200, 100)
    preview_h = st.slider("Preview height (px)", 500, 1200, 780)

    st.divider()
    st.header("Script source")
    js_src = st.radio("Mermaid JS", ["CDN", "Upload file"], horizontal=True)
    js_file = None
    if js_src == "Upload file":
        js_file = st.file_uploader("Upload mermaid.min.js", type=["js"])

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
    }
    if preset_name == "Brand Red":
        base.update({
            "primaryColor": "#FFF5F6",
            "primaryTextColor": "#1D1D1D",
            "primaryBorderColor": "#D61A20",
            "lineColor": "#1D1D1D",
            "clusterBkg": "#FCFCFC",
            "clusterBorder": "#C9CFD6",
        })
    elif preset_name == "Blue":
        base.update({
            "primaryColor": "#F5F9FF",
            "primaryTextColor": "#0B2E59",
            "primaryBorderColor": "#99B8FF",
            "lineColor": "#0B2E59",
        })
    elif preset_name == "Teal":
        base.update({
            "primaryColor": "#F2FBFB",
            "primaryTextColor": "#075E5E",
            "primaryBorderColor": "#7FD1CC",
            "lineColor": "#0F6B6B",
        })
    return base

# ---------- Layout ----------
col1, col2 = st.columns([0.5, 0.5])

with col1:
    st.subheader("Editor")
    st.text_area("Mermaid code", key="code", height=360)
    with st.expander("Templates", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        c1.button("Flowchart", use_container_width=True, on_click=set_template, args=('''
            flowchart TD
              A[Idea] --> B(Design) --> C{Build?}
              C -->|Yes| D[Ship] --> E[Feedback] --> B
              C -->|No| B
        ''',))
        c2.button("Sequence", use_container_width=True, on_click=set_template, args=('''
            sequenceDiagram
              autonumber
              participant U as User
              participant A as App
              U->>A: Login
              A-->>U: JWT
              U->>A: Request data
              A-->>U: JSON payload
        ''',))
        c3.button("Class", use_container_width=True, on_click=set_template, args=('''
            classDiagram
              class Car{
                +vin: string
                +start()
                +stop()
              }
              class EV{
                +charge()
              }
              Car <|-- EV
        ''',))
        c4.button("State", use_container_width=True, on_click=set_template, args=('''
            stateDiagram-v2
              [*] --> Idle
              Idle --> Active: click
              Active --> Idle: timeout
              Active --> [*]
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
    config_json = json.dumps(m_config)

    if js_file is not None:
        mermaid_loader = "<script>" + js_file.getvalue().decode("utf-8", errors="ignore") + "</script>"
    else:
        mermaid_loader = '<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>'

    mermaid_code = st.session_state.get("to_render", st.session_state["code"])
    escaped = html.escape(mermaid_code)

    html_tpl = '''
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        :root {{
          --bg: #ffffff;
          --border: #e6e8eb;
        }}
        * {{ box-sizing: border-box; }}
        body {{
          margin: 0;
          padding: 0;
          background: var(--bg);
          font-family: {FONT};
        }}
        .wrap {{
          background: #ffffff;
          padding: {PADDING}px;
          border: 1px solid var(--border);
          border-radius: 14px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.06);
          overflow: hidden;
        }}
        .holder {{
          width: 100%;
          background: #ffffff;
        }}
        .holder svg {{
          display: block;
          width: 100% !important;
          height: auto !important;
          max-width: 100% !important;
        }}
        .actions {{
          display: flex; gap: 8px; margin: 10px 0 0 0; flex-wrap: wrap;
        }}
        .btn {{
          font-family: inherit;
          font-size: 13px;
          padding: 6px 10px;
          border: 1px solid var(--border);
          border-radius: 8px;
          background: #ffffff;
          cursor: pointer;
        }}
        .btn:hover {{ box-shadow: 0 1px 4px rgba(0,0,0,0.12); }}
        .zoom {{
          transform: scale({ZOOM});
          transform-origin: top left;
        }}
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
          <button class="btn" onclick="copySVG()">Copy SVG</button>
          <button class="btn" onclick="fitNow()">Fit to width</button>
        </div>
      </div>

      <script>
        function fitSVG() {{
          const svg = document.querySelector('#holder svg');
          if (!svg) return;
          svg.removeAttribute('width');
          svg.removeAttribute('height');
          svg.style.width = '100%';
          svg.style.height = 'auto';
          svg.setAttribute('preserveAspectRatio', 'xMinYMin meet');
        }}

        function runMermaid() {{
          mermaid.initialize({CONFIG});
          mermaid.run({{ nodes: [document.getElementById('mm')] }}).then(() => {{
            fitSVG();
          }}).catch(e => {{
            document.getElementById('mm').innerHTML = '<pre style="color:#b00020;">' + e.toString() + '</pre>';
          }});
        }}

        function getSVG() {{
          const svg = document.querySelector('#holder svg');
          if (!svg) return null;
          if (!svg.querySelector('rect.__bg__')) {{
            const r = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            const bbox = svg.getBBox();
            r.setAttribute('x', bbox.x - 8);
            r.setAttribute('y', bbox.y - 8);
            r.setAttribute('width', bbox.width + 16);
            r.setAttribute('height', bbox.height + 16);
            r.setAttribute('fill', '#ffffff');
            r.setAttribute('class', '__bg__');
            svg.insertBefore(r, svg.firstChild);
          }}
          const clone = svg.cloneNode(true);
          clone.removeAttribute('style');
          const xml = new XMLSerializer().serializeToString(clone);
          const svgBlob = new Blob([xml], {{ type: 'image/svg+xml;charset=utf-8' }});
          return {{ blob: svgBlob, xml }};
        }}

        function downloadSVG() {{
          const s = getSVG();
          if (!s) return;
          const a = document.createElement('a');
          a.href = URL.createObjectURL(s.blob);
          a.download = 'diagram.svg';
          document.body.appendChild(a);
          a.click();
          a.remove();
        }}

        function downloadPNG() {{
          const s = getSVG();
          if (!s) return;
          const img = new Image();
          const url = URL.createObjectURL(s.blob);
          img.onload = function() {{
            const canvas = document.createElement('canvas');
            const scaleFactor = 3;
            const w = img.width * scaleFactor;
            const h = img.height * scaleFactor;
            canvas.width = w;
            canvas.height = h;
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, w, h);
            ctx.drawImage(img, 0, 0, w, h);
            const a = document.createElement('a');
            a.href = canvas.toDataURL('image/png');
            a.download = 'diagram.png';
            a.click();
            URL.revokeObjectURL(url);
          }};
          img.src = url;
        }}

        async function copySVG() {{
          const s = getSVG();
          if (!s) return;
          try {{
            await navigator.clipboard.writeText(s.xml);
            alert('SVG copied to clipboard');
          }} catch (err) {{
            alert('Clipboard copy failed: ' + err);
          }}
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
        ESC=escaped
    )

    st.components.v1.html(html_str, height=preview_h, scrolling=True)
