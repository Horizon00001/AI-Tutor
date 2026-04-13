import json
import re
import os
from pathlib import Path
from typing import Literal
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree

try:
    import win32com.client
    HAS_WIN32COM = True
except ImportError:
    HAS_WIN32COM = False

from services.latex_renderer import latex_renderer

LATEX_MAP = {
    '\\lceil': '⌈', '\\rceil': '⌉', '\\lfloor': '⌊', '\\rfloor': '⌋',
    '\\log': 'log', '\\infty': '∞', '\\pi': 'π', '\\times': '×',
    '\\div': '÷', '\\leq': '≤', '\\geq': '≥', '\\neq': '≠',
    '\\approx': '≈', '\\pm': '±', '\\cdot': '·', '\\{': '{', '\\}': '}',
    '\\alpha': 'α', '\\beta': 'β', '\\gamma': 'γ', '\\delta': 'δ',
    '\\epsilon': 'ε', '\\theta': 'θ', '\\lambda': 'λ', '\\mu': 'μ',
    '\\sigma': 'σ', '\\omega': 'ω', '\\Delta': 'Δ', '\\Sigma': 'Σ',
    '\\Omega': 'Ω', '\\rightarrow': '→', '\\leftarrow': '←',
    '\\Rightarrow': '⇒', '\\Leftarrow': '⇐', '\\Leftrightarrow': '⇔',
    '\\equiv': '≡', '\\sim': '∼', '\\propto': '∝', '\\subset': '⊂',
    '\\supset': '⊃', '\\in': '∈', '\\ni': '∋', '\\notin': '∉',
    '\\cup': '∪', '\\cap': '∩', '\\emptyset': '∅', '\\forall': '∀',
    '\\exists': '∃', '\\nabla': '∇', '\\partial': '∂', '\\sum': '∑',
    '\\prod': '∏', '\\int': '∫', '\\oint': '∮', '\\sqrt': '√',
    '\\angle': '∠', '\\circ': '∘', '\\bullet': '∙', '\\ast': '∗'
}


