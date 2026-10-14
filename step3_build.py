# -*- coding: utf-8 -*-
"""
第三步：加接口 —— 顶部无人机抓取槽 与 底部防呆定位卡槽
====================================================
零件：
  1) 01_aero_shell_with_dock        空心外壳 + 顶部 Φ25×10mm 圆孔 + 十字快接槽
  2) 04_shock_base_plate_with_cross 底座 + 底部十字防呆凸起（30×8，向下 3mm）
  3) 03_thermal_core                （复用第二步）气凝胶内胆
装配：
  step3_assembly.step / step3_preview.glb
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
SIDE = 85.0
CORNER_R = 20.0
BASE_T = 8.0
BOSS_R = 10.0        # 底部中心凸台半径（Φ10）
BOSS_H = 3.0         # 底部凸台高度
SHELL_H = 55.0
CHAMFER = 15.0
SHELL_WALL = 3.0
CORE_INSET = 4.0
CORE_WALL = 2.0
DOCK_R = 12.5        # 顶部接口槽半径（Φ25）
DOCK_DEPTH = 10.0    # 顶部接口槽深度
CROSS_LEN = 30.0     # 十字长
CROSS_W = 8.0        # 十字宽


def rounded_box(height):
    """85mm 方 + R20 圆角柱。"""
    return (
        cq.Workplane("XY")
        .rect(SIDE, SIDE)
        .extrude(height)
        .edges("|Z")
        .fillet(CORNER_R)
    )


def aero_body(side, corner_r, height, chamfer):
    """带顶部倒角的圆角方柱。"""
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
# 空心外壳 + 气凝胶内胆（复用第二步，负厚度=向内抽壳）
# ----------------------------------------------------------------------
shell_hollow = aero_body(SIDE, CORNER_R, SHELL_H, CHAMFER).faces("<Z").shell(-SHELL_WALL)
thermal_core = (
    aero_body(SIDE - 2 * CORE_INSET, CORNER_R - CORE_INSET, SHELL_H - CORE_INSET, CHAMFER)
    .faces("<Z").shell(-CORE_WALL)
)

# ----------------------------------------------------------------------
# 底座 + 底部十字防呆凸起（中心 Φ10 凸台 + 30×8 十字臂，均向下 3mm）
# ----------------------------------------------------------------------
base_plate = rounded_box(BASE_T)                                   # z = 0 .. 8
boss = cq.Workplane("XY").circle(BOSS_R).extrude(-BOSS_H)          # Φ10 中心凸台 z = -3 .. 0
bar_x = cq.Workplane("XY").rect(CROSS_LEN, CROSS_W).extrude(-BOSS_H)
bar_y = cq.Workplane("XY").rect(CROSS_W, CROSS_LEN).extrude(-BOSS_H)
base_with_cross = base_plate.union(boss).union(bar_x).union(bar_y)

# ----------------------------------------------------------------------
# 顶部接口槽：Φ25 圆孔 + 十字叠加切除（从 z=55 向下 10mm）
# ----------------------------------------------------------------------
cut_z = SHELL_H - DOCK_DEPTH                                       # z = 45
cut_cylinder = cq.Workplane("XY", origin=(0, 0, cut_z)).circle(DOCK_R).extrude(DOCK_DEPTH + 2)
cut_cross = (
    cq.Workplane("XY", origin=(0, 0, cut_z)).rect(CROSS_LEN, CROSS_W).extrude(DOCK_DEPTH + 2)
    .union(cq.Workplane("XY", origin=(0, 0, cut_z)).rect(CROSS_W, CROSS_LEN).extrude(DOCK_DEPTH + 2))
)
cut_tool = cut_cylinder.union(cut_cross)
shell_with_dock = shell_hollow.cut(cut_tool)

# ----------------------------------------------------------------------
# 导出零件
# ----------------------------------------------------------------------
cq.exporters.export(shell_with_dock.val(), out("01_aero_shell_with_dock.step"))
cq.exporters.export(base_with_cross.val(), out("04_shock_base_plate_with_cross.step"))

# ----------------------------------------------------------------------
# 装配：原点对齐（外壳底 = 内胆底 = 底座顶面 z=8）
# ----------------------------------------------------------------------
assembly = cq.Assembly()
assembly.add(base_with_cross, name="04_shock_base_plate_with_cross",
             color=cq.Color(0.05, 0.05, 0.06))                     # 黑色
assembly.add(shell_with_dock, name="01_aero_shell_with_dock",
             loc=cq.Location(cq.Vector(0, 0, BASE_T)),
             color=cq.Color(0.30, 0.32, 0.36, 0.45))               # 半透明深空灰
assembly.add(thermal_core, name="03_thermal_core",
             loc=cq.Location(cq.Vector(0, 0, BASE_T)),
             color=cq.Color(0.95, 0.95, 0.97))                     # 亮白

assembly.export(out("step3_assembly.step"))
assembly.export(out("step3_preview.glb"), exportType="GLTF")

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
    ("base_with_cross", base_with_cross.val()),
    ("shell_with_dock", shell_with_dock.val()),
    ("thermal_core", thermal_core.val()),
):
    x0, x1, y0, y1, z0, z1 = exact_bounds(shp)
    print(f"  {label:16s} bbox: {x1 - x0:.3f} x {y1 - y0:.3f} x {z1 - z0:.3f} mm"
          f"  (z {z0:.2f} .. {z1:.2f})")

# 内胆仍应无干涉塞进外壳
_inter = thermal_core.val().intersect(shell_with_dock.val())
_iv = _inter.Volume() if len(_inter.Solids()) else 0.0
print(f"  interference (core ∩ shell): {_iv:.4f} mm^3  (expect 0)")

# 底部十字校验：最低处(z=-3)顶点应铺满 ±15mm（十字 30mm 长）
_pts = [v.toTuple() for v in base_with_cross.val().Vertices()]
_minz = min(p[2] for p in _pts)
_bp = [p for p in _pts if abs(p[2] - _minz) < 0.01]
_bx = [p[0] for p in _bp]
_by = [p[1] for p in _bp]
print(f"  base cross span: x {min(_bx):.2f}..{max(_bx):.2f}  y {min(_by):.2f}..{max(_by):.2f}  (expect ±15)")

# 顶部开槽校验：顶面(z=55)面积应因开槽而减小
_top_before = [f for f in shell_hollow.val().Faces() if f.Center().z > 54]
_top_after = [f for f in shell_with_dock.val().Faces() if f.Center().z > 54]
if _top_before and _top_after:
    print(f"  top face area: {_top_before[0].Area():.2f} -> {_top_after[0].Area():.2f} mm^2")

for name in (
    "01_aero_shell_with_dock.step",
    "04_shock_base_plate_with_cross.step",
    "step3_assembly.step",
    "step3_preview.glb",
):
    p = out(name)
    size = os.path.getsize(p) if os.path.exists(p) else 0
    print(f"  [{'OK' if size else 'MISSING'}] {p}  ({size} bytes)")
