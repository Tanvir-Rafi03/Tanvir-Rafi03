#!/usr/bin/env python3
"""
THE GRID — a year of real GitHub contributions as a playable-looking level.

Laid out months-down by days-across, so the year forms a dense terrain block
with a naturally ragged edge (short months leave gaps) rather than a thin
53-week strip. Every day is an extruded voxel tower whose height is that
day's commit count, drawn back-to-front so occlusion is correct, with a
drone running the surface.

Usage:  python3 scripts/gen_arcade.py <username> [out.svg]
Needs:  GH_TOKEN / GITHUB_TOKEN in env (GraphQL contributions API).
"""
import json, os, subprocess, sys, xml.dom.minidom
from datetime import date

W = 1200
AX, AY = 26.5, 0.0    # one day   -> across
BX, BY = 15.0, 14.0   # one month -> right and down (oblique depth)
HZ     = 27.0         # one unit of tower height
MAXH   = 4.4
DUR    = 20.0
CYAN, VIOLET, GREEN, GOLD = "#00e5ff", "#a855ff", "#00ff9d", "#ffb800"
INK, MUTE, DIM = "#eaf6ff", "#8fa8bf", "#54708a"
MONO = "'JetBrains Mono','Fira Code',ui-monospace,'SF Mono',Menlo,Consolas,monospace"
MON = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

PAL = [("#141d38", "#0d152b", "#0a1023"),
       ("#1d5c86", "#154866", "#0f3549"),
       ("#1b93c4", "#137296", "#0d556f"),
       ("#2ec9ee", "#1f9dbd", "#15768f"),
       ("#7df6ff", "#3fc9e0", "#249bb4")]


