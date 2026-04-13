"""
LaTeX 图片渲染服务
使用 matplotlib.mathtext 将 LaTeX 公式渲染为 PNG 图片
"""

import hashlib
import os
from functools import lru_cache
from pathlib import Path
from io import BytesIO

from matplotlib import font_manager
from matplotlib.mathtext import MathTextParser
from matplotlib.pyplot import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

from utils.config import TEMP_DIR


# 全局 MathTextParser 实例
_parser: MathTextParser | None = None


def _get_parser() -> MathTextParser:
    """获取或创建 MathTextParser 单例"""
    global _parser
    if _parser is None:
        _parser = MathTextParser('path')
    return _parser


def _get_cache_dir() -> Path:
    """获取 LaTeX 缓存目录"""
    cache_dir = TEMP_DIR / "latex_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _tex_to_image(tex_string: str, dpi: int = 200) -> tuple[bytes, int, int]:
    """
    将 LaTeX 公式渲染为 PNG 图片

    Args:
        tex_string: LaTeX 公式字符串（不含 $ 符号）
        dpi: 渲染分辨率

    Returns:
        (png_bytes, width_pixels, height_pixels)
    """
    parser = _get_parser()

    # 创建 Figure 和 Canvas
    fig = Figure(facecolor='none', edgecolor='none', figsize=(1, 1))
    canvas = FigureCanvasAgg(fig)

    # 解析 LaTeX 并获取 offset
    prop = font_manager.FontProperties(size=14)
    pixel_metrics = parser.parse(tex_string, dpi=dpi, prop=prop)

    # 计算需要的 figure 大小
    width_inches = pixel_metrics.width / dpi
    height_inches = pixel_metrics.height / dpi

    # 设置 figure 大小（加一点 padding）
    fig.set_size_inches(width_inches * 1.1, height_inches * 1.1)

    # 重新解析并绘制
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    # 用 $ 包裹公式字符串以启用 mathtext 数学模式渲染
    math_text = f'${tex_string}$'
    ax.text(0, 0, math_text, fontproperties=prop, ha='left', va='bottom',
            color='black')

    # 渲染到 BytesIO
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, facecolor='none',
                edgecolor='none', bbox_inches='tight', pad_inches=0.05)
    buf.seek(0)
    png_bytes = buf.read()

    width = int(width_inches * dpi)
    height = int(height_inches * dpi)

    return png_bytes, width, height


def _preprocess_latex(tex_string: str) -> str:
    """
    预处理 LaTeX 字符串，将 matplotlib.mathtext 不支持的写法转换为兼容写法
    """
    import re

    # 修复被转义的大括号：\{ -> {  和  \} -> }
    # 这类问题常见于 AI 输出时被错误转义
    tex_string = tex_string.replace(r'\{', '{')
    tex_string = tex_string.replace(r'\}', '}')
    tex_string = tex_string.replace(r'\left\{', '{')
    tex_string = tex_string.replace(r'\right\{', '}')
    tex_string = tex_string.replace(r'\left\[', '[')
    tex_string = tex_string.replace(r'\right\[', ']')

    # 导数算子转换
    # \frac{d}{dx}f(x) -> d/dx f(x)
    tex_string = re.sub(
        r'\\frac\{\\frac\{d\}\{dx\}\}\{([^}]+)\}',
        r'd/dx \1',
        tex_string
    )

    # \frac{d}{dx} -> d/dx
    tex_string = re.sub(
        r'\\frac\{d\}\{dx\}',
        r'd/dx',
        tex_string
    )

    # 偏导数 \frac{\partial}{\partial x} -> ∂/∂x
    tex_string = re.sub(
        r'\\frac\{\\partial\}\{\\partial\s*([a-zA-Z])\}',
        r'∂/∂\1',
        tex_string
    )

    # \frac{\partial f}{\partial x} -> ∂f/∂x
    tex_string = re.sub(
        r'\\frac\{\\partial\s*([a-zA-Z])\}\{\\partial\s*([a-zA-Z])\}',
        r'∂\1/∂\2',
        tex_string
    )

    # 清理多余的空白
    tex_string = re.sub(r'\s+', ' ', tex_string)

    return tex_string


@lru_cache(maxsize=512)
def _render_latex_cached(tex_string: str) -> str:
    """
    缓存版本的 LaTeX 渲染（对外暴露的接口）

    Args:
        tex_string: LaTeX 公式字符串（不含 $ 符号）

    Returns:
        渲染后的 PNG 图片路径
    """
    # 预处理，转换不兼容的写法
    tex_string = _preprocess_latex(tex_string)

    # 生成唯一文件名
    key = hashlib.md5(tex_string.encode('utf-8')).hexdigest()
    cache_dir = _get_cache_dir()
    output_path = cache_dir / f"latex_{key}.png"

    if output_path.exists():
        return str(output_path)

    # 渲染
    png_bytes, _, _ = _tex_to_image(tex_string, dpi=200)

    # 保存到文件
    with open(output_path, 'wb') as f:
        f.write(png_bytes)

    return str(output_path)


class LatexRenderer:
    """
    LaTeX 图片渲染器
    支持将文本中的 $...$ LaTeX 表达式渲染为图片
    """

    def __init__(self):
        self.parser = _get_parser()

    def render_to_image(self, tex_string: str) -> str:
        """
        渲染单个 LaTeX 公式为图片

        Args:
            tex_string: LaTeX 公式（不含 $ 符号）

        Returns:
            PNG 图片路径
        """
        # 清理空白
        tex_string = tex_string.strip()
        return _render_latex_cached(tex_string)

    def render_text_with_latex(self, text: str) -> list[tuple[str, str | None]]:
        """
        解析文本，将 LaTeX 表达式渲染为图片

        Args:
            text: 包含 $...$ LaTeX 表达式的文本

        Returns:
            List of (text_content, image_path or None)
            混合文本被拆分成普通文本片段和 LaTeX 图片片段
        """
        import re

        # 匹配 $...$ 包裹的 LaTeX（支持转义）
        pattern = re.compile(r'(?<!\\)\$(.*?)(?<!\\)\$|\\\$')

        result = []
        last_end = 0

        for match in pattern.finditer(text):
            # 匹配到的起始位置
            start = match.start()

            # 处理匹配之前的普通文本
            if start > last_end:
                plain_text = text[last_end:start]
                result.append((plain_text, None))

            # 匹配的 LaTeX 内容
            latex_content = match.group(1)

            if latex_content is None:
                # 这是转义的 \$，当作普通文本
                result.append(('$', None))
            else:
                # 渲染 LaTeX
                image_path = self.render_to_image(latex_content)
                result.append((latex_content, image_path))

            last_end = match.end()

        # 处理最后剩余的普通文本
        if last_end < len(text):
            result.append((text[last_end:], None))

        return result


# 全局单例
latex_renderer = LatexRenderer()
