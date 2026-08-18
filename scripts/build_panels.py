#!/usr/bin/env python3
"""Builds every panel of the profile page. Run from the repo root."""
import base64, os, random, sys, xml.dom.minidom
sys.path.insert(0, os.path.dirname(__file__))
from design import *

ART = os.environ.get("ART_DIR", "art")
OUT = "assets"
b64 = lambda p: base64.b64encode(open(p, "rb").read()).decode()


# ─────────────────────────── 01 · OPERATOR ───────────────────────────
def hero():
    uid, H = "h", 460
    PX, PY, PR = 985, 250, 108
    city, face = b64(f"{ART}/hero.jpg"), b64(f"{ART}/face.jpg")

    random.seed(11)
    rain = "".join(
        f'<line class="rn{uid}" x1="{random.randint(-40,1240)}" y1="-70" '
        f'x2="{random.randint(-40,1240)-13}" y2="{-70+random.randint(26,58)}" stroke="#bfe9ff" '
        f'stroke-opacity="{random.uniform(.10,.28):.2f}" stroke-width="1.1" '
        f'style="animation-delay:{random.uniform(0,1.9):.2f}s;animation-duration:{random.uniform(1.1,2.0):.2f}s"/>'
        for _ in range(44))
    ticks = "".join(
        f'<rect x="{PX-.9}" y="{PY-PR-20}" width="1.8" height="{7 if i%3 else 12}" rx=".9" '
        f'fill="{CYAN}" opacity="{.8 if i%3==0 else .35}" transform="rotate({i*7.5} {PX} {PY})"/>'
        for i in range(48))

    XP, XPMAX, LVL = 354, 500, 15
    xpw = 430 * XP / XPMAX

    stats = [("COMMITS", "354"), ("REPOS", "15"), ("STREAK", "5"), ("UPTIME", "100%")]
    stat_svg = "".join(
        f'<text class="f{uid}" x="{PAD+i*118}" y="392" font-size="9.5" letter-spacing="3" fill="{DIM}">{k}</text>'
        f'<text class="f{uid}" x="{PAD+i*118}" y="372" font-size="19" font-weight="700" letter-spacing="1" fill="{INK}">{v}</text>'
        for i, (k, v) in enumerate(stats))

    inner = f'''
  <g>{rain}</g>
  <rect width="{W}" height="{H}" fill="url(#scrim{uid})"/>

  <text class="f{uid}" x="{PAD}" y="122" font-size="12" letter-spacing="6" fill="{GREEN}">// OPERATOR_DOSSIER</text>
  <g>
    <text class="f{uid} ga{uid}" x="{PAD}" y="212" font-size="76" font-weight="700" letter-spacing="2" fill="{ROSE}">TANVIR RAFI</text>
    <text class="f{uid} gb{uid}" x="{PAD}" y="212" font-size="76" font-weight="700" letter-spacing="2" fill="{CYAN}">TANVIR RAFI</text>
    <text class="f{uid}"        x="{PAD}" y="212" font-size="76" font-weight="700" letter-spacing="2" fill="{INK}"
          style="filter:drop-shadow(0 3px 16px rgba(3,0,15,.98))">TANVIR RAFI</text>
  </g>
  <text class="f{uid}" x="{PAD}" y="248" font-size="16" letter-spacing="3" fill="{VIOLET}">CLASS</text>
  <text class="f{uid}" x="{PAD+74}" y="248" font-size="16" letter-spacing="1.5" fill="#dcecfa">FULL-STACK DEVELOPER &#183; UI/UX DESIGNER</text>

  <g>
    <rect x="{PAD}" y="286" width="66" height="26" rx="4" fill="{GOLD}" fill-opacity=".16" stroke="{GOLD}" stroke-opacity=".7"/>
    <text class="f{uid}" x="{PAD+33}" y="304" font-size="13" font-weight="700" letter-spacing="1" fill="{GOLD}" text-anchor="middle">LVL {LVL}</text>
    <rect x="{PAD+80}" y="293" width="430" height="12" rx="6" fill="#0d1a30" stroke="{GOLD}" stroke-opacity=".28"/>
    <rect x="{PAD+80}" y="293" width="{xpw:.0f}" height="12" rx="6" fill="url(#xp{uid})">
      <animate attributeName="width" from="0" to="{xpw:.0f}" dur="2.1s" begin="0s" fill="freeze"
               calcMode="spline" keySplines="0.2 0.85 0.3 1" keyTimes="0;1"/>
    </rect>
    <text class="f{uid}" x="{PAD+522}" y="303" font-size="10.5" letter-spacing="2" fill="{GOLD}" opacity=".85">{XP} / {XPMAX} XP</text>
  </g>

  <path d="M{PAD} 340 H{PAD+470}" stroke="{CYAN}" stroke-opacity=".16"/>
  {stat_svg}

  <g>
    <circle class="ha{uid}" cx="{PX}" cy="{PY}" r="118" fill="none" stroke="{CYAN}" stroke-width="1.5" opacity=".3"/>
    <circle cx="{PX}" cy="{PY}" r="{PR+7}" fill="{BG0}" opacity=".6"/>
    <g clip-path="url(#pc{uid})">
      <image href="data:image/jpeg;base64,{face}" x="{PX-PR}" y="{PY-PR}" width="{PR*2}" height="{PR*2}" preserveAspectRatio="xMidYMid slice"/>
      <image class="sl{uid}" href="data:image/jpeg;base64,{face}" x="{PX-PR}" y="{PY-PR}" width="{PR*2}" height="{PR*2}"
             preserveAspectRatio="xMidYMid slice" opacity="0" style="mix-blend-mode:screen"/>
      <rect x="{PX-PR}" y="{PY-PR}" width="{PR*2}" height="{PR*2}" fill="url(#pl{uid})"/>
      <rect class="sp{uid}" x="{PX-PR}" y="{PY-42}" width="{PR*2}" height="84" fill="url(#ps{uid})" opacity=".5"/>
    </g>
    <circle cx="{PX}" cy="{PY}" r="{PR}" fill="none" stroke="{CYAN}" stroke-width="2.4" opacity=".9"/>
    <circle cx="{PX}" cy="{PY}" r="{PR+14}" fill="none" stroke="{VIOLET}" stroke-width="1.2" opacity=".55"
            stroke-dasharray="24 14" stroke-linecap="round">
      <animateTransform attributeName="transform" type="rotate" from="0 {PX} {PY}" to="360 {PX} {PY}" dur="24s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{PX}" cy="{PY}" r="{PR+27}" fill="none" stroke="{GOLD}" stroke-width="1" opacity=".4"
            stroke-dasharray="4 28" stroke-linecap="round">
      <animateTransform attributeName="transform" type="rotate" from="360 {PX} {PY}" to="0 {PX} {PY}" dur="32s" repeatCount="indefinite"/>
    </circle>
    <g opacity=".5">{ticks}</g>
    <g stroke="{CYAN}" stroke-width="2.2" fill="none" opacity=".95" filter="url(#gl{uid})">
      <path d="M{PX-PR-28} {PY-60} V{PY-PR-28} H{PX-60}"/><path d="M{PX+60} {PY-PR-28} H{PX+PR+28} V{PY-60}"/>
      <path d="M{PX-PR-28} {PY+60} V{PY+PR+28} H{PX-60}"/><path d="M{PX+PR+28} {PY+60} V{PY+PR+28} H{PX+60}"/>
    </g>
    <rect x="{PX-66}" y="{PY+PR+36}" width="132" height="26" rx="4" fill="{BG0}" fill-opacity=".85" stroke="{GREEN}" stroke-opacity=".55"/>
    <circle class="pu{uid}" cx="{PX-46}" cy="{PY+PR+49}" r="4" fill="{GREEN}"/>
    <text class="f{uid}" x="{PX-34}" y="{PY+PR+54}" font-size="10.5" letter-spacing="2.2" fill="{GREEN}">ONLINE &#183; READY</text>
  </g>'''

    extra_css = f'''
    @keyframes rn{uid} {{ 0%{{transform:translateY(0)}} 100%{{transform:translateY(560px)}} }}
    @keyframes ha{uid} {{ 0%,100%{{opacity:.28}} 50%{{opacity:.6}} }}
    @keyframes ga{uid} {{ 0%,86%,100%{{transform:translate(0,0);opacity:0}} 88%{{transform:translate(-5px,2px);opacity:.9}} 92%{{transform:translate(4px,-2px);opacity:.6}} 96%{{transform:translate(-2px,0);opacity:.7}} }}
    @keyframes gb{uid} {{ 0%,86%,100%{{transform:translate(0,0);opacity:0}} 89%{{transform:translate(5px,-2px);opacity:.85}} 93%{{transform:translate(-4px,2px);opacity:.5}} 97%{{transform:translate(3px,0);opacity:.65}} }}
    @keyframes sl{uid} {{ 0%,80%,100%{{opacity:0;transform:translateX(0)}} 84%{{opacity:.8;transform:translateX(-11px)}} 88%{{opacity:.65;transform:translateX(9px)}} 93%{{opacity:.45;transform:translateX(-5px)}} }}
    @keyframes sp{uid} {{ 0%{{transform:translateY(-230px)}} 100%{{transform:translateY(230px)}} }}
    .rn{uid} {{ animation-name:rn{uid}; animation-timing-function:linear; animation-iteration-count:infinite }}
    .ha{uid} {{ animation:ha{uid} 3.4s ease-in-out infinite }}
    .ga{uid} {{ animation:ga{uid} 6s steps(1) infinite }}
    .gb{uid} {{ animation:gb{uid} 6s steps(1) infinite }}
    .sl{uid} {{ animation:sl{uid} 5s steps(1) infinite }}
    .sp{uid} {{ animation:sp{uid} 3.6s cubic-bezier(.5,0,.5,1) infinite }}'''

    extra_defs = f'''
  <linearGradient id="scrim{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{BG0}" stop-opacity=".86"/>
    <stop offset="45%" stop-color="{BG0}" stop-opacity=".58"/>
    <stop offset="74%" stop-color="{BG0}" stop-opacity=".24"/>
    <stop offset="100%" stop-color="{BG0}" stop-opacity=".6"/>
  </linearGradient>
  <linearGradient id="xp{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{GOLD}"/><stop offset="100%" stop-color="#ff7a00"/>
  </linearGradient>
  <linearGradient id="ps{uid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{CYAN}" stop-opacity="0"/>
    <stop offset="50%" stop-color="#ffffff" stop-opacity=".7"/>
    <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
  </linearGradient>
  <pattern id="pl{uid}" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1.4" fill="#00131f" opacity=".36"/></pattern>
  <clipPath id="pc{uid}"><circle cx="{PX}" cy="{PY}" r="{PR}"/></clipPath>'''

    rail = (f'<rect x="{RAIL}" y="0" width="1.4" height="{H}" fill="url(#rail{uid})"/>'
            + "".join(f'<rect x="{RAIL-13}" y="{y}" width="{9 if y%60 else 15}" height="1.4" '
                      f'fill="{CYAN}" opacity="{.42 if y%60 else .8}"/>' for y in range(24, H-12, 20))
            + f'<text class="f{uid}" x="{RAIL-30}" y="{H/2}" font-size="20" font-weight="700" '
              f'letter-spacing="4" fill="{CYAN}" opacity=".85" text-anchor="middle" '
              f'transform="rotate(-90 {RAIL-30} {H/2})">01</text>')
    inner = inner + rail
    svg = shell(uid, H, "01", "", "", (inner, extra_css),
                bg_extra=f'<image href="data:image/jpeg;base64,{city}" x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>',
                head=False)
    return svg.replace(f"<defs>{defs(uid, H)}", f"<defs>{defs(uid, H)}{extra_defs}")


