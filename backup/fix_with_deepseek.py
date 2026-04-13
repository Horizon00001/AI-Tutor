"""
试卷OCR数据修复与结构化工具
====================================

功能说明：
    本脚本用于处理OCR识别的试卷JSON数据，通过DeepSeek API对原始OCR结果进行智能修复和结构化处理。
    主要功能包括：
    1. 读取OCR生成的原始JSON数据
    2. 调用DeepSeek API进行智能解析和纠错
    3. 将处理结果按照标准格式输出为结构化的JSON文件

适用场景：
    - 批量处理扫描或拍照的试卷图片的OCR结果
    - 将非结构化的文本题目转换为结构化数据
    - 自动修正OCR识别错误（如数字混淆、符号错误等）

使用前提：
    - 已安装所需的Python包（见requirements.txt）
    - 配置好.env文件，包含API_KEY和API_URL

"""

# ==================== 导入必要的标准库和第三方库 ====================

# os：操作系统接口，用于读取环境变量
import os

# json：JSON数据处理，用于解析API返回的JSON和读写JSON文件
import json

# sys：系统相关功能，用于访问命令行参数和程序退出
import sys

# typing.List：类型注解支持，用于声明返回类型
from typing import List

# pathlib.Path：面向对象的文件路径处理，更现代化和跨平台
from pathlib import Path

# pydantic.BaseModel, Field：数据验证和设置管理，确保输出数据的正确性
from pydantic import BaseModel, Field

# openai.OpenAI：OpenAI API客户端，用于调用DeepSeek服务
from openai import OpenAI

# dotenv.load_dotenv：从.env文件加载环境变量，隐藏敏感配置
from dotenv import load_dotenv

# ==================== 初始化环境变量配置 ====================

# 获取当前脚本所在目录的.env文件路径
# Path(__file__) 获取当前脚本的绝对路径
# .parent 获取脚本所在文件夹
# / ".env" 拼接.env文件名
env_path = Path(__file__).parent / ".env"

# 加载.env文件中的环境变量到系统环境
# 这些变量包括：API_KEY（API密钥）和 API_URL（API地址）
load_dotenv(dotenv_path=env_path)

# ==================== 定义数据结构模型 ====================

class Question(BaseModel):
    """
    题目数据模型类
    
    该类定义了标准化题目的数据结构，使用Pydantic进行数据验证。
    每个字段都有明确的语义定义，确保输出的题目信息完整且规范。
    
    属性说明：
        title: 题目的唯一标识或所属大题标题，用于区分不同题目
        source: 题目的出处信息，如试卷名称、教材名称等，便于追溯
        content: 修复后的完整题目内容，包含所有已知条件、子题和选项
        answer: 题目的正确答案或计算结果
        analysis: 题目的详细解析，包含知识点、逻辑推导和解题思路
    """
    
    # 题目编号或所属大题标题
    # 例如："第1题"、"第二大题"、"选择题第5题"
    title: str = Field(..., description="题目编号或所属大题标题")
    
    # 题目来源，如试卷名称、书籍名称等
    # 建议同一份试卷的所有题目使用相同的source值
    source: str = Field(..., description="题目来源，如试卷名称、书籍名称等，同一试卷题目来源相同")
    
    # 修复后的完整题干
    # 重要：数学公式和专业符号必须使用LaTeX格式，使用$或$$包裹
    # 例如：$x^2 + y^2 = r^2$ 或 $$\int_0^1 f(x)dx$$
    content: str = Field(..., description="修复后的完整题干。包含已知条件、子题目列表或选项。数学/专业符号必须使用 LaTeX ($ 或 $$)。")
    
    # 该题的参考答案或计算结果
    # 对于选择题给出正确选项，对于计算题给出最终答案
    answer: str = Field(..., description="该题的参考答案或计算结果。")
    
    # 该题的核心知识点解析与逻辑推导过程
    # 包含解题思路、涉及的知识点、关键步骤等
    analysis: str = Field(..., description="该题的核心知识点解析与逻辑推导过程。")