class PPTGenerator:
    def __init__(self):
        self.latex_map = LATEX_MAP

    def clean_latex(self, text: str) -> str:
        for k, v in self.latex_map.items():
            text = text.replace(k, v)
        return text

    def contains_latex(self, text: str) -> bool:
        """检测文本是否包含 LaTeX 公式（$...$ 包裹）"""
        return '$' in text

    def parse_latex_segments(self, text: str) -> list[tuple[Literal['text', 'latex'], str]]:
        """
        解析文本为片段列表

        Returns:
            [('text', '普通文本'), ('latex', '公式内容'), ...]
        """
        segments = []
        # 转义 \$ 情况先处理
        text = text.replace('\\$', '\x00')

        # 匹配 $...$ 包裹的 LaTeX
        pattern = re.compile(r'\$([^\$]+)\$')
        last_end = 0

        for match in pattern.finditer(text):
            start = match.start()
            if start > last_end:
                plain = text[last_end:start].replace('\x00', '$')
                if plain:
                    segments.append(('text', plain))

            latex_content = match.group(1)
            segments.append(('latex', latex_content))
            last_end = match.end()

        if last_end < len(text):
            plain = text[last_end:].replace('\x00', '$')
            if plain:
                segments.append(('text', plain))

        return segments

    def add_mixed_content_to_slide(
        self,
        slide,
        segments: list[tuple[Literal['text', 'latex'], str]],
        x: Inches,
        y: Inches,
        width: Inches,
        height: Inches,
        font_size: int = 20,
        font_bold: bool = False,
    ) -> int:
        """
        向 slide 添加混合内容（文本 + LaTeX 图片）

        Returns:
            使用的 y 位置（用于连续添加内容）
        """
        from PIL import Image as PILImage

        current_y = y
        line_height = Inches(0.35)
        # 根据字体大小自适应公式图片高度
        # 基准：20pt 字体对应 0.5 英寸高度，按比例缩放
        base_font_size = 20
        base_img_height = Inches(0.5)
        max_img_height = base_img_height * (font_size / base_font_size) * 1.2  # 1.2 倍系数确保公式不会太小
        max_img_width = width  # 图片最大宽度不超过文本区域

        for seg_type, seg_content in segments:
            if seg_type == 'text':
                # 清理 LaTeX 字符映射
                clean_text = self.clean_latex(seg_content)

                # 添加文本框
                text_box = slide.shapes.add_textbox(x, current_y, width, Inches(0.5))
                tf = text_box.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                p.text = clean_text
                p.font.size = Pt(font_size)
                p.font.bold = font_bold
                p.font.name = 'Microsoft YaHei'
                p.alignment = PP_ALIGN.LEFT

                current_y += line_height

            else:  # latex
                # 渲染 LaTeX 为图片
                img_path = latex_renderer.render_to_image(seg_content)

                # 获取图片原始尺寸，保持宽高比
                with PILImage.open(img_path) as img:
                    img_w, img_h = img.size

                # 计算缩放后的尺寸（保持宽高比）
                aspect_ratio = img_w / img_h
                # 根据字体大小计算合适的显示宽度
                display_width = min(max_img_width, Inches(6.0))  # 最大 6 英寸
                display_height = display_width / aspect_ratio

                # 如果计算的高度超过最大高度，则按高度缩放
                if display_height > max_img_height:
                    display_height = max_img_height
                    display_width = display_height * aspect_ratio

                # 如果宽度超过最大宽度，则按宽度缩放
                if display_width > max_img_width:
                    display_width = max_img_width
                    display_height = display_width / aspect_ratio

                # 添加图片到幻灯片
                pic = slide.shapes.add_picture(img_path, x, current_y, width=display_width)
                current_y += display_height + Inches(0.1)

        return current_y

    def add_math_text(self, paragraph, text: str):
        """保留原有方法用于简单文本（无 $...$）"""
        text = text.replace('$$', '$')
        parts = re.split(r'\$(.*?)\$', text)
        for i, part in enumerate(parts):
            if not part:
                continue
            run = paragraph.add_run()
            if i % 2 == 1:
                # 如果包含复杂 LaTeX，使用清理后的简单版本
                run.text = self.clean_latex(part)
                run.font.name = 'Cambria Math'
                run.font.italic = True
            else:
                run.text = self.clean_latex(part)
                run.font.name = 'Microsoft YaHei'

    def parse_options(self, content: str) -> list:
        option_pattern = re.compile(r'^\s*([A-D])[)）\.\]]\s*(.*)$', re.MULTILINE)
        matches = option_pattern.findall(content)
        options = []
        if matches:
            for letter, text in matches:
                options.append((letter, text.strip()))
        return options

    def create_title_slide(self, prs, main_title: str, subtitle_text: str):
        slide_layout = prs.slide_layouts[6]
        slide = prs.slides.add_slide(slide_layout)

        title_box = slide.shapes.add_textbox(Inches(0), Inches(2.5), prs.slide_width, Inches(1.2))
        p = title_box.text_frame.paragraphs[0]
        p.text = main_title
        p.font.size = Pt(54)
        p.font.bold = True
        p.font.name = 'Microsoft YaHei'
        p.font.color.rgb = RGBColor(0, 112, 192)
        p.alignment = PP_ALIGN.CENTER

        subtitle_box = slide.shapes.add_textbox(Inches(0), Inches(4.0), prs.slide_width, Inches(0.8))
        p2 = subtitle_box.text_frame.paragraphs[0]
        p2.text = subtitle_text
        p2.font.size = Pt(28)
        p2.font.name = 'Microsoft YaHei'
        p2.font.color.rgb = RGBColor(100, 100, 100)
        p2.alignment = PP_ALIGN.CENTER

    def create_question_slide(self, prs, question_num: int, content: str, source: str, answer: str, analysis: str):
        slide_layout = prs.slide_layouts[6]
        slide = prs.slides.add_slide(slide_layout)

        # 标题
        title_box = slide.shapes.add_textbox(Inches(0), Inches(0.2), Inches(13.333), Inches(0.8))
        p = title_box.text_frame.paragraphs[0]
        p.text = f"第 {question_num} 题"
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.name = 'Microsoft YaHei'
        p.font.color.rgb = RGBColor(0, 112, 192)
        p.alignment = PP_ALIGN.CENTER

        # 解析选项
        options = self.parse_options(content)

        # 题目内容
        if options:
            question_text = content.split('\n')[0]
        else:
            question_text = content

        # 检查是否包含 LaTeX
        if self.contains_latex(question_text):
            # 使用混合内容渲染
            segments = self.parse_latex_segments(question_text)
            self.add_mixed_content_to_slide(
                slide, segments,
                x=Inches(1.0), y=Inches(1.2),
                width=Inches(11.333), height=Inches(1.5),
                font_size=22, font_bold=True
            )
        else:
            # 普通文本
            q_height = Inches(1.5) if options else Inches(4.0)
            q_box = slide.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.333), q_height)
            q_box.text_frame.word_wrap = True
            p = q_box.text_frame.paragraphs[0]
            self.add_math_text(p, question_text)
            p.font.size = Pt(22)
            p.font.bold = True
            p.alignment = PP_ALIGN.LEFT
            p.space_after = Pt(14)

        # 选项（如果存在）
        if options:
            o_box = slide.shapes.add_textbox(Inches(1.5), Inches(2.6), Inches(10.333), Inches(1.8))
            o_box.text_frame.word_wrap = True

            for i in range(0, len(options), 2):
                if i == 0:
                    p = o_box.text_frame.paragraphs[0]
                else:
                    p = o_box.text_frame.add_paragraph()

                p.alignment = PP_ALIGN.LEFT
                p.space_after = Pt(12)
                pPr = p._p.get_or_add_pPr()
                tab = etree.SubElement(pPr, qn('a:tab'))
                tab.set('val', '7620')

                opt1_letter, opt1_text = options[i]
                self.add_math_text(p, f"{opt1_letter}) {opt1_text}")

                if i + 1 < len(options):
                    opt2_letter, opt2_text = options[i+1]
                    spacing_run = p.add_run()
                    spacing_run.text = "\t"
                    self.add_math_text(p, f"{opt2_letter}) {opt2_text}")

                for run in p.runs:
                    run.font.size = Pt(20)

        # 答案和解析区域
        a_y_pos = Inches(4.6) if options else Inches(4.2)

        # 答案
        answer_box = slide.shapes.add_textbox(Inches(1.0), a_y_pos, Inches(11.333), Inches(0.5))
        answer_box.name = "AnimatedAnswerShape"
        ap = answer_box.text_frame.paragraphs[0]
        ap.text = f"【正确答案】 {answer}"
        ap.font.size = Pt(20)
        ap.font.bold = True
        ap.font.color.rgb = RGBColor(0, 150, 0)
        ap.alignment = PP_ALIGN.LEFT

        # 解析
        analysis_y = a_y_pos + Inches(0.5)
        analysis_segments = self.parse_latex_segments(analysis)

        if self.contains_latex(analysis):
            self.add_mixed_content_to_slide(
                slide, [('text', '【解析】 ')] + analysis_segments,
                x=Inches(1.0), y=analysis_y,
                width=Inches(11.333), height=Inches(1.5),
                font_size=18, font_bold=True
            )
        else:
            analysis_box = slide.shapes.add_textbox(Inches(1.0), analysis_y, Inches(11.333), Inches(2.0))
            analysis_box.text_frame.word_wrap = True
            p2 = analysis_box.text_frame.paragraphs[0]

            run = p2.add_run()
            run.text = "【解析】 "
            run.font.bold = True
            run.font.size = Pt(18)
            run.font.color.rgb = RGBColor(100, 100, 100)

            self.add_math_text(p2, analysis)

            for run in p2.runs:
                if not run.font.size:
                    run.font.size = Pt(18)

    def add_animations_via_com(self, pptx_path: Path):
        if not HAS_WIN32COM:
            print("未安装 pywin32，跳过添加动画步骤。")
            return False

        try:
            app = win32com.client.Dispatch("PowerPoint.Application")
            abs_path = os.path.abspath(str(pptx_path))
            prs = app.Presentations.Open(abs_path, WithWindow=False)

            for slide in prs.Slides:
                for shape in slide.Shapes:
                    if shape.Name == "AnimatedAnswerShape":
                        slide.TimeLine.MainSequence.AddEffect(shape, 10, 0, 1)

            prs.Save()
            prs.Close()
            app.Quit()
            return True
        except Exception as e:
            print(f"添加动画时出现异常: {e}")
            try:
                app.Quit()
            except:
                pass
            return False

    def generate(self, questions: list, output_path: Path, title: str = None, use_animation: bool = True) -> Path:
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

        subtitle_text = f"共 {len(questions)} 道题目"

        if title:
            main_title = title
        elif questions and questions[0].get('source'):
            main_title = questions[0]['source']
        else:
            main_title = "试卷评讲"

        self.create_title_slide(prs, main_title, subtitle_text)

        for idx, q in enumerate(questions, 1):
            self.create_question_slide(
                prs, idx,
                q.get('content', ''),
                q.get('source', ''),
                q.get('answer', ''),
                q.get('analysis', '')
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        prs.save(str(output_path))

        if use_animation:
            self.add_animations_via_com(output_path)

        return output_path


ppt_generator = PPTGenerator()
