"""UrbanDreamer main framework figure — v7 (component-rich).

Per the v7 spec: every sub-panel has input -> 3-6 internal parts -> output
-> one equation -> one loss/constraint tag.
Canvas 2600x1200 @ dpi100. Zones: L data (x 8-39), C dynamics model
(x 49-164) with HDV strip below, R actor-critic (x 174-255).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch, Arc
import numpy as np

BG       = "#FFFDF8"
INK      = "#263238"
SUB      = "#59636A"
P2_BG, P2_BD = "#F5F0FF", "#9B7EDE"
ACT_BG, ACT_BD = "#FFF3C4", "#D6B656"
WM_BG,  WM_BD  = "#DFF4E8", "#5A9E6F"
HDV_BG, HDV_BD = "#FCE5D5", "#D58B5A"
CAV_C, HDV_C   = "#3F7FC4", "#E79A3B"
CONG,  ROAD    = "#D7655B", "#9DA9B0"
AR_REAL, AR_WM, AR_IM, AR_HDV, AR_UPD = "#4F81BD", "#4F8F68", "#8A6FD1", "#D58B5A", "#4A4A4A"

plt.rcParams["path.sketch"] = None
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["mathtext.fontset"] = "stix"

fig, ax = plt.subplots(figsize=(26, 12), dpi=100)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 260); ax.set_ylim(0, 120)
ax.axis("off")

MODBIG, MOD, SUBT, LABEL, ANNOT, MICRO, MATH = 30, 24, 21, 17, 15, 14, 18

def text(x, y, s, size=LABEL, bold=False, color=INK, ha="center", va="center",
         z=8, rot=0):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, zorder=z,
            fontweight="bold" if bold else "normal", rotation=rot,
            linespacing=1.35)

def rbox(x, y, w, h, fc, ec, dashed=False, lw=2.6, z=2, rs=2.0, dash=(5, 3.6)):
    b = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0,rounding_size={rs}",
                       fc=fc, ec=ec, lw=lw, zorder=z,
                       linestyle=(0, dash) if dashed else "solid")
    ax.add_patch(b)
    return b

def sticker_bg(x, y, w, h, z=4, rs=1.6):
    rbox(x+0.45, y-0.5, w, h, "#00000018", "none", z=z-1, rs=rs)
    rbox(x, y, w, h, "#FFFFFF", "none", z=z, rs=rs)
    rbox(x, y, w, h, "none", INK, lw=1.4, z=z+6, rs=rs)

def arrow(p1, p2, color=AR_WM, dashed=False, dotted=False, lw=2.4, rad=0.0,
          z=6, ms=16, style="-|>"):
    ls = (0, (1.2, 2.2)) if dotted else ((0, (5, 3)) if dashed else "solid")
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=ms,
                        color=color, lw=lw, zorder=z, linestyle=ls,
                        connectionstyle=f"arc3,rad={rad}", shrinkA=1, shrinkB=1)
    ax.add_patch(a)
    return a

def seg(p1, p2, color=AR_WM, dashed=False, lw=2.4, z=6):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, lw=lw, zorder=z,
            linestyle=(0, (5, 3)) if dashed else "solid")

def loss_tag(x, y, s, color, z=7, size=None):
    size = size or MICRO
    w = 2.2 + len(s) * size * 0.075
    rbox(x-w/2, y-1.6, w, 3.2, "#FFFFFF", color, dashed=True, lw=1.6, z=z, rs=1.0)
    text(x, y, s, size=size, bold=True, color=color, z=z+1)

# ---------------- stickers ----------------
def car(x, y, s=1.0, color=CAV_C, z=6, faded=False):
    al = 0.45 if faded else 1.0
    kw = dict(zorder=z, alpha=al)
    ax.add_patch(FancyBboxPatch((x-4.6*s, y-1.7*s), 9.2*s, 3.4*s,
                 boxstyle="round,pad=0.1,rounding_size=1.2",
                 fc=color, ec=INK, lw=1.6, **kw))
    ax.add_patch(FancyBboxPatch((x-2.2*s, y+0.8*s), 4.4*s, 2.1*s,
                 boxstyle="round,pad=0.1,rounding_size=0.9",
                 fc="#BFE3F0", ec=INK, lw=1.4, **kw))
    for dx in (-2.6, 2.6):
        ax.add_patch(Circle((x+dx*s, y-2.0*s), 1.2*s, fc=INK, ec=INK, **kw))
        ax.add_patch(Circle((x+dx*s, y-2.0*s), 0.5*s, fc="#DDDDDD", **kw))

def route_card(x, y, w=3.4, h=4.4, selected=False, grayed=False, z=6):
    fc = "#E8F5E9" if selected else ("#F2F2F2" if grayed else "#FFFFFF")
    ec = "#5A9E6F" if selected else "#9DA9B0"
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.7",
                 fc=fc, ec=ec, lw=2.2 if selected else 1.4, zorder=z))
    ax.plot([x+0.8, x+w*0.45, x+w-0.8], [y+0.9, y+h-1.6, y+h-0.9],
            color=ec, lw=1.6, zorder=z+1)
    ax.add_patch(Circle((x+0.8, y+0.9), 0.35, fc=INK, zorder=z+2))
    ax.add_patch(Circle((x+w-0.8, y+h-0.9), 0.35, fc=CONG if selected else INK, zorder=z+2))

def mini_graph(x, y, s=1.0, hl_edges=(), z=6, bars=False, seed=3):
    pts = np.array([(0,0),(2.2,1.8),(4.6,0.6),(1.2,-1.9),(3.8,-1.6),(6.0,2.0)],
                   float) * s + (x, y)
    edges = [(0,1),(1,2),(0,3),(3,4),(2,4),(1,3),(2,5),(4,5)]
    for i, (a, b) in enumerate(edges):
        c = CAV_C if i in hl_edges else ROAD
        ax.plot([pts[a][0], pts[b][0]], [pts[a][1], pts[b][1]],
                color=c, lw=2.6 if i in hl_edges else 1.8, zorder=z)
    rng = np.random.RandomState(seed)
    for px, py in pts:
        ax.add_patch(Circle((px, py), 0.75*s, fc="#FFFFFF", ec=INK, lw=1.3, zorder=z+2))
        if bars:
            hb = rng.uniform(0.8, 2.6) * s
            cb = CONG if hb > 2.0*s else ("#F4B942" if hb > 1.4*s else "#7CB87C")
            ax.add_patch(Rectangle((px+0.9*s, py-0.8*s), 0.7*s, hb,
                         fc=cb, ec=INK, lw=0.6, zorder=z+2))

def latent_card(x, y, w=6.5, h=6.0, z=6, seed=0, faded=False):
    al = 0.45 if faded else 1.0
    sticker_bg(x, y, w, h, z=z, rs=1.0)
    rng = np.random.RandomState(seed)
    cols = ["#8FB8DE", "#A8D5BA", "#F4B942", "#E79A3B", "#B39DDB", "#90CAF9"]
    gw, gh = w/4.6, h/4.2
    for i in range(3):
        for j in range(3):
            ax.add_patch(Rectangle((x+0.85+j*(gw+0.4), y+0.85+i*(gh+0.45)), gw, gh,
                         fc=cols[rng.randint(len(cols))], ec=INK, lw=0.5,
                         zorder=z+7, alpha=al))

def road(x1, y1, x2, y2, color=ROAD, z=5, al=1.0):
    ax.plot([x1, x2], [y1, y2], color=color, lw=4.6, zorder=z,
            solid_capstyle="round", alpha=al)
    ax.plot([x1, x2], [y1, y2], color="#FFFFFF", lw=1.1, zorder=z+1,
            linestyle=(0, (2.2, 2.2)), alpha=al)

def city_map(x, y, w=20, h=13, z=6, faded=False, cong=True):
    al = 0.45 if faded else 1.0
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                 boxstyle="round,pad=0.1,rounding_size=1.2",
                 fc="#EDF4EE", ec=INK, lw=1.6, zorder=z, alpha=al))
    road(x-w/2+1.5, y-1.0, x+w/2-1.5, y-1.0, z=z+1, al=al)
    road(x+1.5, y-h/2+1.5, x+1.5, y+h/2-1.5, z=z+1, al=al)
    if cong:
        road(x+2.6, y-1.0, x+7.4, y-1.0, color=CONG, z=z+2, al=al)
    car(x-6.0, y-0.9, s=0.42, color=CAV_C, z=z+3, faded=faded)
    car(x-2.2, y-0.9, s=0.42, color=CAV_C, z=z+3, faded=faded)
    car(x+4.8, y-0.9, s=0.42, color=HDV_C, z=z+3, faded=faded)
    car(x+1.6, y+3.2, s=0.42, color=HDV_C, z=z+3, faded=faded)

def bar_dist(x, y, w=9, h=5, color=HDV_C, z=6, seed=1):
    rng = np.random.RandomState(seed)
    hs = rng.dirichlet(np.ones(4)) * h * 2.6
    bw = w/5.2
    for i, hh in enumerate(hs):
        ax.add_patch(Rectangle((x+i*(bw+0.7), y), bw, hh, fc=color, ec=INK, lw=0.9, zorder=z))
    ax.plot([x-0.5, x+w], [y, y], color=INK, lw=1.3, zorder=z)

def calendar(x, y, w=6, h=6, z=6):
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                 boxstyle="round,pad=0.1,rounding_size=0.7",
                 fc="#FFFFFF", ec=INK, lw=1.5, zorder=z))
    ax.add_patch(Rectangle((x-w/2, y+h/2-1.7), w, 1.7, fc=HDV_C, ec=INK, lw=1.2, zorder=z+1))
    for i in range(2):
        for j in range(3):
            ax.add_patch(Circle((x-w/2+1.3+j*1.7, y-0.6-i*1.6), 0.32, fc=ROAD, zorder=z+2))

def flag(x, y, s=1.0, z=7):
    ax.plot([x, x], [y, y+3.4*s], color=CONG, lw=1.5, zorder=z)
    ax.add_patch(plt.Polygon([(x, y+3.4*s), (x, y+1.8*s), (x+2.6*s, y+2.6*s)],
                 fc=CONG, ec=INK, lw=0.8, zorder=z))

# =====================================================================
# ZONE L — environment & data (x 8..39)
# =====================================================================
sticker_bg(8, 84, 31, 22, z=4)
city_map(23.5, 95, w=26, h=13, z=5)
text(11, 103.2, "SUMO Simulator", size=LABEL, bold=True, ha="left")
text(36.8, 99.3, r"Traffic Field $X_t$", size=MICRO+1, ha="right", z=9)
ax.add_patch(Circle((11.5, 86.3), 0.8, fc=CAV_C, ec=INK, lw=1.0, zorder=8))
text(13.1, 86.3, "CAV", size=MICRO+0.5, ha="left")
ax.add_patch(Circle((19.9, 86.3), 0.8, fc=HDV_C, ec=INK, lw=1.0, zorder=8))
text(21.5, 86.3, "HDV", size=MICRO+0.5, ha="left")

# episode ticker
rbox(11, 77, 21, 4.6, "#FFFFFF", AR_REAL, dashed=True, lw=1.6, z=5, rs=1.2)
ax.add_patch(Arc((15.2, 79.3), 3.0, 3.0, theta1=40, theta2=320,
                 color=AR_REAL, lw=1.6, zorder=7))
text(18.2, 79.3, "episode $e$", size=MICRO+1, ha="left", color=AR_REAL)
arrow((18, 83.7), (18, 82.0), color=AR_REAL, lw=2.2, ms=12)

# replay buffer with transition cards
sticker_bg(8, 46, 31, 20, z=4)
text(23.5, 63.2, "Replay Buffer", size=LABEL, bold=True)
for k in range(3):
    cx = 10.5 + k*9.0
    rbox(cx, 52.5, 8, 8.5, "#FFFFFF", "#B0A58F", lw=1.3, z=5, rs=0.8)
    for j, cc in enumerate(("#8FB8DE", "#F4B942", "#A8D5BA")):
        ax.add_patch(Rectangle((cx+0.7+j*2.5, 55.6), 2.1, 3.6, fc=cc, ec=INK,
                     lw=0.7, zorder=7))
    text(cx+4, 53.8, [r"$X_t$", r"$a_t$", r"$X_{t+1}$"][k], size=MICRO-1.5, z=8)
arrow((21, 76.6), (21, 66.4), color=AR_REAL, lw=2.2, ms=12)
text(23.5, 71.5, "store transitions", size=MICRO, ha="left", color=AR_REAL)
text(23.5, 49.6, "limited real transitions", size=MICRO, color=SUB)
text(23.5, 43.8, r"warm-up: $\epsilon$-greedy episodes", size=MICRO, color=SUB)

# =====================================================================
# ZONE C — Flow-Matching Dynamics Model (x 49..164, y 31..112)
# =====================================================================
rbox(49, 31, 115, 81, WM_BG, WM_BD, lw=3.0)
text(106.5, 108.7, "Flow-Matching Dynamics Model", size=MODBIG, bold=True, color="#3d7a50")

# ---------- C1: Traffic Encoder & Decoder (53..106, 74..104) ----------
rbox(53, 74, 53, 30, "#FFFFFF", WM_BD, lw=1.8, z=3, rs=1.4)
text(79.5, 101.3, "Traffic Encoder & Decoder", size=SUBT, bold=True, color="#3d7a50")
# C1a input graph
mini_graph(56.5, 90, s=0.6, bars=True, z=6)
text(58.5, 86.6, r"$X_t,\ G$", size=MICRO+1)
arrow((61.5, 90), (63.4, 90), lw=2.0, ms=11)
# C1b GCN stack (3 chips + residual arc + LN tag)
for i in range(3):
    rbox(63.8+i*1.1, 87.6+i*0.8, 5.2, 4.6, WM_BG, WM_BD, lw=1.4, z=5+i, rs=0.8)
arrow((66.5, 94.6), (71.5, 94.6), color=WM_BD, lw=1.5, rad=-0.5, ms=9)
text(69, 96.0, "residual", size=MICRO-1.5, color="#3d7a50")
rbox(71.8, 87.4, 3.4, 2.6, "#FFFFFF", WM_BD, lw=1.2, z=8, rs=0.7)
text(73.5, 88.7, "LN", size=MICRO-1.5, color="#3d7a50")
text(69, 85.6, "GCN stack", size=MICRO, color=SUB)
arrow((75.6, 90), (77.5, 90), lw=2.0, ms=11)
# C1c latent
latent_card(77.5, 87, w=6.3, h=6.0, z=6, seed=1)
text(80.6, 94.0, r"$Z_t$", size=MICRO+1)
arrow((84.2, 90), (86.0, 90), lw=2.0, ms=11)
# C1d decoder + reconstructed field
rbox(86, 87.6, 8.5, 4.8, "#E3ECFF", "#3D5BA1", lw=1.5, z=5, rs=0.9)
text(90.2, 90.0, "Decoder", size=MICRO, color="#2c4470")
arrow((94.8, 90), (96.4, 90), lw=2.0, ms=11)
mini_graph(96.8, 90, s=0.55, bars=True, seed=3, z=6)
text(99.5, 94.0, r"$[\hat{c},\ \hat{v}]$", size=MICRO, ha="center")
# C1e reconstruction double-arrow along bottom
seg((58.5, 87.6), (58.5, 84.0), color="#3D5BA1", lw=1.6, z=5)
seg((58.5, 84.0), (99.0, 84.0), color="#3D5BA1", lw=1.6, z=5)
arrow((99.0, 84.0), (99.0, 87.6), color="#3D5BA1", lw=1.6, ms=10, z=5)
arrow((58.5, 84.0), (58.5, 87.6), color="#3D5BA1", lw=1.6, ms=10, z=5)
loss_tag(78, 84.0, r"$\mathcal{L}_{\mathrm{dec}}$", "#3D5BA1")
# micro lines
text(79.5, 80.6, r"$z_{t,u}$: segment $u$ + neighborhood", size=MICRO, color=SUB)
text(79.5, 78.6, "reconstruction + readouts", size=MICRO, color=SUB)
text(79.5, 76.6, "for reward / value targets", size=MICRO, color=SUB)

# ---------- C2: Action Encoder (109..161, 74..104) ----------
rbox(109, 74, 52, 30, ACT_BG, ACT_BD, lw=1.8, z=3, rs=1.4)
text(135, 101.3, "Action Encoder", size=SUBT, bold=True, color="#8a7320")
# C2a two CAV route-fan rows
for r, yy in enumerate((92.5, 86.5)):
    car(113, yy, s=0.36, color=CAV_C, z=6)
    for i in range(4):
        route_card(116.3+i*2.4, yy-2.0, w=2.2, h=3.4,
                   selected=(i == 1), grayed=(i != 1), z=6)
# C2b look-ahead window polyline
px = [127.5, 130.5, 133.5, 137, 140.5]
py = [94.5, 92.8, 94.2, 92.5, 93.8]
ax.plot(px, py, color="#8a7320", lw=2.2, zorder=6, marker="o", ms=4,
        markerfacecolor="#FFFFFF", markeredgecolor=INK)
seg((127.5, 91.3), (133.5, 91.3), color=CONG, lw=1.5, z=6)
seg((127.5, 90.9), (127.5, 91.7), color=CONG, lw=1.5, z=6)
seg((133.5, 90.9), (133.5, 91.7), color=CONG, lw=1.5, z=6)
text(130.5, 89.6, r"look-ahead $\Delta$", size=MICRO-0.5, color=CONG)
# C2c projection funnel
for yy in (92.5, 86.5):
    arrow((126.5, yy), (146.5, 89.5), color=ACT_BD, lw=1.6, rad=-0.1, ms=10)
text(136.5, 86.9, r"$\Pi_G$", size=MATH-2, color="#8a7320")
# C2d pressure field
mini_graph(147.5, 90, s=0.6, hl_edges=(1, 2, 4), z=6)
text(151, 86.2, r"$\Psi_t^{\mathrm{CAV}}$", size=MICRO+1, bold=True)
# C2e equation + C2f notes
text(135, 81.6, r"$\Psi_t^{\mathrm{CAV}}(u) = \frac{1}{|\mathcal{I}_t|}"
                r"\sum_i \xi_{i,t}^{a_i,\Delta}(u)$", size=MATH-2.5)
text(135, 78.8, "same one-hot route:", size=MICRO, color=SUB)
text(135, 76.9, "executed · stored · conditioned", size=MICRO, color=SUB)

# ---------- C3: State-to-State Flow Matching (53..161, 36..70) ----------
rbox(53, 36, 108, 34, "#FFFFFF", WM_BD, lw=1.8, z=3, rs=1.4)
text(110, 67.3, "State-to-State Flow Matching", size=SUBT, bold=True, color="#3d7a50")
text(76, 65.8, r"$x_\tau = (1-\tau)\,Z_t + \tau\,Z_{t+1}$", size=MATH-2)
text(76, 63.5, r"target $\nu^\star = Z_{t+1} - Z_t$", size=MATH-2)
# C3a source
latent_card(55.5, 52, w=6.5, h=6.0, z=6, seed=2)
text(58.7, 50.3, r"$Z_t$", size=MICRO+1)
# C3b interpolation path with 3 intermediate mini cards
fx = np.linspace(63, 93, 80)
fy = 55 + 3.2*np.sin((fx-63)/30*np.pi)
ax.plot(fx, fy, color=AR_WM, lw=2.6, zorder=6)
for f in (0.25, 0.5, 0.75):
    xx = 63 + 30*f
    yy = 55 + 3.2*np.sin(f*np.pi)
    latent_card(xx-1.9, yy-0.2, w=3.8, h=3.4, z=7, seed=int(f*20))
for f in (0, 0.25, 0.5, 0.75, 1.0):
    xx = 63 + 30*f
    ax.plot([xx, xx], [52.2, 53.2], color=INK, lw=1.2, zorder=7)
text(63, 50.6, r"$\tau{=}0$", size=MICRO-1)
text(93, 50.6, r"$\tau{=}1$", size=MICRO-1)
text(78, 49.0, "k explicit Euler steps", size=MICRO, color=SUB)
arrow((fx[-2], fy[-2]), (94.8, 55), color=AR_WM, lw=2.6, ms=12)
# C3 target + reuse
latent_card(95.5, 52, w=6.5, h=6.0, z=6, seed=7)
text(98.7, 50.3, r"$\hat{Z}_{t+1}$", size=MICRO+1)
arrow((102.3, 55), (105.2, 55), color=AR_WM, lw=2.0, ms=10)
latent_card(105.5, 52.6, w=5.4, h=5.0, z=6, seed=9, faded=True)
text(108.2, 50.4, r"$\hat{Z}_{t+2}$", size=MICRO, color=SUB)
text(108.2, 49.0, "(next source)", size=MICRO-1, color=SUB)
# C3c velocity-field network (block-causal transformer)
for i in range(4):
    rbox(112.5, 53.0+i*2.2, 3.6, 1.8, "#8FB8DE", INK, lw=1.0, z=6, rs=0.5)
    arrow((116.3, 53.9+i*2.2), (118.4, 53.9+i*2.2), lw=1.2, ms=7)
text(114.3, 63.6, "segment tokens", size=MICRO-1.5, color=SUB)
rbox(118.5, 52.5, 13, 10.5, WM_BG, WM_BD, lw=1.8, z=5, rs=1.0)
text(125, 61.0, "block-causal", size=MICRO, bold=True, color="#3d7a50")
text(125, 59.2, "Transformer", size=MICRO, bold=True, color="#3d7a50")
# causal mask triangle
for i in range(3):
    for j in range(i+1):
        ax.add_patch(Rectangle((120+j*1.5, 53.6+i*1.5), 1.3, 1.3,
                     fc="#5A9E6F", ec=INK, lw=0.4, zorder=7))
text(122.2, 52.9-0.6+0.2, "", size=1)
# tau embedding chip
rbox(121.5, 64.0, 7, 2.8, "#EFEFEF", ROAD, lw=1.3, z=6, rs=0.8)
text(125, 65.4, r"$\tau$ emb.", size=MICRO-1, color=SUB)
arrow((125, 63.8), (125, 63.2), lw=1.4, ms=8)
# linear head + output
ax.add_patch(plt.Polygon([(133.5, 55.5), (133.5, 60.5), (137, 58.0)],
             fc="#FFFFFF", ec=INK, lw=1.5, zorder=6))
arrow((137.2, 58), (139.6, 58), lw=1.6, ms=9)
text(141.5, 58, r"$\hat\nu_{t,\tau}$", size=MICRO+1, ha="left")
# C3d condition chips + bus into transformer
chips = [(64, r"$\Psi_t^{\mathrm{CAV}}$", ACT_BG, ACT_BD),
         (81, r"$D_t$", "#EDF6FF", "#6FA8DC"),
         (98, r"$\hat{H}_t^{\mathrm{HDV}}$", HDV_BG, HDV_BD),
         (115, r"$c_t$", "#EFEFEF", ROAD)]
for cx, lab, fc, ec in chips:
    rbox(cx-7.5, 40.2, 15, 4.4, fc, ec, lw=1.7, z=5, rs=1.3)
    text(cx, 42.4, lab, size=ANNOT)
    seg((cx, 44.8), (cx, 47.3), color=AR_WM, lw=1.7, z=5)
seg((64, 47.3), (125, 47.3), color=AR_WM, lw=1.7, z=5)
arrow((125, 47.3), (125, 52.1), color=AR_WM, lw=1.8, ms=10)
text(124.5, 42.4, r"$[t/T,\ \mathrm{CAV}\%,\ \mathrm{HDV}\%]$",
     size=MICRO, color=SUB, ha="left")
text(142.5, 42.4, r"condition $\mathcal{C}_t$", size=MICRO+1, color=SUB, ha="left")
# C3g loss + weights + master eq
loss_tag(61.5, 37.8, r"$\mathcal{L}_{\mathrm{FM}}$", WM_BD)
text(68.5, 37.8, r"$w_{t,u}$: congested upweighted",
     size=MICRO, color=SUB, ha="left")
text(133, 37.8, r"$\hat{Z}_{t+1} = F_\phi(Z_t;\ \Psi_t^{\mathrm{CAV}},\ D_t,\ "
                r"\hat{H}_t^{\mathrm{HDV}},\ c_t)$", size=MATH-3)

# ---------- objective strip ----------
text(106.5, 32.9, r"$\mathcal{L}_{\mathrm{WM}} = \mathcal{L}_{\mathrm{FM}}"
                  r" + \lambda_{\mathrm{dec}}\mathcal{L}_{\mathrm{dec}}"
                  r" + \lambda_{\mathrm{resp}}\mathcal{L}_{\mathrm{resp}}$",
     size=MATH-1, color="#3d7a50")

# =====================================================================
# ZONE C-bottom — HDV Response Module (49..164, 14..28)
# =====================================================================
rbox(49, 14, 115, 14, HDV_BG, HDV_BD, lw=2.8)
text(106.5, 25.6, "HDV Response Module", size=MOD, bold=True, color="#a05c2e")
# C4a previous-episode summary
mini_graph(53.5, 19, s=0.55, hl_edges=(1, 4), z=6)
text(56.5, 15.8, r"$\bar{\Psi}_{e-1}^{\mathrm{CAV}}$", size=MICRO, color=SUB)
bar_dist(62, 16.2, w=6.5, h=4.2, seed=2)
text(65.5, 15.0, r"$H_{e-1}^{\mathrm{HDV}}$", size=MICRO, color=SUB)
arrow((70, 19), (73, 19), color=AR_HDV, dotted=True, lw=2.4, ms=10)
# C4b predictor
rbox(73, 16.7, 13, 4.8, "#FFFFFF", HDV_BD, lw=1.6, z=5, rs=1.0)
text(79.5, 19.1, "MLP + softmax", size=MICRO+1, color="#a05c2e")
arrow((86.5, 19), (89.5, 19), color=AR_HDV, dotted=True, lw=2.4, ms=10)
# C4c next-episode response
bar_dist(90, 16.2, w=6.5, h=4.2, seed=5)
text(93.5, 15.0, r"$\hat{H}_e^{\mathrm{HDV}}$", size=MICRO+1, color=SUB)
# C4d supervision + CE
arrow((97.3, 19.8), (100.3, 19.8), color=AR_HDV, lw=1.5, ms=8, style="<|-|>")
bar_dist(101, 16.2, w=6.5, h=4.2, color="#B0844A", seed=8)
text(104.5, 15.0, r"observed $H^\star$", size=MICRO, color=SUB)
loss_tag(98.8, 22.7, r"$\mathcal{L}_{\mathrm{resp}}$", HDV_BD)
# eq + notes
text(126, 20.6, r"$(\bar{\Psi}_{e-1}^{\mathrm{CAV}},\ H_{e-1}^{\mathrm{HDV}})"
                r"\rightarrow \hat{H}_e^{\mathrm{HDV}}$", size=MATH-2.5)
text(126, 18.0, "soft-label CE · separate optimizer", size=MICRO, color=SUB)
text(126, 16.1, "fixed within imagined episode", size=MICRO, color=SUB)
# dotted cross-episode arrow + calendar
arrow((59, 22.3), (93, 22.3), color=AR_HDV, dotted=True, lw=2.2, rad=-0.25, ms=10)
text(76, 23.9, "episode-level adaptation", size=MICRO, color=SUB)
calendar(156.5, 19.6, w=5.5, h=5.8, z=6)
# K3: HDV module -> condition chip
arrow((98, 28.2), (98, 39.8), color=AR_HDV, lw=2.6)

# =====================================================================
# ZONE R — Actor-Critic Learner (174..255, 14..112)
# =====================================================================
rbox(174, 14, 81, 98, P2_BG, P2_BD, lw=3.0)
text(214.5, 108.7, "Actor-Critic Learner", size=MODBIG, bold=True, color="#6a4fc4")

# ---------- R1: Vehicle-Level Imagination (178..251, 76..104) ----------
rbox(178, 76, 73, 28, "#FFFFFF", P2_BD, lw=1.8, z=3, rs=1.4)
text(181, 101.2, "Vehicle-Level Imagination", size=SUBT, bold=True, color="#6a4fc4", ha="left")
text(248, 101.2, r"$L_{\mathrm{im}}$ steps", size=MICRO+1, color=SUB, ha="right")
# R1a replay-state chip
rbox(180, 92, 7, 5.5, "#FFFFFF", AR_REAL, lw=1.5, z=5, rs=0.9)
text(183.5, 96.0, "replay", size=MICRO-1)
text(183.5, 94.3, "state", size=MICRO-1)
text(183.5, 90.6, r"$(e, t_{start})$", size=MICRO-1.5, color=SUB)
arrow((187.3, 94.8), (189.8, 94.8), color=AR_REAL, lw=1.8, ms=10)
# R1b latent rollout chain
xs_snap = (190, 202, 214)
labs = (r"$Z_t$", r"$\hat{Z}_{t+1}$", r"$\hat{Z}_{t+2}$")
for i, (xx, lab) in enumerate(zip(xs_snap, labs)):
    latent_card(xx, 92, w=6.5, h=6.0, z=6, seed=10+i)
    text(xx+3.2, 90.4, lab, size=MICRO)
    if i < 2:
        arrow((xx+6.8, 95), (xx+11.6, 95), color=AR_IM, lw=2.2, ms=11)
text(224, 95, "…", size=16, color="#6a4fc4")
# R1f faded crossed SUMO
city_map(241.5, 94.5, w=9, h=6.5, z=5, faded=True, cong=False)
ax.plot([237.4, 245.6], [91.6, 97.4], color=SUB, lw=1.3, zorder=9)
text(241.5, 89.9, "no SUMO", size=MICRO, color=SUB)
text(241.5, 88.5, "queries", size=MICRO, color=SUB)
# R1c decoder readout pair
latent_card(190, 82.5, w=5.6, h=5.2, z=6, seed=21)
text(188.6, 85.1, r"$\hat{v}$", size=MICRO, ha="right")
latent_card(198, 82.5, w=5.6, h=5.2, z=6, seed=33)
text(196.6, 85.1, r"$\hat{n}$", size=MICRO, ha="right")
arrow((205, 91.6), (205, 88.4), color=AR_WM, lw=1.8, ms=9)
text(193.5, 80.9, r"$\hat\tau(u) = \ell(u)/\hat v_{t,u}$", size=MICRO, color=SUB)
text(193.5, 79.4, "decoder readouts", size=MICRO-1, color=SUB)
# R1d wrapper timeline table (shifted left, clear of the crossed SUMO)
rows = [(87.6, "v1", 2, None), (84.2, "v2", 1, "depart"), (80.8, "v3", 3, "arrive")]
for ry, vid, prog, ev in rows:
    text(207.3, ry+0.9, vid, size=MICRO-1, color=SUB, ha="left")
    for b in range(4):
        bx = 211 + b*4.3
        done = b < prog
        ax.add_patch(Rectangle((bx, ry), 3.8, 1.9,
                     fc="#8FB8DE" if done else "#FFFFFF", ec=INK, lw=0.9,
                     zorder=6, linestyle="solid" if (ev != "depart" or b > 0)
                     else (0, (2, 2))))
    cx = 211 + prog*4.3 + 1.9
    ax.add_patch(plt.Polygon([(cx-0.9, ry+2.6), (cx+0.9, ry+2.6), (cx, ry+1.9)],
                 fc=CONG, ec=INK, lw=0.6, zorder=7))
    if ev == "depart":
        text(212.9, 83.0, "depart", size=MICRO-1.5, color=AR_IM, ha="left")
    if ev == "arrive":
        flag(229.6, ry+1.9, s=0.8)
text(211, 79.3, "identity-preserving vehicle wrapper", size=MICRO+0.5, bold=True, ha="left")
text(206.8, 77.8, "positions · route progress · departures · arrivals",
     size=MICRO-1.5, color=SUB, ha="left")
# R1e readout -> wrapper
arrow((208, 83.5), (210.6, 83.5), color=AR_WM, lw=1.8, ms=9)

# ---------- R2: Parameter-Shared CAV Actor (178..251, 52..74) ----------
rbox(178, 52, 73, 22, "#FFFFFF", P2_BD, lw=1.8, z=3, rs=1.4)
text(214.5, 71.3, "Parameter-Shared CAV Actor", size=SUBT, bold=True, color="#6a4fc4")
# R2a route feature construction
for b in range(4):
    ax.add_patch(Rectangle((181+b*3.8, 63.5), 3.3, 2.6,
                 fc=("#8FB8DE", "#A8D5BA", "#F4B942", "#E79A3B")[b],
                 ec=INK, lw=0.8, zorder=6))
text(187.6, 67.2, "route segments", size=MICRO-1, color=SUB)
for b in range(4):
    arrow((182.6+b*3.8, 63.2), (199.5, 61.6), color=SUB, lw=1.2, rad=-0.08, ms=7)
text(195.5, 59.6, "mean-pool", size=MICRO-1, color=SUB)
rbox(200.5, 60.3, 6.5, 3.2, "#FFFFFF", P2_BD, lw=1.4, z=6, rs=0.8)
text(203.7, 61.9, r"$\varphi_{i,t,k}$", size=MICRO-0.5)
# R2b context chip
rbox(181, 54.5, 21, 3.4, "#EFEFEF", ROAD, lw=1.4, z=6, rs=0.9)
text(191.5, 56.2, r"$g_t = [\bar z_t,\ t/T,\ \mathrm{CAV}\%]$", size=MICRO-0.5)
# R2c scorer (one chip, multiple arrows in)
rbox(210, 58.5, 7, 6.5, P2_BG, P2_BD, lw=1.6, z=6, rs=0.9)
text(213.5, 61.7, r"$f_\theta$", size=MATH-2)
arrow((207.2, 61.9), (209.7, 61.9), lw=1.6, ms=9)
arrow((202, 58.0), (209.5, 59.5), lw=1.6, ms=9, rad=-0.2)
# R2d masked softmax bar
text(233, 67.2, "masked softmax", size=MICRO, color=SUB)
probs = [0.9, 2.6, 0.0, 1.6]
for i, pb in enumerate(probs):
    bx = 222 + i*6.0
    if i == 2:
        ax.add_patch(Rectangle((bx, 57.5), 4.2, 3.2, fc="#F2F2F2", ec=INK,
                     lw=1.0, zorder=6))
        ax.plot([bx+0.6, bx+3.6], [58.1, 60.1], color=CONG, lw=1.6, zorder=7)
        ax.plot([bx+0.6, bx+3.6], [60.1, 58.1], color=CONG, lw=1.6, zorder=7)
        text(bx+2.1, 55.9, r"$m{=}0$", size=MICRO-1.5, color=CONG)
    else:
        sel = (i == 1)
        ax.add_patch(Rectangle((bx, 57.5), 4.2, pb*1.6+1.2,
                     fc="#A8D5BA" if sel else "#8FB8DE",
                     ec="#5A9E6F" if sel else INK, lw=2.2 if sel else 1.0,
                     zorder=6))
        if sel:
            text(bx+2.1, 55.9, "sampled", size=MICRO-1.5, color="#3d7a50")
text(233, 53.6, r"route action $a_{i,t}$", size=MICRO, color=SUB)
arrow((233, 57.2), (233, 55.2), color=AR_IM, lw=1.6, ms=9)
# R2e sharing note
text(196.5, 52.9, "scorer shared across CAVs & route slots", size=MICRO, color=SUB)

# ---------- R3: critics ----------
# per-vehicle critic (178..213, 26..48)
rbox(178, 26, 35, 22, "#FFFFFF", P2_BD, lw=1.8, z=3, rs=1.4)
text(195.5, 45.6, "Per-Vehicle Critic", size=SUBT-1, bold=True, color="#6a4fc4")
for i in range(3):
    rbox(180.5, 39.0+i*1.9, 4.6, 1.6, "#FFFFFF", INK, lw=0.9, z=6, rs=0.4)
    text(182.8, 39.8+i*1.9, f"$o_{i+1}$", size=MICRO-2)
arrow((185.4, 41.7), (187.6, 41.7), lw=1.4, ms=8)
rbox(187.6, 40.2, 5.5, 3.2, P2_BG, P2_BD, lw=1.3, z=6, rs=0.7)
text(190.3, 41.8, "MLP", size=MICRO-1)
# attention matrix
for i in range(3):
    for j in range(3):
        heat = 0.25 + 0.6*np.random.RandomState(i*3+j+5).rand()
        ax.add_patch(Rectangle((195+j*2.1, 38.6+i*2.05), 1.9, 1.9,
                     fc=plt.cm.Purples(heat), ec=INK, lw=0.5, zorder=6))
text(198.2, 37.4, "self-attention", size=MICRO-1.5, color=SUB)
# value cards
for i in range(3):
    rbox(203.5, 39.0+i*1.9, 4.6, 1.6, "#E8E3F7", P2_BD, lw=0.9, z=6, rs=0.4)
    text(205.8, 39.8+i*1.9, f"$v_{i+1}$", size=MICRO-2)
text(195.5, 35.9, r"$r_i = -\min(\Delta t, \hat T^{\mathrm{rem}})/\kappa_r$",
     size=MICRO, color=SUB)
# lambda-return chain
for i in range(3):
    ax.add_patch(Circle((183.5+i*6, 31.5), 1.1, fc="#B39DDB", ec=INK, lw=0.9, zorder=6))
    text(183.5+i*6, 31.5, f"$v_{i+1}$", size=MICRO-2.5, z=7)
arrow((184.8, 31.9), (188.3, 32.4), color=AR_IM, lw=1.4, rad=-0.35, ms=8)
arrow((190.8, 32.4), (194.3, 31.9), color=AR_IM, lw=1.4, rad=-0.35, ms=8)
flag(197.5, 30.4, s=0.7)
text(195.5, 28.2, r"$\lambda$-return by vehicle identity", size=MICRO, color=SUB)

# global critic (216..251, 26..48)
rbox(216, 26, 35, 22, "#FFFFFF", P2_BD, lw=1.8, z=3, rs=1.4)
text(233.5, 45.6, "Global Critic", size=SUBT-1, bold=True, color="#6a4fc4")
rbox(219, 41.3, 6.5, 3.0, "#FFFFFF", INK, lw=1.0, z=6, rs=0.7)
text(222.2, 42.8, r"$\bar z_t$", size=MICRO)
rbox(219, 37.8, 6.5, 3.0, "#EFEFEF", ROAD, lw=1.0, z=6, rs=0.7)
text(222.2, 39.3, r"$c_t$", size=MICRO)
arrow((225.7, 42.8), (228.2, 41.5), lw=1.4, ms=8)
arrow((225.7, 39.3), (228.2, 40.2), lw=1.4, ms=8)
rbox(228.4, 39.2, 8.5, 4.2, "#E8E3F7", P2_BD, lw=1.4, z=6, rs=0.8)
text(232.6, 41.3, r"$v^{\mathrm{global}}_t$", size=MICRO)
text(233.5, 35.9, r"$r^g = -\kappa_g N_{\mathrm{active}}\Delta t / N_{\mathrm{veh}}$",
     size=MICRO, color=SUB)
text(233.5, 34.1, r"imagined: $N_{\mathrm{active}} = \sum_u \hat n_{t,u}$",
     size=MICRO, color=SUB)
text(233.5, 32.3, r"$\sum_t r^g = -\kappa_g \times$ mean travel time",
     size=MICRO, color=SUB)
text(233.5, 30.5, r"$\Psi$-free baseline", size=MICRO, color=SUB)
text(233.5, 28.7, "(action-independent)", size=MICRO, color=SUB)

# ---------- R4: advantage & update (178..251, 16..22) ----------
rbox(196, 16.5, 36, 5.0, "#FFFFFF", AR_UPD, lw=1.8, z=5, rs=1.1)
text(214, 19.0, r"$A^{\mathrm{veh}}_{i,t} + \alpha_g\, A^{\mathrm{global}}_t$",
     size=MATH-1)
text(234, 19.0, "PPO clip", size=MICRO, color=SUB, ha="left")
text(234, 17.4, "+ entropy", size=MICRO, color=SUB, ha="left")
arrow((198, 25.7), (206, 21.8), color=AR_UPD, lw=1.8, ms=10)
arrow((231, 25.7), (223, 21.8), color=AR_UPD, lw=1.8, ms=10)
arrow((214, 16.2), (214, 7.8), color=AR_UPD, dashed=True, lw=2.4)
text(216, 11.2, "actor update", size=MICRO+1, ha="left", color=AR_UPD)

# =====================================================================
# cross-zone connectors
# =====================================================================
# K1: replay -> Zone C (real transitions)
seg((39.3, 56), (44, 56), color=AR_REAL, lw=3.0)
seg((44, 56), (44, 90), color=AR_REAL, lw=3.0)
arrow((44, 90), (54, 90), color=AR_REAL, lw=3.0)
text(41.5, 73, r"real transitions", size=MICRO+1, color=AR_REAL, rot=90, ha="center")

# K2: Zone C -> R1 (learned transition + readouts)
seg((100, 73.7), (100, 72), color=AR_WM, lw=2.6)
seg((100, 72), (164, 72), color=AR_WM, lw=2.6)
seg((164, 72), (169, 72), color=AR_WM, lw=2.6)
seg((169, 72), (169, 88), color=AR_WM, lw=2.6)
arrow((169, 88), (177.6, 88), color=AR_WM, lw=2.6)
text(132, 73.4, "learned transition + readouts", size=MICRO, color=AR_WM)

# K5: actor update -> bottom return -> next collection episode
seg((5.5, 7.5), (214, 7.5), color=AR_UPD, dashed=True, lw=2.4)
arrow((5.5, 7.5), (5.5, 94), color=AR_UPD, dashed=True, lw=2.4)
arrow((5.5, 94), (7.6, 94), color=AR_UPD, dashed=True, lw=2.4)
text(120, 5.4, "Updated policy → execute sampled routes in the next collection episode",
     size=LABEL-1, color=AR_UPD)

plt.subplots_adjust(left=0.003, right=0.997, top=0.997, bottom=0.003)
out = "figure/main_figure_v7.png"
plt.savefig(out, facecolor=BG)
print("saved", out)
