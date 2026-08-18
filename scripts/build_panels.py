#!/usr/bin/env python3
"""Builds the editorial profile sheet. Run from the repo root."""
import base64, os, sys, xml.dom.minidom
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import *

ART = os.environ.get("ART_DIR", "art")
OUT = "assets"
b64 = lambda p: base64.b64encode(open(p, "rb").read()).decode()
esc = lambda t: str(t).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# ══════════════════════════ 01 · MASTHEAD ══════════════════════════
def masthead():
    uid, H = "a", 560
    face = b64(f"{ART}/face.jpg")
    PX, PY, PR = 900, 268, 152

    ticker = ("FULL-STACK DEVELOPER   ✦   UI/UX DESIGNER   ✦   TORONTO, CANADA   ✦   "
              "OPEN TO OPPORTUNITIES   ✦   ") * 3
    facts = [("BASED", "Toronto, CA"), ("FIELD", "Full-stack"),
             ("SHIPPED", "15 repos"), ("STATUS", "Available")]
    fact_svg = ""
    for i, (k, v) in enumerate(facts):
        x = grid(i * 1.62)
        fact_svg += (rule(x, H - 96, x + COL * 1.35)
                     + label(uid, x, H - 76, k)
                     + f'<text class="d{uid}" x="{x}" y="{H-48}" font-size="20" font-weight="600" '
                       f'letter-spacing="-.3" fill="{INK}">{esc(v)}</text>')

    body = f'''
  <g clip-path="url(#tick{uid})">
    <text class="m{uid} tk{uid}" x="0" y="34" font-size="10.5" letter-spacing="3.4" fill="{INK35}">{ticker}</text>
  </g>
  {rule(0, 52, W)}

  {label(uid, MARGIN, 96, "PORTFOLIO / 2026", RED)}
  {label(uid, W-MARGIN, 96, "NO. 01", INK35, anchor="end")}

  <text class="d{uid}" x="{MARGIN-8}" y="252" font-size="146" font-weight="800" letter-spacing="-7" fill="{INK}">TANVIR</text>
  <text class="d{uid}" x="{MARGIN-8}" y="374" font-size="146" font-weight="800" letter-spacing="-7" fill="{RED}">RAFI</text>

  <g>
    <rect x="{MARGIN}" y="410" width="34" height="3" fill="{INK}"/>
    <text class="d{uid}" x="{MARGIN+52}" y="418" font-size="17" font-weight="500" letter-spacing="-.2" fill="{INK60}">
      I build interfaces that stay fast under load.
    </text>
  </g>

  <g>
    <clipPath id="pc{uid}"><circle cx="{PX}" cy="{PY}" r="{PR}"/></clipPath>
    <circle cx="{PX}" cy="{PY}" r="{PR+16}" fill="{PAPER2}"/>
    <g clip-path="url(#pc{uid})">
      <image href="data:image/jpeg;base64,{face}" x="{PX-PR}" y="{PY-PR}" width="{PR*2}" height="{PR*2}"
             preserveAspectRatio="xMidYMid slice" filter="url(#duo{uid})"/>
      <rect class="ht{uid}" x="{PX-PR}" y="{PY-PR}" width="{PR*2}" height="{PR*2}" fill="url(#dots{uid})" opacity=".5"/>
    </g>
    <circle cx="{PX}" cy="{PY}" r="{PR}" fill="none" stroke="{INK}" stroke-width="1.5"/>
    <circle class="soft{uid}" cx="{PX-PR-16}" cy="{PY}" r="5" fill="{RED}"/>
    {label(uid, PX, PY+PR+52, "OPERATOR — TANVIR MAHMUD RAFI", INK35, anchor="middle")}
  </g>

  {fact_svg}
  {rule(MARGIN, H-24, W-MARGIN, INK, 2)}'''

    xd = f'''
  <filter id="duo{uid}" color-interpolation-filters="sRGB">
    <feColorMatrix type="saturate" values="0"/>
    <feComponentTransfer>
      <feFuncR type="table" tableValues="0.87 0.96"/>
      <feFuncG type="table" tableValues="0.16 0.94"/>
      <feFuncB type="table" tableValues="0.03 0.89"/>
    </feComponentTransfer>
  </filter>
  <pattern id="dots{uid}" width="4" height="4" patternUnits="userSpaceOnUse">
    <circle cx="1" cy="1" r=".85" fill="{PAPER}" opacity=".55"/>
  </pattern>
  <clipPath id="tick{uid}"><rect x="0" y="0" width="{W}" height="52"/></clipPath>'''

    xc = f'''
    @keyframes tk{uid} {{ 0% {{ transform:translateX(0) }} 100% {{ transform:translateX(-770px) }} }}
    @keyframes ht{uid} {{ 0%,100% {{ transform:translate(0,0) }} 50% {{ transform:translate(2px,2px) }} }}
    .tk{uid} {{ animation:tk{uid} 26s linear infinite }}
    .ht{uid} {{ animation:ht{uid} 5s ease-in-out infinite }}'''
    return panel(uid, H, body, xd, xc, seam=False)


