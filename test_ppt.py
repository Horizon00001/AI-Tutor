"""
测试 PPT 生成功能，包含公式
"""
from pathlib import Path
from services.ppt_generator import ppt_generator

# 测试题目数据（包含各种公式）
test_questions = [
    {
        "content": "若圆的方程为 $x^2 + y^2 = r^2$，则圆的面积为多少？",
        "source": "数学测试卷",
        "answer": "A",
        "analysis": "圆的面积公式为 $S = \\pi r^2$，根据圆的方程 $x^2 + y^2 = r^2$ 可知半径为 $r$，因此面积为 $\\pi r^2$。"
    },
    {
        "content": "计算定积分 $\\int_{0}^{1} x^2 dx$ 的值。\nA) $\\frac{1}{2}$\nB) $\\frac{1}{3}$\nC) $\\frac{1}{4}$\nD) $1$",
        "source": "数学测试卷",
        "answer": "B",
        "analysis": "根据积分公式 $\\int x^n dx = \\frac{x^{n+1}}{n+1} + C$，有 $\\int_{0}^{1} x^2 dx = \\left[\\frac{x^3}{3}\\right]_{0}^{1} = \\frac{1}{3} - 0 = \\frac{1}{3}$。"
    },
    {
        "content": "已知 $\\alpha + \\beta = \\pi$，求 $\\sin \\alpha + \\sin \\beta$ 的最大值。",
        "source": "数学测试卷",
        "answer": "C",
        "analysis": "利用和差化积公式：$\\sin \\alpha + \\sin \\beta = 2\\sin\\frac{\\alpha+\\beta}{2}\\cos\\frac{\\alpha-\\beta}{2} = 2\\sin\\frac{\\pi}{2}\\cos\\frac{\\alpha-\\beta}{2} = 2\\cos\\frac{\\alpha-\\beta}{2}$，最大值为 $2$。"
    },
    {
        "content": "求极限 $\\lim_{x \\to 0} \\frac{\\sin x}{x}$ 的值。\nA) $0$\nB) $1$\nC) $\\infty$\nD) 不存在",
        "source": "数学测试卷",
        "answer": "B",
        "analysis": "这是重要的极限公式，$\\lim_{x \\to 0} \\frac{\\sin x}{x} = 1$。可以用洛必达法则或泰勒展开证明。"
    },
    {
        "content": "计算 $\\sum_{i=1}^{n} i$ 的和。",
        "source": "数学测试卷",
        "answer": "D",
        "analysis": "等差数列求和公式：$\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$。可以用数学归纳法证明。"
    }
]

output_path = Path("test_output_公式测试.pptx")

print("开始生成 PPT...")
print(f"共 {len(test_questions)} 道题目\n")

try:
    result_path = ppt_generator.generate(
        questions=test_questions,
        output_path=output_path,
        title="公式渲染测试",
        use_animation=False  # 禁用动画，加快生成速度
    )
    print(f"✓ PPT 生成成功！")
    print(f"  文件路径: {result_path.absolute()}")
    print(f"  文件大小: {result_path.stat().st_size / 1024:.1f} KB")
except Exception as e:
    print(f"✗ 生成失败: {e}")
    import traceback
    traceback.print_exc()
