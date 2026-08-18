"""Shared design tokens. Every panel imports these so the page reads as one screen."""
W        = 1200          # every panel is exactly this wide
RAIL     = 62            # left rail column, continuous down the whole page
PAD      = 92            # content starts here

BG0, BG1 = "#05010f", "#0b0322"
INK      = "#eaf6ff"
MUTE     = "#7d94ad"
DIM      = "#4a6076"
CYAN     = "#00e5ff"
VIOLET   = "#a855ff"
GOLD     = "#ffb800"
GREEN    = "#00ff9d"
ROSE     = "#ff2d78"

MONO = "'JetBrains Mono','Fira Code',ui-monospace,'SF Mono',Menlo,Consolas,monospace"


def defs(uid, h, glow=True):
    """Gradients/patterns shared by every panel. uid keeps ids unique per file."""
    g = f'''
  <linearGradient id="bg{uid}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{BG0}"/><stop offset="100%" stop-color="{BG1}"/>
  </linearGradient>
  <linearGradient id="rail{uid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{CYAN}" stop-opacity=".55"/>
    <stop offset="50%" stop-color="{VIOLET}" stop-opacity=".45"/>
    <stop offset="100%" stop-color="{CYAN}" stop-opacity=".55"/>
  </linearGradient>
  <linearGradient id="sweep{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{CYAN}" stop-opacity="0"/>
    <stop offset="50%" stop-color="{CYAN}" stop-opacity=".13"/>
    <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
  </linearGradient>
  <pattern id="sl{uid}" width="3" height="3" patternUnits="userSpaceOnUse">
    <rect width="3" height="1" fill="#9fe6ff" opacity=".05"/>
  </pattern>'''
    if glow:
        g += f'''
  <filter id="gl{uid}" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur stdDeviation="3.2" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>'''
    return g


def css(uid, extra=""):
    return f'''
    .f{uid} {{ font-family:{MONO} }}
    @keyframes sw{uid} {{ 0% {{ transform:translateX(-320px) }} 100% {{ transform:translateX({W+60}px) }} }}
    @keyframes pu{uid} {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.24 }} }}
    .sw{uid} {{ animation:sw{uid} 7s cubic-bezier(.4,0,.2,1) infinite }}
    .pu{uid} {{ animation:pu{uid} 1.6s ease-in-out infinite }}
    {extra}'''


def shell(uid, h, num, eyebrow, title, inner, bg_extra="", head=True):
    """Flat-edged panel + continuous left rail. No rounding: panels butt into one slab."""
    ticks = "".join(
        f'<rect x="{RAIL-13}" y="{y}" width="{9 if y % 60 else 15}" height="1.4" '
        f'fill="{CYAN}" opacity="{.42 if y % 60 else .8}"/>'
        for y in range(24, h - 12, 20))
    header = ""
    if head:
        header = f'''
  <text class="f{uid}" x="{PAD}" y="46" font-size="11" letter-spacing="5" fill="{GREEN}" opacity=".9">// {eyebrow}</text>
  <text class="f{uid}" x="{PAD}" y="82" font-size="27" font-weight="700" letter-spacing="7" fill="{INK}">{title}</text>
  <path d="M{PAD} 98 H{W-PAD}" stroke="{CYAN}" stroke-opacity=".2"/>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{title}">
<title>{title}</title>
<defs>{defs(uid, h)}
  <style><![CDATA[{css(uid, inner[1])}]]></style>
</defs>
<g>
  <rect width="{W}" height="{h}" fill="url(#bg{uid})"/>
  {bg_extra}
  <rect width="{W}" height="{h}" fill="url(#sl{uid})"/>
  <rect class="sw{uid}" x="0" y="0" width="320" height="{h}" fill="url(#sweep{uid})"/>
  <rect x="{RAIL}" y="0" width="1.4" height="{h}" fill="url(#rail{uid})"/>
  {ticks}
  <text class="f{uid}" x="{RAIL-30}" y="{h/2}" font-size="20" font-weight="700" letter-spacing="4"
        fill="{CYAN}" opacity=".85" text-anchor="middle"
        transform="rotate(-90 {RAIL-30} {h/2})">{num}</text>
  {header}
  {inner[0]}
</g>
</svg>'''
