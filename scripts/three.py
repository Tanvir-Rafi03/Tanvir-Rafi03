"""
Minimal 3D engine for SVG.

A README cannot execute JavaScript, so Three.js is not an option there.
Instead we do the real work up front: rotate geometry in 3D, apply a
perspective divide, and bake every frame into a SMIL `values` list. The
result is genuine projected 3D that animates in a plain <img> SVG with no
scripting at all.
"""
import math

FRAMES = 36           # one full revolution, 10 deg per frame


def rot(p, ax, ay, az):
    x, y, z = p
    cy, sy = math.cos(ay), math.sin(ay)
    x, z = x*cy + z*sy, -x*sy + z*cy
    cx, sx = math.cos(ax), math.sin(ax)
    y, z = y*cx - z*sx, y*sx + z*cx
    cz, sz = math.cos(az), math.sin(az)
    x, y = x*cz - y*sz, x*sz + y*cz
    return (x, y, z)


def project(p, cx, cy, fov=520, dist=760):
    """Perspective divide. Returns (x, y, scale) — scale drives depth cues."""
    x, y, z = p
    s = fov / max(1e-3, dist + z)
    return (cx + x*s, cy + y*s, s)


def ring(n=64, r=1.0, tilt=0.0):
    """Points on a circle in the XZ plane, tilted about X."""
    pts = []
    for i in range(n):
        a = 2*math.pi*i/n
        p = (r*math.cos(a), 0.0, r*math.sin(a))
        pts.append(rot(p, tilt, 0, 0))
    return pts


def ring_frames(cx, cy, r, tilt, spin_axis="y", frames=FRAMES, wobble=0.0):
    """A rotating ring as a list of SVG path 'd' strings, one per frame."""
    base, out = ring(48, r, tilt), []
    for f in range(frames):
        t = 2*math.pi*f/frames
        ax = wobble*math.sin(t)
        pts = []
        for p in base:
            q = rot(p, ax, t if spin_axis == "y" else 0, t if spin_axis == "z" else 0)
            X, Y, _ = project(q, cx, cy)
            pts.append(f"{X:.1f},{Y:.1f}")
        out.append("M" + "L".join(pts) + "Z")
    return out


def orb_frames(cx, cy, r, tilt, phase=0.0, frames=FRAMES):
    """A bead riding a ring: returns per-frame (x, y, depth-scale)."""
    out = []
    for f in range(frames):
        t = 2*math.pi*f/frames
        a = t + phase
        p = rot((r*math.cos(a), 0.0, r*math.sin(a)), tilt, 0, 0)
        out.append(project(p, cx, cy))
    return out


def smil(attr, vals, dur, extra=""):
    return (f'<animate attributeName="{attr}" values="{";".join(vals)}" '
            f'dur="{dur}s" repeatCount="indefinite" calcMode="linear"{extra}/>')


# ── isometric helpers for the voxel contribution terrain ──────────────────
ISO_X, ISO_Y = 0.8660254, 0.5      # cos30 / sin30


def iso(gx, gy, gz, ox, oy, s=1.0, yk=1.0):
    """Grid coords -> screen. gz is tower height in cells. yk flattens the view."""
    return (ox + (gx - gy) * ISO_X * s,
            oy + (gx + gy) * ISO_Y * s * yk - gz * s)


def tower(gx, gy, h, ox, oy, s, top, left, right, cap=None, yk=1.0):
    """One extruded voxel column drawn as three shaded faces."""
    tx, ty = iso(gx, gy, h, ox, oy, s, yk)
    hw, hh = ISO_X * s, ISO_Y * s * yk
    top_f  = f"{tx:.1f},{ty-hh:.1f} {tx+hw:.1f},{ty:.1f} {tx:.1f},{ty+hh:.1f} {tx-hw:.1f},{ty:.1f}"
    bz     = iso(gx, gy, 0, ox, oy, s, yk)[1]
    left_f = f"{tx-hw:.1f},{ty:.1f} {tx:.1f},{ty+hh:.1f} {tx:.1f},{bz+hh:.1f} {tx-hw:.1f},{bz:.1f}"
    rght_f = f"{tx+hw:.1f},{ty:.1f} {tx:.1f},{ty+hh:.1f} {tx:.1f},{bz+hh:.1f} {tx+hw:.1f},{bz:.1f}"
    o = (f'<polygon points="{left_f}" fill="{left}"/>'
         f'<polygon points="{rght_f}" fill="{right}"/>'
         f'<polygon points="{top_f}" fill="{top}"/>')
    if cap:
        o += f'<polygon points="{top_f}" fill="{cap}" opacity=".55"/>'
    return o