# ─────────────────────────── 02 · LOADOUT ───────────────────────────
LOADOUT = [
    ("FRONTEND", CYAN, [("React",4),("JavaScript",4),("HTML5",5),("CSS3",5),
                        ("Tailwind",4),("TypeScript",3),("Figma",3)]),
    ("BACKEND",  VIOLET,[("Node.js",3),("Express",3),("PostgreSQL",3),("MongoDB",3),
                        ("MySQL",3),("Java",3),("PHP",2)]),
    ("TOOLING",  GOLD,  [("Git",4),("GitHub",4),("Vite",4),("Vercel",3),
                        ("Firebase",2),("Unity",2)]),
]
TIER = {1:"E",2:"D",3:"B",4:"A",5:"S"}


def loadout():
    uid, H = "l", 400
    colw, gap = 336, 22
    body, n = [], 0
    for ci,(cat, col, skills) in enumerate(LOADOUT):
        cx = PAD + ci*(colw+gap)
        body.append(f'<text class="f{uid}" x="{cx}" y="140" font-size="12" font-weight="700" letter-spacing="4" fill="{col}">{cat}</text>')
        body.append(f'<path d="M{cx} 150 H{cx+colw}" stroke="{col}" stroke-opacity=".3"/>')
        for si,(name, lv) in enumerate(skills):
            y = 178 + si*32
            body.append(f'<text class="f{uid}" x="{cx}" y="{y}" font-size="12.5" fill="#cfe3f5">{name}</text>')
            # tier badge
            body.append(f'<rect x="{cx+colw-26}" y="{y-13}" width="22" height="18" rx="3" fill="{col}" fill-opacity=".16" stroke="{col}" stroke-opacity=".5"/>')
            body.append(f'<text class="f{uid}" x="{cx+colw-15}" y="{y}" font-size="11" font-weight="700" fill="{col}" text-anchor="middle">{TIER[lv]}</text>')
            # 5 pips, filled to level
            for p in range(5):
                px = cx + colw - 164 + p*22
                on = p < lv
                body.append(
                    f'<rect x="{px}" y="{y-11}" width="16" height="7" rx="2" '
                    f'fill="{col if on else "#12233a"}" opacity="{.95 if on else 1}">'
                    + (f'<animate attributeName="opacity" values=".95;.3;.95" keyTimes="0;0.5;1" '
                       f'dur="2.8s" begin="{(n*0.07 + p*0.12) % 2.8:.2f}s" repeatCount="indefinite"/>' if on else '')
                    + '</rect>')
            n += 1
    inner = ("".join(body), "")
    return shell(uid, H, "02", "TECH_STACK", "LOADOUT", inner)


