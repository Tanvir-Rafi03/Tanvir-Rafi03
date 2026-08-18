#!/usr/bin/env python3
"""
NEURAL GRID // DEFRAG
Renders a GitHub contribution calendar as an animated cyberpunk arcade game:
a data-worm snakes through the grid consuming contribution cells while a HUD
tracks the score. Pure SVG + CSS/SMIL animation, no JS, no external assets.

Usage:  python3 scripts/gen_arcade.py <username> [out.svg]
Requires: GITHUB_TOKEN in env (for the GraphQL contributions API).
"""
import json, os, subprocess, sys, datetime

CELL, GAP = 12, 3
PITCH     = CELL + GAP
X0, Y0    = 58, 86
ROWS      = 7
DUR       = 16.0          # seconds for one full sweep
TRAIL     = 6             # snake body segments

# level ramp: empty -> peak
RAMP = ["#0b1030", "#12557f", "#0a9ad6", "#31d6ff", "#8dfff0"]
MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]


def fetch(user):
    q = """
    { user(login: "%s") { contributionsCollection { contributionCalendar {
        totalContributions
        weeks { firstDay contributionDays { contributionCount date weekday } } } } } }
    """ % user
    out = subprocess.run(["gh", "api", "graphql", "-f", "query=" + q],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def level(c, peak):
    if c <= 0: return 0
    if peak <= 1: return 4
    q = c / peak
    if q > 0.5:  return 4
    if q > 0.25: return 3
    if q > 0.1:  return 2
    return 1


def build(cal, user):
    weeks = cal["weeks"]
    cols  = len(weeks)
    total = cal["totalContributions"]

    # index days by (col,row)
    day = {}
    for c, wk in enumerate(weeks):
        for d in wk["contributionDays"]:
            day[(c, int(d["weekday"]))] = d["contributionCount"]
    day_date = {}
    for c, wk in enumerate(weeks):
        for dd in wk["contributionDays"]:
            day_date[(c, int(dd["weekday"]))] = dd["date"]
    peak   = max(day.values()) if day else 0
    active = sum(1 for v in day.values() if v > 0)

    # longest streak of consecutive active days
    seq = [day[(c, r)] for c in range(cols) for r in range(ROWS) if (c, r) in day]
    best = run = 0
    for v in seq:
        run = run + 1 if v > 0 else 0
        best = max(best, run)

    cx = lambda c: X0 + c * PITCH + CELL / 2
    cy = lambda r: Y0 + r * PITCH + CELL / 2

    # ── serpentine path: down col0, up col1, down col2 ... ──
    pts, order = [], []
    for c in range(cols):
        rows = range(ROWS) if c % 2 == 0 else range(ROWS - 1, -1, -1)
        for r in rows:
            pts.append((cx(c), cy(r)))
            order.append((c, r))

    # cumulative distance -> per-cell delay
    dist, acc = [0.0], 0.0
    for i in range(1, len(pts)):
        (ax, ay), (bx, by) = pts[i - 1], pts[i]
        acc += abs(bx - ax) + abs(by - ay)
        dist.append(acc)
    speed = acc / DUR

    path = "M%.1f,%.1f " % pts[0] + " ".join("L%.1f,%.1f" % p for p in pts[1:])

    # ── cells ──
    cells = []
    for i, (c, r) in enumerate(order):
        if (c, r) not in day:
            continue
        n  = day[(c, r)]
        lv = level(n, peak)
        d  = dist[i] / speed
        cls = "c e" if lv == 0 else "c"
        gl  = ' filter="url(#gl)"' if lv >= 3 else ''
        cells.append(
            '<rect class="%s" x="%d" y="%d" width="%d" height="%d" rx="2.5" fill="%s"%s '
            'style="animation-delay:%.2fs"><title>%s: %d</title></rect>'
            % (cls, X0 + c * PITCH, Y0 + r * PITCH, CELL, CELL, RAMP[lv], gl, d,
               day_date.get((c, r), ''), n))

    # ── month ticks ──
    months, seen = [], None
    for c, wk in enumerate(weeks):
        m = int(wk["firstDay"][5:7])
        if m != seen and c < cols - 1:
            months.append('<text class="ax" x="%d" y="%d">%s</text>'
                          % (X0 + c * PITCH, Y0 - 12, MONTHS[m - 1]))
            seen = m

    # ── score readout: N steps synced to the sweep ──
    STEPS = 20
    seg   = DUR / STEPS
    cum, running = [], 0
    for i, (c, r) in enumerate(order):
        running += day.get((c, r), 0)
        cum.append(running)
    score = []
    for k in range(STEPS):
        idx = min(int((k + 1) / STEPS * len(cum)) - 1, len(cum) - 1)
        # last step holds the true total and stays visible when animation does not run
        cls = 'sc sc0' if k == STEPS - 1 else 'sc'
        score.append('<text class="%s" x="%d" y="48" text-anchor="end" style="animation-delay:%.2fs">%d</text>'
                     % (cls, X0 + 742, k * seg, cum[idx]))

    # ── snake ──
    snake = []
    for s in range(TRAIL, -1, -1):
        lead = -(TRAIL - s) * 0.055
        if s == TRAIL:   # head
            body = ('<g class="head" filter="url(#gl)">'
                    '<circle r="13" fill="#00ffe0" opacity=".2"/>'
                    '<circle r="8.5" fill="#00ffe0" opacity=".45"/>'
                    '<circle r="5.6" fill="#f2fffd"/><circle r="2.6" fill="#00ffe0"/></g>')
        else:
            o = 0.20 + 0.62 * (s / TRAIL)
            body = ('<circle r="%.1f" fill="#00ffe0" opacity="%.2f" filter="url(#gl)"/>'
                    % (2.6 + 3.4 * (s / TRAIL), o))
        snake.append(
            '<g>%s<animateMotion dur="%.1fs" repeatCount="indefinite" begin="%.3fs" '
            'path="%s" keyPoints="0;1" keyTimes="0;1" calcMode="linear"/></g>'
            % (body, DUR, lead, path))

    W = X0 + cols * PITCH + 20
    H = Y0 + ROWS * PITCH + 74
    gridw = cols * PITCH - GAP

    css = """
  .f  { font-family:'JetBrains Mono','Fira Code',ui-monospace,'SF Mono',Menlo,Consolas,monospace; }
  .ax { font-size:10px; fill:#4c7ba6; letter-spacing:2px; }
  .lb { font-size:9px;  fill:#4c7ba6; letter-spacing:2px; }
  .t1 { font-size:19px; fill:#eaf6ff; font-weight:700; letter-spacing:5px; }
  .t2 { font-size:10px; fill:#00c853; letter-spacing:4px; }
  .hk { font-size:9px;  fill:#5a7fa0; letter-spacing:3px; }
  .hv { font-size:15px; fill:#eaf6ff; font-weight:700; letter-spacing:1px; }
  .sc { font-size:30px; fill:#00ffe0; font-weight:700; letter-spacing:1px;
        opacity:0; animation:step DURs linear infinite;
        filter:drop-shadow(0 0 6px rgba(0,255,224,.55)); }
  .sc0{ opacity:1 }
  .c  { transform-box:fill-box; transform-origin:center;
        animation:eat DURs linear infinite; }
  .e  { animation-name:eatdim; }
  @keyframes eat {
      0%   { opacity:1;  transform:scale(1.8); }
      2.4% { opacity:.95; transform:scale(1.2); }
      5%   { opacity:.12; transform:scale(.9); }
     70%   { opacity:.12; transform:scale(.9); }
     86%   { opacity:1;  transform:scale(1); }
    100%   { opacity:1;  transform:scale(1); }
  }
  @keyframes eatdim {
      0%   { opacity:.9;  transform:scale(1.5); }
      4%   { opacity:.35; transform:scale(1); }
      9%   { opacity:.62; transform:scale(1); }
    100%   { opacity:.62; transform:scale(1); }
  }
  @keyframes step { 0%,4.6% { opacity:1 } 4.7%,100% { opacity:0 } }
  @keyframes blip { 0%,100% { opacity:1 } 50% { opacity:.28 } }
  @keyframes scan { 0% { transform:translateX(-140px) } 100% { transform:translateX(WIDTHpx) } }
  .blip { animation:blip 1.5s ease-in-out infinite; }
  .scan { animation:scan DURs linear infinite; }
""".replace("DURs", "%.1fs" % DUR).replace("GRIDWpx", "%dpx" % gridw).replace("WIDTHpx", "%dpx" % W)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{user} contribution arcade — {total} contributions">
<title>NEURAL GRID // DEFRAG — {total} contributions</title>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#03000f"/><stop offset="100%" stop-color="#080126"/>
  </linearGradient>
  <radialGradient id="vig" cx="50%" cy="45%" r="70%">
    <stop offset="0%" stop-color="#7000ff" stop-opacity=".16"/>
    <stop offset="100%" stop-color="#000" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="sw" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#00bfff" stop-opacity="0"/>
    <stop offset="50%" stop-color="#00ffe0" stop-opacity=".13"/>
    <stop offset="100%" stop-color="#00bfff" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="bl" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#00ffe0"/><stop offset="60%" stop-color="#00bfff"/>
    <stop offset="100%" stop-color="#7000ff"/>
  </linearGradient>
  <pattern id="sl" width="3" height="3" patternUnits="userSpaceOnUse">
    <rect width="3" height="1" fill="#7fd8ff" opacity=".045"/>
  </pattern>
  <filter id="gl" x="-70%" y="-70%" width="240%" height="240%">
    <feGaussianBlur stdDeviation="2.6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <clipPath id="cf"><rect width="{W}" height="{H}" rx="10"/></clipPath>
  <style><![CDATA[{css}]]></style>
</defs>
<g clip-path="url(#cf)" class="f">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#vig)"/>
  <rect width="{W}" height="{H}" fill="url(#sl)"/>
  <rect class="scan" x="0" y="0" width="140" height="{H}" fill="url(#sw)"/>

  <text class="t2" x="24" y="30">// NEURAL_GRID</text>
  <text class="t1" x="24" y="56">DEFRAG</text>
  <circle class="blip" cx="214" cy="25" r="4" fill="#00c853"/>
  <text class="t2" x="226" y="30">RUNNING</text>
  <text class="hk" x="{X0 + 742}" y="26" text-anchor="end">SCORE</text>
  {"".join(score)}

  <text class="lb" x="24" y="{cy(1) + 3}">MON</text>
  <text class="lb" x="24" y="{cy(3) + 3}">WED</text>
  <text class="lb" x="24" y="{cy(5) + 3}">FRI</text>
  {"".join(months)}

  <rect x="{X0 - 8}" y="{Y0 - 8}" width="{gridw + 16}" height="{ROWS * PITCH - GAP + 16}"
        rx="6" fill="none" stroke="#00bfff" stroke-opacity=".14"/>
  {"".join(cells)}
  {"".join(snake)}

  <rect x="{X0}" y="{Y0 + ROWS * PITCH + 14}" width="{gridw}" height="3" rx="1.5" fill="#00bfff" fill-opacity=".12"/>
  <rect x="{X0}" y="{Y0 + ROWS * PITCH + 14}" width="{gridw}" height="3" rx="1.5" fill="url(#bl)">
    <animate attributeName="width" from="0" to="{gridw}" dur="{DUR}s" begin="0s" repeatCount="indefinite"/></rect>

  <g transform="translate(24,{H - 20})">
    <text class="hk" x="0"   y="0">TOTAL</text>   <text class="hv" x="0"   y="-16">{total}</text>
    <text class="hk" x="120" y="0">ACTIVE DAYS</text><text class="hv" x="120" y="-16">{active}</text>
    <text class="hk" x="300" y="0">PEAK</text>    <text class="hv" x="300" y="-16">{peak}</text>
    <text class="hk" x="400" y="0">BEST STREAK</text><text class="hv" x="400" y="-16">{best}</text>
    <text class="hk" x="560" y="0">RANGE</text>
    <text class="hv" x="560" y="-16" style="font-size:12px">{weeks[0]["firstDay"]} → {weeks[-1]["contributionDays"][-1]["date"]}</text>
  </g>

  <g stroke="#00bfff" stroke-width="1.6" fill="none" opacity=".7">
    <path d="M14 34 V14 H34"/><path d="M{W - 34} 14 H{W - 14} V34"/>
    <path d="M14 {H - 34} V{H - 14} H34"/><path d="M{W - 14} {H - 34} V{H - 14} H{W - 34}"/>
  </g>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="none" stroke="#00bfff" stroke-opacity=".18"/>
</g>
</svg>'''


if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "Tanvir-Rafi03"
    out  = sys.argv[2] if len(sys.argv) > 2 else "assets/contribution-arcade.svg"
    svg  = build(fetch(user), user)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out} ({len(svg):,} bytes)")
