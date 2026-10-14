# -*- coding: utf-8 -*-
"""
第二步：做内腔 —— 外壳抽壳 与 独立气凝胶内胆
================================================
零件：
  1) 01_aero_shell_hollow  空心气动外壳（壁厚 3mm，底面开口）
  2) 03_thermal_core       气凝胶恒温内胆（单边比内腔小 1mm 公差，壁厚 2mm，底面开口）
装配：
  step2_assembly.step / step2_preview.glb
  （外壳半透明深灰、内胆亮白、底座黑色）
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
# 公共参数（单位：mm）
# ----------------------------------------------------------------------
SIDE = 85.0        # 方形边长
CORNER_R = 20.0    # 四角大圆角半径
BASE_T = 8.0       # 底座主体厚度
BOSS_R = 10.0      # 底部定位凸台半径
BOSS_H = 3.0       # 底部定位凸台高度
SHELL_H = 55.0     # 外壳总高度
CHAMFER = 15.0     # 顶部倒角深度
SHELL_WALL = 3.0   # 外壳抽壳壁厚
CORE_INSET = 4.0   # 内胆相对外壳轮廓的单边内缩量（3 壁厚 + 1 公差）
CORE_WALL = 2.0    # 内胆抽壳壁厚


def rounded_box(height):
    """85mm 方 + R20 圆角柱（底座复用）。"""
    return (
        cq.Workplane("XY")
        .rect(SIDE, SIDE)
        .extrude(height)
        .edges("|Z")
        .fillet(CORNER_R)
    )


def aero_body(side, corner_r, height, chamfer):
    """带顶部倒角的圆角方柱（科幻多边形流线体）。"""
    return (
        cq.Workplane("XY")
        .rect(side, side)
        .extrude(height)
        .edges("|Z")
        .fillet(corner_r)
        .faces(">Z")
        .edges()
        .chamfer(chamfer)
    )


# ----------------------------------------------------------------------
# 底座（复用第一步，仅用于装配）
# ----------------------------------------------------------------------
base = (
    rounded_box(BASE_T)
    .faces("<Z").workplane().circle(BOSS_R).extrude(BOSS_H)
)

# ----------------------------------------------------------------------
# 1) 空心外壳：向内抽壳 3mm，底面开口（扣下来的倒多边形罩子）
#    注意：CadQuery 2.x 的 shell() 中，负厚度 = 向内抽壳，正厚度 = 向外增厚。
# ----------------------------------------------------------------------
shell_hollow = aero_body(SIDE, CORNER_R, SHELL_H, CHAMFER).faces("<Z").shell(-SHELL_WALL)

# ----------------------------------------------------------------------
# 2) 气凝胶内胆：单边内缩 4mm（=3 壁厚 + 1 公差），高度 -4，向内抽壳 2mm 底面开口
# ----------------------------------------------------------------------
core_side = SIDE - 2 * CORE_INSET      # 85 - 8 = 77
core_r = CORNER_R - CORE_INSET         # 20 - 4 = 16
core_h = SHELL_H - CORE_INSET          # 55 - 4 = 51
thermal_core = aero_body(core_side, core_r, core_h, CHAMFER).faces("<Z").shell(-CORE_WALL)

# ----------------------------------------------------------------------
# 导出单个零件 STEP
# ----------------------------------------------------------------------
cq.exporters.export(shell_hollow.val(), out("01_aero_shell_hollow.step"))
cq.exporters.export(thermal_core.val(), out("03_thermal_core.step"))

# ----------------------------------------------------------------------
# 装配：外壳底部 = 内胆底部 = 底座顶面（z = 8）
# ----------------------------------------------------------------------
assembly = cq.Assembly()
assembly.add(base, name="04_shock_base_plate", color=cq.Color(0.05, 0.05, 0.06))
assembly.add(
    shell_hollow, name="01_aero_shell_hollow",
    loc=cq.Location(cq.Vector(0, 0, BASE_T)),
    color=cq.Color(0.30, 0.32, 0.36, 0.45),   # 半透明深空灰
)
assembly.add(
    thermal_core, name="03_thermal_core",
    loc=cq.Location(cq.Vector(0, 0, BASE_T)),
    color=cq.Color(0.95, 0.95, 0.97),          # 亮白
)

assembly.export(out("step2_assembly.step"))
assembly.export(out("step2_preview.glb"), exportType="GLTF")

# ----------------------------------------------------------------------
# 自检：精确边界 / 干涉 / 文件
# ----------------------------------------------------------------------
def exact_bounds(shape):
    pts = [v.toTuple() for v in shape.Vertices()]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    zs = [p[2] for p in pts]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


for label, shp in (
    ("base", base.val()),
    ("shell_hollow", shell_hollow.val()),
    ("thermal_core", thermal_core.val()),
):
    x0, x1, y0, y1, z0, z1 = exact_bounds(shp)
    print(f"  {label:13s} bbox: {x1 - x0:.3f} x {y1 - y0:.3f} x {z1 - z0:.3f} mm"
          f"  (z {z0:.2f} .. {z1:.2f})")

print(f"  solids: shell={len(shell_hollow.val().Solids())}"
      f" core={len(thermal_core.val().Solids())}"
      f" base={len(base.val().Solids())}")

# 干涉校验：内胆与外壳壁的公共体积应约为 0（即内胆确实塞进了内腔、互不干涉）
_inter = thermal_core.val().intersect(shell_hollow.val())
_iv = _inter.Volume() if len(_inter.Solids()) else 0.0
print(f"  interference (core ∩ shell): {_iv:.4f} mm^3  (expect 0)")

for name in (
    "01_aero_shell_hollow.step",
    "03_thermal_core.step",
    "step2_assembly.step",
    "step2_preview.glb",
):
    p = out(name)
    size = os.path.getsize(p) if os.path.exists(p) else 0
    print(f"  [{'OK' if size else 'MISSING'}] {p}  ({size} bytes)")
