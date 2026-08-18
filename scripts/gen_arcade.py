#!/usr/bin/env python3
"""
THE GRID — a year of GitHub contributions played as Breakout.

The contribution calendar is already a wall of coloured bricks, so it is
played as one. Three balls are simulated at 240Hz with real reflection off
the walls, the paddle and the bricks; the resulting bounce paths are baked
into SMIL polylines and each brick is given the exact timestamp it was
smashed. Nothing is faked - the animation is a replay of the simulation.

Usage:  python3 scripts/gen_arcade.py <username> [out.svg]
Needs:  GH_TOKEN / GITHUB_TOKEN in env (GraphQL contributions API).
"""
import json, math, os, random, subprocess, sys, xml.dom.minidom

W          = 1200
CELL, GAP  = 15, 4
PITCH      = CELL + GAP
ROWS       = 7
DUR        = 26.0
X0, Y0     = 116, 150
FIELD_BOT  = 432
PADDLE_Y   = 400
PADDLE_W   = 96
BALL_R     = 6.5
SPEED      = 470.0
BALLS      = 3

CANVAS, BORDER = "#0d1117", "#30363d"
FG, FG_MUTE    = "#e6edf3", "#7d8590"
RAMP  = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
BALL, PADDLE = "#eafff0", "#58a6ff"
HOT = "#39d353"
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


