"""UrbanDreamer main framework figure — v2, following the detailed spec.

Canvas 2400x1050 @ dpi 100. Left Phase I container (x 3-29%), central
three-module bridge (x 33-66%), right Phase II container (x 70-97%).
Hand-sketched outlines + Office-clipart stickers. Math in STIX.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch, Arc
import numpy as np

# ---------------- palette (spec §4) ----------------
BG       = "#FFFDF8"
INK      = "#263238"
SUB      = "#59636A"
P1_BG, P1_BD = "#EDF6FF", "#6FA8DC"
P2_BG, P2_BD = "#F5F0FF", "#9B7EDE"
ACT_BG, ACT_BD = "#FFF3C4", "#D6B656"
WM_BG,  WM_BD  = "#DFF4E8", "#5A9E6F"
HDV_BG, HDV_BD = "#FCE5D5", "#D58B5A"
CAV_C, HDV_C   = "#3F7FC4", "#E79A3B"
CONG,  ROAD    = "#D7655B", "#9DA9B0"
AR_REAL, AR_WM, AR_IM, AR_HDV, AR_UPD = "#4F81BD", "#4F8F68", "#8A6FD1", "#D58B5A", "#4A4A4A"

plt.rcParams["path.sketch"] = (1.0, 12, 2)
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["mathtext.fontset"] = "stix"

fig, ax = plt.subplots(figsize=(24, 10.5), dpi=100)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 240); ax.set_ylim(0, 105)
ax.axis("off")

# ---------------- typography ----------------
PHASE, MOD, MODBIG, LABEL, ANNOT, MATH = 20, 15, 18, 10.5, 9, 12

def text(x, y, s, size=LABEL, bold=False, color=INK, ha="center", va="center",
         z=8, math=False, rot=0):
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
    """soft shadow + white cutline + thin dark outline"""
    rbox(x+0.45, y-0.5, w, h, "#00000018", "none", z=z-1, rs=rs)
    rbox(x, y, w, h, "#FFFFFF", "none", z=z, rs=rs)
    rbox(x, y, w, h, "none", INK, lw=1.4, z=z+6, rs=rs)

def arrow(p1, p2, color=AR_WM, dashed=False, dotted=False, lw=2.4, rad=0.0,
          z=6, ms=15, elbow=False):
    cs = "angle,angleA=0,angleB=90,rad=4" if elbow else f"arc3,rad={rad}"
    ls = (0, (1.2, 2.2)) if dotted else ((0, (5, 3)) if dashed else "solid")
    a = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=ms,
                        color=color, lw=lw, zorder=z, linestyle=ls,
                        connectionstyle=cs, shrinkA=1, shrinkB=1)
    ax.add_patch(a)
    return a

# ---------------- clip-art stickers ----------------
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

def route_card(x, y, w=3.6, h=4.6, selected=False, z=6):
    fc = "#E8F5E9" if selected else "#FFFFFF"
    ec = "#5A9E6F" if selected else "#9DA9B0"
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.7",
                 fc=fc, ec=ec, lw=2.2 if selected else 1.4, zorder=z))
    ax.plot([x+0.8, x+w*0.45, x+w-0.8], [y+0.9, y+h-1.6, y+h-0.9],
            color=ec, lw=1.6, zorder=z+1)
    ax.add_patch(Circle((x+0.8, y+0.9), 0.35, fc=INK, zorder=z+2))
    ax.add_patch(Circle((x+w-0.8, y+h-0.9), 0.35, fc=CONG if selected else INK, zorder=z+2))

def mini_graph(x, y, s=1.0, hl_edges=(), z=6, seed=3, messages=False):
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

def latent_card(x, y, w=7, h=6.5, z=6, seed=0):
    sticker_bg(x, y, w, h, z=z, rs=1.0)
    rng = np.random.RandomState(seed)
    cols = ["#8FB8DE", "#A8D5BA", "#F4B942", "#E79A3B", "#B39DDB", "#90CAF9"]
    gw, gh = w/4.6, h/4.2
    for i in range(3):
        for j in range(3):
            ax.add_patch(Rectangle((x+0.9+j*(gw+0.45), y+0.9+i*(gh+0.5)), gw, gh,
                         fc=cols[rng.randint(len(cols))], ec=INK, lw=0.5, zorder=z+7))

def file_tray(x, y, w=15, h=10, z=6):
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h*0.62,
                 boxstyle="round,pad=0.1,rounding_size=1.0",
                 fc="#F2C879", ec=INK, lw=1.6, zorder=z))
    for i, c in enumerate(("#FFFFFF", "#EDF6FF", "#FFF3C4")):
        ax.add_patch(Rectangle((x-w/2+1.6+i*0.9, y-0.4+i*1.15), w-3.2, 2.6,
                     fc=c, ec=INK, lw=0.9, zorder=z+1+i))
    ax.add_patch(Circle((x, y-h/2+1.4), 0.8, fc=INK, zorder=z+4))

def clock(x, y, r=2.6, z=6):
    ax.add_patch(Circle((x, y), r, fc="#FFFFFF", ec=INK, lw=1.6, zorder=z))
    ax.plot([x, x], [y, y+r*0.6], color=INK, lw=1.6, zorder=z+1)
    ax.plot([x, x+r*0.48], [y, y-0.15*r], color=INK, lw=1.6, zorder=z+1)

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

def city_map(x, y, w=20, h=13, z=6, faded=False, cong=True):
    al = 0.45 if faded else 1.0
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                 boxstyle="round,pad=0.1,rounding_size=1.2",
                 fc="#EAF3EA" if not faded else "#EFEFEA", ec=INK, lw=1.6,
                 zorder=z, alpha=al))
    ax.plot([x-w/2+1, x+w/2-1], [y-0.5, y-0.5], color="#FFFFFF", lw=3.4, zorder=z+1, alpha=al)
    ax.plot([x+1.5, x+1.5], [y-h/2+1, y+h/2-1], color="#FFFFFF", lw=3.4, zorder=z+1, alpha=al)
    if cong:
        ax.plot([x+2.8, x+6.8], [y-0.5, y-0.5], color=CONG, lw=3.4, zorder=z+2, alpha=al)
    car(x-5.5, y-0.4, s=0.4, color=CAV_C, z=z+3, faded=faded)
    car(x-2.0, y-0.4, s=0.4, color=CAV_C, z=z+3, faded=faded)
    car(x+4.6, y-0.4, s=0.4, color=HDV_C, z=z+3, faded=faded)
    car(x+1.6, y+3.4, s=0.4, color=HDV_C, z=z+3, faded=faded)

def gauge(x, y, w=13, h=7, z=6):
    sticker_bg(x, y, w, h, z=z, rs=1.0)
    ax.add_patch(Arc((x+3.6, y+2.2), 4.6, 4.6, theta1=0, theta2=180,
                     color=INK, lw=1.5, zorder=z+7))
    ax.plot([x+3.6, x+4.9], [y+2.2, y+3.9], color=CONG, lw=1.8, zorder=z+8)
    for i, hh in enumerate((1.6, 2.6, 3.4)):
        ax.add_patch(Rectangle((x+7.2+i*1.7, y+1.2), 1.1, hh,
                     fc=(WM_BD, "#F4B942", CONG)[i], ec=INK, lw=0.7, zorder=z+7))

# =====================================================================
# LEFT — Phase I container (x 8..69, y 22..85)
# =====================================================================
rbox(8, 22, 61, 63, P1_BG, P1_BD, dashed=True, lw=3.0, rs=2.2)
text(38.5, 82.2, "Phase I · Grounded SUMO Interaction", size=PHASE, bold=True, color=P1_BD)
text(38.5, 78.8, "Simulator-grounded collection", size=ANNOT+0.5, color=SUB)

# --- upper: road network sticker ---
sticker_bg(13, 60, 51, 17, z=4)
city_map(38.5, 68.5, w=44, h=13, z=5)
text(16.5, 75.2, "Mixed-autonomy Traffic", size=LABEL, bold=True, ha="left")
text(60.5, 61.8, r"Traffic Field  $X_t$", size=ANNOT+1, ha="right")
ax.add_patch(Circle((17.2, 62.0), 0.8, fc=CAV_C, ec=INK, lw=1.0, zorder=8))
text(18.6, 62.0, "CAV", size=ANNOT, ha="left")
ax.add_patch(Circle((25.4, 62.0), 0.8, fc=HDV_C, ec=INK, lw=1.0, zorder=8))
text(27.0, 62.0, "HDV", size=ANNOT, ha="left")

# --- replay buffer ---
sticker_bg(12, 40, 18, 13, z=4)
file_tray(21, 45.5, w=13, h=8, z=6)
text(21, 51.3, "Replay Buffer", size=LABEL, bold=True)
text(21, 41.2, "Limited Real Transitions", size=ANNOT)

# --- actor ---
sticker_bg(36, 38, 29, 18, z=4)
car(41.5, 49.5, s=0.62, color=CAV_C, z=7)
text(50.5, 53.7, "Parameter-shared CAV Actor", size=LABEL, bold=True)
text(50.5, 50.9, "Candidate Routes (K = 4)", size=ANNOT, color=SUB)
for i in range(4):
    route_card(45.0+i*4.3, 43.0, selected=(i == 1), z=7)
text(50.5, 40.6, r"Route Actions  $a_t$", size=ANNOT+1)

# actor -> roadnet (execute)
arrow((51, 56.2), (51, 59.6), color=AR_REAL, lw=2.6)
text(53.2, 57.9, "Execute Selected Routes", size=ANNOT, ha="left", color=AR_REAL)
# roadnet -> replay (real transition)
arrow((16.5, 59.6), (19.5, 53.8), color=AR_REAL, lw=2.6)
text(10.8, 57.2, "Real Transition", size=ANNOT, ha="left", color=AR_REAL)
text(10.8, 55.4, r"$(X_t, a_t, X_{t+1})$", size=ANNOT, ha="left", color=AR_REAL)

# =====================================================================
# CENTRAL BRIDGE (x 80..158)
# =====================================================================
# ---------- Module 1: Graph-aligned Action Encoder (y 66..86) ----------
rbox(80, 66, 78, 20, ACT_BG, ACT_BD, lw=2.8)
text(119, 83.4, "Graph-aligned Action Encoder", size=MOD, bold=True, color="#8a7320")
for k in range(3):
    yy = 70.8 + k*3.6
    car(87.5, yy, s=0.4, color=CAV_C, z=6)
    route_card(92.0, yy-1.9, w=3.0, h=3.8, selected=(k == 0), z=6)
    arrow((95.6, yy), (111.5, 75.2), color=ACT_BD, lw=1.8, rad=-0.15, ms=10)
text(91, 68.0, "Per-CAV Route Choices", size=ANNOT, color=SUB)
text(109, 79.8, "Project onto Road Segments", size=ANNOT, color=SUB)
mini_graph(127, 75.5, s=1.05, hl_edges=(1, 4), z=6)
text(133.5, 70.0, r"Planned CAV Pressure  $\Psi_t^{\mathrm{CAV}}$", size=ANNOT+0.5, bold=True)
text(133.5, 67.4, r"$\Psi_t^{\mathrm{CAV}} = \Pi_G(a_t, \mathcal{I}_t)$", size=MATH-1)

# ---------- Module 2: Flow-Matching World Model (y 30..62) ----------
rbox(80, 30, 78, 32, WM_BG, WM_BD, lw=3.0)
text(119, 59.2, "Flow-Matching Traffic World Model", size=MODBIG, bold=True, color="#3d7a50")
text(119, 56.0, r"$x_\tau = (1-\tau)\,Z_t + \tau\,Z_{t+1}$", size=MATH)

# pipeline: X_t,G -> GNN -> Z_t -> flow -> Zhat -> decoder
mini_graph(84.5, 48.0, s=0.62, z=6)
text(87.5, 43.6, r"$X_t,\ G$", size=ANNOT+1)
arrow((91.5, 48.5), (96.0, 48.5), lw=2.0, ms=11)
mini_graph(97.5, 48.0, s=0.62, z=6, messages=True)
text(101, 43.6, "GNN Encoder", size=ANNOT)
arrow((104.5, 48.5), (109.0, 48.5), lw=2.0, ms=11)
latent_card(109.5, 45.3, w=6.4, h=6.0, z=6, seed=1)
text(112.7, 43.6, r"$Z_t$", size=ANNOT+1)
# flow trajectory
fx = np.linspace(117, 129.5, 60)
fy = 48.5 + 3.4*np.sin((fx-117)/12.5*np.pi)
ax.plot(fx, fy, color=AR_WM, lw=2.6, zorder=6)
arrow((fx[-3], fy[-3]), (130.5, 48.5), color=AR_WM, lw=2.6, ms=13)
for i, f in enumerate((0.25, 0.5, 0.75)):
    xx = 117 + 12.5*f
    yy = 48.5 + 3.4*np.sin(f*np.pi)
    ax.add_patch(Circle((xx, yy), 0.85, fc="#FFFFFF", ec=AR_WM, lw=1.6, zorder=7))
text(123.3, 53.6, "State-to-State", size=ANNOT, color="#3d7a50")
text(123.3, 51.9, "Flow Matching", size=ANNOT, color="#3d7a50")
latent_card(131.5, 45.3, w=6.4, h=6.0, z=6, seed=7)
text(134.7, 43.6, r"$\hat{Z}_{t+1}$", size=ANNOT+1)
arrow((138.5, 48.5), (142.5, 48.5), lw=2.0, ms=11)
gauge(143.0, 45.3, w=13.5, h=6.6, z=6)
text(149.8, 43.6, "Traffic Decoder:", size=ANNOT, ha="center")
text(149.8, 41.9, "Speed & Vehicle Count", size=ANNOT, ha="center", color=SUB)

# condition chips
chips = [(91, r"$\Psi_t^{\mathrm{CAV}}$", ACT_BG, ACT_BD),
         (109.5, r"$D_t$", P1_BG, P1_BD),
         (128, r"$\hat{H}_t^{\mathrm{HDV}}$", HDV_BG, HDV_BD),
         (146.5, r"$c_t$", "#EFEFEF", ROAD)]
for cx, lab, fc, ec in chips:
    rbox(cx-8, 34.2, 16, 4.4, fc, ec, lw=1.8, z=5, rs=1.4)
    text(cx, 36.4, lab, size=ANNOT+1.5)
    arrow((cx, 38.8), (cx, 44.8), color=AR_WM, lw=1.8, ms=10)
text(119, 32.4, r"$\hat{Z}_{t+1} = F_\phi\left(Z_t;\ \Psi_t^{\mathrm{CAV}},\ D_t,\ "
                r"\hat{H}_t^{\mathrm{HDV}},\ c_t\right)$", size=MATH-0.5)
text(119, 30.9+0.2, "", size=ANNOT)  # spacer
text(119, 31.2, "", size=1)
text(119, 30.6, "Graph-structured latent traffic dynamics", size=ANNOT, color=SUB)

# ---------- Module 3: Slow-timescale HDV Response (y 15..27.5) ----------
rbox(80, 15, 78, 12.5, HDV_BG, HDV_BD, lw=2.8)
text(119, 25.2, "Slow-timescale HDV Response", size=MOD-1, bold=True, color="#a05c2e")
car(85.5, 20.5, s=0.42, color=HDV_C, z=6)
car(89.5, 19.0, s=0.42, color=HDV_C, z=6)
bar_dist(94.5, 18.3, w=8, h=4.4, seed=2)
text(98.5, 16.6, "Previous Episode", size=ANNOT-0.5, color=SUB)
text(108.5, 22.6, "CAV Pressure Summary", size=ANNOT-0.5, color=SUB)
text(108.5, 20.9, "+ HDV Background", size=ANNOT-0.5, color=SUB)
arrow((103.5, 21.5), (132.5, 21.5), color=AR_HDV, dotted=True, lw=2.6, rad=-0.3)
text(118, 18.3, r"$(\bar{\Psi}_{e-1}^{\mathrm{CAV}},\ H_{e-1}^{\mathrm{HDV}})"
                r"\ \rightarrow\ \hat{H}_e^{\mathrm{HDV}}$", size=MATH-1.5)
bar_dist(133.5, 18.3, w=8, h=4.4, seed=5)
text(137.5, 16.6, r"Next-episode HDV Response  $\hat{H}_e^{\mathrm{HDV}}$",
     size=ANNOT-0.5, color=SUB, ha="center")
calendar(152.5, 21.0, w=6.5, h=6.5, z=6)
# module3 -> condition chips
arrow((128, 27.7), (128, 33.8), color=AR_HDV, lw=2.6)

# =====================================================================
# RIGHT — Phase II container (x 168..232, y 22..85)
# =====================================================================
rbox(168, 22, 64, 63, P2_BG, P2_BD, dashed=True, lw=3.0, rs=2.2)
text(200, 82.2, "Phase II · Imagined Policy Optimization", size=PHASE-1, bold=True, color=P2_BD)

# --- imagined rollout ---
text(172.5, 77.6, "Imagined Traffic Rollout", size=LABEL, bold=True, ha="left", color="#6a4fc4")
text(229.5, 77.6, r"$L_{\mathrm{im}} = 8$", size=LABEL, ha="right", color="#6a4fc4")
rbox(169.5, 68, 7.5, 6, "#FFFFFF", AR_REAL, lw=1.6, z=5, rs=1.0)
text(173.2, 71.7, "replay", size=ANNOT-1)
text(173.2, 70.0, "state", size=ANNOT-1)
arrow((177.3, 71), (181.8, 71), color=AR_REAL, lw=2.0, ms=11)
xs_snap = (182.5, 195.5, 208.5)
labs = (r"$Z_t$", r"$\hat{Z}_{t+1}$", r"$\hat{Z}_{t+2}$")
for i, (xx, lab) in enumerate(zip(xs_snap, labs)):
    latent_card(xx, 68, w=7, h=6.5, z=6, seed=10+i)
    text(xx+3.5, 66.0, lab, size=ANNOT+0.5)
    if i < 2:
        arrow((xx+7.3, 71), (xx+12.7, 71), color=AR_IM, lw=2.4, ms=12)
text(220.5, 71, "…", size=18, color="#6a4fc4")

# faded crossed SUMO
city_map(227, 61.5, w=9.5, h=6.5, z=5, faded=True, cong=False)
ax.plot([222.6, 231.4], [58.6, 64.4], color=SUB, lw=1.4, zorder=9)
text(227, 56.6, "No additional", size=ANNOT-0.5, color=SUB)
text(227, 55.0, "SUMO queries", size=ANNOT-0.5, color=SUB)

# --- vehicle wrapper ---
sticker_bg(171, 46.5, 51, 11, z=4)
text(196.5, 55.6, "Identity-preserving Vehicle Wrapper", size=LABEL, bold=True)
ax.plot([173.5, 219.5], [51.2, 51.2], color=ROAD, lw=3.0, zorder=6, solid_capstyle="round")
for xx, cid in ((180, "1"), (193, "2"), (206, "3")):
    car(xx, 52.4, s=0.5, color=CAV_C, z=7)
    text(xx, 48.6, cid, size=ANNOT-0.5, color=SUB)
    if xx < 200:
        arrow((xx+3.6, 51.2), (xx+9.4, 51.2), color=AR_IM, lw=1.8, ms=10)
ax.plot([216.5, 216.5], [51.2, 55.0], color=CONG, lw=1.6, zorder=7)
ax.add_patch(plt.Polygon([(216.5, 55.0), (216.5, 53.2), (219.2, 54.1)],
             fc=CONG, ec=INK, lw=0.8, zorder=7))
text(196.5, 47.2, "Positions · Route Progress · Departures · Arrivals",
     size=ANNOT-0.3, color=SUB)

# --- critics ---
sticker_bg(172, 30.5, 27, 13.5, z=4)
text(185.5, 42.0, "Per-vehicle Critic", size=LABEL, bold=True)
for i, xx in enumerate((176.3, 182.6, 188.9)):
    car(xx, 37.6, s=0.38, color=CAV_C, z=7)
    text(xx+2.6, 37.6, f"$v_{i+1}$", size=ANNOT)
text(185.5, 32.3, "Vehicle-specific Credit", size=ANNOT-0.3, color=SUB)

sticker_bg(201, 30.5, 27, 13.5, z=4)
text(214.5, 42.0, "Global Critic", size=LABEL, bold=True)
mini_graph(206.5, 36.6, s=0.55, z=7)
text(220.5, 37.6, r"$v^{\mathrm{global}}_t$", size=ANNOT+1)
text(214.5, 32.6, "Network-level", size=ANNOT-0.3, color=SUB)
text(214.5, 31.3, "Congestion Credit", size=ANNOT-0.3, color=SUB)

# rollout/wrapper -> critics
arrow((188, 46.2), (186.5, 44.3), color=AR_IM, lw=2.0, ms=10)
arrow((212, 46.2), (213.5, 44.3), color=AR_IM, lw=2.0, ms=10)

# --- advantage node & update ---
rbox(186.5, 23.6, 27, 4.6, "#FFFFFF", AR_UPD, lw=1.8, z=5, rs=1.2)
text(200, 25.9, r"$A^{\mathrm{veh}}_{i,t} + \alpha_g\, A^{\mathrm{global}}_t$",
     size=MATH-0.5)
arrow((192, 30.3), (195, 28.4), color=AR_UPD, lw=2.0, ms=10)
arrow((211, 30.3), (208, 28.4), color=AR_UPD, lw=2.0, ms=10)

# =====================================================================
# cross-container connectors
# =====================================================================
# replay -> world model (main real-data path)
arrow((30.3, 46.5), (79.6, 48.5), color=AR_REAL, lw=3.0)
text(55, 49.4, "real transitions  (train world model)", size=ANNOT, color=AR_REAL)

# actor -> action encoder (elbow)
arrow((65.2, 47), (80.5, 76), color=AR_REAL, lw=2.6, elbow=True)
text(74.6, 61.5, r"route actions  $a_t$", size=ANNOT, color=AR_REAL, rot=90)

# module1 Psi -> chip
arrow((95, 65.6), (95, 38.9), color=AR_WM, lw=2.2)

# decoder -> wrapper
arrow((156.6, 47.5), (170.6, 51.5), color=AR_WM, lw=2.6, rad=-0.2)
text(163.5, 52.8, r"$\hat{v},\ \hat{n}$", size=ANNOT, color=AR_WM)

# imagined rollout -> wrapper
arrow((199, 67.6), (199, 57.9), color=AR_IM, lw=2.2)

# PPO update + long quiet return along bottom
arrow((200, 23.3), (200, 13.0), color=AR_UPD, dashed=True, lw=2.4)
ax.plot([50, 200], [13.0, 13.0], color=AR_UPD, lw=2.4, zorder=6,
        linestyle=(0, (5, 3)))
arrow((50, 13.0), (50, 37.6), color=AR_UPD, dashed=True, lw=2.4)
text(200.5, 16.2, "PPO Actor Update", size=ANNOT, ha="left", color=AR_UPD)
text(125, 11.0, "Updated Policy for the Next Collection Episode",
     size=LABEL, color=AR_UPD)

# restrained result label, lower-right
text(231.5, 17.5, "Sample-efficient", size=ANNOT+0.5, ha="right", color=SUB, bold=True)
text(231.5, 15.6, "CAV Routing Policy", size=ANNOT+0.5, ha="right", color=SUB, bold=True)

plt.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.005)
out = "figure/main_figure_v2.png"
plt.savefig(out, facecolor=BG)
print("saved", out)
