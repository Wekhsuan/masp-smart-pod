# -*- coding: utf-8 -*-
"""
第四步：抠细节 —— 智能显控面板 与 散热百叶窗
============================================
零件：
  1) 05_smart_panel          智能显控屏幕（Y+ 面，微凹）
  2) 01_aero_shell_final     最终外壳（顶部快接槽 + 屏幕框/锁孔/指纹 + 百叶排风槽）
  3) 03_thermal_core         （复用）气凝胶内胆
  4) 04_shock_base_plate_with_cross（复用）底座
装配：
  advanced_pod_assembly_final.step / .glb
  （外壳深空灰半透明、面板近黑、内胆亮白、底座哑光黑）
"""

import os
import cadquery as cq

# ----------------------------------------------------------------------
# 工作目录
# ----------------------------------------------------------------------
WORK = r"D:\保鲜箱_传输架\保鲜箱"
os.makedirs(WORK, exist_ok=True)


def out(name: str) -> str:
    return os.path.join(WORK, name)


# ----------------------------------------------------------------------
# 基础参数（单位：mm）
# ----------------------------------------------------------------------
SIDE = 85.0
CORNER_R = 20.0
BASE_T = 8.0
BOSS_R = 10.0
BOSS_H = 3.0
SHELL_H = 55.0
CHAMFER = 15.0
SHELL_WALL = 3.0
CORE_INSET = 4.0
CORE_WALL = 2.0
DOCK_R = 12.5
DOCK_DEPTH = 10.0
CROSS_LEN = 30.0
CROSS_W = 8.0

WALL_Y = SIDE / 2.0            # Y+ 外壁面 = 42.5
WALL_T = SHELL_WALL            # 壁厚 = 3

# 面板参数
PANEL_W = 40.0                 # 屏幕框宽
PANEL_H = 15.0                 # 屏幕框高
PANEL_D = 2.0                  # 屏幕框内凹深度
PANEL_Z = 24.0                 # 屏幕框中心高度
SCREEN_W = 38.0                # 屏幕宽
SCREEN_H = 13.0                # 屏幕高
SCREEN_T = 1.8                 # 屏幕厚度(Y)
SCREEN_RECESS = 0.2            # 屏幕表面微凹量
LOCK_R = 1.5                   # 锁孔半径(Φ3)
LOCK_X = -8.0
FP_LEN = 8.0                   # 指纹槽长
FP_W = 4.0                     # 指纹槽宽
FP_X = 8.0
FEATURE_Z = 11.0               # 锁孔/指纹中心高度

# 百叶参数
LOUVER_W = 30.0
LOUVER_H = 2.0
LOUVER_ANGLE = 30.0
LOUVER_N = 4
LOUVER_Z0 = 10.0
LOUVER_DZ = 8.0


def rounded_box(height):
    return (
        cq.Workplane("XY").rect(SIDE, SIDE).extrude(height).edges("|Z").fillet(CORNER_R)
    )


def aero_body(side, corner_r, height, chamfer):
    return (
        cq.Workplane("XY").rect(side, side).extrude(height)
        .edges("|Z").fillet(corner_r)
        .faces(">Z").edges().chamfer(chamfer)
    )


# ----------------------------------------------------------------------
# 外壳（含顶部快接槽，复用第三步）
# ----------------------------------------------------------------------
shell_hollow = aero_body(SIDE, CORNER_R, SHELL_H, CHAMFER).faces("<Z").shell(-SHELL_WALL)
cut_z = SHELL_H - DOCK_DEPTH
dock_cut = (
    cq.Workplane("XY", origin=(0, 0, cut_z)).circle(DOCK_R).extrude(DOCK_DEPTH + 2)
    .union(cq.Workplane("XY", origin=(0, 0, cut_z)).rect(CROSS_LEN, CROSS_W).extrude(DOCK_DEPTH + 2))
    .union(cq.Workplane("XY", origin=(0, 0, cut_z)).rect(CROSS_W, CROSS_LEN).extrude(DOCK_DEPTH + 2))
)
shell_with_dock = shell_hollow.cut(dock_cut)

# ----------------------------------------------------------------------
# 内胆 / 底座（复用）
# ----------------------------------------------------------------------
thermal_core = (
    aero_body(SIDE - 2 * CORE_INSET, CORNER_R - CORE_INSET, SHELL_H - CORE_INSET, CHAMFER)
    .faces("<Z").shell(-CORE_WALL)
)
base_with_cross = (
    rounded_box(BASE_T)
    .union(cq.Workplane("XY").circle(BOSS_R).extrude(-BOSS_H))
    .union(cq.Workplane("XY").rect(CROSS_LEN, CROSS_W).extrude(-BOSS_H))
    .union(cq.Workplane("XY").rect(CROSS_W, CROSS_LEN).extrude(-BOSS_H))
)

# ----------------------------------------------------------------------
# 侧面 A：屏幕框凹槽（Y+ 面，内凹 2mm）
# ----------------------------------------------------------------------
recess_cut = (
    cq.Workplane("XY")
    .box(PANEL_W, PANEL_D + 0.5, PANEL_H)
    .translate((0, WALL_Y - PANEL_D / 2 + 0.25, PANEL_Z))
)