def simulate(cols, alive, wall_l, wall_r, brick_top, brick_bot):
    """Bounce three balls around the field; return paths, paddle track, kills."""
    kills, tracks, paddle = {}, [], []
    rng = random.Random(7)
    for b in range(BALLS):
        ang = math.radians(rng.uniform(-62, -118))
        x, y = wall_l + (wall_r - wall_l) * (0.25 + 0.25 * b), FIELD_BOT - 150
        vx, vy = SPEED * math.cos(ang), SPEED * math.sin(ang)
        pts, dist, t = [(x, y)], 0.0, 0.0
        dt = 1 / 240
        while t < DUR:
            nx, ny = x + vx * dt, y + vy * dt
            hit = False
            if nx < wall_l + BALL_R or nx > wall_r - BALL_R:
                vx = -vx; hit = True
            if ny < brick_top - 44:
                vy = -vy; hit = True
            # paddle: auto-play, always intercepts
            if ny > PADDLE_Y - BALL_R and vy > 0:
                vy = -vy
                vx += rng.uniform(-40, 40)
                sp = math.hypot(vx, vy) or SPEED
                vx, vy = vx / sp * SPEED, vy / sp * SPEED
                hit = True
            # bricks
            if brick_top <= ny <= brick_bot:
                c = int((nx - X0) // PITCH)
                r = int((ny - Y0) // PITCH)
                if 0 <= c < cols and 0 <= r < ROWS and alive.get((c, r)):
                    alive[(c, r)] = False
                    prev = kills.get((c, r))
                    if prev is None or t < prev: kills[(c, r)] = t
                    vy = -vy; hit = True
            if hit:
                pts.append((x, y))
            x, y = (x + vx * dt, y + vy * dt) if hit else (nx, ny)
            dist += math.hypot(vx * dt, vy * dt)
            t += dt
            if b == 0 and len(paddle) < 240 and abs(t * 240 / DUR - len(paddle)) < .5:
                paddle.append((t, x))
        pts.append((x, y))
        tracks.append(pts)
    return tracks, paddle, kills


def build(cal, user):
    uid   = "b"
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
    wall_l, wall_r = X0 - 14, X0 + gw + 14

    alive  = {(c, r): True for c in range(cols) for r in range(ROWS) if (c, r) in day}
    tracks, paddle, kills = simulate(cols, dict(alive), wall_l, wall_r, Y0, Y0 + gh)

    # bricks: smashed ones vanish at their real simulation timestamp
    cells = []
    for c in range(cols):
        for r in range(ROWS):
            if (c, r) not in day: continue
            n = day[(c, r)]
            L = lvl(n, peak)
            base = (f'x="{X0 + c*PITCH}" y="{Y0 + r*PITCH}" width="{CELL}" height="{CELL}" rx="3" '
                    f'fill="{RAMP[L]}" stroke="#ffffff" stroke-opacity=".05"')
            t = kills.get((c, r))
            if t is None:
                cells.append(f'<rect {base}><title>{n} on {dates[(c,r)]}</title></rect>')
            else:
                cells.append(f'<rect class="br{uid}" {base} style="animation-delay:{t:.2f}s">'
                             f'<title>{n} on {dates[(c,r)]}</title></rect>')

    # balls
    balls = ""
    for pts in tracks:
        d = "M%.1f,%.1f " % pts[0] + " ".join("L%.1f,%.1f" % p for p in pts[1:])
        balls += (f'<g><circle r="{BALL_R+5}" fill="{BALL}" opacity=".16"/>'
                  f'<circle r="{BALL_R}" fill="{BALL}"/>'
                  f'<animateMotion dur="{DUR}s" repeatCount="indefinite" path="{d}" '
                  f'keyPoints="0;1" keyTimes="0;1" calcMode="linear"/></g>')

    # paddle tracks ball one
    if paddle:
        xs = [f"{max(wall_l, min(wall_r - PADDLE_W, x - PADDLE_W/2)):.0f}" for _, x in paddle]
        xs.append(xs[0])
        kt = ";".join(f"{i/(len(xs)-1):.4f}" for i in range(len(xs)))
        pad = (f'<rect x="{xs[0]}" y="{PADDLE_Y}" width="{PADDLE_W}" height="11" rx="5.5" fill="{PADDLE}">'
               f'<animate attributeName="x" values="{";".join(xs)}" keyTimes="{kt}" '
               f'dur="{DUR}s" repeatCount="indefinite" calcMode="linear"/></rect>')
    else:
        pad = ""

    labels, seen = "", None
    for c, wk in enumerate(weeks):
        m = int(wk["firstDay"][5:7])
        if m != seen and c < cols - 1:
            labels += (f'<text class="m{uid}" x="{X0 + c*PITCH}" y="{Y0-10}" font-size="11" fill="{FG_MUTE}">{MONTHS[m-1]}</text>')
            seen = m
    for r, nm in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        labels += (f'<text class="m{uid}" x="{X0-22}" y="{Y0 + r*PITCH + 12}" font-size="11" '
                   f'fill="{FG_MUTE}" text-anchor="end">{nm}</text>')

    # score climbs with bricks actually smashed
    ks = sorted(kills.items(), key=lambda kv: kv[1])
    STEPS, score, running = 22, "", 0
    marks = []
    for (c, r), t in ks:
        running += day[(c, r)]
        marks.append((t, running))
    if marks:
        for k in range(1, STEPS):
            tt = k * DUR / STEPS
            val = 0
            for t, v in marks:
                if t <= tt: val = v
                else: break
            cls = f"sc{uid} sz{uid}" if k == STEPS - 1 else f"sc{uid}"
            score += (f'<text class="m{uid} {cls}" x="{X0+gw}" y="72" font-size="30" font-weight="700" '
                      f'fill="{HOT}" text-anchor="end" style="animation-delay:{tt:.2f}s">{val}</text>')

    lg_x = X0 + gw - 168
    H = FIELD_BOT + 96
    legend = f'<text class="m{uid}" x="{lg_x}" y="{FIELD_BOT+35}" font-size="11" fill="{FG_MUTE}">Less</text>'
    for i in range(5):
        legend += (f'<rect x="{lg_x + 36 + i*18}" y="{FIELD_BOT+24}" width="{CELL}" height="{CELL}" rx="3" '
                   f'fill="{RAMP[i]}" stroke="#ffffff" stroke-opacity=".05"/>')
    legend += f'<text class="m{uid}" x="{lg_x + 134}" y="{FIELD_BOT+35}" font-size="11" fill="{FG_MUTE}">More</text>'

    stats, sx = "", X0
    for k, v in [("ACTIVE DAYS", active), ("BUSIEST DAY", peak), ("LONGEST STREAK", best)]:
        stats += (f'<text class="m{uid}" x="{sx}" y="{FIELD_BOT+50}" font-size="10" letter-spacing="1.5" fill="{FG_MUTE}">{k}</text>'
                  f'<text class="m{uid}" x="{sx}" y="{FIELD_BOT+32}" font-size="19" font-weight="700" fill="{FG}">{v}</text>')
        sx += 200

    body = f'''
  <rect width="{W}" height="{H}" fill="{CANVAS}"/>
  <rect x="18" y="18" width="{W-36}" height="{H-36}" rx="8" fill="none" stroke="{BORDER}"/>
  <text class="m{uid}" x="{X0}" y="52" font-size="16" fill="{FG}">{total} contributions in the last year</text>
  <text class="m{uid}" x="{X0}" y="74" font-size="11" fill="{FG_MUTE}">{weeks[0]["firstDay"]} &#8211; {weeks[-1]["contributionDays"][-1]["date"]}</text>
  <text class="m{uid}" x="{X0+gw}" y="46" font-size="10" letter-spacing="3" fill="{FG_MUTE}" text-anchor="end">SCORE</text>
  {score}
  <text class="m{uid}" x="{X0+gw}" y="92" font-size="10" letter-spacing="2" fill="{FG_MUTE}" text-anchor="end">HI {total}</text>
  <g>
    <rect x="{X0+gw-92}" y="106" width="86" height="20" rx="10" fill="{HOT}" fill-opacity=".14" stroke="{HOT}" stroke-opacity=".45"/>
    <circle class="bl{uid}" cx="{X0+gw-78}" cy="116" r="3.4" fill="{HOT}"/>
    <text class="m{uid}" x="{X0+gw-66}" y="120" font-size="9.5" letter-spacing="1.6" fill="{HOT}">PLAYING</text>
  </g>
  <rect x="{wall_l}" y="{Y0-52}" width="{wall_r-wall_l}" height="{FIELD_BOT-Y0+64}" rx="6"
        fill="#ffffff" fill-opacity=".012" stroke="{BORDER}" stroke-opacity=".8"/>
  {labels}
  {"".join(cells)}
  {pad}
  {balls}
  {legend}
  {stats}'''

    css = f'''
    .m{uid} {{ font-family:{MONO} }}
    @keyframes br{uid} {{
      0%   {{ opacity:1; transform:scale(1) }}
      1.4% {{ opacity:1; transform:scale(1.6) }}
      4%   {{ opacity:0; transform:scale(.3) }}
      93%  {{ opacity:0; transform:scale(.3) }}
      99%  {{ opacity:1; transform:scale(1) }}
      100% {{ opacity:1; transform:scale(1) }} }}
    @keyframes st{uid} {{ 0%,4.2% {{ opacity:1 }} 4.3%,100% {{ opacity:0 }} }}
    @keyframes bl{uid} {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.25 }} }}
    .br{uid} {{ transform-box:fill-box; transform-origin:center; animation:br{uid} {DUR}s linear infinite }}
    .sc{uid} {{ opacity:0; animation:st{uid} {DUR}s linear infinite }}
    .sz{uid} {{ opacity:1 }}
    .bl{uid} {{ animation:bl{uid} 1.4s ease-in-out infinite }}'''

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="{total} contributions played as Breakout">'
            f'<title>{total} contributions in the last year</title>'
            f'<defs><style><![CDATA[{css}]]></style></defs>{body}</svg>')


if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "Tanvir-Rafi03"
    out  = sys.argv[2] if len(sys.argv) > 2 else "assets/02-grid.svg"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w").write(build(fetch(user), user))
    xml.dom.minidom.parse(out)
    print(f"wrote {out} ({os.path.getsize(out):,} bytes)")