def process_ocr_data(ocr_json_path: str) -> List[Question]:
    """
    使用 DeepSeek API 处理 OCR JSON 数据并返回结构化题目
    
    参数说明：
        ocr_json_path (str): OCR生成的JSON文件路径
        
    返回值：
        List[Question]: 结构化的题目对象列表
        
    工作流程：
        1. 读取OCR生成的原始JSON文件内容
        2. 加载系统提示词（用于指导AI如何处理数据）
        3. 初始化OpenAI客户端连接到DeepSeek API
        4. 发送请求到DeepSeek API进行智能处理
        5. 解析API返回的JSON结果
        6. 使用Pydantic模型验证和转换数据
        7. 返回结构化的题目列表
        
    异常处理：
        - 文件读取失败时退出程序
        - API调用或JSON解析失败时退出程序
    """
    
    # ==================== 第一步：读取OCR原始数据 ====================
    
    # 使用UTF-8编码读取OCR生成的JSON文件
    # encoding='utf-8' 确保正确处理中文内容
    try:
        with open(ocr_json_path, 'r', encoding='utf-8') as f:
            ocr_data = f.read()  # 读取全部内容为字符串
    except Exception as e:
        # 捕获文件不存在、权限不足等异常
        print(f"错误: 无法读取 OCR 文件 {ocr_json_path}: {e}")
        sys.exit(1)  # 异常退出程序，返回错误码1

    # ==================== 第二步：加载系统提示词 ====================
    
    # 构建提示词文件的完整路径（与脚本同目录）
    # prompt.txt 包含指导AI如何处理OCR数据的指令
    prompt_path = Path(__file__).parent / "prompt.txt"
    
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()  # 读取提示词内容
    except Exception as e:
        print(f"错误: 无法读取提示词文件 {prompt_path}: {e}")
        sys.exit(1)

    # ==================== 第三步：获取API配置信息 ====================
    
    # 从环境变量读取API凭证
    # 这些变量在程序启动时从.env文件加载
    api_key = os.getenv("API_KEY")    # DeepSeek API密钥
    api_url = os.getenv("API_URL")     # DeepSeek API服务地址

    # 验证必要的配置是否存在
    if not api_key or not api_url:
        print("错误: .env 文件中缺少 API_KEY 或 API_URL")
        print("请确保.env文件包含以下内容：")
        print("API_KEY=your_api_key_here")
        print("API_URL=https://api.deepseek.com")
        sys.exit(1)

    # ==================== 第四步：初始化API客户端 ====================
    
    # 创建OpenAI客户端实例
    # 注意：这里使用的是OpenAI SDK，但连接到的是DeepSeek的API端点
    # base_url 指定了API的服务地址
    client = OpenAI(
        api_key=api_key,
        base_url=api_url
    )

    # 打印处理状态信息
    print(f"正在调用 DeepSeek API 处理 {Path(ocr_json_path).name}...")

    # ==================== 第五步：调用DeepSeek API进行智能处理 ====================
    
    # 构建发送给API的消息
    # system_prompt: 系统角色设定，告诉AI应该扮演什么角色和如何处理数据
    # user message: 包含实际的OCR数据，让AI进行处理
    
    try:
        # 调用Chat Completions API
        # model: 使用的模型名称，deepseek-chat 是DeepSeek的对话模型
        # messages: 对话消息列表，包含系统提示和用户输入
        # response_format: 指定返回格式为JSON对象
        # stream: 是否使用流式响应，False表示等待完整响应
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                # 系统消息：定义AI的角色和任务
                {"role": "system", "content": system_prompt},
                # 用户消息：提供需要处理的OCR数据
                {"role": "user", "content": f"以下是需要处理的 OCR JSON 数据：\n\n{ocr_data}"}
            ],
            response_format={"type": "json_object"},  # 要求返回JSON格式
            stream=False  # 等待完整响应，不使用流式输出
        )
        
        # ==================== 第六步：解析API响应 ====================
        
        # 获取API返回的消息内容
        # response.choices[0] 是第一个（也是通常唯一的）回复选项
        # .message.content 提取回复的文本内容（JSON字符串）
        content = response.choices[0].message.content
        
        # 将JSON字符串解析为Python字典对象
        data = json.loads(content)
        
        # ==================== 第七步：处理不同的JSON结构 ====================
        
        # DeepSeek可能返回不同的JSON结构，需要兼容处理：
        # 1. {"questions": [...]} - 包含questions键的对象
        # 2. [...] - 直接的数组格式
        # 3. {...} - 单个题目对象
        
        if isinstance(data, dict) and "questions" in data:
            # 情况1：返回的是包含questions键的字典
            items = data["questions"]
        elif isinstance(data, list):
            # 情况2：返回的是直接的数组
            items = data
        else:
            # 情况3：返回的是单个题目对象
            # 将其包装成列表以保持一致性
            items = [data] if isinstance(data, dict) else []

        # ==================== 第八步：数据验证和类型转换 ====================
        
        # 使用Pydantic模型进行数据验证和转换
        # **item 将字典展开为关键字参数
        # Question(**item) 创建Question实例，同时进行字段验证
        # 如果字段不符合定义（如缺少必需字段或类型错误），会抛出异常
        questions = [Question(**item) for item in items]
        
        # 返回结构化的题目列表
        return questions

    except Exception as e:
        # 捕获API调用失败、JSON解析错误、数据验证失败等所有异常
        print(f"API 调用或解析失败: {e}")
        
        # 如果已经获取到原始响应内容，打印出来便于调试
        if 'content' in locals():
            print(f"原始响应内容: {content}")
        
        sys.exit(1)  # 异常退出

