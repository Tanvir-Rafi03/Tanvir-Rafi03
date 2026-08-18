#!/usr/bin/env python3
"""Builds the profile panels. Run from the repo root."""
import base64, os, random, sys, xml.dom.minidom
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import three as T

ART = os.environ.get("ART_DIR", "art")
OUT = "assets"
W   = 1200
b64 = lambda p: base64.b64encode(open(p, "rb").read()).decode()

CYAN, VIOLET, GREEN, ROSE, GOLD = "#00e5ff", "#a855ff", "#00ff9d", "#ff2d78", "#ffb800"
INK, MUTE = "#eaf6ff", "#8fa8bf"
MONO = "'JetBrains Mono','Fira Code',ui-monospace,'SF Mono',Menlo,Consolas,monospace"


# ═══════════════════════ 01 · HERO ═══════════════════════
def hero():
    uid, H = "h", 600
    city, face = b64(f"{ART}/hero2.jpg"), b64(f"{ART}/face2.jpg")
    CX, CY, PR = 600, 268, 176              # portrait is the subject now

    # three perspective-projected rings, baked frame by frame
    rings, dur = "", [17, 23, 29]
    specs = [(PR + 62, 0.46, "y", CYAN,   2.4, .85),
             (PR + 112, 1.02, "y", VIOLET, 2.0, .72),
             (PR + 164, 0.24, "z", GOLD,  1.5, .5)]
    for i, (r, tilt, axis, col, sw, op) in enumerate(specs):
        fr = T.ring_frames(CX, CY, r, tilt, axis, wobble=.18)
        rings += (f'<path fill="none" stroke="{col}" stroke-width="{sw}" opacity="{op}" filter="url(#gl{uid})" d="{fr[0]}">'
                  f'{T.smil("d", fr + [fr[0]], dur[i])}</path>')
        for ph in (0, 2.1, 4.2):
            o = T.orb_frames(CX, CY, r, tilt, ph)
            xs = [f"{p[0]:.1f}" for p in o] + [f"{o[0][0]:.1f}"]
            ys = [f"{p[1]:.1f}" for p in o] + [f"{o[0][1]:.1f}"]
            rs = [f"{2.0 + 4.2*(p[2]-.55):.2f}" for p in o] + [f"{2.0 + 4.2*(o[0][2]-.55):.2f}"]
            rings += (f'<circle cx="{xs[0]}" cy="{ys[0]}" r="{rs[0]}" fill="{col}" filter="url(#gl{uid})">'
                      f'{T.smil("cx", xs, dur[i])}{T.smil("cy", ys, dur[i])}{T.smil("r", rs, dur[i])}</circle>')

    random.seed(5)
    rain = "".join(
        f'<line class="rn{uid}" x1="{random.randint(-40,1240)}" y1="-70" '
        f'x2="{random.randint(-40,1240)-12}" y2="{-70+random.randint(24,54)}" stroke="#bfe9ff" '
        f'stroke-opacity="{random.uniform(.08,.22):.2f}" stroke-width="1" '
        f'style="animation-delay:{random.uniform(0,1.9):.2f}s;animation-duration:{random.uniform(1.2,2.1):.2f}s"/>'
        for _ in range(38))

    ticks = "".join(
        f'<rect x="{CX-.9}" y="{CY-PR-16}" width="1.8" height="{6 if i%3 else 11}" rx=".9" '
        f'fill="{CYAN}" opacity="{.85 if i%3==0 else .35}" transform="rotate({i*6} {CX} {CY})"/>'
        for i in range(60))

    chips, cx0 = "", 396
    for txt, col in [("AVAILABLE", GREEN), ("REACT", CYAN), ("NODE.JS", VIOLET), ("TORONTO", CYAN)]:
        w = 26 + len(txt) * 8.2
        chips += (f'<rect x="{cx0:.0f}" y="540" width="{w:.0f}" height="28" rx="4" fill="#02000c" '
                  f'fill-opacity=".7" stroke="{col}" stroke-opacity=".6"/>'
                  f'<text class="m{uid}" x="{cx0+w/2:.0f}" y="559" font-size="11.5" letter-spacing="2" '
                  f'fill="{col}" text-anchor="middle">{txt}</text>')
        cx0 += w + 12

    body = f'''
  <image href="data:image/jpeg;base64,{city}" x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>
  <g>{rain}</g>
  <rect width="{W}" height="{H}" fill="url(#vg{uid})"/>
  <rect width="{W}" height="{H}" fill="url(#sl{uid})"/>
  <rect class="sw{uid}" x="0" y="0" width="380" height="{H}" fill="url(#swg{uid})"/>

  <circle cx="{CX}" cy="{CY}" r="{PR+150}" fill="url(#hal{uid})"/>
  {rings}

  <circle cx="{CX}" cy="{CY}" r="{PR+9}" fill="#03000f" opacity=".72"/>
  <g clip-path="url(#pc{uid})">
    <image href="data:image/jpeg;base64,{face}" x="{CX-PR}" y="{CY-PR}" width="{PR*2}" height="{PR*2}" preserveAspectRatio="xMidYMid slice"/>
    <image class="gs{uid}" href="data:image/jpeg;base64,{face}" x="{CX-PR}" y="{CY-PR}" width="{PR*2}" height="{PR*2}"
           preserveAspectRatio="xMidYMid slice" opacity="0" style="mix-blend-mode:screen"/>
    <rect x="{CX-PR}" y="{CY-PR}" width="{PR*2}" height="{PR*2}" fill="url(#pl{uid})"/>
    <rect class="sp{uid}" x="{CX-PR}" y="{CY-46}" width="{PR*2}" height="92" fill="url(#ps{uid})" opacity=".45"/>
  </g>
  <circle cx="{CX}" cy="{CY}" r="{PR}" fill="none" stroke="{CYAN}" stroke-width="2.6" opacity=".95"/>
  <g opacity=".5">{ticks}</g>
  <g stroke="{CYAN}" stroke-width="2.4" fill="none" opacity=".95" filter="url(#gl{uid})">
    <path d="M{CX-PR-30} {CY-96} V{CY-PR-30} H{CX-96}"/><path d="M{CX+96} {CY-PR-30} H{CX+PR+30} V{CY-96}"/>
    <path d="M{CX-PR-30} {CY+96} V{CY+PR+30} H{CX-96}"/><path d="M{CX+PR+30} {CY+96} V{CY+PR+30} H{CX+96}"/>
  </g>

  <text class="m{uid}" x="{CX}" y="500" font-size="34" font-weight="700" letter-spacing="9"
        fill="{INK}" text-anchor="middle" style="filter:drop-shadow(0 2px 12px rgba(3,0,15,.95))">TANVIR RAFI</text>
  <text class="m{uid}" x="{CX}" y="524" font-size="12" letter-spacing="5" fill="{MUTE}" text-anchor="middle">FULL-STACK DEVELOPER &#183; UI/UX DESIGNER</text>
  {chips}

  <g stroke="{CYAN}" stroke-width="2" fill="none" opacity=".7">
    <path d="M22 52 V22 H52"/><path d="M{W-52} 22 H{W-22} V52"/>
    <path d="M22 {H-52} V{H-22} H52"/><path d="M{W-22} {H-52} V{H-22} H{W-52}"/>
  </g>
  <text class="m{uid}" x="34" y="40" font-size="11" letter-spacing="4" fill="{GREEN}">// SYS.PROFILE_LOADED</text>
  <text class="m{uid}" x="{W-34}" y="40" font-size="11" letter-spacing="4" fill="{MUTE}" text-anchor="end">ONLINE</text>
  <circle class="pu{uid}" cx="{W-92}" cy="36" r="4" fill="{GREEN}"/>'''

    defs = f'''
  <linearGradient id="vg{uid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#03000f" stop-opacity=".62"/>
    <stop offset="40%" stop-color="#03000f" stop-opacity=".2"/>
    <stop offset="100%" stop-color="#03000f" stop-opacity=".88"/>
  </linearGradient>
  <radialGradient id="hal{uid}" cx="50%" cy="50%" r="50%">
    <stop offset="55%" stop-color="{VIOLET}" stop-opacity=".22"/>
    <stop offset="100%" stop-color="#03000f" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="swg{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{CYAN}" stop-opacity="0"/>
    <stop offset="50%" stop-color="{CYAN}" stop-opacity=".09"/>
    <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="ps{uid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{CYAN}" stop-opacity="0"/>
    <stop offset="50%" stop-color="#ffffff" stop-opacity=".65"/>
    <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
  </linearGradient>
  <pattern id="sl{uid}" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height="1" fill="#9fe6ff" opacity=".05"/></pattern>
  <pattern id="pl{uid}" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1.3" fill="#00131f" opacity=".34"/></pattern>
  <clipPath id="pc{uid}"><circle cx="{CX}" cy="{CY}" r="{PR}"/></clipPath>
  <filter id="gl{uid}" x="-70%" y="-70%" width="240%" height="240%">
    <feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>'''

    css = f'''
    .m{uid} {{ font-family:{MONO} }}
    @keyframes rn{uid} {{ 0%{{transform:translateY(0)}} 100%{{transform:translateY(680px)}} }}
    @keyframes sw{uid} {{ 0%{{transform:translateX(-400px)}} 100%{{transform:translateX({W+60}px)}} }}
    @keyframes pu{uid} {{ 0%,100%{{opacity:1}} 50%{{opacity:.25}} }}
    @keyframes sp{uid} {{ 0%{{transform:translateY(-240px)}} 100%{{transform:translateY(240px)}} }}
    @keyframes gs{uid} {{ 0%,82%,100%{{opacity:0;transform:translateX(0)}} 86%{{opacity:.75;transform:translateX(-10px)}} 90%{{opacity:.6;transform:translateX(8px)}} 95%{{opacity:.4;transform:translateX(-4px)}} }}
    .rn{uid} {{ animation-name:rn{uid}; animation-timing-function:linear; animation-iteration-count:infinite }}
    .sw{uid} {{ animation:sw{uid} 7s cubic-bezier(.4,0,.2,1) infinite }}
    .pu{uid} {{ animation:pu{uid} 1.6s ease-in-out infinite }}
    .sp{uid} {{ animation:sp{uid} 3.8s cubic-bezier(.5,0,.5,1) infinite }}
    .gs{uid} {{ animation:gs{uid} 6s steps(1) infinite }}'''

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="Tanvir Rafi — full-stack developer and UI/UX designer">'
            f'<title>TANVIR RAFI</title><defs>{defs}<style><![CDATA[{css}]]></style></defs>'
            f'<g clip-path="url(#fr{uid})">{body}</g>'
            f'<defs><clipPath id="fr{uid}"><rect width="{W}" height="{H}" rx="10"/></clipPath></defs></svg>')



