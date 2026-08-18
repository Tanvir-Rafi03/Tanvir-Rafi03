#!/usr/bin/env python3
"""
THE GRID — GitHub's own contribution calendar, played as snake.

Deliberately faithful to the real thing: same 53x7 layout, same day and
month labels, GitHub's dark-mode green ramp, and the Less/More legend. A
snake then runs the serpentine route eating every day-cell while the score
climbs, so it reads as the familiar table and as a game at the same time.

Usage:  python3 scripts/gen_arcade.py <username> [out.svg]
Needs:  GH_TOKEN / GITHUB_TOKEN in env (GraphQL contributions API).
"""
import json, os, subprocess, sys, xml.dom.minidom

W          = 1200
CELL, GAP  = 15, 4
PITCH      = CELL + GAP
ROWS       = 7
DUR        = 22.0
X0, Y0     = 116, 150
SEGS       = 11

# GitHub dark-mode palette
CANVAS, BORDER = "#0d1117", "#30363d"
FG, FG_MUTE    = "#e6edf3", "#7d8590"
RAMP  = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
SNAKE, SNAKE_HD = "#39d353", "#eafff0"
ACCENT = "#58a6ff"

MONO   = "'JetBrains Mono','Fira Code',ui-monospace,'SF Mono',Menlo,Consolas,monospace"
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


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
    uid   = "s"
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

    gw = cols * PITCH - GAP
    gh = ROWS * PITCH - GAP
    cx = lambda c: X0 + c * PITCH + CELL / 2
    cy = lambda r: Y0 + r * PITCH + CELL / 2

    # serpentine route: down a week, across, up the next
    route, order = [], []
    for c in range(cols):
        rng = range(ROWS) if c % 2 == 0 else range(ROWS - 1, -1, -1)
        for r in rng:
            route.append((cx(c), cy(r))); order.append((c, r))
    dist, acc = [0.0], 0.0
    for i in range(1, len(route)):
        (ax, ay), (bx, by) = route[i-1], route[i]
        acc += abs(bx-ax) + abs(by-ay); dist.append(acc)
    speed = acc / DUR
    path  = "M%.1f,%.1f " % route[0] + " ".join("L%.1f,%.1f" % p for p in route[1:])

    # cells — uniform squares, exactly like the real calendar
    cells, cum, running = [], [], 0
    for i, (c, r) in enumerate(order):
        n = day.get((c, r), 0)
        running += n; cum.append(running)
        if (c, r) not in day: continue
        L = lvl(n, peak)
        cells.append(
            f'<rect class="ea{uid}" x="{X0 + c*PITCH}" y="{Y0 + r*PITCH}" width="{CELL}" height="{CELL}" '
            f'rx="3" fill="{RAMP[L]}" stroke="#ffffff" stroke-opacity=".04" '
            f'style="animation-delay:{dist[i]/speed:.2f}s">'
            f'<title>{n} contributions on {dates[(c,r)]}</title></rect>')

    # snake
    snake = ""
    for i in range(SEGS):
        lead = -(SEGS - i) * 0.05
        t = i / (SEGS - 1)
        if i == 0:
            g = (f'<rect x="-9" y="-9" width="18" height="18" rx="5" fill="{SNAKE_HD}"/>'
                 f'<rect x="-5" y="-5" width="10" height="10" rx="3" fill="{SNAKE}"/>')
        else:
            sz = 15 - 6.5 * t
            g = (f'<rect x="{-sz/2:.1f}" y="{-sz/2:.1f}" width="{sz:.1f}" height="{sz:.1f}" '
                 f'rx="{sz/3.6:.1f}" fill="{SNAKE}" opacity="{0.92 - 0.62*t:.2f}"/>')
        snake += (f'<g>{g}<animateMotion dur="{DUR}s" repeatCount="indefinite" begin="{lead:.3f}s" '
                  f'path="{path}" keyPoints="0;1" keyTimes="0;1" calcMode="linear"/></g>')

    # month labels across the top, day labels down the left
    labels, seen = "", None
    for c, wk in enumerate(weeks):
        m = int(wk["firstDay"][5:7])
        if m != seen and c < cols - 1:
            labels += (f'<text class="m{uid}" x="{X0 + c*PITCH}" y="{Y0-10}" font-size="11" '
                       f'fill="{FG_MUTE}">{MONTHS[m-1]}</text>')
            seen = m
    for r, nm in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        labels += (f'<text class="m{uid}" x="{X0-12}" y="{cy(r)+4:.0f}" font-size="11" '
                   f'fill="{FG_MUTE}" text-anchor="end">{nm}</text>')

    # Less / More legend, bottom right
    lg_x = X0 + gw - 168
    lg_y = Y0 + gh + 26
    legend = f'<text class="m{uid}" x="{lg_x}" y="{lg_y+11}" font-size="11" fill="{FG_MUTE}">Less</text>'
    for i in range(5):
        legend += (f'<rect x="{lg_x + 36 + i*18}" y="{lg_y}" width="{CELL}" height="{CELL}" rx="3" '
                   f'fill="{RAMP[i]}" stroke="#ffffff" stroke-opacity=".04"/>')
    legend += f'<text class="m{uid}" x="{lg_x + 134}" y="{lg_y+11}" font-size="11" fill="{FG_MUTE}">More</text>'

    # live score, resting on the true total
    STEPS, seg = 20, DUR / 20
    score = ""
    for k in range(1, STEPS):
        idx = min(int((k+1)/STEPS*len(cum)) - 1, len(cum) - 1)
        cls = f"sc{uid} sz{uid}" if k == STEPS - 1 else f"sc{uid}"
        score += (f'<text class="m{uid} {cls}" x="{X0+gw}" y="72" font-size="30" font-weight="700" '
                  f'fill="{SNAKE}" text-anchor="end" style="animation-delay:{k*seg:.2f}s">{cum[idx]}</text>')

    H = lg_y + 104
    stats, sx = "", X0
    for k, v in [("ACTIVE DAYS", active), ("BUSIEST DAY", peak), ("LONGEST STREAK", best)]:
        stats += (f'<text class="m{uid}" x="{sx}" y="{H-26}" font-size="10" letter-spacing="1.5" fill="{FG_MUTE}">{k}</text>'
                  f'<text class="m{uid}" x="{sx}" y="{H-44}" font-size="19" font-weight="700" fill="{FG}">{v}</text>')
        sx += 210

    body = f'''
  <rect width="{W}" height="{H}" fill="{CANVAS}"/>
  <rect x="18" y="18" width="{W-36}" height="{H-36}" rx="8" fill="none" stroke="{BORDER}"/>

  <text class="m{uid}" x="{X0}" y="52" font-size="16" fill="{FG}">{total} contributions in the last year</text>
  <text class="m{uid}" x="{X0}" y="74" font-size="11" fill="{FG_MUTE}">{weeks[0]["firstDay"]} &#8211; {weeks[-1]["contributionDays"][-1]["date"]}</text>
  <text class="m{uid}" x="{X0+gw}" y="46" font-size="10" letter-spacing="3" fill="{FG_MUTE}" text-anchor="end">SCORE</text>
  {score}
  <g>
    <rect x="{X0+gw-92}" y="88" width="86" height="20" rx="10" fill="{SNAKE}" fill-opacity=".14" stroke="{SNAKE}" stroke-opacity=".45"/>
    <circle class="bl{uid}" cx="{X0+gw-78}" cy="98" r="3.4" fill="{SNAKE}"/>
    <text class="m{uid}" x="{X0+gw-66}" y="102" font-size="9.5" letter-spacing="1.6" fill="{SNAKE}">PLAYING</text>
  </g>

  {labels}
  {"".join(cells)}
  {snake}
  {legend}
  {stats}'''

    css = f'''
    .m{uid} {{ font-family:{MONO} }}
    @keyframes ea{uid} {{
      0%   {{ opacity:1; transform:scale(1.55) }}
      3%   {{ opacity:.9; transform:scale(1.15) }}
      6%   {{ opacity:.14; transform:scale(.62) }}
      72%  {{ opacity:.14; transform:scale(.62) }}
      88%  {{ opacity:1; transform:scale(1) }}
      100% {{ opacity:1; transform:scale(1) }} }}
    @keyframes st{uid} {{ 0%,4.6% {{ opacity:1 }} 4.7%,100% {{ opacity:0 }} }}
    @keyframes bl{uid} {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.25 }} }}
    .ea{uid} {{ transform-box:fill-box; transform-origin:center; animation:ea{uid} {DUR}s linear infinite }}
    .sc{uid} {{ opacity:0; animation:st{uid} {DUR}s linear infinite }}
    .sz{uid} {{ opacity:1 }}
    .bl{uid} {{ animation:bl{uid} 1.4s ease-in-out infinite }}'''

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="{total} contributions in the last year, played as snake">'
            f'<title>{total} contributions in the last year</title>'
            f'<defs><style><![CDATA[{css}]]></style></defs>{body}</svg>')


if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "Tanvir-Rafi03"
    out  = sys.argv[2] if len(sys.argv) > 2 else "assets/02-grid.svg"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w").write(build(fetch(user), user))
    xml.dom.minidom.parse(out)
    print(f"wrote {out} ({os.path.getsize(out):,} bytes)")
