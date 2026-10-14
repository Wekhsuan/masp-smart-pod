# -*- coding: utf-8 -*-
"""
打印导出：高精度 STL（3 个打印件）+ 多组件 3MF（整机装配）
==========================================================
说明：气凝胶内胆为发泡灌注，不参与打印；但整机 3MF 参考件仍将其纳入。
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


# 网格精度：线性弦差 0.01mm + 角度容差 0.05 rad（高精度，足以满足 FDM/SLA）
TOL = 0.01
ANG_TOL = 0.05

# ----------------------------------------------------------------------
# 读取最终零件
# ----------------------------------------------------------------------
base = cq.importers.importStep(out("04_shock_base_plate_with_cross.step")).val()
shell = cq.importers.importStep(out("01_aero_shell_final.step")).val()
panel = cq.importers.importStep(out("05_smart_panel.step")).val()
core = cq.importers.importStep(out("03_thermal_core.step")).val()

# ----------------------------------------------------------------------
# 高精度 STL（3 个打印件）
# ----------------------------------------------------------------------
cq.exporters.export(base, out("print_part_base_plate.stl"), tolerance=TOL, angularTolerance=ANG_TOL)
cq.exporters.export(shell, out("print_part_aero_shell.stl"), tolerance=TOL, angularTolerance=ANG_TOL)
cq.exporters.export(panel, out("print_part_smart_panel.stl"), tolerance=TOL, angularTolerance=ANG_TOL)

# ----------------------------------------------------------------------
# 多组件 3MF（整机装配：外壳 / 内胆 / 面板上移 8mm 到底座顶面）
# ----------------------------------------------------------------------
BASE_T = 8.0
parts = [
    base,
    shell.translate(cq.Vector(0, 0, BASE_T)),
    core.translate(cq.Vector(0, 0, BASE_T)),
    panel.translate(cq.Vector(0, 0, BASE_T)),
]
compound = cq.Compound.makeCompound(parts)
cq.exporters.export(compound, out("advanced_pod_assembly_final.3mf"), tolerance=TOL, angularTolerance=ANG_TOL)

# ----------------------------------------------------------------------
# 回显
# ----------------------------------------------------------------------
for name in (
    "print_part_base_plate.stl",
    "print_part_aero_shell.stl",
    "print_part_smart_panel.stl",
    "advanced_pod_assembly_final.3mf",
):
    p = out(name)
    size = os.path.getsize(p) if os.path.exists(p) else 0
    print(f"  [{'OK' if size else 'MISSING'}] {p}  ({size} bytes)")