# ═══════════════════════ 03 · LINKS ═══════════════════════
PROJ = [("01","AI RESUME BUILDER","TYPESCRIPT / REACT / POSTGRES",CYAN),
        ("02","PORTFOLIO","REACT 19 / VITE 7 / LENIS",GREEN),
        ("03","ECOWORLD","NODE / EXPRESS / POSTGRES",VIOLET),
        ("04","PHOTOBOOTH","ELECTRON / JAVASCRIPT","#ff7b54"),
        ("05","NIER: AUTOMATA","HTML / CSS / JS",GOLD),
        ("06","CLASSIFIED","BUILDING . . .",ROSE)]
TW, TH = 392, 152
LW, LH = 294, 108


def tile(num, title, sub, col):
    uid = "t" + num
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{TW}" height="{TH}" viewBox="0 0 {TW} {TH}" '
            f'role="img" aria-label="{title}"><title>{title}</title><defs>'
            f'<linearGradient id="b{uid}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0%" stop-color="#04001a"/><stop offset="100%" stop-color="#0a0330"/></linearGradient>'
            f'<radialGradient id="g{uid}" cx="4%" cy="0%" r="94%">'
            f'<stop offset="0%" stop-color="{col}" stop-opacity=".26"/><stop offset="100%" stop-color="{col}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="s{uid}" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0%" stop-color="{col}" stop-opacity="0"/><stop offset="50%" stop-color="{col}" stop-opacity=".16"/>'
            f'<stop offset="100%" stop-color="{col}" stop-opacity="0"/></linearGradient>'
            f'<style><![CDATA[.m{uid}{{font-family:{MONO}}}'
            f'@keyframes s{uid}{{0%{{transform:translateX(-170px)}}100%{{transform:translateX({TW+30}px)}}}}'
            f'@keyframes a{uid}{{0%,100%{{transform:translateX(0)}}50%{{transform:translateX(6px)}}}}'
            f'@keyframes p{uid}{{0%,100%{{opacity:.6}}50%{{opacity:1}}}}'
            f'.s{uid}{{animation:s{uid} 5s cubic-bezier(.4,0,.2,1) infinite}}'
            f'.a{uid}{{animation:a{uid} 2.1s ease-in-out infinite}}'
            f'.p{uid}{{animation:p{uid} 2.8s ease-in-out infinite}}]]></style></defs>'
            f'<rect width="{TW}" height="{TH}" rx="8" fill="url(#b{uid})"/>'
            f'<rect width="{TW}" height="{TH}" rx="8" fill="url(#g{uid})"/>'
            f'<rect class="s{uid}" x="0" y="0" width="170" height="{TH}" fill="url(#s{uid})"/>'
            f'<rect class="p{uid}" x="0" y="8" width="3" height="{TH-16}" fill="{col}"/>'
            f'<text class="m{uid}" x="{TW-22}" y="52" font-size="34" font-weight="700" fill="{col}" fill-opacity=".16" text-anchor="end">{num}</text>'
            f'<text class="m{uid}" x="24" y="42" font-size="9" letter-spacing="3" fill="{col}" opacity=".85">// PROJECT_{num}</text>'
            f'<text class="m{uid}" x="24" y="76" font-size="16" font-weight="700" letter-spacing=".5" fill="{INK}">{title}</text>'
            f'<text class="m{uid}" x="24" y="104" font-size="9.5" letter-spacing="1.6" fill="{MUTE}">{sub}</text>'
            f'<text class="m{uid}" x="24" y="{TH-22}" font-size="9" letter-spacing="2.6" fill="{col}" opacity=".9">OPEN</text>'
            f'<g class="a{uid}"><path d="M{TW-40} {TH-27} h16 m-5 -5 l5 5 l-5 5" stroke="{col}" stroke-width="1.6" '
            f'fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>'
            f'<rect x=".6" y=".6" width="{TW-1.2}" height="{TH-1.2}" rx="8" fill="none" stroke="{col}" stroke-opacity=".3"/></svg>')




