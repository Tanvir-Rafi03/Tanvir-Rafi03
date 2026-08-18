#!/usr/bin/env python3
"""Builds the Minecraft-themed profile. Run from the repo root."""
import base64, os, random, sys, xml.dom.minidom
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mc import *

ART = os.environ.get("ART_DIR", "art")
OUT = "assets"
b64 = lambda p: base64.b64encode(open(p, "rb").read()).decode()
PX  = 'style="image-rendering:pixelated;image-rendering:crisp-edges"'


def svg(uid, h, defs, css, body, w=W):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" shape-rendering="crispEdges">'
            f'<defs>{defs}<style><![CDATA[{css}]]></style></defs>{body}</svg>')


# ══════════════════════ 01 · THE OVERWORLD ══════════════════════
def world():
    uid, H = "w", 512
    skin = b64(f"{ART}/skin40.png")
    GY, B = 344, 32

    random.seed(4)
    clouds = ""
    for cy, cw, dur, o in [(58, 150, 46, 1), (118, 108, 62, .9), (86, 190, 78, .72)]:
        seg = (f'<g><rect x="0" y="{cy}" width="{cw}" height="22" fill="#ffffff" opacity="{o}"/>'
               f'<rect x="{cw*0.22:.0f}" y="{cy-14}" width="{cw*0.5:.0f}" height="14" fill="#ffffff" opacity="{o}"/></g>')
        clouds += (f'<g class="cl{uid}" style="animation-duration:{dur}s">{seg}'
                   f'<g transform="translate(700,0)">{seg}</g>'
                   f'<g transform="translate(1400,0)">{seg}</g></g>')

    ground = ""
    for i in range(W // B + 1):
        x = i * B
        ground += block(x, GY, B, GRASS_T, GRASS_S)
        for d in range(1, 6):
            y = GY + d * B
            if y > H: break
            ground += block(x, y, B, DIRT, "#7a4d25")
    random.seed(9)
    for _ in range(10):
        ground += block(random.randrange(0, W // B) * B, GY + random.choice([2, 3]) * B, B, STONE, STONE_D)
    for ore in (DIAMOND, EMERALD, GOLD):
        ground += block(random.randrange(0, W // B) * B, GY + random.choice([3, 4]) * B, B, STONE, STONE_D, ore)

    # ── player, left ──
    PXx, PYy, PS = 84, 172, 168
    player = (f'<rect x="{PXx-6}" y="{PYy-6}" width="{PS+12}" height="{PS+12}" fill="#2f2115"/>'
              f'<image href="data:image/png;base64,{skin}" x="{PXx}" y="{PYy}" width="{PS}" height="{PS}" {PX}/>'
              f'<rect x="{PXx+PS/2-136}" y="{PYy-52}" width="272" height="36" fill="#000000" opacity=".55"/>'
              + text("TANVIR_RAFI", PXx+PS/2, PYy-44, 4, TXT, True, None, "middle"))

    # ── centred HUD, like the real game ──
    HX, HW_, HY = 250, 700, 396
    hearts = "".join(heart(HX + i*30, HY, 3) for i in range(10))
    food   = "".join(block(HX + HW_ - 24 - i*30, HY, 24, "#c8873f", "#8d5c26") for i in range(10))
    xpy    = HY + 42
    hud = (f'<rect x="{HX-24}" y="{HY-18}" width="{HW_+48}" height="118" fill="#000000" opacity=".38"/>'
           + hearts + food
           + bevel(HX, xpy, HW_, 22, "#1c1c1c", "#2e2e2e", "#0d0d0d", 3)
           + f'<rect x="{HX+3}" y="{xpy+3}" width="{HW_-6}" height="16" fill="#0f2a0d"/>'
           + f'<rect x="{HX+3}" y="{xpy+3}" width="{(HW_-6)*0.71:.0f}" height="16" fill="{EMERALD}"/>'
           + f'<rect x="{HX+3}" y="{xpy+3}" width="{(HW_-6)*0.71:.0f}" height="5" fill="#5cf58e"/>'
           + text("15", HX + HW_/2, xpy + 28, 5, "#7fff9c", True, "#123d1b", "middle"))

    body = f'''
  <rect width="{W}" height="{H}" fill="url(#sky{uid})"/>
  <rect x="1046" y="46" width="64" height="64" fill="#fff6b0"/>
  <rect x="1058" y="58" width="40" height="40" fill="#ffffff"/>
  {clouds}
  {ground}
  {player}
  {text("MINECRAFT PROFILE", 60, 34, 4, GOLD, True, GOLD_SH)}
  {text("SINGLEPLAYER / SURVIVAL / TORONTO", 60, 76, 3, "#eaf4ff")}
  <g>
    {text("FULL-STACK", 430, 150, 6, TXT)}
    {text("DEVELOPER", 430, 202, 6, TXT)}
    {text("UI / UX DESIGNER", 430, 258, 4, "#d8e8ff")}
    {text("BUILDING THINGS THAT DON'T LAG", 430, 296, 3, "#c3d8f2")}
  </g>
  {hud}'''

    defs = (f'<linearGradient id="sky{uid}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0%" stop-color="{SKY_T}"/><stop offset="100%" stop-color="{SKY_B}"/></linearGradient>')
    css = f'''
    @keyframes cl{uid} {{ 0% {{ transform:translateX(0) }} 100% {{ transform:translateX(-700px) }} }}
    .cl{uid} {{ animation-name:cl{uid}; animation-timing-function:linear; animation-iteration-count:infinite }}'''
    return svg(uid, H, defs, css, body)


# ══════════════════════ 03 · INVENTORY ══════════════════════
INV = [
    ("REACT",4,DIAMOND,"#2fbfae"), ("JS",4,GOLD,"#c9b93b"),
    ("TS",3,LAPIS,"#1e4a94"), ("HTML+CSS",5,"#e0704a","#b0532f"),
    ("TAILWIND",4,"#38bdf8","#2a8fbd"), ("FIGMA",3,"#a259ff","#7b41c4"),
    ("NODE.JS",3,EMERALD,"#11a84a"), ("EXPRESS",3,"#b9b9b9","#8c8c8c"),
    ("POSTGRES",3,"#4a9fd8","#367aa5"), ("MONGODB",3,"#4db33d","#3a8830"),
    ("MYSQL",3,"#4fa8cc","#3b7f9b"), ("JAVA",3,"#e08b2f","#ab6823"),
    ("GIT",4,REDSTONE,"#93211d"), ("VITE",4,"#bf80ff","#9160c4"),
    ("VERCEL",3,"#e6e6e6","#a9a9a9"), ("FIREBASE",2,"#ffca28","#c79b1e"),
    ("UNITY",2,"#9fa4ad","#787c84"), ("PHP",2,"#8892be","#69708f"),
]


def inventory():
    uid, H = "i", 492
    cols, S, GAP, RGAP = 9, 104, 8, 46
    gw = cols*S + (cols-1)*GAP
    x0 = (W - gw)//2
    y0 = 128
    body = (f'<rect width="{W}" height="{H}" fill="#3a3a3a"/>'
            f'<rect width="{W}" height="{H}" fill="url(#dirt{uid})" opacity=".5"/>'
            + bevel(x0-22, 56, gw+44, H-92, GUI, GUI_LT, GUI_DK, 6)
            + text("INVENTORY", x0, 82, 4, "#404040", False))
    for i,(name, cnt, top, side) in enumerate(INV):
        r, c = divmod(i, cols)
        x, y = x0 + c*(S+GAP), y0 + r*(S+RGAP)
        body += slot(x, y, S)
        body += f'<g class="it{uid}" style="animation-delay:{(i*0.17)%3.2:.2f}s">'
        body += block(x+18, y+18, S-36, top, side, "#ffffff" if cnt >= 4 else None)
        body += '</g>'
        body += text(str(cnt), x+S-10, y+S-26, 3, TXT, True, None, "end")
        body += text(name, x+S//2, y+S+10, 2, "#3d3d3d", False, None, "middle")
    return svg(uid, H, f'''
    <pattern id="dirt{uid}" width="32" height="32" patternUnits="userSpaceOnUse">
      <rect width="32" height="32" fill="#6b4423"/><rect x="0" y="0" width="16" height="16" fill="#79502a"/>
      <rect x="16" y="16" width="16" height="16" fill="#5e3b1e"/><rect x="8" y="20" width="8" height="8" fill="#83592f"/>
    </pattern>''', f'''
    @keyframes it{uid} {{ 0%,100% {{ transform:translateY(0) }} 50% {{ transform:translateY(-3px) }} }}
    .it{uid} {{ animation:it{uid} 3.2s ease-in-out infinite }}''', body)


# ══════════════════════ 04 · ADVANCEMENTS ══════════════════════
ADV = [
    ("AI RESUME BUILDER","TYPESCRIPT / REACT / POSTGRES","CHALLENGE COMPLETE!",DIAMOND,"#2fbfae",GOLD),
    ("PORTFOLIO","REACT 19 / VITE 7 / LENIS","ADVANCEMENT MADE!",EMERALD,"#11a84a",TXT),
    ("ECOWORLD","NODE / EXPRESS / POSTGRES","ADVANCEMENT MADE!","#4db33d","#3a8830",TXT),
    ("PHOTOBOOTH","ELECTRON / JAVASCRIPT","ADVANCEMENT MADE!","#e0704a","#b0532f",TXT),
    ("NIER AUTOMATA","HTML / CSS / JAVASCRIPT","ADVANCEMENT MADE!",GOLD,"#c9b93b",TXT),
    ("CLASSIFIED","???","GOAL REACHED!",REDSTONE,"#93211d","#a8a8a8"),
]
AW, AH = 592, 170


def advancement(title, stack, kind, top, side, kind_col):
    uid = "a" + title[:3].lower().replace(" ", "")
    return svg(uid, AH, "", f'''
    @keyframes gl{uid} {{ 0%,100% {{ opacity:.55 }} 50% {{ opacity:1 }} }}
    @keyframes bb{uid} {{ 0%,100% {{ transform:translateY(0) }} 50% {{ transform:translateY(-4px) }} }}
    .gl{uid} {{ animation:gl{uid} 2.6s ease-in-out infinite }}
    .bb{uid} {{ animation:bb{uid} 3s ease-in-out infinite }}''',
    f'''
  <rect width="{AW}" height="{AH}" fill="#0f0f0f"/>
  {bevel(10, 14, AW-20, AH-28, "#100010", "#4b1ba0", "#2d0a63", 4)}
  <rect class="gl{uid}" x="14" y="18" width="{AW-28}" height="4" fill="{top}" opacity=".7"/>
  <g class="bb{uid}">{block(42, 52, 64, top, side, "#ffffff")}</g>
  {text(kind, 128, 44, 3, kind_col)}
  {text(title, 128, 74, 4, TXT)}
  {text(stack, 128, 116, 2, "#9a9a9a")}
  {text("[ OPEN ]", AW-34, 138, 3, "#7fb238", True, None, "end")}''', AW)


# ══════════════════════ 05 · HOTBAR ══════════════════════
BAR = [("PORTFOLIO","TANVIRRAFI.VERCEL.APP",DIAMOND,"#2fbfae"),
       ("EMAIL","TMRAFI@MYSENECA.CA",EMERALD,"#11a84a"),
       ("GITHUB","TANVIR-RAFI03","#c0b0ff","#8f7fd0"),
       ("LINKEDIN","CONNECT",LAPIS,"#1e4a94")]
HW, HH = 300, 186


def hotbar_slot(label_txt, value, top, side):
    uid = "h" + label_txt[:3].lower()
    return svg(uid, HH, f'''
    <pattern id="d{uid}" width="32" height="32" patternUnits="userSpaceOnUse">
      <rect width="32" height="32" fill="#6b4423"/><rect x="0" y="0" width="16" height="16" fill="#79502a"/>
      <rect x="16" y="16" width="16" height="16" fill="#5e3b1e"/></pattern>''', f'''
    @keyframes bb{uid} {{ 0%,100% {{ transform:translateY(0) }} 50% {{ transform:translateY(-4px) }} }}
    .bb{uid} {{ animation:bb{uid} 2.8s ease-in-out infinite }}''',
    f'''
  <rect width="{HW}" height="{HH}" fill="#3a3a3a"/>
  <rect width="{HW}" height="{HH}" fill="url(#d{uid})" opacity=".45"/>
  {bevel(HW/2-46, 26, 92, 92, SLOT, SLOT_DK, SLOT_LT, 4)}
  <g class="bb{uid}">{block(HW/2-28, 44, 56, top, side, "#ffffff")}</g>
  {text(label_txt, HW/2, 128, 3, GOLD, True, GOLD_SH, "middle")}
  {text(value, HW/2, 150, 2, "#e8e8e8", True, None, "middle")}''', HW)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    files = {"01-world.svg": world(), "03-inventory.svg": inventory()}
    for i, a in enumerate(ADV, 1):
        files[f"adv-{i:02d}.svg"] = advancement(*a)
    for b in BAR:
        files[f"bar-{b[0].lower()}.svg"] = hotbar_slot(*b)
    for n, s in files.items():
        p = os.path.join(OUT, n); open(p, "w").write(s); xml.dom.minidom.parse(p)
    print(f"built {len(files)} panels, all XML valid")
