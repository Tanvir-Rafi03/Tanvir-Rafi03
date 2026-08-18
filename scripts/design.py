"""
Editorial design system.
Warm paper, heavy grotesk display type, hairline rules, one vermilion accent.
Every panel imports these so the whole page reads as one printed object.
"""
W      = 1200
MARGIN = 84                       # generous outer margin — air is the point
COL    = (W - MARGIN*2) / 12      # 12-column grid
grid   = lambda n: MARGIN + COL*n

PAPER  = "#f2efe6"
PAPER2 = "#e8e3d6"
INK    = "#14110f"
INK60  = "#5c554d"
INK35  = "#9a9288"
RULE   = "#c9c2b4"
RED    = "#e8330a"
BLUE   = "#1b3fa0"

DISP = "'Helvetica Neue',Helvetica,Arial,'Segoe UI',sans-serif"
MONO = "'JetBrains Mono','SF Mono',ui-monospace,Menlo,Consolas,monospace"


def label(uid, x, y, txt, fill=None, size=9.5, anchor="start"):
    """Small-caps tracking-out label — the workhorse of the system."""
    return (f'<text class="d{uid}" x="{x}" y="{y}" font-size="{size}" font-weight="600" '
            f'letter-spacing="2.6" fill="{fill or INK35}" text-anchor="{anchor}">{txt}</text>')


def rule(x1, y, x2, colour=RULE, w=1):
    return f'<path d="M{x1} {y} H{x2}" stroke="{colour}" stroke-width="{w}"/>'


def base_css(uid):
    return f'''
    .d{uid} {{ font-family:{DISP} }}
    .m{uid} {{ font-family:{MONO} }}
    @keyframes band{uid} {{ 0% {{ transform:translateX(-460px) }} 100% {{ transform:translateX({W+80}px) }} }}
    @keyframes soft{uid} {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.45 }} }}
    .band{uid} {{ animation:band{uid} 9s cubic-bezier(.45,0,.25,1) infinite }}
    .soft{uid} {{ animation:soft{uid} 2.4s ease-in-out infinite }}'''


def panel(uid, h, body, extra_defs="", extra_css="", bg=PAPER, seam=True):
    """Flat-edged paper panel. Panels butt together into one continuous sheet."""
    top = rule(0, 0.5, W, RULE) if seam else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img">
<defs>
  <linearGradient id="bd{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{RED}" stop-opacity="0"/>
    <stop offset="50%" stop-color="{RED}" stop-opacity=".07"/>
    <stop offset="100%" stop-color="{RED}" stop-opacity="0"/>
  </linearGradient>{extra_defs}
  <style><![CDATA[{base_css(uid)}{extra_css}]]></style>
</defs>
<rect width="{W}" height="{h}" fill="{bg}"/>
<rect class="band{uid}" x="0" y="0" width="460" height="{h}" fill="url(#bd{uid})"/>
{top}
{body}
</svg>'''