def main():
    """
    程序主函数
    
    负责处理命令行参数、协调整个处理流程、保存结果文件。
    
    工作流程：
        1. 验证命令行参数是否提供
        2. 调用process_ocr_data函数获取处理结果
        3. 准备输出目录和文件路径
        4. 将结果转换为JSON格式并保存
        5. 打印处理总结信息
        
    命令行用法：
        python fix_with_deepseek.py <ocr_json_path>
        
    示例：
        python fix_with_deepseek.py output/Exercises1/Exercises1_content_list.json
    """
    
    # ==================== 第一步：验证命令行参数 ====================
    
    # sys.argv[0] 是脚本自身名称
    # sys.argv[1] 是第一个实际参数（OCR JSON文件路径）
    # 如果没有提供参数，提示用户正确的使用方法
    
    if len(sys.argv) < 2:
        # 打印用法说明
        print("用法: python deepseek.py <ocr_json_path>")
        # 打印具体示例，帮助用户理解
        print("示例: python deepseek.py output/Exercises1/Exercises1_content_list.json")
        print("\n提示：")
        print("- 确保已经配置好 .env 文件（包含 API_KEY 和 API_URL）")
        print("- 确保 prompt.txt 文件存在于脚本同目录")
        sys.exit(1)  # 异常退出，返回错误码1

    # ==================== 第二步：获取和处理OCR数据 ====================
    
    # 从命令行参数获取OCR文件的路径
    ocr_path = sys.argv[1]
    
    # 调用核心处理函数，该函数会：
    # 1. 读取OCR JSON文件
    # 2. 调用DeepSeek API进行处理
    # 3. 返回结构化的题目列表
    questions = process_ocr_data(ocr_path)
    
    # ==================== 第三步：准备输出目录 ====================
    
    # 按照用户要求，所有输出文件统一放到output/processed_json目录
    # 创建Path对象表示output/processed_json目录
    output_root = Path("output/processed_json")
    
    # mkdir(exist_ok=True)：创建目录，如果已存在也不报错
    # parents=True：如果是多级目录，同时创建父目录
    output_root.mkdir(exist_ok=True)
    
    # ==================== 第四步：生成输出文件路径 ====================
    
    # Path(ocr_path).stem 获取文件名（不含扩展名）
    # 例如：input.json -> input
    file_stem = Path(ocr_path).stem
    
    # 拼接输出文件的完整路径
    # 输出格式：output/{原文件名}_cleaned.json
    # 例如：output/Exercises1_content_list_cleaned.json
    output_file = output_root / f"{file_stem}_cleaned.json"
    
    # ==================== 第五步：转换和保存结果 ====================
    
    # 将Pydantic模型对象转换为字典列表
    # model_dump()：将Pydantic模型序列化为字典
    # result_json 现在是一个普通的Python列表，可以被json.dump处理
    result_json = [q.model_dump() for q in questions]
    
    # 将结果写入JSON文件
    # encoding='utf-8'：确保正确保存中文内容
    # ensure_ascii=False：允许JSON文件中包含非ASCII字符（如中文）
    # indent=2：使用2空格缩进，使JSON文件更易读
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_json, f, ensure_ascii=False, indent=2)
    
    # ==================== 第六步：打印处理总结 ====================
    
    print(f"\n处理完成！")
    print(f"解析题目数量: {len(questions)}")
    print(f"结果已保存至: {output_file}")
    
    # 可选：打印每个题目的简要信息
    if questions:
        print("\n题目列表：")
        for i, q in enumerate(questions, 1):
            # 显示题目序号、标题和来源
            print(f"  {i}. [{q.title}] - 来源: {q.source}")

# ==================== 程序入口点 ====================

# Python的特殊变量，当脚本被直接运行时，其值为"__main__"
# 当脚本被导入到其他模块时，其值是模块名
# 这样可以控制代码的执行时机，只有直接运行脚本时才执行main()

if __name__ == "__main__":
    """
    程序入口点
    
    这是Python程序的传统写法，确保：
    1. 当脚本被直接运行时，调用main()函数
    2. 当脚本被导入时，不会自动执行main()
    3. 便于代码测试和模块化
    """
    main()