# ─────────────────────────── 04 · MISSION CARDS ───────────────────────────
MISSIONS = [
    ("01","AI RESUME BUILDER",CYAN,"LEGENDARY",
     ["AI-powered resume generation,","formatting and tailoring with","real-time suggestions."],
     ["TypeScript","React","PostgreSQL"],"DEPLOYED"),
    ("02","PORTFOLIO",GREEN,"EPIC",
     ["Cyberpunk HUD portfolio — boot","sequence, command palette,","particle net, custom cursor."],
     ["React 19","Vite 7","Lenis"],"DEPLOYED"),
    ("03","ECOWORLD",VIOLET,"EPIC",
     ["Climate-solutions showcase.","Full-stack with REST routes","and a Postgres backend."],
     ["Node","Express","PostgreSQL"],"DEPLOYED"),
    ("04","PHOTOBOOTH","#ff7b54","RARE",
     ["Fish-themed Electron desktop","photobooth — filters, shutter","and retro photo strips."],
     ["Electron","JavaScript","CSS"],"DEPLOYED"),
    ("05","NIER: AUTOMATA",GOLD,"RARE",
     ["Cinematic fan tribute with","atmospheric visuals and fluid","dystopian motion."],
     ["HTML","CSS","JS"],"DEPLOYED"),
    ("06","CLASSIFIED",ROSE,"???",
     ["Next build in progress.","Something is compiling in","the dark. Stay tuned."],
     ["???"],"IN PROGRESS"),
]
CW, CH = 600, 190