# ══════════════════════════ 03 · INDEX (skills) ══════════════════════════
INDEX = [
    ("FRONT OF HOUSE", [("React",4),("JavaScript",4),("TypeScript",3),("HTML & CSS",5),
                        ("Tailwind",4),("Figma",3)]),
    ("BACK OF HOUSE",  [("Node.js",3),("Express",3),("PostgreSQL",3),("MongoDB",3),
                        ("MySQL",3),("Java",3)]),
    ("WORKSHOP",       [("Git",4),("Vite",4),("Vercel",3),("Firebase",2),
                        ("Unity",2),("PHP",2)]),
]


def index_panel():
    uid, H = "b", 452
    colw = (W - MARGIN*2 - 56*2) / 3
    body = (label(uid, MARGIN, 46, "INDEX", RED)
            + label(uid, W-MARGIN, 46, "NO. 03", INK35, anchor="end")
            + f'<text class="d{uid}" x="{MARGIN-4}" y="118" font-size="62" font-weight="800" '
              f'letter-spacing="-3" fill="{INK}">What I use</text>'
            + rule(MARGIN, 150, W-MARGIN, INK, 2))
    for ci, (cat, items) in enumerate(INDEX):
        cx = MARGIN + ci * (colw + 56)
        body += label(uid, cx, 186, cat, INK)
        body += rule(cx, 198, cx + colw)
        for si, (name, lv) in enumerate(items):
            y = 232 + si * 36
            dots = "".join(
                f'<circle cx="{cx+colw-52+d*13}" cy="{y-5}" r="2.6" '
                f'fill="{RED if d < lv else RULE}"'
                + (f'><animate attributeName="opacity" values="1;.35;1" keyTimes="0;.5;1" '
                   f'dur="3s" begin="{(ci*.4+si*.18+d*.1)%3:.2f}s" repeatCount="indefinite"/></circle>'
                   if d < lv else '/>')
                for d in range(5))
            body += (f'<text class="d{uid}" x="{cx}" y="{y}" font-size="16" font-weight="500" '
                     f'letter-spacing="-.2" fill="{INK}">{esc(name)}</text>'
                     + dots
                     + rule(cx, y + 13, cx + colw, PAPER2))
    return panel(uid, H, body)


# ══════════════════════════ 04 · WORK ══════════════════════════
WORK = [
    ("01","AI Resume Builder","TypeScript · React · PostgreSQL",
     ["Generates, formats and tailors résumés","with real-time AI suggestions."],RED),
    ("02","Portfolio","React 19 · Vite 7 · Lenis",
     ["Boot sequence, command palette,","particle field, custom cursor."],INK),
    ("03","EcoWorld","Node · Express · PostgreSQL",
     ["Climate-solutions platform built on","REST routes and a Postgres store."],BLUE),
    ("04","Photobooth","Electron · JavaScript",
     ["Desktop photobooth with live filters","and retro printed photo strips."],RED),
    ("05","NieR: Automata","HTML · CSS · JavaScript",
     ["Cinematic tribute site — atmospheric","visuals and long fluid motion."],INK),
    ("06","Classified","—",
     ["Next build in progress.","Something is compiling."],INK35),
]
CW, CH = 600, 234


def work_card(num, title, stack, lines, accent):
    uid = f"w{num}"
    body = "".join(f'<text class="d{uid}" x="46" y="{140+i*24}" font-size="14.5" font-weight="400" '
                   f'letter-spacing="-.1" fill="{INK60}">{esc(l)}</text>' for i, l in enumerate(lines))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}" role="img" aria-label="{title}">
