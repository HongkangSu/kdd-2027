"""UrbanDreamer main architecture figure — hand-sketched draft.

Canvas 2400x1350 px @ dpi 150. Two independent dashed phase containers
bridged by three stacked modules. Style: xkcd wobble + clip-art stickers.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch, Arc
import numpy as np

# ---------- palette ----------
BG       = "#FAF7F2"
INK      = "#2B2B2B"
CAPTION  = "#6B6259"
TEAL     = "#2E7D6B"; TEAL_BG   = "#E8F3F0"
ORANGE   = "#C05621"; ORANGE_BG = "#FBEEE3"
ENC_BG   = "#FFF4D6"; ENC_BD    = "#8C6D1F"
DYN_BG   = "#FFE3E3"; DYN_BD    = "#A13D3D"
DEC_BG   = "#E3ECFF"; DEC_BD    = "#3D5BA1"
ARROW    = "#4A4A4A"
UPDATE   = "#A13D3D"
STICKER  = {"car": "#F4B942", "car2": "#5BA4CF", "car3": "#E06C5A",
            "road": "#9C948A", "node": "#FFFFFF", "hl": "#7CB87C"}

plt.rcParams["path.sketch"] = (1.2, 12, 2)   # scale, length, randomness
plt.rcParams["font.family"] = "DejaVu Sans"

fig, ax = plt.subplots(figsize=(16, 9), dpi=150)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 240); ax.set_ylim(0, 135)
ax.axis("off")

# ---------- helpers ----------
def rbox(x, y, w, h, fc, ec, dashed=False, lw=2.2, pad=0.6):
    b = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad={pad},rounding_size=1.6",
                       fc=fc, ec=ec, lw=lw,
                       linestyle=(0, (5, 3)) if dashed else "solid",
                       zorder=2)
    ax.add_patch(b)
    return b

def text(x, y, s, size=10, bold=False, color=INK, ha="center", va="center", z=6):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, zorder=z,
            fontweight="bold" if bold else "normal", linespacing=1.25)

def arrow(p1, p2, color=ARROW, dashed=False, lw=2.0, style="-|>", rad=0.0, z=4, ms=14):
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=ms,
                        color=color, lw=lw, zorder=z,
                        linestyle=(0, (4, 3)) if dashed else "solid",
                        connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(a)
    return a

# ---------- clip-art stickers ----------
def car(x, y, s=1.0, color="#F4B942", z=5):
    """cartoon car, ~ (9s x 4.5s) centered at (x,y)"""
    ax.add_patch(FancyBboxPatch((x-4.5*s, y-1.6*s), 9*s, 3.2*s,
                 boxstyle="round,pad=0.1,rounding_size=1.2",
                 fc=color, ec=INK, lw=1.8, zorder=z))
    ax.add_patch(FancyBboxPatch((x-2.2*s, y+0.9*s), 4.4*s, 2.0*s,
                 boxstyle="round,pad=0.1,rounding_size=0.9",
                 fc="#BFE3F0", ec=INK, lw=1.6, zorder=z))
    for dx in (-2.6, 2.6):
        ax.add_patch(Circle((x+dx*s, y-1.9*s), 1.15*s, fc=INK, ec=INK, zorder=z+1))
        ax.add_patch(Circle((x+dx*s, y-1.9*s), 0.45*s, fc="#DDDDDD", ec=INK, lw=0.8, zorder=z+2))

def clock(x, y, r=3.2, z=5):
    ax.add_patch(Circle((x, y), r, fc="#FFFFFF", ec=INK, lw=1.8, zorder=z))
    ax.plot([x, x], [y, y+r*0.62], color=INK, lw=1.8, zorder=z+1)
    ax.plot([x, x+r*0.5], [y, y-0.2*r], color=INK, lw=1.8, zorder=z+1)
    ax.add_patch(Circle((x, y), 0.35, fc=INK, zorder=z+2))

def checklist(x, y, w=7.5, h=8.5, z=5):
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                 boxstyle="round,pad=0.1,rounding_size=0.8",
                 fc="#FFFFFF", ec=INK, lw=1.8, zorder=z))
    for i, yy in enumerate((y+2.4, y+0.2, y-2.0)):
        ax.plot([x-w/2+1.3, x-w/2+2.3], [yy-0.3, yy-1.1], color=TEAL, lw=1.6, zorder=z+1)
        ax.plot([x-w/2+2.3, x-w/2+3.6], [yy-1.1, yy+0.7], color=TEAL, lw=1.6, zorder=z+1)
        ax.plot([x-w/2+4.3, x+w/2-1.2], [yy-0.2, yy-0.2], color="#BBBBBB", lw=1.4, zorder=z+1)

def person(x, y, s=1.0, color="#8FB8DE", z=5):
    ax.add_patch(Circle((x, y+2.6*s), 1.3*s, fc="#F2C894", ec=INK, lw=1.6, zorder=z))
    ax.add_patch(FancyBboxPatch((x-1.7*s, y-2.6*s), 3.4*s, 4.2*s,
                 boxstyle="round,pad=0.1,rounding_size=1.0",
                 fc=color, ec=INK, lw=1.6, zorder=z))

def circular_arrow(x, y, r=4.6, color=TEAL, z=4):
    ax.add_patch(Arc((x, y), 2*r, 2*r, theta1=300, theta2=220,
                     color=color, lw=1.8, zorder=z, linestyle=(0, (4, 2))))
    ax.add_patch(FancyArrowPatch((x+r*np.cos(np.deg2rad(220)), y+r*np.sin(np.deg2rad(220))),
                                 (x+r*np.cos(np.deg2rad(205)), y+r*np.sin(np.deg2rad(205))),
                                 arrowstyle="-|>", mutation_scale=12, color=color, lw=1.8, zorder=z))

def fork_road(x, y, s=1.0, hl=1, z=5):
    """one road splitting into three; hl = which branch highlighted (0,1,2)"""
    ax.plot([x-6*s, x-1*s], [y, y], color=STICKER["road"], lw=3.2, zorder=z, solid_capstyle="round")
    for i, dy in enumerate((3.2, 0.0, -3.2)):
        c = STICKER["hl"] if i == hl else STICKER["road"]
        w = 4.0 if i == hl else 3.0
        xs = [x-1*s, x+2.2*s, x+5.5*s]
        ys = [y, y+dy*0.55, y+dy]
        ax.plot(xs, ys, color=c, lw=w, zorder=z+1, solid_capstyle="round")

def city_map(x, y, w=16, h=11, z=5):
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                 boxstyle="round,pad=0.1,rounding_size=1.0",
                 fc="#DCEBDD", ec=INK, lw=1.8, zorder=z))
    for f in (-0.18, 0.22):
        ax.plot([x-w/2+1, x+w/2-1], [y+f*h, y+f*h], color="#FFFFFF", lw=2.6, zorder=z+1)
    ax.plot([x-0.1*w, x-0.1*w], [y-h/2+1, y+h/2-1], color="#FFFFFF", lw=2.6, zorder=z+1)
    car(x-3.6, y+0.22*h, s=0.42, color=STICKER["car"], z=z+2)
    car(x+3.4, y-0.18*h, s=0.42, color=STICKER["car2"], z=z+2)

def drawer(x, y, w=15, h=9, z=5):
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h,
                 boxstyle="round,pad=0.1,rounding_size=0.9",
                 fc="#D9C7A7", ec=INK, lw=1.8, zorder=z))
    ax.plot([x-w/2, x+w/2], [y, y], color=INK, lw=1.4, zorder=z+1)
    for yy in (y+2.2, y-2.2):
        ax.plot([x-2.2, x+2.2], [yy, yy], color=INK, lw=1.8, zorder=z+1)

def road_graph(x, y, z=5):
    """small segment-node graph with speed bars"""
    pts = [(x-11, y+3.5), (x-4, y+6.5), (x+3, y+4.5), (x+10, y+6.0),
           (x-8, y-3.5), (x+0.5, y-2.0), (x+8.5, y-4.0), (x+13, y+0.5)]
    edges = [(0,1),(1,2),(2,3),(0,4),(4,5),(5,2),(5,6),(6,7),(3,7),(2,7)]
    for a, b in edges:
        ax.plot([pts[a][0], pts[b][0]], [pts[a][1], pts[b][1]],
                color=STICKER["road"], lw=1.8, zorder=z)
    rng = np.random.RandomState(3)
    for i, (px, py) in enumerate(pts):
        ax.add_patch(Circle((px, py), 1.35, fc=STICKER["node"], ec=INK, lw=1.5, zorder=z+2))
        hbar = rng.uniform(1.0, 3.2)
        cbar = "#E06C5A" if hbar > 2.4 else ("#F4B942" if hbar > 1.6 else "#7CB87C")
        ax.add_patch(Rectangle((px+1.6, py-1.1), 0.9, hbar, fc=cbar, ec=INK, lw=0.7, zorder=z+2))

# =====================================================================
# LAYER 1+2: containers & bridge
# =====================================================================
# left phase container
rbox(10, 26, 85, 84, TEAL_BG, TEAL, dashed=True, lw=2.6)
text(52.5, 105.5, "Phase A · World-Model Learning", size=15, bold=True, color=TEAL)
text(52.5, 101.5, "(real transitions)", size=11, color=CAPTION)

# right phase container
rbox(145, 26, 85, 84, ORANGE_BG, ORANGE, dashed=True, lw=2.6)
text(187.5, 105.5, "Phase B · Imagined Actor–Critic", size=15, bold=True, color=ORANGE)
text(187.5, 101.5, "(no simulator in the loop)", size=11, color=CAPTION)

# bridge modules
rbox(100, 88, 40, 14, ENC_BG, ENC_BD, lw=2.4)
text(120, 96.6, "GCN Encoder", size=12.5, bold=True, color=ENC_BD)
text(120, 91.8, "Z_t = f(X_t, G)", size=10.5)

rbox(100, 56, 40, 24, DYN_BG, DYN_BD, lw=2.4)
text(120, 75.5, "Flow-Matching Dynamics", size=12.5, bold=True, color=DYN_BD)
text(120, 71.5, "velocity field ν_φ", size=10.5)
text(120, 67.8, "block-causal Transformer", size=10.5)
text(120, 63.4, "Euler integrate τ:  Z_t → Ẑ_t+1", size=10.5)
text(120, 59.6, "× L_im imagined steps", size=9.5, color=CAPTION)

rbox(100, 32, 40, 14, DEC_BG, DEC_BD, lw=2.4)
text(120, 40.6, "Decoder", size=12.5, bold=True, color=DEC_BD)
text(120, 35.8, "readouts:  speed v̂ ,  count n̂", size=10.5)

# bridge vertical arrows
arrow((120, 88), (120, 80.5))
arrow((120, 56), (120, 46.5))
# multi-step self loop on dynamics
arrow((140, 72), (140, 62), rad=-0.9, color=DYN_BD, lw=1.8)

# =====================================================================
# LEFT container content
# =====================================================================
city_map(28, 91, w=19, h=12)
text(28, 83.0, "SUMO simulator", size=10, color=CAPTION)

drawer(28, 70, w=16, h=9)
text(28, 63.6, "replay buffer B", size=10, color=CAPTION)
arrow((28, 84.5), (28, 75.5))

road_graph(66, 90)
text(66, 81.5, "traffic field X_t  (segment nodes)", size=10, color=CAPTION)

# --- four condition stickers ---
cy = 49
text(52.5, 57.5, "transition condition  C_t", size=10.5, bold=True, color=CAPTION)
# 1: Psi_CAV
fork_road(22, cy, s=0.75, hl=0)
car(22, cy+5.2, s=0.5, color=STICKER["car"])
text(22, cy-6.2, "Ψ_CAV", size=10, bold=True)
text(22, cy-9.0, "planned pressure", size=8.5, color=CAPTION)
# 2: demand clock
clock(43.5, cy+1.2, r=3.4)
car(49.5, cy-3.4, s=0.45, color=STICKER["car3"])
text(43.5, cy-6.2, "D_t", size=10, bold=True)
text(43.5, cy-9.0, "departure demand", size=8.5, color=CAPTION)
# 3: HDV response
person(65, cy+0.5, s=0.9)
circular_arrow(65, cy+0.8, r=5.0)
text(65, cy-6.2, "Ĥ_HDV", size=10, bold=True)
text(65, cy-9.0, "episode-level response", size=8.5, color=CAPTION)
# 4: context checklist
checklist(86, cy+0.6, w=7.5, h=9)
text(86, cy-6.2, "c_t", size=10, bold=True)
text(86, cy-9.0, "episode context", size=8.5, color=CAPTION)

# loss tags
for xx, lab in ((30, "L_FM"), (48, "L_dec"), (66, "L_resp")):
    rbox(xx-6.5, 29.5, 13, 5.5, "#FFFFFF", UPDATE, dashed=True, lw=1.6, pad=0.3)
    text(xx, 32.2, lab, size=10, bold=True, color=UPDATE)

# left -> bridge arrows
arrow((38, 70), (99, 95))          # replay -> encoder
arrow((80, 90), (99, 96))          # graph -> encoder
for sx in (22, 43.5, 65, 86):      # conditions -> dynamics
    arrow((sx, cy+8.5), (99, 64), rad=0.12)

# =====================================================================
# RIGHT container content
# =====================================================================
# imagination rollout lane
lane_y = 88
ax.plot([152, 222], [lane_y, lane_y], color=STICKER["road"], lw=3.4, zorder=3,
        solid_capstyle="round")
for xx, cc in ((162, STICKER["car"]), (180, STICKER["car2"]), (198, STICKER["car3"])):
    car(xx, lane_y+1.6, s=0.55, color=cc)
for xx in (170, 188, 206):
    arrow((xx, lane_y), (xx+6, lane_y), lw=1.6, ms=10)
# loop-back arrow (multi-step imagination)
arrow((222, lane_y-1.5), (152, lane_y-1.5), rad=0.35, color=DYN_BD, lw=1.8, dashed=True)
text(187, 95.5, "vehicle wrapper:  advance / depart / arrive", size=10, color=CAPTION)
text(187, 78.5, "imagined rollout  (Z_t → Ẑ_t+1 → …)", size=10.5, bold=True, color=DYN_BD)

# actor sticker
rbox(150, 52, 34, 18, "#FFFFFF", ORANGE, lw=2.0)
fork_road(158, 60, s=0.7, hl=2)
car(157.5, 64.5, s=0.45, color=STICKER["car"])
text(172, 65.5, "shared actor π_θ", size=11, bold=True)
text(172, 61.5, "masked route softmax", size=9, color=CAPTION)
text(172, 57.8, "per-CAV candidate routes", size=9, color=CAPTION)

# critics
rbox(190, 60, 36, 12, "#FFFFFF", DEC_BD, lw=2.0)
text(208, 68.6, "per-vehicle critic", size=11, bold=True, color=DEC_BD)
text(208, 64.6, "attention over active CAVs", size=9, color=CAPTION)
rbox(190, 46, 36, 11, "#FFFFFF", TEAL, lw=2.0)
text(208, 53.6, "global critic", size=11, bold=True, color=TEAL)
text(208, 49.8, "network value  (z̄_t, c_t)", size=9, color=CAPTION)

# advantage tag
rbox(156, 30, 62, 9, "#FFFFFF", UPDATE, dashed=True, lw=1.8, pad=0.3)
text(187, 34.5, "A_actor = A_veh + α_g · A_global   →  PPO update", size=10.5,
     bold=True, color=UPDATE)

# right-side wiring
arrow((167, 52), (167, 44), color=UPDATE, dashed=True)          # actor <- adv
arrow((167, 44), (167, 40))
arrow((208, 46), (208, 40), color=UPDATE, dashed=True)          # critics -> adv
arrow((187, 84), (167, 71))                                      # lane -> actor
arrow((187, 84), (208, 72.5))                                    # lane -> critic

# bridge -> right container
arrow((140, 39), (160, 84), rad=-0.25, color=DEC_BD, lw=2.2)
text(146.5, 60, "v̂, n̂ → τ̂", size=9.5, color=DEC_BD)

# losses dashed arrows from bridge to loss tags (update flow)
arrow((100, 62), (73, 33.5), color=UPDATE, dashed=True, lw=1.5, rad=0.15)
arrow((100, 95), (42, 33.5), color=UPDATE, dashed=True, lw=1.5, rad=0.1)

plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
out = "figure/main_figure_draft.png"
plt.savefig(out, facecolor=BG)
print("saved", out)