def mission(idx, title, col, rarity, lines, chips, state):
    uid = f"m{idx}"
    chipx, cs = 30, []
    for c in chips:
        w = 10 + len(c)*6.7
        cs.append(f'<rect x="{chipx:.0f}" y="{CH-46}" width="{w:.0f}" height="20" rx="3" fill="{col}" fill-opacity=".10" stroke="{col}" stroke-opacity=".4"/>'
                  f'<text class="f{uid}" x="{chipx+w/2:.0f}" y="{CH-32}" font-size="9.5" letter-spacing="1" fill="{col}" text-anchor="middle">{c}</text>')
        chipx += w+7
    body = "".join(f'<text class="f{uid}" x="30" y="{104+i*17}" font-size="11.5" fill="#9fb8cf">{l}</text>' for i,l in enumerate(lines))
    live = state == "DEPLOYED"
    sw = len(state)*7.9
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}" role="img" aria-label="{title}">
<title>{title} — {rarity}</title>
<defs>
  <linearGradient id="b{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="{BG0}"/><stop offset="100%" stop-color="{BG1}"/></linearGradient>
  <radialGradient id="g{uid}" cx="4%" cy="0%" r="92%"><stop offset="0%" stop-color="{col}" stop-opacity=".26"/><stop offset="100%" stop-color="{col}" stop-opacity="0"/></radialGradient>
  <linearGradient id="s{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{col}" stop-opacity="0"/><stop offset="50%" stop-color="{col}" stop-opacity=".15"/><stop offset="100%" stop-color="{col}" stop-opacity="0"/></linearGradient>
  <pattern id="p{uid}" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height="1" fill="{col}" opacity=".05"/></pattern>
  <style><![CDATA[
    .f{uid} {{ font-family:{MONO} }}
    @keyframes s{uid} {{ 0% {{ transform:translateX(-200px) }} 100% {{ transform:translateX({CW+40}px) }} }}
    @keyframes p{uid} {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.25 }} }}
    @keyframes a{uid} {{ 0%,100% {{ opacity:.5 }} 50% {{ opacity:1 }} }}
    .s{uid} {{ animation:s{uid} 5s cubic-bezier(.4,0,.2,1) infinite }}
    .p{uid} {{ animation:p{uid} 1.5s ease-in-out infinite }}
    .a{uid} {{ animation:a{uid} 3s ease-in-out infinite }}
  ]]></style>
