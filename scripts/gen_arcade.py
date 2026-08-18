#!/usr/bin/env python3
"""
THE GRID — a year of real GitHub contributions as a playable-looking level.

Every day becomes an extruded voxel tower whose height is that day's commit
count, laid out in isometric projection and drawn back-to-front so the
occlusion is correct. A drone runs the serpentine path across the terrain,
following the surface, while the score climbs.

Usage:  python3 scripts/gen_arcade.py <username> [out.svg]
Needs:  GH_TOKEN / GITHUB_TOKEN in env (GraphQL contributions API).
"""
import json, os, subprocess, sys, xml.dom.minidom
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import three as T

W    = 1200
ROWS = 7
AX, AY = 17.6, 0.0   # one week -> straight across
BX, BY = 9.4, 8.6    # one day  -> right and down (oblique depth)
HZ     = 23.0        # one unit of tower height, in px
MAXH   = 3.6         # tallest tower, in height units
DUR  = 18.0
CYAN, VIOLET, GREEN, GOLD = "#00e5ff", "#a855ff", "#00ff9d", "#ffb800"
INK, MUTE, DIM = "#eaf6ff", "#8fa8bf", "#54708a"
MONO = "'JetBrains Mono','Fira Code',ui-monospace,'SF Mono',Menlo,Consolas,monospace"
MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

# level -> (top, left, right)
PAL = [("#16203c", "#0e1730", "#0a1226"),
       ("#1d5c86", "#154866", "#0f3549"),
       ("#1b93c4", "#137296", "#0d556f"),
       ("#2ec9ee", "#1f9dbd", "#15768f"),
       ("#7df6ff", "#3fc9e0", "#249bb4")]


