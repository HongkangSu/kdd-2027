"""UrbanDreamer main framework figure — v4.

Content reorganized to mirror the Method section:
  center : Flow-Matching Dynamics Model
             - Traffic Encoder & Decoder
             - Action Encoder (planned CAV pressure)
             - State-to-State Flow Matching (conditioned)
  below  : HDV Response Module (episode-level)
  right  : Actor-Critic Learner
             - Vehicle-Level Imagination
             - Parameter-Shared CAV Actor
             - Per-Vehicle Critic / Global Critic
  left   : SUMO environment + replay buffer (data context)
Straight lines (no sketch wobble).
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

fig, ax = plt.subplots(figsize=(24, 10.5), dpi=100)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 240); ax.set_ylim(0, 105)
ax.axis("off")

MODBIG, MOD, SUBT, LABEL, ANNOT, MATH = 18, 14, 11, 10, 8.5, 11

def text(x, y, s, size=LABEL, bold=False, color=INK, ha="center", va="center",
         z=8, rot=0):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, zorder=z,
            fontweight="bold" if bold else "normal", rotation=rot,
            linespacing=1.3)

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
          z=6, ms=14):
    ls = (0, (1.2, 2.2)) if dotted else ((0, (5, 3)) if dashed else "solid")
    a = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=ms,
                        color=color, lw=lw, zorder=z, linestyle=ls,
                        connectionstyle=f"arc3,rad={rad}", shrinkA=1, shrinkB=1)
    ax.add_patch(a)
    return a

def seg(p1, p2, color=AR_WM, dashed=False, lw=2.4, z=6):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, lw=lw, zorder=z,
            linestyle=(0, (5, 3)) if dashed else "solid")

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

def route_card(x, y, w=3.4, h=4.4, selected=False, z=6):
    fc = "#E8F5E9" if selected else "#FFFFFF"
    ec = "#5A9E6F" if selected else "#9DA9B0"
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.7",
                 fc=fc, ec=ec, lw=2.2 if selected else 1.4, zorder=z))
    ax.plot([x+0.8, x+w*0.45, x+w-0.8], [y+0.9, y+h-1.6, y+h-0.9],
            color=ec, lw=1.6, zorder=z+1)
    ax.add_patch(Circle((x+0.8, y+0.9), 0.35, fc=INK, zorder=z+2))
    ax.add_patch(Circle((x+w-0.8, y+h-0.9), 0.35, fc=CONG if selected else INK, zorder=z+2))

def mini_graph(x, y, s=1.0, hl_edges=(), z=6, messages=False):
    pts = np.array([(0,0),(2.2,1.8),(4.6,0.6),(1.2,-1.9),(3.8,-1.6),(6.0,2.0)],
                   float) * s + (x, y)
    edges = [(0,1),(1,2),(0,3),(3,4),(2,4),(1,3),(2,5),(4,5)]
    for i, (a, b) in enumerate(edges):
        c = CAV_C if i in hl_edges else ROAD
        ax.plot([pts[a][0], pts[b][0]], [pts[a][1], pts[b][1]],
                color=c, lw=2.6 if i in hl_edges else 1.8, zorder=z)
    for px, py in pts:
        ax.add_patch(Circle((px, py), 0.75*s, fc="#FFFFFF", ec=INK, lw=1.3, zorder=z+2))
    if messages:
        for (a, b) in ((0,1),(3,1),(4,2)):
            mx, my = (pts[a]+pts[b])/2
            ax.add_patch(Circle((mx, my), 0.42*s, fc=WM_BD, ec="none", zorder=z+3))

def latent_card(x, y, w=6.5, h=6.0, z=6, seed=0):
    sticker_bg(x, y, w, h, z=z, rs=1.0)
    rng = np.random.RandomState(seed)
    cols = ["#8FB8DE", "#A8D5BA", "#F4B942", "#E79A3B", "#B39DDB", "#90CAF9"]
    gw, gh = w/4.6, h/4.2
    for i in range(3):
        for j in range(3):
            ax.add_patch(Rectangle((x+0.85+j*(gw+0.4), y+0.85+i*(gh+0.45)), gw, gh,
                         fc=cols[rng.randint(len(cols))], ec=INK, lw=0.5, zorder=z+7))

def file_tray(x, y, w=15, h=10, z=6):
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h*0.62,
                 boxstyle="round,pad=0.1,rounding_size=1.0",
                 fc="#F2C879", ec=INK, lw=1.6, zorder=z))
    for i, c in enumerate(("#FFFFFF", "#EDF6FF", "#FFF3C4")):
        ax.add_patch(Rectangle((x-w/2+1.6+i*0.9, y-0.4+i*1.15), w-3.2, 2.6,
                     fc=c, ec=INK, lw=0.9, zorder=z+1+i))
    ax.add_patch(Circle((x, y-h/2+1.4), 0.8, fc=INK, zorder=z+4))

def calendar(x, y, w=6, h=6, z=6):
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                 boxstyle="round,pad=0.1,rounding_size=0.7",
                 fc="#FFFFFF", ec=INK, lw=1.5, zorder=z))
    ax.add_patch(Rectangle((x-w/2, y+h/2-1.7), w, 1.7, fc=HDV_C, ec=INK, lw=1.2, zorder=z+1))
    for i in range(2):
        for j in range(3):
            ax.add_patch(Circle((x-w/2+1.3+j*1.7, y-0.6-i*1.6), 0.32, fc=ROAD, zorder=z+2))

def bar_dist(x, y, w=9, h=5, color=HDV_C, z=6, seed=1):
    rng = np.random.RandomState(seed)
    hs = rng.dirichlet(np.ones(4)) * h * 2.6
    bw = w/5.2
    for i, hh in enumerate(hs):
        ax.add_patch(Rectangle((x+i*(bw+0.7), y), bw, hh, fc=color, ec=INK, lw=0.9, zorder=z))
    ax.plot([x-0.5, x+w], [y, y], color=INK, lw=1.3, zorder=z)

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

# =====================================================================
# LEFT — SUMO environment & replay (data context, no container)
# =====================================================================
sticker_bg(10, 60, 34, 20, z=4)
city_map(27, 69.6, w=29, h=13, z=5)
text(13.5, 78.2, "SUMO Simulator", size=LABEL, bold=True, ha="left")
ax.add_patch(Circle((14.2, 62.2), 0.8, fc=CAV_C, ec=INK, lw=1.0, zorder=8))
text(15.8, 62.2, "CAV", size=ANNOT, ha="left")
ax.add_patch(Circle((22.6, 62.2), 0.8, fc=HDV_C, ec=INK, lw=1.0, zorder=8))
text(24.2, 62.2, "HDV", size=ANNOT, ha="left")
text(42.3, 62.2, r"Traffic Field  $X_t$", size=ANNOT+0.5, ha="right")

sticker_bg(10, 38, 20, 14, z=4)
file_tray(20, 44.5, w=14, h=9, z=6)
text(20, 50.4, "Replay Buffer", size=LABEL, bold=True)
text(20, 39.4, r"$(X_t, a_t, X_{t+1})$", size=ANNOT+0.5)
text(20, 36.3, "limited real transitions", size=ANNOT, color=SUB)

arrow((21, 59.5), (21, 52.8), color=AR_REAL, lw=2.6)
text(23.5, 56.2, "store", size=ANNOT, ha="left", color=AR_REAL)

# =====================================================================
# CENTER — Flow-Matching Dynamics Model (x 52..148, y 30..86)
# =====================================================================
rbox(52, 30, 96, 56, WM_BG, WM_BD, lw=3.0)
text(100, 83.2, "Flow-Matching Dynamics Model", size=MODBIG, bold=True, color="#3d7a50")

# ---- sub-block 1: Traffic Encoder & Decoder (x 56..98, y 62..79) ----
rbox(56, 62, 42, 17, "#FFFFFF", WM_BD, lw=1.8, z=3, rs=1.4)
text(77, 76.6, "Traffic Encoder & Decoder", size=SUBT, bold=True, color="#3d7a50")
mini_graph(59, 70.5, s=0.55, z=6)
text(61.5, 66.6, r"$X_t,\ G$", size=ANNOT+0.5)
arrow((64.8, 70.5), (67.5, 70.5), lw=2.0, ms=10)
rbox(67.5, 67.5, 11.5, 6, WM_BG, WM_BD, lw=1.5, z=5, rs=1.0)
text(73.2, 70.5, "GCN Encoder", size=ANNOT+0.5, bold=True, color="#3d7a50")
arrow((79.5, 70.5), (82, 70.5), lw=2.0, ms=10)
latent_card(82, 67.5, w=6.5, h=6.0, z=6, seed=1)
text(91.5, 70.5, r"$Z_t$", size=ANNOT+0.5, ha="left")
arrow((85.2, 67.2), (85.2, 66.2), lw=2.0, ms=10)
rbox(79.5, 62.9, 15.5, 3.4, DEC_BG := "#E3ECFF", "#3D5BA1", lw=1.5, z=5, rs=0.9)
text(87.2, 64.6, r"Decoder:  $\hat{c},\ \hat{v}$", size=ANNOT+0.5, color="#2c4470")

# ---- sub-block 2: Action Encoder (x 102..146, y 62..79) ----
rbox(102, 62, 42, 17, ACT_BG, ACT_BD, lw=1.8, z=3, rs=1.4)
text(123, 76.6, "Action Encoder", size=SUBT, bold=True, color="#8a7320")
for k in range(3):
    yy = 67.3 + k*3.1
    car(107, yy, s=0.33, color=CAV_C, z=6)
    route_card(110.5, yy-1.6, w=2.6, h=3.3, selected=(k == 0), z=6)
    arrow((113.7, yy), (120.5, 70.4), color=ACT_BD, lw=1.6, rad=-0.12, ms=9)
text(109.5, 63.6, r"one-hot routes $a_t$", size=ANNOT-0.3, color=SUB)
mini_graph(124.5, 71.5, s=0.62, hl_edges=(1, 4), z=6)
text(131.5, 66.8, r"planned CAV pressure", size=ANNOT-0.3, color=SUB, ha="left")
text(131.5, 64.9, r"$\Psi_t^{\mathrm{CAV}} = \Pi_G(a_t, \mathcal{I}_t)$",
     size=MATH-1.5, ha="left")

# ---- sub-block 3: State-to-State Flow Matching (x 56..146, y 34..58) ----
rbox(56, 34, 88, 22, "#FFFFFF", WM_BD, lw=1.8, z=3, rs=1.4)
text(100, 53.8, "State-to-State Flow Matching", size=SUBT, bold=True, color="#3d7a50")
latent_card(59, 45, w=6.5, h=6.0, z=6, seed=2)
text(62.2, 43.3, r"$Z_t$", size=ANNOT+0.5)
fx = np.linspace(67.5, 81, 60)
fy = 48 + 2.4*np.sin((fx-67.5)/13.5*np.pi)
ax.plot(fx, fy, color=AR_WM, lw=2.6, zorder=6)
arrow((fx[-3], fy[-3]), (82.5, 48), color=AR_WM, lw=2.6, ms=12)
for f in (0.25, 0.5, 0.75):
    xx = 67.5 + 13.5*f
    yy = 48 + 2.4*np.sin(f*np.pi)
    ax.add_patch(Circle((xx, yy), 0.8, fc="#FFFFFF", ec=AR_WM, lw=1.5, zorder=7))
text(74.2, 52.2, r"velocity field $\nu_\phi$", size=ANNOT+0.5, color="#3d7a50")
text(74.2, 44.9, "Euler steps", size=ANNOT-0.3, color=SUB)
latent_card(83.5, 45, w=6.5, h=6.0, z=6, seed=7)
text(86.7, 43.3, r"$\hat{Z}_{t+1}$", size=ANNOT+0.5)
text(117.5, 49.8, r"$x_\tau = (1-\tau)\,Z_t + \tau\,Z_{t+1}$", size=MATH-0.5)
text(117.5, 46.9, r"$\hat{Z}_{t+1} = Z_t + \int_0^1 \nu_\phi\, d\tau$", size=MATH-0.5)
text(117.5, 44.0, "block-causal Transformer", size=ANNOT-0.3, color=SUB)

# condition chips
chips = [(66, r"$\Psi_t^{\mathrm{CAV}}$", ACT_BG, ACT_BD),
         (84, r"$D_t$", "#EDF6FF", "#6FA8DC"),
         (102, r"$\hat{H}_t^{\mathrm{HDV}}$", HDV_BG, HDV_BD),
         (120, r"$c_t$", "#EFEFEF", ROAD)]
for cx, lab, fc, ec in chips:
    rbox(cx-7.5, 36.8, 15, 4.2, fc, ec, lw=1.7, z=5, rs=1.3)
    text(cx, 38.9, lab, size=ANNOT+1)
    arrow((cx, 41.2), (cx, 44.4), color=AR_WM, lw=1.7, ms=9)
text(130.5, 38.9, r"condition $\mathcal{C}_t$", size=ANNOT, color=SUB, ha="left")
text(100, 31.6, r"$\hat{Z}_{t+1} = F_\phi\left(Z_t;\ \Psi_t^{\mathrm{CAV}},\ D_t,\ "
                r"\hat{H}_t^{\mathrm{HDV}},\ c_t\right)$", size=MATH-0.5)

# =====================================================================
# BELOW CENTER — HDV Response Module (x 52..148, y 13..27)
# =====================================================================
rbox(52, 13, 96, 14, HDV_BG, HDV_BD, lw=2.8)
text(100, 24.6, "HDV Response Module", size=MOD, bold=True, color="#a05c2e")
car(57.5, 19.3, s=0.4, color=HDV_C, z=6)
car(61.5, 17.9, s=0.4, color=HDV_C, z=6)
bar_dist(65.5, 16.2, w=7, h=4.2, seed=2)
text(69, 14.7, "previous episode", size=ANNOT-0.5, color=SUB)
arrow((73.5, 19.5), (77, 19.5), color=AR_HDV, dotted=True, lw=2.4, ms=10)
rbox(77, 17.2, 12, 4.8, "#FFFFFF", HDV_BD, lw=1.6, z=5, rs=1.0)
text(83, 19.6, "MLP + softmax", size=ANNOT+0.5, color="#a05c2e")
arrow((89.5, 19.5), (93, 19.5), color=AR_HDV, dotted=True, lw=2.4, ms=10)
bar_dist(94, 16.2, w=7, h=4.2, seed=5)
text(97.5, 14.7, r"$\hat{H}_e^{\mathrm{HDV}}$", size=ANNOT+0.5, color=SUB)
text(119, 20.6, r"$(\bar{\Psi}_{e-1}^{\mathrm{CAV}},\ H_{e-1}^{\mathrm{HDV}})"
                r"\ \rightarrow\ \hat{H}_e^{\mathrm{HDV}}$", size=MATH-1.5)
text(119, 17.6, "episode-level adaptation", size=ANNOT-0.3, color=SUB)
calendar(140, 19.8, w=5.5, h=5.8, z=6)
# HDV module -> condition chip
arrow((102, 27.2), (102, 36.4), color=AR_HDV, lw=2.6)

# =====================================================================
# RIGHT — Actor-Critic Learner (x 154..232, y 14..86)
# =====================================================================
rbox(154, 14, 78, 72, P2_BG, P2_BD, lw=3.0)
text(193, 83.2, "Actor-Critic Learner", size=MODBIG, bold=True, color="#6a4fc4")

# ---- Vehicle-Level Imagination (x 158..228, y 58..79) ----
rbox(158, 58, 70, 21, "#FFFFFF", P2_BD, lw=1.8, z=3, rs=1.4)
text(161, 76.4, "Vehicle-Level Imagination", size=SUBT, bold=True, color="#6a4fc4", ha="left")
text(226, 76.4, r"$L_{\mathrm{im}}$ steps", size=ANNOT, color=SUB, ha="right")
rbox(160.5, 68, 6, 5, "#FFFFFF", AR_REAL, lw=1.5, z=5, rs=0.9)
text(163.5, 71.6, "replay", size=ANNOT-1.5)
text(163.5, 70.0, "state", size=ANNOT-1.5)
arrow((166.8, 70.5), (169.6, 70.5), color=AR_REAL, lw=1.8, ms=9)
xs_snap = (170, 182, 194)
labs = (r"$Z_t$", r"$\hat{Z}_{t+1}$", r"$\hat{Z}_{t+2}$")
for i, (xx, lab) in enumerate(zip(xs_snap, labs)):
    latent_card(xx, 68, w=6.5, h=6.0, z=6, seed=10+i)
    text(xx+3.2, 66.6, lab, size=ANNOT)
    if i < 2:
        arrow((xx+6.8, 71), (xx+11.6, 71), color=AR_IM, lw=2.2, ms=11)
text(204, 71, "…", size=16, color="#6a4fc4")
city_map(219.5, 71, w=9, h=6.5, z=5, faded=True, cong=False)
ax.plot([215.4, 223.6], [68.1, 73.9], color=SUB, lw=1.3, zorder=9)
text(219.5, 65.9, "no SUMO", size=ANNOT-1, color=SUB)
text(219.5, 64.6, "queries", size=ANNOT-1, color=SUB)
# wrapper lane
ax.plot([162, 212], [61.8, 61.8], color=ROAD, lw=2.8, zorder=6, solid_capstyle="round")
for xx, cid in ((168, "1"), (181, "2"), (194, "3")):
    car(xx, 62.8, s=0.42, color=CAV_C, z=7)
    text(xx, 60.0, cid, size=ANNOT-1, color=SUB)
    if xx < 190:
        arrow((xx+3.2, 61.8), (xx+9.0, 61.8), color=AR_IM, lw=1.6, ms=9)
ax.plot([207, 207], [61.8, 65.2], color=CONG, lw=1.5, zorder=7)
ax.add_patch(plt.Polygon([(207, 65.2), (207, 63.5), (209.6, 64.3)],
             fc=CONG, ec=INK, lw=0.8, zorder=7))
text(172, 58.9, "vehicle wrapper:  positions · route progress · arrivals",
     size=ANNOT-0.3, color=SUB, ha="left")
arrow((185, 67.7), (185, 64.2), color=SUB, lw=1.6, ms=9)

# ---- Parameter-Shared CAV Actor (x 158..228, y 40..55) ----
rbox(158, 40, 70, 15, "#FFFFFF", P2_BD, lw=1.8, z=3, rs=1.4)
text(193, 52.6, "Parameter-Shared CAV Actor", size=SUBT, bold=True, color="#6a4fc4")
car(166, 46.3, s=0.5, color=CAV_C, z=7)
for i in range(4):
    route_card(172.5+i*3.9, 43.4, w=3.3, selected=(i == 1), z=7)
text(206.5, 47.4, "masked softmax over", size=ANNOT, color=SUB)
text(206.5, 45.6, "K candidate routes", size=ANNOT, color=SUB)
text(180.5, 41.6, r"route action $a_{i,t}$", size=ANNOT, color=SUB)
arrow((193, 57.7), (193, 55.4), color=AR_IM, lw=2.2, ms=11)

# ---- critics ----
rbox(158, 22, 34, 15, "#FFFFFF", P2_BD, lw=1.8, z=3, rs=1.4)
text(175, 34.6, "Per-Vehicle Critic", size=SUBT, bold=True, color="#6a4fc4")
for i, xx in enumerate((163.5, 170, 176.5)):
    car(xx, 29.5, s=0.36, color=CAV_C, z=7)
    text(xx+2.5, 29.5, f"$v_{i+1}$", size=ANNOT)
text(175, 25.3, "MLP + self-attention", size=ANNOT-0.3, color=SUB)
text(175, 23.5, "vehicle-specific credit", size=ANNOT-0.3, color=SUB)

rbox(194, 22, 34, 15, "#FFFFFF", P2_BD, lw=1.8, z=3, rs=1.4)
text(211, 34.6, "Global Critic", size=SUBT, bold=True, color="#6a4fc4")
mini_graph(201, 29.3, s=0.5, z=7)
text(214.5, 29.5, r"$v^{\mathrm{global}}_t$", size=ANNOT+1)
text(211, 25.3, r"input $(\bar{z}_t, c_t)$", size=ANNOT-0.3, color=SUB)
text(211, 23.5, "network-level credit", size=ANNOT-0.3, color=SUB)

arrow((175, 39.7), (175, 37.5), color=AR_IM, lw=2.0, ms=10)
arrow((211, 39.7), (211, 37.5), color=AR_IM, lw=2.0, ms=10)

# ---- advantage node ----
rbox(176, 15.5, 34, 4.8, "#FFFFFF", AR_UPD, lw=1.8, z=5, rs=1.1)
text(193, 17.9, r"$A^{\mathrm{veh}}_{i,t} + \alpha_g\, A^{\mathrm{global}}_t$",
     size=MATH-0.5)
arrow((182, 21.7), (188, 20.6), color=AR_UPD, lw=1.8, ms=9)
arrow((204, 21.7), (198, 20.6), color=AR_UPD, lw=1.8, ms=9)

# =====================================================================
# cross-module connectors
# =====================================================================
# replay -> WM (real transitions bus; one clean crossing with the dashed return)
seg((30.3, 45), (46, 45), color=AR_REAL, lw=3.0)
seg((46, 45), (46, 70), color=AR_REAL, lw=3.0)
arrow((46, 70), (57, 70), color=AR_REAL, lw=3.0)
text(44.0, 57, r"real transitions", size=ANNOT, color=AR_REAL, rot=90, ha="center")

# WM -> imagination (learned transition + decoder readouts)
seg((85, 62.6), (85, 60.5), color=AR_WM, lw=2.6)
seg((85, 60.5), (147, 60.5), color=AR_WM, lw=2.6)
seg((147, 60.5), (147, 64), color=AR_WM, lw=2.6)
arrow((147, 64), (158.5, 64), color=AR_WM, lw=2.6)
text(152.8, 67.6, "learned", size=ANNOT-1, color=AR_WM)
text(152.8, 66.3, "transition", size=ANNOT-1, color=AR_WM)

# PPO update -> bottom return -> execute in SUMO
arrow((193, 15.2), (193, 10.2), color=AR_UPD, dashed=True, lw=2.4)
seg((40, 10), (193, 10), color=AR_UPD, dashed=True, lw=2.4)
arrow((40, 10), (40, 59.3), color=AR_UPD, dashed=True, lw=2.4)
text(194.5, 12.8, "PPO Actor Update", size=ANNOT, ha="left", color=AR_UPD)
text(115, 8.0, "Updated policy → execute sampled routes in the next collection episode",
     size=LABEL, color=AR_UPD)

plt.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.005)
out = "figure/main_figure_v4.png"
plt.savefig(out, facecolor=BG)
print("saved", out)