# 屏幕（05_smart_panel，独立实体，表面微凹 0.2mm）
smart_panel = (
    cq.Workplane("XY")
    .box(SCREEN_W, SCREEN_T, SCREEN_H)
    .translate((0, WALL_Y - SCREEN_T / 2 - SCREEN_RECESS, PANEL_Z))
)

# 锁孔 + 指纹（Y+ 面，内凹 2mm）
lock_cut = (
    cq.Workplane("XZ").circle(LOCK_R).extrude(PANEL_D + 0.5)
    .translate((LOCK_X, WALL_Y - PANEL_D, FEATURE_Z))
)
fp_cut = (
    cq.Workplane("XZ").slot2D(FP_LEN, FP_W).extrude(PANEL_D + 0.5)
    .translate((FP_X, WALL_Y - PANEL_D, FEATURE_Z))
)

# ----------------------------------------------------------------------
# 侧面 B：散热百叶窗（Y- 面，4 道 30° 倾斜贯通槽）
# ----------------------------------------------------------------------
def louver_slot(z):
    return (
        cq.Workplane("XY")
        .box(LOUVER_W, WALL_T + 1, LOUVER_H)
        .rotate((0, 0, 0), (1, 0, 0), LOUVER_ANGLE)
        .translate((0, -WALL_Y, z))
    )


louver_cut = louver_slot(LOUVER_Z0)
for i in range(1, LOUVER_N):
    louver_cut = louver_cut.union(louver_slot(LOUVER_Z0 + i * LOUVER_DZ))

# ----------------------------------------------------------------------
# 最终外壳
# ----------------------------------------------------------------------
shell_final = shell_with_dock.cut(recess_cut).cut(lock_cut).cut(fp_cut).cut(louver_cut)

# ----------------------------------------------------------------------
# 导出零件
# ----------------------------------------------------------------------
cq.exporters.export(smart_panel.val(), out("05_smart_panel.step"))
cq.exporters.export(shell_final.val(), out("01_aero_shell_final.step"))

# ----------------------------------------------------------------------
# 终极装配
# ----------------------------------------------------------------------
assembly = cq.Assembly()
assembly.add(base_with_cross, name="04_shock_base_plate_with_cross",
             color=cq.Color(0.06, 0.06, 0.07))                       # 哑光黑
assembly.add(thermal_core, name="03_thermal_core",
             loc=cq.Location(cq.Vector(0, 0, BASE_T)),
             color=cq.Color(0.95, 0.95, 0.97))                       # 亮白
assembly.add(shell_final, name="01_aero_shell_final",
             loc=cq.Location(cq.Vector(0, 0, BASE_T)),
             color=cq.Color(0.25, 0.27, 0.31, 0.55))                 # 深空灰半透明
assembly.add(smart_panel, name="05_smart_panel",
             loc=cq.Location(cq.Vector(0, 0, BASE_T)),
             color=cq.Color(0.04, 0.05, 0.09))                       # 近黑（发光质感）

assembly.export(out("advanced_pod_assembly_final.step"))
assembly.export(out("advanced_pod_assembly_final.glb"), exportType="GLTF")

# ----------------------------------------------------------------------
# 自检
# ----------------------------------------------------------------------
def exact_bounds(shape):
    pts = [v.toTuple() for v in shape.Vertices()]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    zs = [p[2] for p in pts]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


for label, shp in (
    ("shell_final", shell_final.val()),
    ("base_with_cross", base_with_cross.val()),
    ("thermal_core", thermal_core.val()),
    ("smart_panel", smart_panel.val()),
):
    x0, x1, y0, y1, z0, z1 = exact_bounds(shp)
    print(f"  {label:16s} bbox: {x1 - x0:.3f} x {y1 - y0:.3f} x {z1 - z0:.3f} mm"
          f"  (z {z0:.2f} .. {z1:.2f})")

print(f"  solids: shell={len(shell_final.val().Solids())}"
      f" core={len(thermal_core.val().Solids())}"
      f" base={len(base_with_cross.val().Solids())}"
      f" panel={len(smart_panel.val().Solids())}")
print(f"  shell faces: {len(shell_final.val().Faces())}")

# 面板应恰好落入凹槽，不与外壳壁干涉
_inter = smart_panel.val().intersect(shell_final.val())
_iv = _inter.Volume() if len(_inter.Solids()) else 0.0
print(f"  panel ∩ shell volume: {_iv:.4f} mm^3 (expect 0)")

# 内胆仍无干涉
_inter2 = thermal_core.val().intersect(shell_final.val())
_iv2 = _inter2.Volume() if len(_inter2.Solids()) else 0.0
print(f"  core ∩ shell volume: {_iv2:.4f} mm^3 (expect 0)")

for name in (
    "05_smart_panel.step",
    "01_aero_shell_final.step",
    "advanced_pod_assembly_final.step",
    "advanced_pod_assembly_final.glb",
):
    p = out(name)
    size = os.path.getsize(p) if os.path.exists(p) else 0
    print(f"  [{'OK' if size else 'MISSING'}] {p}  ({size} bytes)")
