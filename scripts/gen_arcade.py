#!/usr/bin/env python3
"""
THE GRID — a year of real GitHub contributions as a retro snake game.

A glowing data-worm runs the serpentine route through the calendar,
consuming every day-cell it crosses while the score climbs. Cells flash,
pop and respawn behind the tail. Flat 2D, CRT framing, pure SVG.

Usage:  python3 scripts/gen_arcade.py <username> [out.svg]
Needs:  GH_TOKEN / GITHUB_TOKEN in env (GraphQL contributions API).
"""
import json, math, os, subprocess, sys, xml.dom.minidom

W          = 1200
CELL, GAP  = 16, 4
PITCH      = CELL + GAP
ROWS       = 7
DUR        = 22.0
Y0         = 176

FRAME  = "#1d4fd0"
WORM   = "#5cf7ff"
SEGS   = 10          # head + body segments
CYAN, VIOLET, GREEN, GOLD = "#00e5ff", "#a855ff", "#00ff9d", "#ffb800"
INK, MUTE, DIM = "#eaf6ff", "#8fa8bf", "#54708a"
MONO = "'JetBrains Mono','Fira Code',ui-monospace,'SF Mono',Menlo,Consolas,monospace"
DOT  = ["#18244a", "#1f6a94", "#22a3cf", "#3ad4f5", "#9dfbff"]
MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]


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


def worm(dur, path):
    """Head plus trailing segments, all riding the same route on a stagger."""
    out = []
    for i in range(SEGS):
        lead = -(SEGS - i) * 0.052            # head is furthest along
        t    = i / (SEGS - 1)
        if i == 0:
            g = (f'<circle r="12" fill="{WORM}" opacity=".18"/>'
                 f'<rect x="-7.5" y="-7.5" width="15" height="15" rx="4" fill="#eafeff"/>'
                 f'<rect x="-4" y="-4" width="8" height="8" rx="2.5" fill="{WORM}"/>')
        else:
            sz = 13 - 5.4 * t
            g = (f'<rect x="{-sz/2:.1f}" y="{-sz/2:.1f}" width="{sz:.1f}" height="{sz:.1f}" '
                 f'rx="{sz/3.4:.1f}" fill="{WORM}" opacity="{0.85 - 0.6*t:.2f}"/>')
        out.append(f'<g>{g}<animateMotion dur="{dur}s" repeatCount="indefinite" '
                   f'begin="{lead:.3f}s" path="{path}" keyPoints="0;1" keyTimes="0;1" '
                   f'calcMode="linear"/></g>')
    return "".join(out)