</defs>
<g>
  <rect width="{CW}" height="{CH}" fill="url(#b{uid})"/>
  <rect width="{CW}" height="{CH}" fill="url(#g{uid})"/>
  <rect width="{CW}" height="{CH}" fill="url(#p{uid})"/>
  <rect class="s{uid}" x="0" y="0" width="200" height="{CH}" fill="url(#s{uid})"/>
  <rect class="a{uid}" x="0" y="0" width="3" height="{CH}" fill="{col}"/>
  <text class="f{uid}" x="{CW-24}" y="60" font-size="48" font-weight="700" fill="{col}" fill-opacity=".12" text-anchor="end">{idx}</text>
  <text class="f{uid}" x="30" y="40" font-size="9.5" letter-spacing="3" fill="{col}" opacity=".8">// MISSION_{idx}</text>
  <text class="f{uid}" x="30" y="70" font-size="18" font-weight="700" letter-spacing="1.5" fill="{INK}">{title}</text>
  <text class="f{uid}" x="{CW-24}" y="88" font-size="9" letter-spacing="3" fill="{col}" opacity=".85" text-anchor="end">{rarity}</text>
  {body}
  {"".join(cs)}
  <circle class="p{uid}" cx="{CW-34-sw:.0f}" cy="{CH-38}" r="3.6" fill="{GREEN if live else col}"/>
  <text class="f{uid}" x="{CW-24}" y="{CH-34}" font-size="9.5" letter-spacing="2" fill="{GREEN if live else col}" text-anchor="end">{state}</text>
  <g stroke="{col}" stroke-width="1.4" fill="none" opacity=".5">
    <path d="M12 28 V12 H28"/><path d="M{CW-28} 12 H{CW-12} V28"/>
    <path d="M12 {CH-28} V{CH-12} H28"/><path d="M{CW-12} {CH-28} V{CH-12} H{CW-28}"/>
  </g>
  <rect x=".6" y=".6" width="{CW-1.2}" height="{CH-1.2}" fill="none" stroke="{col}" stroke-opacity=".28"/>
