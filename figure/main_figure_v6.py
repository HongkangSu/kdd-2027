"""UrbanDreamer main framework figure — v6.

Readability pass over v5: fonts scaled ~1.9x so the figure stays legible
when scaled to acmart \textwidth (~0.29x), annotations trimmed to fit.
Same Method-aligned skeleton:
  center : Flow-Matching Dynamics Model (3 sub-blocks)
  below  : HDV Response Module
  right  : Actor-Critic Learner (imagination / actor / two critics)
  left   : SUMO + replay (data context)
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

# ---- typography (canvas pt; printed size = canvas x 0.29 at \textwidth) ----
MODBIG, MOD, SUBT, LABEL, ANNOT, MICRO, MATH = 28, 22, 20, 16, 14, 13.5, 17

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
          z=6, ms=16):
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
# LEFT — SUMO & replay (x 6..40)
# =====================================================================
sticker_bg(7, 60, 32, 20, z=4)
city_map(23, 69.6, w=27, h=12.5, z=5)
text(10.5, 78.0, "SUMO Simulator", size=LABEL, bold=True, ha="left")
text(36.8, 74.8, r"Traffic Field $X_t$", size=MICRO+1, ha="right", z=9)
ax.add_patch(Circle((11.2, 62.2), 0.8, fc=CAV_C, ec=INK, lw=1.0, zorder=8))
text(12.8, 62.2, "CAV", size=MICRO+0.5, ha="left")
ax.add_patch(Circle((19.6, 62.2), 0.8, fc=HDV_C, ec=INK, lw=1.0, zorder=8))
text(21.2, 62.2, "HDV", size=MICRO+0.5, ha="left")

sticker_bg(7, 38, 19, 14, z=4)
file_tray(16.5, 44.5, w=13, h=8.5, z=6)
text(16.5, 50.2, "Replay Buffer", size=LABEL, bold=True)
text(16.5, 39.6, r"$(X_t, a_t, X_{t+1})$", size=MICRO+1.5)
text(16.5, 36.3, "limited transitions", size=MICRO, color=SUB)

arrow((18, 59.5), (18, 52.8), color=AR_REAL, lw=2.6)
text(20.5, 56.2, "store", size=MICRO+0.5, ha="left", color=AR_REAL)

# =====================================================================
# CENTER — Flow-Matching Dynamics Model (x 46..146, y 26..88)
# =====================================================================
rbox(46, 26, 100, 62, WM_BG, WM_BD, lw=3.0)
text(96, 84.8, "Flow-Matching Dynamics Model", size=MODBIG, bold=True, color="#3d7a50")

# ---- sub-block 1: Traffic Encoder & Decoder (x 50..93, y 57..81) ----
rbox(50, 57, 43, 24, "#FFFFFF", WM_BD, lw=1.8, z=3, rs=1.4)
text(71.5, 78.3, "Traffic Encoder & Decoder", size=SUBT, bold=True, color="#3d7a50")
mini_graph(53, 70, s=0.5, z=6)
text(55.5, 66.0, r"$X_t,\ G$", size=MICRO+1)
arrow((58.8, 70), (61.0, 70), lw=2.0, ms=11)
rbox(61, 67, 12.5, 6, WM_BG, WM_BD, lw=1.5, z=5, rs=1.0)
text(67.2, 70, "GCN Encoder", size=MICRO+1, bold=True, color="#3d7a50")
arrow((74, 70), (76.3, 70), lw=2.0, ms=11)
latent_card(76.3, 67, w=6.3, h=6.0, z=6, seed=1)
text(85.3, 70, r"$Z_t$", size=MICRO+1, ha="left")
rbox(71.5, 63.4, 17.5, 3.2, "#E3ECFF", "#3D5BA1", lw=1.5, z=5, rs=0.9)
text(80.2, 65.0, r"Decoder: $[\hat{c},\ \hat{v}]$", size=MICRO+1, color="#2c4470")
text(71.5, 61.5, "residual GCN + LayerNorm", size=MICRO, color=SUB)
text(71.5, 59.8, r"$z_{t,u}$: segment + neighborhood", size=MICRO, color=SUB)
text(71.5, 58.1, "readouts for reward & value", size=MICRO, color=SUB)

# ---- sub-block 2: Action Encoder (x 96..143, y 57..81) ----
rbox(96, 57, 47, 24, ACT_BG, ACT_BD, lw=1.8, z=3, rs=1.4)
text(119.5, 78.3, "Action Encoder", size=SUBT, bold=True, color="#8a7320")
for k in range(3):
    yy = 68.6 + k*3.1
    car(100.8, yy, s=0.33, color=CAV_C, z=6)
    route_card(104.2, yy-1.6, w=2.6, h=3.3, selected=(k == 0), z=6)
    arrow((107.4, yy), (112.5, 71.4), color=ACT_BD, lw=1.6, rad=-0.12, ms=10)
mini_graph(114.5, 72.2, s=0.58, hl_edges=(1, 4), z=6)
text(123, 67.6, "planned CAV pressure", size=MICRO+0.5, ha="left")
text(123, 65.6, r"$\Psi_t^{\mathrm{CAV}} = \Pi_G(a_t, \mathcal{I}_t)$",
     size=MATH-2, ha="left")
text(119.5, 61.7, r"segments within look-ahead $\Delta$", size=MICRO, color=SUB)
text(119.5, 59.9, "same one-hot route:", size=MICRO, color=SUB)
text(119.5, 58.1, "executed · stored · conditioned", size=MICRO, color=SUB)

# ---- sub-block 3: State-to-State Flow Matching (x 50..143, y 29..54) ----
rbox(50, 29, 93, 25, "#FFFFFF", WM_BD, lw=1.8, z=3, rs=1.4)
text(96.5, 51.6, "State-to-State Flow Matching", size=SUBT, bold=True, color="#3d7a50")
latent_card(54, 42, w=6.5, h=6.0, z=6, seed=2)
text(57.2, 40.3, r"$Z_t$", size=MICRO+1)
fx = np.linspace(62.5, 76, 60)
fy = 45 + 2.3*np.sin((fx-62.5)/13.5*np.pi)
ax.plot(fx, fy, color=AR_WM, lw=2.6, zorder=6)
arrow((fx[-3], fy[-3]), (77.2, 45), color=AR_WM, lw=2.6, ms=12)
for f in (0.25, 0.5, 0.75):
    xx = 62.5 + 13.5*f
    yy = 45 + 2.3*np.sin(f*np.pi)
    ax.add_patch(Circle((xx, yy), 0.8, fc="#FFFFFF", ec=AR_WM, lw=1.5, zorder=7))
text(69.2, 50.0, r"velocity field $\nu_\phi$", size=MICRO+1, color="#3d7a50")
text(69.2, 48.2, "(block-causal Transformer)", size=MICRO, color=SUB)
latent_card(78, 42, w=6.5, h=6.0, z=6, seed=7)
text(81.2, 40.3, r"$\hat{Z}_{t+1}$", size=MICRO+1)
text(115.5, 49.2, r"$x_\tau = (1-\tau)\,Z_t + \tau\,Z_{t+1}$", size=MATH-1.5)
text(115.5, 46.4, r"target $\nu^\star = Z_{t+1} - Z_t$", size=MATH-1.5)
text(115.5, 43.6, r"$\hat{Z}_{t+1} = Z_t + \int_0^1 \nu_\phi\, d\tau$", size=MATH-1.5)
text(69.2, 40.3, "k Euler steps", size=MICRO, color=SUB)

# condition chips
chips = [(61, r"$\Psi_t^{\mathrm{CAV}}$", ACT_BG, ACT_BD),
         (78, r"$D_t$", "#EDF6FF", "#6FA8DC"),
         (95, r"$\hat{H}_t^{\mathrm{HDV}}$", HDV_BG, HDV_BD),
         (112, r"$c_t$", "#EFEFEF", ROAD)]
for cx, lab, fc, ec in chips:
    rbox(cx-7.5, 32.6, 15, 4.4, fc, ec, lw=1.7, z=5, rs=1.3)
    text(cx, 34.8, lab, size=ANNOT)
    arrow((cx, 37.2), (cx, 41.4), color=AR_WM, lw=1.7, ms=10)
text(124.5, 34.8, r"condition $\mathcal{C}_t$", size=MICRO+1, color=SUB, ha="left")
text(96.5, 30.5, r"$\hat{Z}_{t+1} = F_\phi\left(Z_t;\ \Psi_t^{\mathrm{CAV}},\ D_t,\ "
                 r"\hat{H}_t^{\mathrm{HDV}},\ c_t\right)$", size=MATH-2)
text(141.5, 30.5, r"$w_{t,u}$: congested upweighted", size=MICRO, color=SUB, ha="right")

# overall WM objective
text(96, 27.2, r"$\mathcal{L}_{\mathrm{WM}} = \mathcal{L}_{\mathrm{FM}}"
               r" + \lambda_{\mathrm{dec}}\mathcal{L}_{\mathrm{dec}}"
               r" + \lambda_{\mathrm{resp}}\mathcal{L}_{\mathrm{resp}}$",
     size=MATH-1, color="#3d7a50")

# =====================================================================
# BELOW CENTER — HDV Response Module (x 46..146, y 10..24)
# =====================================================================
rbox(46, 10, 100, 14, HDV_BG, HDV_BD, lw=2.8)
text(96, 22.1, "HDV Response Module", size=MOD, bold=True, color="#a05c2e")
car(52, 16.8, s=0.4, color=HDV_C, z=6)
car(55.8, 15.4, s=0.4, color=HDV_C, z=6)
bar_dist(59.5, 13.7, w=7, h=4.2, seed=2)
text(63, 12.0, "previous episode", size=MICRO, color=SUB)
arrow((67.5, 17.5), (70.5, 17.5), color=AR_HDV, dotted=True, lw=2.4, ms=10)
rbox(70.5, 15.4, 13, 4.6, "#FFFFFF", HDV_BD, lw=1.6, z=5, rs=1.0)
text(77, 17.7, "MLP + softmax", size=MICRO+1, color="#a05c2e")
arrow((84, 17.5), (86.8, 17.5), color=AR_HDV, dotted=True, lw=2.4, ms=10)
bar_dist(87.5, 13.7, w=7, h=4.2, seed=5)
text(91, 12.0, r"$\hat{H}_e^{\mathrm{HDV}}$", size=MICRO+1, color=SUB)
text(114.5, 18.6, r"$(\bar{\Psi}_{e-1}^{\mathrm{CAV}},\ H_{e-1}^{\mathrm{HDV}})"
                  r"\rightarrow \hat{H}_e^{\mathrm{HDV}}$", size=MATH-2)
text(114.5, 15.9, r"soft-label CE vs. observed $H^\star$", size=MICRO, color=SUB)
text(114.5, 14.1, "separate optimizer · fixed within episode", size=MICRO, color=SUB)
calendar(138.5, 17.3, w=5.5, h=5.8, z=6)
# HDV module -> condition chip
arrow((95, 24.2), (95, 32.2), color=AR_HDV, lw=2.6)

# =====================================================================
# RIGHT — Actor-Critic Learner (x 152..234, y 10..88)
# =====================================================================
rbox(152, 10, 82, 78, P2_BG, P2_BD, lw=3.0)
text(193, 84.8, "Actor-Critic Learner", size=MODBIG, bold=True, color="#6a4fc4")

# ---- Vehicle-Level Imagination (x 156..230, y 54..80) ----
rbox(156, 54, 74, 26, "#FFFFFF", P2_BD, lw=1.8, z=3, rs=1.4)
text(159, 77.3, "Vehicle-Level Imagination", size=SUBT, bold=True, color="#6a4fc4", ha="left")
text(227.5, 77.3, r"$L_{\mathrm{im}}$ steps", size=MICRO+1, color=SUB, ha="right")
rbox(158.5, 67, 6.5, 5.5, "#FFFFFF", AR_REAL, lw=1.5, z=5, rs=0.9)
text(161.7, 71.1, "replay", size=MICRO)
text(161.7, 69.3, "state", size=MICRO)
arrow((165.3, 69.8), (167.8, 69.8), color=AR_REAL, lw=1.8, ms=10)
xs_snap = (168, 180, 192)
labs = (r"$Z_t$", r"$\hat{Z}_{t+1}$", r"$\hat{Z}_{t+2}$")
for i, (xx, lab) in enumerate(zip(xs_snap, labs)):
    latent_card(xx, 67.2, w=6.5, h=6.0, z=6, seed=10+i)
    text(xx+3.2, 65.5, lab, size=MICRO+0.5)
    if i < 2:
        arrow((xx+6.8, 70.2), (xx+11.6, 70.2), color=AR_IM, lw=2.2, ms=11)
text(202, 70.2, "…", size=16, color="#6a4fc4")
city_map(217.5, 70.2, w=9, h=6.5, z=5, faded=True, cong=False)
ax.plot([213.4, 221.6], [67.3, 73.1], color=SUB, lw=1.3, zorder=9)
text(217.5, 65.3, "no SUMO", size=MICRO, color=SUB)
text(217.5, 63.9, "queries", size=MICRO, color=SUB)
# wrapper lane
ax.plot([160, 208], [61.0, 61.0], color=ROAD, lw=2.8, zorder=6, solid_capstyle="round")
for xx, cid in ((166, "1"), (179, "2"), (192, "3")):
    car(xx, 62.0, s=0.42, color=CAV_C, z=7)
    text(xx, 59.2, cid, size=MICRO, color=SUB)
    if xx < 188:
        arrow((xx+3.2, 61.0), (xx+9.0, 61.0), color=AR_IM, lw=1.6, ms=9)
ax.plot([203, 203], [61.0, 64.4], color=CONG, lw=1.5, zorder=7)
ax.add_patch(plt.Polygon([(203, 64.4), (203, 62.7), (205.6, 63.5)],
             fc=CONG, ec=INK, lw=0.8, zorder=7))
arrow((183, 66.9), (183, 63.8), color=SUB, lw=1.6, ms=9)
text(193, 57.0, r"wrapper consumes $\hat\tau(u) = \ell(u)/\hat v_{t,u}$ along routes",
     size=MICRO, color=SUB)
text(193, 55.2, "replay-init · departures join · arrivals leave",
     size=MICRO, color=SUB)

# ---- Parameter-Shared CAV Actor (x 156..230, y 35..51) ----
rbox(156, 35, 74, 16, "#FFFFFF", P2_BD, lw=1.8, z=3, rs=1.4)
text(193, 48.6, "Parameter-Shared CAV Actor", size=SUBT, bold=True, color="#6a4fc4")
car(163.5, 42.3, s=0.5, color=CAV_C, z=7)
for i in range(4):
    route_card(169.5+i*4.2, 39.6, w=3.4, selected=(i == 1), z=7)
text(177.5, 45.6, "K candidate routes", size=MICRO, color=SUB)
text(213, 43.6, "masked softmax", size=MICRO+1, color=SUB)
text(213, 41.9, r"over valid $m_{i,t,k}$", size=MICRO+1, color=SUB)
text(193, 37.9, r"route feature $\varphi_{i,t,k}$: mean-pooled latents",
     size=MICRO, color=SUB)
text(193, 36.2, r"context $g_t$ · shared across CAVs & slots",
     size=MICRO, color=SUB)
arrow((193, 53.7), (193, 51.3), color=AR_IM, lw=2.2, ms=11)

# ---- critics (y 20..33) ----
rbox(156, 20, 37, 13, "#FFFFFF", P2_BD, lw=1.8, z=3, rs=1.4)
text(174.5, 31.2, "Per-Vehicle Critic", size=SUBT-1, bold=True, color="#6a4fc4")
for i, xx in enumerate((164, 171, 178)):
    car(xx, 27.6, s=0.34, color=CAV_C, z=7)
    text(xx+2.6, 27.6, f"$v_{i+1}$", size=MICRO+1)
text(174.5, 24.6, "self-attention over active CAVs", size=MICRO, color=SUB)
text(174.5, 22.9, r"$r_i = -\min(\Delta t, \hat T^{\mathrm{rem}})/\kappa_r$", size=MICRO, color=SUB)
text(174.5, 21.2, r"$\lambda$-return by vehicle identity", size=MICRO, color=SUB)

rbox(195, 20, 35, 13, "#FFFFFF", P2_BD, lw=1.8, z=3, rs=1.4)
text(212.5, 31.2, "Global Critic", size=SUBT-1, bold=True, color="#6a4fc4")
mini_graph(202, 27.4, s=0.48, z=7)
text(216, 27.6, r"$v^{\mathrm{global}}_t$", size=MICRO+2)
text(212.5, 24.6, r"$r^g = -\kappa_g N_{\mathrm{active}}\Delta t / N_{\mathrm{veh}}$",
     size=MICRO, color=SUB)
text(212.5, 22.9, r"imagined: $N_{\mathrm{active}} = \sum_u \hat n_{t,u}$", size=MICRO, color=SUB)
text(212.5, 21.2, r"$\sum_t r^g \propto$ mean travel time", size=MICRO, color=SUB)

arrow((174.5, 34.7), (174.5, 33.5), color=AR_IM, lw=2.0, ms=10)
arrow((212.5, 34.7), (212.5, 33.5), color=AR_IM, lw=2.0, ms=10)

# ---- advantage node ----
rbox(176, 13.5, 34, 5.0, "#FFFFFF", AR_UPD, lw=1.8, z=5, rs=1.1)
text(193, 16.0, r"$A^{\mathrm{veh}}_{i,t} + \alpha_g\, A^{\mathrm{global}}_t$",
     size=MATH-1)
text(212, 16.0, "PPO clip + entropy", size=MICRO+1, color=SUB, ha="left")
arrow((180, 19.8), (186, 18.7), color=AR_UPD, lw=1.8, ms=9)
arrow((206, 19.8), (200, 18.7), color=AR_UPD, lw=1.8, ms=9)

# =====================================================================
# cross-module connectors
# =====================================================================
# replay -> WM (real transitions bus)
seg((26.3, 45), (42, 45), color=AR_REAL, lw=3.0)
seg((42, 45), (42, 70), color=AR_REAL, lw=3.0)
arrow((42, 70), (51, 70), color=AR_REAL, lw=3.0)
text(44.2, 57, r"real transitions", size=MICRO+1, color=AR_REAL, rot=90, ha="center")

# WM -> imagination (learned transition + readouts)
seg((80, 63.2), (80, 55.5), color=AR_WM, lw=2.6)
seg((80, 55.5), (149, 55.5), color=AR_WM, lw=2.6)
seg((149, 55.5), (149, 64), color=AR_WM, lw=2.6)
arrow((149, 64), (156.5, 64), color=AR_WM, lw=2.6)
text(113, 56.8, "learned transition + readouts", size=MICRO, color=AR_WM)

# PPO update -> bottom return -> execute in SUMO
arrow((193, 13.2), (193, 5.8), color=AR_UPD, dashed=True, lw=2.4)
seg((40, 5.5), (193, 5.5), color=AR_UPD, dashed=True, lw=2.4)
arrow((40, 5.5), (40, 59.3), color=AR_UPD, dashed=True, lw=2.4)
text(194.5, 8.4, "PPO Actor Update", size=MICRO+1, ha="left", color=AR_UPD)
text(117, 3.4, "Updated policy → execute sampled routes in the next collection episode",
     size=LABEL-1, color=AR_UPD)

plt.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.005)
out = "figure/main_figure_v6.png"
plt.savefig(out, facecolor=BG)
print("saved", out)
