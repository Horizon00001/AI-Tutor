# `generate_ppt.py` 修改计划

## 1. 目标摘要 (Summary)

重构 `generate_ppt.py`，将题目、选项、答案和解析合并到同一页幻灯片中，优化排版使其居中显示，并增加对 LaTeX 公式的基础识别和渲染。最后通过 COM 接口（`win32com`）为答案和解析部分添加“点击后显示”的动画交互效果。

## 2. 现状分析 (Current State Analysis)

* 目前的代码将题目和答案分别生成在不同的幻灯片中，不方便实际讲课演示。

* 文本排版使用的是默认的左对齐，未作居中处理。

* 未处理 LaTeX 公式，导致带有 `$` 或 `$$` 的公式源码直接暴露在 PPT 中。

* 缺乏 PPT 内的动画交互（无法实现“先看题，点击后再看答案”的效果）。

## 3. 拟议更改 (Proposed Changes)

**修改目标文件**: `f:\大二下学期\杂项\ai教育\试卷讲解demo\generate_ppt.py`

### 3.1 增加 LaTeX 公式基础解析与渲染

* **增加映射表**: 建立 `LATEX_MAP` 字典，将常见 LaTeX 符号（如 `\pi`, `\times`, `\leq`, `\geq`, `\frac` 等）替换为 Unicode 字符，以优化显示。

* **编写** **`add_math_text(paragraph, text)`** **函数**:

  * 使用正则表达式提取 `$` 或 `$$` 包裹的公式部分。

  * 将非公式部分字体设置为 `Microsoft YaHei`，公式部分字体设置为 `Cambria Math` 并倾斜，从而在视觉上与标准数学公式相似。

### 3.2 优化版面布局与合并幻灯片

* **合并问答**: 取消 `create_answer_slide` 函数，统一使用 `create_question_slide`。

* **自定义排版与居中**:

  * 不再使用默认占位符，改用 `slide.shapes.add_textbox` 并指定绝对位置（`Inches`），精确控制题目、选项、答案的分布。

  * 将所有段落的 `alignment` 属性设置为 `PP_ALIGN.CENTER` 实现居中。

* **标记答案区域**: 将存放答案和解析的文本框（Shape）的 `name` 属性设置为 `AnimatedAnswerShape`，为后续添加动画提供标识。

### 3.3 增加动画交互逻辑

* **引入** **`win32com.client`**: 在生成 PPTX 文件后，进行后处理。

* **编写** **`add_animations(pptx_path)`** **函数**:

  * 通过 `win32com` 后台启动 PowerPoint 应用，打开生成的 PPTX 文件。

  * 遍历所有幻灯片，找到名为 `AnimatedAnswerShape` 的形状。

  * 为这些形状添加“出现（Appear）”动画，并设置为“单击时（On Click）”触发（参数 `10, 0, 1`）。

  * 保存并退出。

## 4. 假设与决策 (Assumptions & Decisions)

* **环境假设**: 运行环境为 Windows 且安装有 Microsoft PowerPoint，支持 `win32com` 接口（已在之前的测试中验证可行）。

* **公式渲染降级**: 考虑到纯文本渲染的局限性，复杂二维公式（如多重嵌套分数、积分号）将以一维线性字符形式或替换后的 Unicode 形式展现，能够满足绝大部分选择题的阅读需求。

* **合并策略**: 所有的题目及其答案都在同一页展示，可以大幅减少 PPT 页数，提升讲课连贯性。

## 5. 验证步骤 (Verification steps)

1. 运行修改后的 `generate_ppt.py`。
2. 检查输出目录下生成的 PPTX 文件。
3. 确认版面：题目和选项是否居中显示，公式中的 `$` 符号是否消失且字体正确变更。
4. 确认动画：开启放映模式，检查答案和解析是否默认隐藏，且点击鼠标后才出现。

