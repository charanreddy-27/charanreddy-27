#!/usr/bin/env python3
"""Generate the profile banner (assets/hero-dark.svg, assets/hero-light.svg).

Design rules, learned from what the previous banner got wrong:

  * Everything legible is painted at t=0. The old banner faded its entire info
    panel in over ~4s, so anyone landing on the profile saw an empty rectangle
    for the first few seconds. Motion here is decoration only — remove every
    <animate> and the banner still reads correctly.
  * No dead space. The old one was 1180x610 with a 40%-wide column of
    illegible ASCII; this is 1180x360 and every band carries content.
  * No external fonts. GitHub renders these through its image proxy, so only
    generic families resolve.
  * No anchors. GitHub strips links from rendered SVG — clickable things have
    to be badges in the README.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from palettes import get, PALETTES

W, H = 1180, 360
MONO = "ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace"
SANS = "-apple-system,BlinkMacSystemFont,Segoe UI,Noto Sans,Helvetica,Arial,sans-serif"

NAME = "Chanda Charan Reddy"
KICKER = "AI  ·  AUTOMATION  ·  DEVELOPER TOOLING"
LEDE = "I build production LLM systems."
SUB1 = "Multimodal input in, executable BPMN 2.0 out."
SUB2 = "Springer-published in deep learning. Ex-DRDO."
META = [
    ("NOW", "AI Intern · Infineon Technologies"),
    ("BASE", "Bengaluru, India"),
    ("EDU", "B.Tech CSE (Data Science) · Christ University"),
]
STACK = "Python · TypeScript · PyTorch · LangChain · FastAPI · Postgres · Redis · Docker · OpenShift · AWS"


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def code_lines(c):
    """(text, colour) segments per line of the little pipeline.py panel."""
    kw, st, fn, id_, cm, op = c["accent2"], c["ok"], c["accent"], c["text"], c["dim"], c["muted"]
    return [
        [("from", kw), (" agent ", id_), ("import", kw), (" Planner, Retriever", id_)],
        [],
        [("pipe", id_), (" = ", op), ("(", op), ("Planner", fn), ("(", op), ("model", id_), ("=", op), ('"claude"', st), (")", op)],
        [("        | ", op), ("Retriever", fn), ("(", op), ("store", id_), ("=", op), ('"pgvector"', st), (")", op)],
        [("        | ", op), ("Synthesizer", fn), ("(", op), ("cite", id_), ("=", op), ("True", kw), ("))", op)],
        [],
        [("# sketch, prose, diagram -> workflow", cm)],
        [("model", id_), (" = ", op), ("pipe", id_), (".", op), ("run", fn), ("(", op), ("sketch", id_), (")", op)],
    ]


def build(pal_name, mode):
    c = get(pal_name, mode)
    dark = mode == "dark"
    o = []
    a = o.append

    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
      f'fill="none" role="img" aria-label="{esc(NAME)} — {esc(LEDE)}">')
    a(f'<title>{esc(NAME)} · {esc(LEDE)} · Bengaluru, India</title>')

    # ---- defs -------------------------------------------------------------
    a('<defs>')
    a(f'<clipPath id="card"><rect x="6" y="6" width="{W-12}" height="{H-12}" rx="18"/></clipPath>')
    a(f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
      f'<stop offset="0" stop-color="{c["bg"]}"/>'
      f'<stop offset=".5" stop-color="{c["panel"]}"/>'
      f'<stop offset="1" stop-color="{c["bg"]}"/></linearGradient>')
    # slow accent sweep along the hairline at the top of the card
    a(f'<linearGradient id="sweep" gradientUnits="userSpaceOnUse" x1="-460" y1="0" x2="0" y2="0">'
      f'<stop offset="0" stop-color="{c["accent"]}" stop-opacity="0"/>'
      f'<stop offset=".5" stop-color="{c["accent"]}" stop-opacity="{".95" if dark else ".8"}"/>'
      f'<stop offset="1" stop-color="{c["accent"]}" stop-opacity="0"/>'
      f'<animateTransform attributeName="gradientTransform" type="translate" '
      f'values="0 0;{W+520} 0" dur="6s" repeatCount="indefinite"/></linearGradient>')
    a(f'<radialGradient id="glow" cx=".5" cy=".5" r=".5">'
      f'<stop offset="0" stop-color="{c["accent"]}" stop-opacity="{"0.16" if dark else "0.10"}"/>'
      f'<stop offset="1" stop-color="{c["accent"]}" stop-opacity="0"/></radialGradient>')
    a('<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
      f'<circle cx="1.2" cy="1.2" r="1.2" fill="{c["text"]}" opacity="{"0.05" if dark else "0.06"}"/></pattern>')
    a('</defs>')

    # ---- card -------------------------------------------------------------
    a('<g clip-path="url(#card)">')
    a(f'<rect x="6" y="6" width="{W-12}" height="{H-12}" fill="url(#bg)"/>')
    a(f'<rect x="6" y="6" width="{W-12}" height="{H-12}" fill="url(#dots)"/>')
    a(f'<ellipse cx="150" cy="70" rx="420" ry="260" fill="url(#glow)"/>')
    a(f'<rect x="6" y="6" width="{W-12}" height="2.5" fill="url(#sweep)"/>')
    a('</g>')
    a(f'<rect x="6.5" y="6.5" width="{W-13}" height="{H-13}" rx="18" fill="none" '
      f'stroke="{c["line"]}" stroke-width="1"/>')

    L = 46          # left gutter
    # ---- kicker -----------------------------------------------------------
    a(f'<circle cx="{L+4}" cy="52" r="4" fill="{c["accent"]}">'
      f'<animate attributeName="opacity" values="1;.25;1" dur="2.4s" repeatCount="indefinite"/></circle>')
    a(f'<text x="{L+20}" y="57" font-family="{MONO}" font-size="11.5" letter-spacing="2.2" '
      f'fill="{c["accent"]}" font-weight="600">{esc(KICKER)}</text>')

    # ---- name -------------------------------------------------------------
    a(f'<text x="{L}" y="112" font-family="{SANS}" font-size="42" font-weight="700" '
      f'letter-spacing="-1" fill="{c["text"]}">{esc(NAME)}</text>')

    # ---- lede -------------------------------------------------------------
    a(f'<text x="{L}" y="150" font-family="{SANS}" font-size="18" font-weight="600" '
      f'fill="{c["accent2"]}">{esc(LEDE)}</text>')
    a(f'<text x="{L}" y="176" font-family="{SANS}" font-size="14.5" fill="{c["muted"]}">{esc(SUB1)}</text>')
    a(f'<text x="{L}" y="197" font-family="{SANS}" font-size="14.5" fill="{c["muted"]}">{esc(SUB2)}</text>')

    # ---- meta rows --------------------------------------------------------
    y = 236
    for label, value in META:
        a(f'<text x="{L}" y="{y}" font-family="{MONO}" font-size="10.5" letter-spacing="1.4" '
          f'fill="{c["dim"]}">{esc(label)}</text>')
        a(f'<text x="{L+52}" y="{y}" font-family="{SANS}" font-size="13.5" '
          f'fill="{c["text"]}" opacity=".92">{esc(value)}</text>')
        y += 23

    # ---- bottom strip -----------------------------------------------------
    a(f'<line x1="{L}" y1="303" x2="{W-46}" y2="303" stroke="{c["line"]}" stroke-width="1"/>')
    a(f'<text x="{L}" y="329" font-family="{MONO}" font-size="11.5" letter-spacing=".3" '
      f'fill="{c["dim"]}">{esc(STACK)}</text>')
    a(f'<text x="{W-46}" y="329" text-anchor="end" font-family="{MONO}" font-size="11.5" '
      f'fill="{c["muted"]}">github.com/charanreddy-27<tspan fill="{c["dim"]}">  ·  </tspan>'
      f'<tspan fill="{c["accent"]}">charanreddy.dev</tspan></text>')

    # ---- code panel -------------------------------------------------------
    px, py, pw, ph = 686, 38, 448, 246
    a(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12" fill="{c["panel2"]}" '
      f'stroke="{c["line"]}" stroke-width="1"/>')
    a(f'<line x1="{px}" y1="{py+32}" x2="{px+pw}" y2="{py+32}" stroke="{c["line"]}" stroke-width="1"/>')
    for i, col in enumerate([c["accent2"], c["accent"], c["ok"]]):
        a(f'<circle cx="{px+20+i*16}" cy="{py+16}" r="4.5" fill="{col}" opacity=".85"/>')
    a(f'<text x="{px+pw-18}" y="{py+20}" text-anchor="end" font-family="{MONO}" font-size="11" '
      f'fill="{c["dim"]}">pipeline.py</text>')

    cx0, cy0, fs, lh = px + 20, py + 58, 12.5, 21
    chw = fs * 0.6
    for li, segs in enumerate(code_lines(c)):
        yy = cy0 + li * lh
        x = cx0
        for txt, col in segs:
            a(f'<text x="{x:.1f}" y="{yy}" font-family="{MONO}" font-size="{fs}" '
              f'fill="{col}" xml:space="preserve">{esc(txt)}</text>')
            x += len(txt) * chw
        if li == 7:  # blinking cursor after the last statement
            a(f'<rect x="{x+2:.1f}" y="{yy-10}" width="7" height="13" fill="{c["accent"]}">'
              f'<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" repeatCount="indefinite"/></rect>')

    a('</svg>')
    return "\n".join(o)


if __name__ == "__main__":
    pal = sys.argv[1] if len(sys.argv) > 1 else "ember"
    outdir = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else
                          pathlib.Path(__file__).parent.parent / "assets")
    outdir.mkdir(parents=True, exist_ok=True)
    assert pal in PALETTES, f"unknown palette {pal!r}; have {list(PALETTES)}"
    for mode in ("dark", "light"):
        p = outdir / f"hero-{mode}.svg"
        p.write_text(build(pal, mode))
        print(f"{p}  {p.stat().st_size/1024:.1f} KB")
