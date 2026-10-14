# -*- coding: utf-8 -*-
"""
第一步：打地基 —— 减震对接底座 与 气动导流外壳初胚
====================================================

零件：
  1) 04_shock_base_plate  减震底座（边长85mm 方 + R20 四角圆角 + 底部定位凸台）
  2) 01_aero_shell        气动导流外壳主体（实心初胚，顶部 15mm 深度倒角）

装配：
  step1_assembly.step / step1_preview.glb（外壳深空灰、底座黑色）

依赖：cadquery（建议 2.2+）
"""

import math
import os
import cadquery as cq

# ----------------------------------------------------------------------
# 工作目录（若不存在则自动创建）
# ----------------------------------------------------------------------
WORK = r"D:\保鲜箱_传输架\保鲜箱"
os.makedirs(WORK, exist_ok=True)


def out(name: str) -> str:
    return os.path.join(WORK, name)


# ----------------------------------------------------------------------
# 公共参数（单位：mm）
# ----------------------------------------------------------------------
SIDE = 85.0        # 方形边长
CORNER_R = 20.0    # 四角大圆角半径（外接圆半径约 60mm，可嵌入内缘 62.5mm 转盘护栏）
BASE_T = 8.0       # 底座主体厚度
BOSS_R = 10.0      # 底部定位凸台半径
BOSS_H = 3.0       # 底部定位凸台高度
SHELL_H = 55.0     # 外壳向上拉伸总高度
CHAMFER = 15.0     # 顶部倒角深度


def rounded_box(height):
    """公共轮廓体：边长 85mm 方形拉伸，四角 R20 大圆角（沿竖直棱倒圆角）。"""
    return (
        cq.Workplane("XY")
        .rect(SIDE, SIDE)
        .extrude(height)
        .edges("|Z")
        .fillet(CORNER_R)
    )


# ----------------------------------------------------------------------
# 1) 04_shock_base_plate —— 减震底座
# ----------------------------------------------------------------------
base = (
    rounded_box(BASE_T)                   # 主体厚 8mm（z = 0 .. 8），四角 R20
    .faces("<Z")                          # 选底面
    .workplane()                          # 在底面建立工作面（法向朝下）
    .circle(BOSS_R)                       # 底面正中心，半径 10
    .extrude(BOSS_H)                      # 向下凸出 3mm（z = -3 .. 0）
)

# ----------------------------------------------------------------------
# 2) 01_aero_shell —— 气动导流外壳主体（实心初胚）
# ----------------------------------------------------------------------
shell = (
    rounded_box(SHELL_H)                  # 向上拉伸 55mm（z = 0 .. 55），四角 R20
    .faces(">Z")                          # 选顶面
    .edges()                              # 顶面边界（直边 + 圆弧边）
    .chamfer(CHAMFER)                     # 顶部 15mm 深度倒角 → 多边形流线体
)

# ----------------------------------------------------------------------
# 导出单个零件 STEP
# ----------------------------------------------------------------------
cq.exporters.export(base.val(), out("04_shock_base_plate.step"))
cq.exporters.export(shell.val(), out("01_aero_shell.step"))

# ----------------------------------------------------------------------
# 初步装配：外壳底部与底座顶部重合（外壳上移 8mm）
# ----------------------------------------------------------------------
assembly = cq.Assembly()
assembly.add(
    base,
    name="04_shock_base_plate",
    color=cq.Color(0.05, 0.05, 0.06),      # 黑色
)
assembly.add(
    shell,
    name="01_aero_shell",
    loc=cq.Location(cq.Vector(0, 0, BASE_T)),  # 底座顶面位于 z=8
    color=cq.Color(0.27, 0.28, 0.31),      # 深空灰
)

assembly.export(out("step1_assembly.step"))
assembly.export(out("step1_preview.glb"), exportType="GLTF")

# ----------------------------------------------------------------------
# 几何自检（精确顶点边界 + 凸台校验）
#   底座：85 x 85 x 11（8 主体 + 3 凸台，z = -3 .. 8）
#   外壳：85 x 85 x 55（z = 0 .. 55）
# ----------------------------------------------------------------------
def _exact_bounds(shape):
    pts = [v.toTuple() for v in shape.Vertices()]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    zs = [p[2] for p in pts]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


for _label, _shape in (("base", base.val()), ("shell", shell.val())):
    x0, x1, y0, y1, z0, z1 = _exact_bounds(_shape)
    print(f"  {_label:5s} bbox: {x1 - x0:.3f} x {y1 - y0:.3f} x {z1 - z0:.3f} mm"
          f"  (z {z0:.2f} .. {z1:.2f})")

_boss = [f for f in base.val().Faces()
         if abs(f.Center().z - (-BOSS_H)) < 0.01]
if _boss:
    _b = _boss[0]
    print(f"  boss  bottom: area {_b.Area():.2f} mm^2 (expect {math.pi * BOSS_R ** 2:.2f}),"
          f" center ({_b.Center().x:.2f}, {_b.Center().y:.2f}, {_b.Center().z:.2f})")

# ----------------------------------------------------------------------
# 结果回显
# ----------------------------------------------------------------------
for name in (
    "04_shock_base_plate.step",
    "01_aero_shell.step",
    "step1_assembly.step",
    "step1_preview.glb",
):
    p = out(name)
    size = os.path.getsize(p) if os.path.exists(p) else 0
    print(f"  [{'OK' if size else 'MISSING'}] {p}  ({size} bytes)")