def fetch(user):
    q = """{ user(login: "%s") { contributionsCollection { contributionCalendar {
        totalContributions
        weeks { firstDay contributionDays { contributionCount date weekday } } } } } }""" % user
    out = subprocess.run(["gh","api","graphql","-f","query="+q],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def lvl(c, peak):
    if c <= 0: return 0
    q = c / peak if peak else 1
    return 4 if q > .5 else 3 if q > .25 else 2 if q > .1 else 1


def build(cal, user):
    uid   = "g"
    weeks = cal["weeks"]; cols = len(weeks); total = cal["totalContributions"]
    day, dates = {}, {}
    for c, wk in enumerate(weeks):
        for d in wk["contributionDays"]:
            day[(c, int(d["weekday"]))]   = d["contributionCount"]
            dates[(c, int(d["weekday"]))] = d["date"]
    peak   = max(day.values()) if day else 1
    active = sum(1 for v in day.values() if v > 0)
    seq = [day[(c,r)] for c in range(cols) for r in range(ROWS) if (c,r) in day]
    best = run = 0
    for v in seq:
        run = run + 1 if v > 0 else 0
        best = max(best, run)

    hgt = lambda n: 0.14 if n <= 0 else 0.14 + MAXH * (n / peak) ** 0.62

    def P(u, v, h, ox, oy):
        """Oblique projection: weeks across, days receding, height up."""
        return (ox + u * AX + v * BX, oy + u * AY + v * BY - h * HZ)

    gw = cols * AX + ROWS * BX
    OX = (W - gw) / 2
    OY = 252

    def voxel(c, r, h, top, left, right, cap=None):
        A = P(c,   r,   h, OX, OY); B = P(c+1, r,   h, OX, OY)
        C = P(c+1, r+1, h, OX, OY); D = P(c,   r+1, h, OX, OY)
        C0 = P(c+1, r+1, 0, OX, OY); D0 = P(c, r+1, 0, OX, OY)
        B0 = P(c+1, r,   0, OX, OY)
        f = lambda *p: " ".join(f"{q[0]:.1f},{q[1]:.1f}" for q in p)
        o = (f'<polygon points="{f(D,C,C0,D0)}" fill="{left}"/>'
             f'<polygon points="{f(B,C,C0,B0)}" fill="{right}"/>'
             f'<polygon points="{f(A,B,C,D)}" fill="{top}"/>')
        if cap:
            o += f'<polygon points="{f(A,B,C,D)}" fill="{cap}" opacity=".5"/>'
        return o

    # painter's algorithm: far rows first, then left to right
    order = sorted(((c, r) for c in range(cols) for r in range(ROWS) if (c, r) in day),
                   key=lambda t: (t[1], t[0]))
    towers = []
    for c, r in order:
        n = day[(c, r)]
        L = lvl(n, peak)
        top, left, right = PAL[L]
        g = voxel(c, r, hgt(n), top, left, right, "#ffffff" if L >= 4 else None)
        if L >= 1:
            g = f'<g class="pl{uid}" style="animation-delay:{(c*0.09 + r*0.14) % 3.6:.2f}s">{g}</g>'
        cx_, cy_ = P(c + .5, r + .5, hgt(n), OX, OY)
        towers.append(f'{g}<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="9" fill="#0000">'
                      f'<title>{dates[(c,r)]}: {n}</title></circle>')

    # drone runs the serpentine path along the surface
    pts = []
    for c in range(cols):
        for r in (range(ROWS) if c % 2 == 0 else range(ROWS - 1, -1, -1)):
            if (c, r) not in day: continue
            x, y = P(c + .5, r + .5, hgt(day[(c, r)]) + 0.34, OX, OY)
            pts.append(f"{x:.1f},{y:.1f}")
    path = "M" + "L".join(pts)
    drone = (f'<g><circle r="16" fill="{GREEN}" opacity=".15"/><circle r="8.5" fill="{GREEN}" opacity=".42"/>'
             f'<circle r="4.6" fill="#eaffef"/>'
             f'<animateMotion dur="{DUR}s" repeatCount="indefinite" path="{path}" '
             f'keyPoints="0;1" keyTimes="0;1" calcMode="linear"/></g>')

    H = int(OY + ROWS * BY + 156)

    # score steps, resting on the true total
    STEPS = 20
    cum, run2 = [], 0
    for c in range(cols):
        for r in (range(ROWS) if c % 2 == 0 else range(ROWS - 1, -1, -1)):
            if (c, r) in day:
                run2 += day[(c, r)]; cum.append(run2)
    score = ""
    for k in range(1, STEPS):
        idx = min(int((k + 1) / STEPS * len(cum)) - 1, len(cum) - 1)
        cls = f"sc{uid} sz{uid}" if k == STEPS - 1 else f"sc{uid}"
        score += (f'<text class="m{uid} {cls}" x="{W-40}" y="104" font-size="42" font-weight="700" '
                  f'fill="{GOLD}" text-anchor="end" style="animation-delay:{k*DUR/STEPS:.2f}s">{cum[idx]}</text>')

    months, seen = "", None
    for c, wk in enumerate(weeks):
        m = int(wk["firstDay"][5:7])
        if m != seen and c < cols - 1:
            mx, my = P(c, ROWS, 0, OX, OY)
            months += (f'<text class="m{uid}" x="{mx:.0f}" y="{my+22:.0f}" font-size="8.5" '
                       f'letter-spacing="2" fill="{DIM}" text-anchor="middle">{MONTHS[m-1]}</text>')
            seen = m

    stats, sx = "", 40
    for k, v in [("CONTRIBUTIONS", total), ("ACTIVE DAYS", active),
                 ("PEAK / DAY", peak), ("BEST STREAK", best)]:
        stats += (f'<text class="m{uid}" x="{sx}" y="{H-30}" font-size="9" letter-spacing="3" fill="{DIM}">{k}</text>'
                  f'<text class="m{uid}" x="{sx}" y="{H-48}" font-size="21" font-weight="700" fill="{INK}">{v}</text>')
        sx += 210

    body = f'''
  <rect width="{W}" height="{H}" fill="url(#bg{uid})"/>
  <rect width="{W}" height="{H}" fill="url(#vg{uid})"/>
  <rect width="{W}" height="{H}" fill="url(#sl{uid})"/>
  <rect class="sw{uid}" x="0" y="0" width="360" height="{H}" fill="url(#swg{uid})"/>
  <text class="m{uid}" x="40" y="46" font-size="11" letter-spacing="4" fill="{GREEN}">// CONTRIBUTION_ENGINE</text>
  <text class="m{uid}" x="40" y="88" font-size="30" font-weight="700" letter-spacing="7" fill="{INK}">THE GRID</text>
  <text class="m{uid}" x="{W-40}" y="62" font-size="9" letter-spacing="3" fill="{DIM}" text-anchor="end">SCORE</text>
  {score}
  <text class="m{uid}" x="40" y="112" font-size="9.5" letter-spacing="2" fill="{DIM}">{weeks[0]["firstDay"]} &#8594; {weeks[-1]["contributionDays"][-1]["date"]}</text>
  {months}
  {"".join(towers)}
  {drone}
  {stats}
  <g stroke="{CYAN}" stroke-width="1.8" fill="none" opacity=".55">
    <path d="M18 44 V18 H44"/><path d="M{W-44} 18 H{W-18} V44"/>
    <path d="M18 {H-44} V{H-18} H44"/><path d="M{W-18} {H-44} V{H-18} H{W-44}"/>
  </g>'''

    defs = f'''
  <linearGradient id="bg{uid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#03000f"/><stop offset="100%" stop-color="#0a0326"/></linearGradient>
  <radialGradient id="vg{uid}" cx="50%" cy="48%" r="72%">
    <stop offset="0%" stop-color="{VIOLET}" stop-opacity=".17"/><stop offset="100%" stop-color="#000" stop-opacity="0"/></radialGradient>
  <linearGradient id="swg{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{CYAN}" stop-opacity="0"/><stop offset="50%" stop-color="{CYAN}" stop-opacity=".07"/>
    <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>
  <pattern id="sl{uid}" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height="1" fill="#9fe6ff" opacity=".04"/></pattern>'''

    css = f'''
    .m{uid} {{ font-family:{MONO} }}
    @keyframes pl{uid} {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.72 }} }}
    @keyframes sw{uid} {{ 0% {{ transform:translateX(-380px) }} 100% {{ transform:translateX({W+60}px) }} }}
    @keyframes st{uid} {{ 0%,4.6% {{ opacity:1 }} 4.7%,100% {{ opacity:0 }} }}
    .pl{uid} {{ animation:pl{uid} 3.6s ease-in-out infinite }}
    .sw{uid} {{ animation:sw{uid} 8s cubic-bezier(.4,0,.2,1) infinite }}
    .sc{uid} {{ opacity:0; animation:st{uid} {DUR}s linear infinite; filter:drop-shadow(0 0 8px rgba(255,184,0,.45)) }}
    .sz{uid} {{ opacity:1 }}'''

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="The Grid — {total} contributions as an isometric voxel terrain">'
            f'<title>THE GRID — {total} contributions</title>'
            f'<defs>{defs}<style><![CDATA[{css}]]></style></defs>{body}</svg>')


if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "Tanvir-Rafi03"
    out  = sys.argv[2] if len(sys.argv) > 2 else "assets/02-grid.svg"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w").write(build(fetch(user), user))
    xml.dom.minidom.parse(out)
    print(f"wrote {out} ({os.path.getsize(out):,} bytes)")