def fetch(user):
    q = """{ user(login: "%s") { contributionsCollection { contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } } } } } }""" % user
    out = subprocess.run(["gh","api","graphql","-f","query="+q],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def lvl(c, peak):
    if c <= 0: return 0
    q = c / peak if peak else 1
    return 4 if q > .5 else 3 if q > .25 else 2 if q > .1 else 1


def build(cal, user):
    uid   = "g"
    total = cal["totalContributions"]
    days  = [d for wk in cal["weeks"] for d in wk["contributionDays"]]
    days.sort(key=lambda d: d["date"])

    # month rows, day-of-month columns
    months, cell = [], {}
    for d in days:
        y, m, dd = (int(x) for x in d["date"].split("-"))
        key = (y, m)
        if key not in months: months.append(key)
        cell[(key, dd)] = (d["contributionCount"], d["date"])
    rows = len(months)
    peak = max((v[0] for v in cell.values()), default=1) or 1
    active = sum(1 for v in cell.values() if v[0] > 0)

    streak = best = 0
    for d in days:
        streak = streak + 1 if d["contributionCount"] > 0 else 0
        best = max(best, streak)

    hgt = lambda n: 0.12 if n <= 0 else 0.12 + MAXH * (n / peak) ** 0.6
    OX  = (W - (31*AX + rows*BX)) / 2 + 22
    OY  = 190
    P   = lambda u, v, h: (OX + u*AX + v*BX, OY + u*AY + v*BY - h*HZ)

    def voxel(c, r, h, top, left, right, cap=None):
        A, B_ = P(c, r, h), P(c+1, r, h)
        C, Dd = P(c+1, r+1, h), P(c, r+1, h)
        C0, D0, B0 = P(c+1, r+1, 0), P(c, r+1, 0), P(c+1, r, 0)
        f = lambda *p: " ".join(f"{q[0]:.1f},{q[1]:.1f}" for q in p)
        o = (f'<polygon points="{f(Dd,C,C0,D0)}" fill="{left}"/>'
             f'<polygon points="{f(B_,C,C0,B0)}" fill="{right}"/>'
             f'<polygon points="{f(A,B_,C,Dd)}" fill="{top}"/>')
        if cap: o += f'<polygon points="{f(A,B_,C,Dd)}" fill="{cap}" opacity=".5"/>'
        return o

    towers = []
    for r, key in enumerate(months):                 # back rows first
        for c in range(31):
            if (key, c+1) not in cell: continue
            n, dt = cell[(key, c+1)]
            L = lvl(n, peak)
            top, left, right = PAL[L]
            g = voxel(c, r, hgt(n), top, left, right, "#ffffff" if L >= 4 else None)
            if L >= 1:
                g = f'<g class="pl{uid}" style="animation-delay:{(c*0.07 + r*0.19) % 3.4:.2f}s">{g}</g>'
            px, py = P(c + .5, r + .5, hgt(n))
            towers.append(f'{g}<circle cx="{px:.1f}" cy="{py:.1f}" r="10" fill="#0000">'
                          f'<title>{dt}: {n}</title></circle>')

    # drone: serpentine along the surface
    pts, cum, run = [], [], 0
    for r, key in enumerate(months):
        rng = range(31) if r % 2 == 0 else range(30, -1, -1)
        for c in rng:
            if (key, c+1) not in cell: continue
            n = cell[(key, c+1)][0]
            x, y = P(c + .5, r + .5, hgt(n) + 0.32)
            pts.append(f"{x:.1f},{y:.1f}")
            run += n; cum.append(run)
    path = "M" + "L".join(pts)
    drone = (f'<g><circle r="17" fill="{GREEN}" opacity=".14"/><circle r="9" fill="{GREEN}" opacity=".4"/>'
             f'<circle r="4.8" fill="#eaffef"/>'
             f'<animateMotion dur="{DUR}s" repeatCount="indefinite" path="{path}" '
             f'keyPoints="0;1" keyTimes="0;1" calcMode="linear"/></g>')

    # month labels down the left edge
    labels = ""
    for r, (y, m) in enumerate(months):
        lx, ly = P(-0.4, r + .5, 0)
        labels += (f'<text class="m{uid}" x="{lx:.0f}" y="{ly+4:.0f}" font-size="9" letter-spacing="2" '
                   f'fill="{DIM}" text-anchor="end">{MON[m-1]} {str(y)[2:]}</text>')
    for c in (0, 6, 13, 20, 27):
        tx, ty = P(c + .5, -0.35, 0)
        labels += (f'<text class="m{uid}" x="{tx:.0f}" y="{ty:.0f}" font-size="8.5" letter-spacing="1.5" '
                   f'fill="{DIM}" text-anchor="middle">{c+1:02d}</text>')

    STEPS = 20
    score = ""
    for k in range(1, STEPS):
        idx = min(int((k+1)/STEPS*len(cum))-1, len(cum)-1)
        cls = f"sc{uid} sz{uid}" if k == STEPS-1 else f"sc{uid}"
        score += (f'<text class="m{uid} {cls}" x="{W-42}" y="104" font-size="44" font-weight="700" '
                  f'fill="{GOLD}" text-anchor="end" style="animation-delay:{k*DUR/STEPS:.2f}s">{cum[idx]}</text>')

    H = int(OY + rows*BY + 128)
    stats, sx = "", 42
    for k, v in [("CONTRIBUTIONS", total), ("ACTIVE DAYS", active),
                 ("PEAK / DAY", peak), ("BEST STREAK", best)]:
        stats += (f'<text class="m{uid}" x="{sx}" y="{H-28}" font-size="9" letter-spacing="3" fill="{DIM}">{k}</text>'
                  f'<text class="m{uid}" x="{sx}" y="{H-46}" font-size="21" font-weight="700" fill="{INK}">{v}</text>')
        sx += 210

    legend, lx = "", W - 330
    for i, nm in enumerate(["NONE", "LOW", "MED", "HIGH", "PEAK"]):
        legend += (f'<rect x="{lx}" y="{H-56}" width="13" height="8" fill="{PAL[i][0]}"/>'
                   f'<text class="m{uid}" x="{lx+18}" y="{H-49}" font-size="8" letter-spacing="1.4" fill="{DIM}">{nm}</text>')
        lx += 62

    body = f'''
  <rect width="{W}" height="{H}" fill="url(#bg{uid})"/>
  <rect width="{W}" height="{H}" fill="url(#vg{uid})"/>
  <rect width="{W}" height="{H}" fill="url(#sl{uid})"/>
  <rect class="sw{uid}" x="0" y="0" width="360" height="{H}" fill="url(#swg{uid})"/>
  <text class="m{uid}" x="42" y="48" font-size="11" letter-spacing="4" fill="{GREEN}">// CONTRIBUTION_ENGINE</text>
  <text class="m{uid}" x="42" y="92" font-size="32" font-weight="700" letter-spacing="8" fill="{INK}">THE GRID</text>
  <text class="m{uid}" x="42" y="118" font-size="9.5" letter-spacing="2" fill="{DIM}">{days[0]["date"]} &#8594; {days[-1]["date"]}  &#183;  {rows} MONTHS</text>
  <text class="m{uid}" x="{W-42}" y="62" font-size="9" letter-spacing="3" fill="{DIM}" text-anchor="end">SCORE</text>
  {score}
  {labels}
  {"".join(towers)}
  {drone}
  {stats}{legend}
  <g stroke="{CYAN}" stroke-width="1.8" fill="none" opacity=".5">
    <path d="M18 44 V18 H44"/><path d="M{W-44} 18 H{W-18} V44"/>
    <path d="M18 {H-44} V{H-18} H44"/><path d="M{W-18} {H-44} V{H-18} H{W-44}"/>
  </g>'''

    defs = f'''
  <linearGradient id="bg{uid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#03000f"/><stop offset="100%" stop-color="#0a0326"/></linearGradient>
  <radialGradient id="vg{uid}" cx="52%" cy="46%" r="70%">
    <stop offset="0%" stop-color="{VIOLET}" stop-opacity=".18"/><stop offset="100%" stop-color="#000" stop-opacity="0"/></radialGradient>
  <linearGradient id="swg{uid}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{CYAN}" stop-opacity="0"/><stop offset="50%" stop-color="{CYAN}" stop-opacity=".07"/>
    <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>
  <pattern id="sl{uid}" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height="1" fill="#9fe6ff" opacity=".04"/></pattern>'''

    css = f'''
    .m{uid} {{ font-family:{MONO} }}
    @keyframes pl{uid} {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.74 }} }}
    @keyframes sw{uid} {{ 0% {{ transform:translateX(-380px) }} 100% {{ transform:translateX({W+60}px) }} }}
    @keyframes st{uid} {{ 0%,4.6% {{ opacity:1 }} 4.7%,100% {{ opacity:0 }} }}
    .pl{uid} {{ animation:pl{uid} 3.4s ease-in-out infinite }}
    .sw{uid} {{ animation:sw{uid} 8s cubic-bezier(.4,0,.2,1) infinite }}
    .sc{uid} {{ opacity:0; animation:st{uid} {DUR}s linear infinite; filter:drop-shadow(0 0 8px rgba(255,184,0,.45)) }}
    .sz{uid} {{ opacity:1 }}'''

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="The Grid — {total} contributions as a voxel terrain">'
            f'<title>THE GRID — {total} contributions</title>'
            f'<defs>{defs}<style><![CDATA[{css}]]></style></defs>{body}</svg>')


if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "Tanvir-Rafi03"
    out  = sys.argv[2] if len(sys.argv) > 2 else "assets/02-grid.svg"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w").write(build(fetch(user), user))
    xml.dom.minidom.parse(out)
    print(f"wrote {out} ({os.path.getsize(out):,} bytes)")