</g>
</svg>'''


# ─────────────────────────── 05 · COMMS ───────────────────────────
COMMS = [
    ("portfolio","PORTFOLIO","tanvirrafi.vercel.app",CYAN,"M4 12 L12 4 L20 12 M7 10 V20 H17 V10"),
    ("email","EMAIL","tmrafi@myseneca.ca",GREEN,"M3 6 H21 V18 H3 Z M3 6 L12 13 L21 6"),
    ("github","GITHUB","Tanvir-Rafi03",VIOLET,"M9 19c-4 1.4-4-2-6-2.5m12 4.5v-3.6c0-1 .1-1.4-.5-2 2.8-.3 5.5-1.4 5.5-6a4.6 4.6 0 0 0-1.3-3.2 4.3 4.3 0 0 0-.1-3.2s-1-.3-3.4 1.3a11.6 11.6 0 0 0-6 0C6.7 2.7 5.7 3 5.7 3a4.3 4.3 0 0 0-.1 3.2A4.6 4.6 0 0 0 4.3 9.4c0 4.6 2.7 5.7 5.5 6-.6.6-.6 1.2-.5 2V21"),
    ("linkedin","LINKEDIN","connect",GOLD,"M5 9v10M5 5.5v.01M10 19v-5a3 3 0 0 1 6 0v5"),
]
TW, TH = 300, 104


def comm(slug, label, value, col, icon):
    uid = f"c{slug}"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{TW}" height="{TH}" viewBox="0 0 {TW} {TH}" role="img" aria-label="{label} {value}">
<title>{label} — {value}</title>
<defs>
  <linearGradient id="b{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="{BG0}"/><stop offset="100%" stop-color="{BG1}"/></linearGradient>
  <radialGradient id="g{uid}" cx="8%" cy="0%" r="95%"><stop offset="0%" stop-color="{col}" stop-opacity=".28"/><stop offset="100%" stop-color="{col}" stop-opacity="0"/></radialGradient>
  <linearGradient id="s{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{col}" stop-opacity="0"/><stop offset="50%" stop-color="{col}" stop-opacity=".2"/><stop offset="100%" stop-color="{col}" stop-opacity="0"/></linearGradient>
  <style><![CDATA[
    .f{uid} {{ font-family:{MONO} }}
    @keyframes s{uid} {{ 0% {{ transform:translateX(-140px) }} 100% {{ transform:translateX({TW+30}px) }} }}
    @keyframes p{uid} {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.25 }} }}
    @keyframes a{uid} {{ 0%,100% {{ transform:translateX(0) }} 50% {{ transform:translateX(5px) }} }}
    .s{uid} {{ animation:s{uid} 4.4s cubic-bezier(.4,0,.2,1) infinite }}
    .p{uid} {{ animation:p{uid} 1.5s ease-in-out infinite }}
    .a{uid} {{ animation:a{uid} 1.8s ease-in-out infinite }}
  ]]></style>
</defs>
<g>
  <rect width="{TW}" height="{TH}" fill="url(#b{uid})"/><rect width="{TW}" height="{TH}" fill="url(#g{uid})"/>
  <rect class="s{uid}" x="0" y="0" width="140" height="{TH}" fill="url(#s{uid})"/>
  <rect x="0" y="0" width="3" height="{TH}" fill="{col}" opacity=".85"/>
  <g transform="translate(26,34)" stroke="{col}" stroke-width="1.7" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="{icon}"/></g>
  <text class="f{uid}" x="70" y="46" font-size="10" letter-spacing="3" fill="{col}" opacity=".9">{label}</text>
  <text class="f{uid}" x="70" y="68" font-size="12" fill="#e6f2fb">{value}</text>
  <g class="a{uid}"><path d="M{TW-32} {TH/2-6} l6 6 l-6 6" stroke="{col}" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity=".9"/></g>
  <circle class="p{uid}" cx="{TW-48}" cy="{TH/2}" r="3" fill="{col}"/>
  <g stroke="{col}" stroke-width="1.4" fill="none" opacity=".5">
    <path d="M11 26 V11 H26"/><path d="M{TW-26} {TH-11} H{TW-11} V{TH-26}"/>
  </g>
  <rect x=".6" y=".6" width="{TW-1.2}" height="{TH-1.2}" fill="none" stroke="{col}" stroke-opacity=".3"/>
</g>
</svg>'''


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    files = {"01-operator.svg": hero(), "02-loadout.svg": loadout()}
    for m in MISSIONS:
        files[f"mission-{m[0]}.svg"] = mission(*m)
    for c in COMMS:
        files[f"comm-{c[0]}.svg"] = comm(*c)
    for name, svg in files.items():
        path = os.path.join(OUT, name)
        open(path, "w").write(svg)
        xml.dom.minidom.parse(path)
    print(f"built {len(files)} panels, all XML valid")
    for n in sorted(files): print(f"  {n:22} {len(files[n]):>8,} bytes")