def build(cal, user):
    uid   = "p"
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

    gw = cols*PITCH - GAP
    X0 = (W - gw) // 2
    cx = lambda c: X0 + c*PITCH + CELL/2
    cy = lambda r: Y0 + r*PITCH + CELL/2

    # ── maze route: left-right, drop, right-left ──
    route, order = [], []
    for r in range(ROWS):
        rng = range(cols) if r % 2 == 0 else range(cols-1, -1, -1)
        for c in rng:
            route.append((cx(c), cy(r))); order.append((c, r))
    dist, acc = [0.0], 0.0
    for i in range(1, len(route)):
        (ax, ay), (bx, by) = route[i-1], route[i]
        acc += abs(bx-ax) + abs(by-ay); dist.append(acc)
    speed = acc / DUR
    path  = "M%.1f,%.1f " % route[0] + " ".join("L%.1f,%.1f" % p for p in route[1:])

    # ── dots ──
    cells, cum, running = [], [], 0
    for i, (c, r) in enumerate(order):
        n  = day.get((c, r), 0)
        running += n; cum.append(running)
        if (c, r) not in day: continue
        L  = lvl(n, peak)
        d  = dist[i] / speed
        if L == 4:      # power pellet
            g = (f'<circle cx="{cx(c):.0f}" cy="{cy(r):.0f}" r="7" fill="{DOT[4]}"/>'
                 f'<circle class="pw{uid}" cx="{cx(c):.0f}" cy="{cy(r):.0f}" r="7" fill="none" '
                 f'stroke="{DOT[4]}" stroke-width="1.6"/>')
        elif L == 0:
            g = f'<circle cx="{cx(c):.0f}" cy="{cy(r):.0f}" r="2.4" fill="{DOT[0]}"/>'
        else:
            s = 5 + L*1.6
            g = (f'<rect x="{cx(c)-s/2:.1f}" y="{cy(r)-s/2:.1f}" width="{s:.1f}" height="{s:.1f}" '
                 f'rx="1.6" fill="{DOT[L]}"/>')
        cells.append(f'<g class="ea{uid}" style="animation-delay:{d:.2f}s">{g}'
                     f'<title>{dates[(c,r)]}: {n}</title></g>')

    snake = worm(DUR, path)

    # ── month ticks ──
    months, seen = "", None
    for c, wk in enumerate(weeks):
        m = int(wk["firstDay"][5:7])
        if m != seen and c < cols-1:
            months += (f'<text class="m{uid}" x="{X0 + c*PITCH}" y="{Y0-18}" font-size="8.5" '
                       f'letter-spacing="2" fill="{DIM}">{MONTHS[m-1]}</text>')
            seen = m

    # ── arcade score, resting on the true total ──
    STEPS, seg = 20, DUR/20
    score = ""
    for k in range(1, STEPS):
        idx = min(int((k+1)/STEPS*len(cum))-1, len(cum)-1)
        cls = f"sc{uid} sz{uid}" if k == STEPS-1 else f"sc{uid}"
        score += (f'<text class="m{uid} {cls}" x="{X0+186}" y="86" font-size="30" font-weight="700" '
                  f'fill="{INK}" text-anchor="end" style="animation-delay:{k*seg:.2f}s">{cum[idx]}</text>')

    lives = "".join(f'<rect x="{X0+gw-22-i*26}" y="72" width="13" height="13" rx="3.5" '
                    f'fill="{WORM}" opacity="{0.9 - i*0.22:.2f}"/>' for i in range(3))

    gy1 = Y0 + ROWS*PITCH - GAP
    H   = gy1 + 128
    stats, sx = "", X0
    for k, v in [("CONTRIBUTIONS", total), ("ACTIVE DAYS", active),
                 ("PEAK / DAY", peak), ("BEST STREAK", best)]:
        stats += (f'<text class="m{uid}" x="{sx}" y="{H-30}" font-size="9" letter-spacing="3" fill="{DIM}">{k}</text>'
                  f'<text class="m{uid}" x="{sx}" y="{H-48}" font-size="20" font-weight="700" fill="{INK}">{v}</text>')
        sx += 200

    body = f'''
  <rect width="{W}" height="{H}" fill="url(#bg{uid})"/>
  <rect width="{W}" height="{H}" fill="url(#vg{uid})"/>
  <rect width="{W}" height="{H}" fill="url(#sl{uid})"/>

  <text class="m{uid}" x="{X0}" y="46" font-size="11" letter-spacing="4" fill="{GREEN}">// CONTRIBUTION_ENGINE</text>
  <text class="m{uid}" x="{X0}" y="62" font-size="10" letter-spacing="4" fill="{WORM}">SCORE</text>
  {score}
  <text class="m{uid}" x="{X0+gw}" y="46" font-size="10" letter-spacing="4" fill="{MUTE}" text-anchor="end">HI-SCORE</text>
  <text class="m{uid}" x="{X0+gw}" y="62" font-size="10" letter-spacing="3" fill="{GOLD}" text-anchor="end">{total}</text>
  {lives}
  <text class="m{uid}" x="{X0+330}" y="86" font-size="10" letter-spacing="3" fill="{DIM}">DEFRAG RUNNING</text>

  <rect x="{X0-16}" y="{Y0-40}" width="{gw+32}" height="{ROWS*PITCH-GAP+56}" rx="10"
        fill="none" stroke="{FRAME}" stroke-width="3"/>
  <rect x="{X0-10}" y="{Y0-34}" width="{gw+20}" height="{ROWS*PITCH-GAP+44}" rx="7"
        fill="none" stroke="{FRAME}" stroke-width="1.4" opacity=".55"/>
  {months}
  {"".join(cells)}
  {snake}
  {stats}'''

    defs = f'''
  <linearGradient id="bg{uid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#03000f"/><stop offset="100%" stop-color="#080322"/></linearGradient>
  <radialGradient id="vg{uid}" cx="50%" cy="46%" r="72%">
    <stop offset="0%" stop-color="{VIOLET}" stop-opacity=".15"/><stop offset="100%" stop-color="#000" stop-opacity="0"/></radialGradient>
  <pattern id="sl{uid}" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height="1" fill="#9fe6ff" opacity=".04"/></pattern>'''

    css = f'''
    .m{uid} {{ font-family:{MONO} }}
    @keyframes ea{uid} {{ 0% {{ opacity:1; transform:scale(1.9) }} 3% {{ opacity:.9; transform:scale(1.2) }}
      6% {{ opacity:0; transform:scale(.5) }} 74% {{ opacity:0; transform:scale(.5) }}
      88% {{ opacity:1; transform:scale(1) }} 100% {{ opacity:1; transform:scale(1) }} }}
    @keyframes pw{uid} {{ 0% {{ r:7px; opacity:.85 }} 100% {{ r:13px; opacity:0 }} }}
    @keyframes st{uid} {{ 0%,4.6% {{ opacity:1 }} 4.7%,100% {{ opacity:0 }} }}
    .ea{uid} {{ transform-box:fill-box; transform-origin:center; animation:ea{uid} {DUR}s linear infinite }}
    .pw{uid} {{ animation:pw{uid} 1.6s ease-out infinite }}
    .sc{uid} {{ opacity:0; animation:st{uid} {DUR}s linear infinite }}
    .sz{uid} {{ opacity:1 }}'''

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="The Grid — {total} contributions played as an arcade maze">'
            f'<title>THE GRID — {total} contributions</title>'
            f'<defs>{defs}<style><![CDATA[{css}]]></style></defs>{body}</svg>')


if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "Tanvir-Rafi03"
    out  = sys.argv[2] if len(sys.argv) > 2 else "assets/02-grid.svg"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w").write(build(fetch(user), user))
    xml.dom.minidom.parse(out)
    print(f"wrote {out} ({os.path.getsize(out):,} bytes)")