# ═══════════════════════ 03 · ARTWORK ═══════════════════════
def artwork():
    uid, H = "a", 600
    img = b64(f"{ART}/artwork.jpg")
    random.seed(21)
    rain = "".join(
        f'<line class="rn{uid}" x1="{random.randint(-40,1240)}" y1="-80" '
        f'x2="{random.randint(-40,1240)-14}" y2="{-80+random.randint(28,62)}" stroke="#cdefff" '
        f'stroke-opacity="{random.uniform(.07,.20):.2f}" stroke-width="1" '
        f'style="animation-delay:{random.uniform(0,2.1):.2f}s;animation-duration:{random.uniform(1.3,2.3):.2f}s"/>'
        for _ in range(42))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="Cyberpunk cityscape artwork"><title>NIGHT CITY</title><defs>'
            f'<linearGradient id="vg{uid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0%" stop-color="#03000f" stop-opacity=".55"/>'
            f'<stop offset="34%" stop-color="#03000f" stop-opacity="0"/>'
            f'<stop offset="100%" stop-color="#03000f" stop-opacity=".72"/></linearGradient>'
            f'<linearGradient id="swg{uid}" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0%" stop-color="{CYAN}" stop-opacity="0"/>'
            f'<stop offset="50%" stop-color="{CYAN}" stop-opacity=".085"/>'
            f'<stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>'
            f'<pattern id="sl{uid}" width="3" height="3" patternUnits="userSpaceOnUse">'
            f'<rect width="3" height="1" fill="#9fe6ff" opacity=".05"/></pattern>'
            f'<clipPath id="fr{uid}"><rect width="{W}" height="{H}" rx="10"/></clipPath>'
            f'<style><![CDATA[.m{uid}{{font-family:{MONO}}}'
            f'@keyframes rn{uid}{{0%{{transform:translateY(0)}}100%{{transform:translateY(700px)}}}}'
            f'@keyframes sw{uid}{{0%{{transform:translateX(-420px)}}100%{{transform:translateX({W+60}px)}}}}'
            f'@keyframes pu{uid}{{0%,100%{{opacity:1}}50%{{opacity:.25}}}}'
            f'.rn{uid}{{animation-name:rn{uid};animation-timing-function:linear;animation-iteration-count:infinite}}'
            f'.sw{uid}{{animation:sw{uid} 9s cubic-bezier(.4,0,.2,1) infinite}}'
            f'.pu{uid}{{animation:pu{uid} 1.8s ease-in-out infinite}}]]></style></defs>'
            f'<g clip-path="url(#fr{uid})">'
            f'<image href="data:image/jpeg;base64,{img}" x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>'
            f'<g>{rain}</g>'
            f'<rect width="{W}" height="{H}" fill="url(#vg{uid})"/>'
            f'<rect width="{W}" height="{H}" fill="url(#sl{uid})"/>'
            f'<rect class="sw{uid}" x="0" y="0" width="420" height="{H}" fill="url(#swg{uid})"/>'
            f'<text class="m{uid}" x="40" y="46" font-size="11" letter-spacing="4" fill="{GREEN}">// NIGHT_CITY</text>'
            f'<circle class="pu{uid}" cx="{W-148}" cy="42" r="4" fill="{GREEN}"/>'
            f'<text class="m{uid}" x="{W-40}" y="46" font-size="10" letter-spacing="3" fill="{MUTE}" text-anchor="end">RENDERING</text>'
            f'<text class="m{uid}" x="40" y="{H-38}" font-size="14" letter-spacing="3" fill="{INK}" '
            f'style="filter:drop-shadow(0 2px 10px rgba(3,0,15,.95))">BUILT AFTER DARK</text>'
            f'<g stroke="{CYAN}" stroke-width="2" fill="none" opacity=".65">'
            f'<path d="M22 52 V22 H52"/><path d="M{W-52} 22 H{W-22} V52"/>'
            f'<path d="M22 {H-52} V{H-22} H52"/><path d="M{W-22} {H-52} V{H-22} H{W-52}"/></g>'
            f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="10" fill="none" stroke="{CYAN}" stroke-opacity=".2"/>'
            f'</g></svg>')


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    files = {"01-hero.svg": hero(), "03-artwork.svg": artwork()}
    for n, s in files.items():
        p = os.path.join(OUT, n); open(p, "w").write(s); xml.dom.minidom.parse(p)
        print(f"  {n:20} {len(s):>9,} bytes")
    print("all XML valid")
