#!/usr/bin/env python3
"""
03 · CAMPAIGN_MAP
A year of real GitHub contributions rendered as an arcade sweep: a data-worm
runs a serpentine path through the grid, consuming each day-cell as it passes
while the score climbs. Pure SVG + CSS/SMIL. No JS, no external assets.

Usage:  python3 scripts/gen_arcade.py <username> [out.svg]
Needs:  GH_TOKEN / GITHUB_TOKEN in env (GraphQL contributions API).
"""
import json, os, subprocess, sys, xml.dom.minidom
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import *

CELL, GAP = 15, 4
PITCH     = CELL + GAP
X0, Y0    = PAD, 150
ROWS, DUR = 7, 16.0
TRAIL     = 6
RAMP   = ["#0c1330", "#14507d", "#0a92cf", "#31d6ff", "#9dfff2"]
MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]


def fetch(user):
    q = """{ user(login: "%s") { contributionsCollection { contributionCalendar {
        totalContributions
        weeks { firstDay contributionDays { contributionCount date weekday } } } } } }""" % user
    out = subprocess.run(["gh","api","graphql","-f","query="+q],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def level(c, peak):
    if c <= 0: return 0
    q = c / peak if peak else 1
    return 4 if q > .5 else 3 if q > .25 else 2 if q > .1 else 1


def build(cal, user):
    uid   = "a"
    weeks = cal["weeks"]; cols = len(weeks); total = cal["totalContributions"]
    day, dates = {}, {}
    for c, wk in enumerate(weeks):
        for d in wk["contributionDays"]:
            day[(c, int(d["weekday"]))]   = d["contributionCount"]
            dates[(c, int(d["weekday"]))] = d["date"]
    peak   = max(day.values()) if day else 0
    active = sum(1 for v in day.values() if v > 0)
    seq = [day[(c,r)] for c in range(cols) for r in range(ROWS) if (c,r) in day]
    best = run = 0
    for v in seq:
        run = run + 1 if v > 0 else 0
        best = max(best, run)

    cx = lambda c: X0 + c*PITCH + CELL/2
    cy = lambda r: Y0 + r*PITCH + CELL/2

    pts, order = [], []
    for c in range(cols):
        for r in (range(ROWS) if c % 2 == 0 else range(ROWS-1, -1, -1)):
            pts.append((cx(c), cy(r))); order.append((c, r))
    dist, acc = [0.0], 0.0
    for i in range(1, len(pts)):
        (ax,ay),(bx,by) = pts[i-1], pts[i]
        acc += abs(bx-ax) + abs(by-ay); dist.append(acc)
    speed = acc / DUR
    path = "M%.1f,%.1f " % pts[0] + " ".join("L%.1f,%.1f" % p for p in pts[1:])

    cells = []
    for i,(c,r) in enumerate(order):
        if (c,r) not in day: continue
        n, lv = day[(c,r)], level(day[(c,r)], peak)
        gl = f' filter="url(#gl{uid})"' if lv >= 3 else ''
        cells.append(
            f'<rect class="c{uid}{" e"+uid if lv==0 else ""}" x="{X0+c*PITCH}" y="{Y0+r*PITCH}" '
            f'width="{CELL}" height="{CELL}" rx="3" fill="{RAMP[lv]}"{gl} '
            f'style="animation-delay:{dist[i]/speed:.2f}s"><title>{dates[(c,r)]}: {n}</title></rect>')

    months, seen = [], None
    for c, wk in enumerate(weeks):
        m = int(wk["firstDay"][5:7])
        if m != seen and c < cols-1:
            months.append(f'<text class="f{uid}" x="{X0+c*PITCH}" y="{Y0-14}" font-size="9.5" letter-spacing="2" fill="{DIM}">{MONTHS[m-1]}</text>')
            seen = m

    STEPS, seg = 20, DUR/20
    cum, run2 = [], 0
    for c, r in order:
        run2 += day.get((c,r), 0); cum.append(run2)
    score = []
    for k in range(1, STEPS):
        idx = min(int((k+1)/STEPS*len(cum))-1, len(cum)-1)
        cls = f"sc{uid} sz{uid}" if k == STEPS-1 else f"sc{uid}"
        score.append(f'<text class="f{uid} {cls}" x="{W-PAD}" y="86" font-size="30" font-weight="700" '
                     f'fill="{GOLD}" text-anchor="end" style="animation-delay:{k*seg:.2f}s">{cum[idx]}</text>')

    snake = []
    for s in range(TRAIL, -1, -1):
        lead = -(TRAIL-s)*0.055
        if s == TRAIL:
            b = (f'<g filter="url(#gl{uid})"><circle r="14" fill="{CYAN}" opacity=".2"/>'
                 f'<circle r="9" fill="{CYAN}" opacity=".45"/><circle r="6" fill="#f2fffd"/>'
                 f'<circle r="2.8" fill="{CYAN}"/></g>')
        else:
            b = (f'<circle r="{2.8+3.6*(s/TRAIL):.1f}" fill="{CYAN}" '
                 f'opacity="{.2+.62*(s/TRAIL):.2f}" filter="url(#gl{uid})"/>')
        snake.append(f'<g>{b}<animateMotion dur="{DUR}s" repeatCount="indefinite" begin="{lead:.3f}s" '
                     f'path="{path}" keyPoints="0;1" keyTimes="0;1" calcMode="linear"/></g>')

    H = Y0 + ROWS*PITCH + 96
    gridw = cols*PITCH - GAP
    stats = [("TOTAL",total),("ACTIVE DAYS",active),("PEAK/DAY",peak),("BEST STREAK",best)]
    stat_svg = "".join(
        f'<text class="f{uid}" x="{X0+i*150}" y="{H-26}" font-size="9" letter-spacing="3" fill="{DIM}">{k}</text>'
        f'<text class="f{uid}" x="{X0+i*150}" y="{H-44}" font-size="17" font-weight="700" fill="{INK}">{v}</text>'
        for i,(k,v) in enumerate(stats))

    inner = f'''
  <text class="f{uid}" x="{W-PAD}" y="60" font-size="9.5" letter-spacing="3" fill="{DIM}" text-anchor="end">SCORE</text>
  {"".join(score)}
  <text class="f{uid}" x="{X0-38}" y="{cy(1)+3}" font-size="8.5" letter-spacing="2" fill="{DIM}">MON</text>
  <text class="f{uid}" x="{X0-38}" y="{cy(3)+3}" font-size="8.5" letter-spacing="2" fill="{DIM}">WED</text>
  <text class="f{uid}" x="{X0-38}" y="{cy(5)+3}" font-size="8.5" letter-spacing="2" fill="{DIM}">FRI</text>
  {"".join(months)}
  {"".join(cells)}
  {"".join(snake)}
  <rect x="{X0}" y="{Y0+ROWS*PITCH+16}" width="{gridw}" height="3" rx="1.5" fill="{CYAN}" fill-opacity=".12"/>
  <rect x="{X0}" y="{Y0+ROWS*PITCH+16}" width="{gridw}" height="3" rx="1.5" fill="url(#bar{uid})">
    <animate attributeName="width" from="0" to="{gridw}" dur="{DUR}s" begin="0s" repeatCount="indefinite"/></rect>
  {stat_svg}
  <text class="f{uid}" x="{W-PAD}" y="{H-26}" font-size="9" letter-spacing="2" fill="{DIM}" text-anchor="end">{weeks[0]["firstDay"]} &#8594; {weeks[-1]["contributionDays"][-1]["date"]}</text>'''

    extra = f'''
    @keyframes eat{uid} {{ 0%{{opacity:1;transform:scale(1.8)}} 2.4%{{opacity:.95;transform:scale(1.2)}}
      5%{{opacity:.12;transform:scale(.9)}} 70%{{opacity:.12;transform:scale(.9)}}
      86%{{opacity:1;transform:scale(1)}} 100%{{opacity:1;transform:scale(1)}} }}
    @keyframes dim{uid} {{ 0%{{opacity:.9;transform:scale(1.5)}} 4%{{opacity:.32;transform:scale(1)}}
      9%{{opacity:.6;transform:scale(1)}} 100%{{opacity:.6;transform:scale(1)}} }}
    @keyframes st{uid} {{ 0%,4.6%{{opacity:1}} 4.7%,100%{{opacity:0}} }}
    .c{uid} {{ transform-box:fill-box; transform-origin:center; animation:eat{uid} {DUR}s linear infinite }}
    .e{uid} {{ animation-name:dim{uid} }}
    .sc{uid} {{ opacity:0; animation:st{uid} {DUR}s linear infinite;
                filter:drop-shadow(0 0 7px rgba(255,184,0,.5)) }}
    .sz{uid} {{ opacity:1 }}'''

    svg = shell(uid, H, "03", "CONTRIBUTION_ENGINE", "CAMPAIGN MAP", (inner, extra))
    return svg.replace(f"<defs>{defs(uid, H)}", f"<defs>{defs(uid, H)}"
        f'\n  <linearGradient id="bar{uid}" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0%" stop-color="{CYAN}"/><stop offset="60%" stop-color="{VIOLET}"/>'
        f'<stop offset="100%" stop-color="{GOLD}"/></linearGradient>')


if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "Tanvir-Rafi03"
    out  = sys.argv[2] if len(sys.argv) > 2 else "assets/03-campaign.svg"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w").write(build(fetch(user), user))
    xml.dom.minidom.parse(out)
    print(f"wrote {out} ({os.path.getsize(out):,} bytes)")