<title>{title}</title>
<defs>
  <linearGradient id="bd{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{accent}" stop-opacity="0"/>
    <stop offset="50%" stop-color="{accent}" stop-opacity=".06"/>
    <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
  </linearGradient>
  <style><![CDATA[
    .d{uid} {{ font-family:{DISP} }} .m{uid} {{ font-family:{MONO} }}
    @keyframes bd{uid} {{ 0% {{ transform:translateX(-260px) }} 100% {{ transform:translateX({CW+40}px) }} }}
    @keyframes ar{uid} {{ 0%,100% {{ transform:translateX(0) }} 50% {{ transform:translateX(7px) }} }}
    .bd{uid} {{ animation:bd{uid} 6.5s cubic-bezier(.45,0,.25,1) infinite }}
    .ar{uid} {{ animation:ar{uid} 2.1s ease-in-out infinite }}
  ]]></style>
</defs>
<rect width="{CW}" height="{CH}" fill="{PAPER}"/>
<rect class="bd{uid}" x="0" y="0" width="260" height="{CH}" fill="url(#bd{uid})"/>
<path d="M0 .5 H{CW}" stroke="{RULE}"/><path d="M.5 0 V{CH}" stroke="{RULE}"/>
<text class="d{uid}" x="46" y="74" font-size="46" font-weight="800" letter-spacing="-2" fill="{accent}" opacity=".22">{num}</text>
<text class="d{uid}" x="118" y="74" font-size="27" font-weight="700" letter-spacing="-1" fill="{INK}">{esc(title)}</text>
<path d="M46 92 H{CW-46}" stroke="{RULE}"/>
<text class="d{uid}" x="46" y="116" font-size="9.5" font-weight="600" letter-spacing="2.4" fill="{accent}">{esc(stack)}</text>
{body}
<g class="ar{uid}"><path d="M{CW-72} {CH-46} h26 m-7 -7 l7 7 l-7 7" stroke="{INK}" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>
<text class="d{uid}" x="46" y="{CH-40}" font-size="9.5" font-weight="600" letter-spacing="2.4" fill="{INK35}">VIEW PROJECT</text>
</svg>'''


# ══════════════════════════ 05 · COLOPHON ══════════════════════════
LINKS = [("portfolio","PORTFOLIO","tanvirrafi.vercel.app"),
         ("email","EMAIL","tmrafi@myseneca.ca"),
         ("github","GITHUB","Tanvir-Rafi03"),
         ("linkedin","LINKEDIN","connect")]
LW, LH = 300, 132


def link_tile(slug, label_txt, value):
    uid = f"l{slug}"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{LW}" height="{LH}" viewBox="0 0 {LW} {LH}" role="img" aria-label="{label_txt} {value}">
<title>{label_txt} — {value}</title>
<defs>
  <linearGradient id="bd{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{RED}" stop-opacity="0"/><stop offset="50%" stop-color="{RED}" stop-opacity=".08"/>
    <stop offset="100%" stop-color="{RED}" stop-opacity="0"/></linearGradient>
  <style><![CDATA[
    .d{uid} {{ font-family:{DISP} }}
    @keyframes bd{uid} {{ 0% {{ transform:translateX(-150px) }} 100% {{ transform:translateX({LW+30}px) }} }}
    @keyframes ar{uid} {{ 0%,100% {{ transform:translateX(0) }} 50% {{ transform:translateX(6px) }} }}
    .bd{uid} {{ animation:bd{uid} 5.5s cubic-bezier(.45,0,.25,1) infinite }}
    .ar{uid} {{ animation:ar{uid} 2s ease-in-out infinite }}
  ]]></style>
</defs>
<rect width="{LW}" height="{LH}" fill="{INK}"/>
<rect class="bd{uid}" x="0" y="0" width="150" height="{LH}" fill="url(#bd{uid})"/>
<path d="M.5 0 V{LH}" stroke="#2e2a26"/>
<text class="d{uid}" x="34" y="52" font-size="9.5" font-weight="600" letter-spacing="2.6" fill="{RED}">{label_txt}</text>
<text class="d{uid}" x="34" y="82" font-size="15" font-weight="500" letter-spacing="-.2" fill="{PAPER}">{esc(value)}</text>
<g class="ar{uid}"><path d="M{LW-58} 74 h22 m-6 -6 l6 6 l-6 6" stroke="{PAPER}" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>
</svg>'''


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    files = {"01-masthead.svg": masthead(), "03-index.svg": index_panel()}
    for w in WORK:
        files[f"work-{w[0]}.svg"] = work_card(*w)
    for l in LINKS:
        files[f"link-{l[0]}.svg"] = link_tile(*l)
    for n, s in files.items():
        p = os.path.join(OUT, n); open(p, "w").write(s); xml.dom.minidom.parse(p)
    print(f"built {len(files)} panels, all XML valid")
