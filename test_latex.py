"""
测试 LaTeX 公式渲染功能
"""
import os
from services.latex_renderer import latex_renderer

# 测试公式列表
test_formulas = [
    r"x^2 + y^2 = r^2",
    r"\frac{a}{b} + \frac{c}{d}",
    r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}",
    r"\int_{0}^{1} x^2 dx = \frac{1}{3}",
    r"E = mc^2",
    r"\alpha + \beta = \gamma",
    r"\sqrt{x^2 + y^2}",
    r"\lim_{x \to 0} \frac{\sin x}{x} = 1",
]

print("开始测试 LaTeX 公式渲染...\n")

for i, formula in enumerate(test_formulas, 1):
    print(f"测试 {i}: {formula}")
    try:
        img_path = latex_renderer.render_to_image(formula)
        if os.path.exists(img_path):
            print(f"  ✓ 渲染成功: {img_path}")
        else:
            print(f"  ✗ 文件未生成")
    except Exception as e:
        print(f"  ✗ 渲染失败: {e}")
    print()

print("测试完成!")
