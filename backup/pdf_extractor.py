"""
MinerU PDF文档提取工具
==================

该脚本用于将PDF文件上传至MinerU平台进行文档内容提取，
支持批量处理、进度轮询和结果自动下载。

主要功能流程：
1. 从.env文件读取API认证令牌
2. 验证命令行参数的PDF文件
3. 向MinerU API申请批量上传URL
4. 将PDF文件上传至指定存储位置
5. 轮询等待文档提取完成
6. 下载并解压提取结果，保留content_list.json文件

依赖：requests, pathlib
"""

import json
import sys
import time
import zipfile
from pathlib import Path

import requests


def load_token():
    """
    从当前脚本目录下的.env文件中读取API认证令牌

    Returns:
        str or None: 读取到的token字符串，如果文件不存在或未找到token则返回None
    """
    # 获取当前脚本所在目录的路径
    env_path = Path(__file__).parent / ".env"
    # 检查.env文件是否存在
    if env_path.exists():
        # 逐行读取文件内容
        for line in env_path.read_text(encoding="utf-8").splitlines():
            # 查找以"token="开头的行
            if line.startswith("token="):
                # 提取token值（取"="后面的部分），去除首尾空白字符
                return line.split("token=", 1)[1].strip()
    return None


# 加载API认证令牌
token = load_token()
# 如果未找到token，输出警告并退出程序
if not token:
    print("Warning: token not found in .env file")
    sys.exit(1)

# MinerU API端点配置
# 批量申请文件上传URL的API地址
upload_url = "https://mineru.net/api/v4/file-urls/batch"
# 批量查询提取结果的API地址模板，{batch_id}会被实际批次ID替换
result_url_template = "https://mineru.net/api/v4/extract-results/batch/{batch_id}"

# HTTP请求头配置
header = {
    "Content-Type": "application/json",  # 指定发送JSON格式数据
    "Authorization": f"Bearer {token}"    # Bearer令牌认证方式
}

# 输出目录配置：所有提取结果将保存在此目录下
output_dir = Path("output/raw_json")
# 轮询间隔时间（秒）：检查文档处理状态的频率
poll_interval = 3
# 轮询超时时间（秒）：最大等待处理完成的时间
poll_timeout = 300


def get_file_paths():
    """
    从命令行参数中获取并验证PDF或图片文件路径

    该函数处理命令行输入，验证文件存在性及格式正确性

    Returns:
        list[Path]: 验证通过的PDF或图片文件Path对象列表

    Raises:
        sys.exit: 当参数缺失或没有有效文件时退出程序
    """
    # 检查是否提供了命令行参数（第一个参数是脚本自身）
    if len(sys.argv) < 2:
        print("Usage: python pdf_extractor.py <file1.pdf|file1.png|file1.jpg> [file2.pdf] ...")
        print("Example: python pdf_extractor.py Exercises1.pdf image.png photo.jpg")
        sys.exit(1)

    file_paths = []
    # 支持的文件格式
    supported_formats = ['.pdf', '.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp']
    
    # 遍历所有命令行参数（跳过第一个参数，即脚本名称）
    for arg in sys.argv[1:]:
        path = Path(arg)
        # 验证文件是否存在
        if not path.exists():
            print(f"Error: File not found: {path}")
            sys.exit(1)
        
        # 检查文件格式是否支持
        if path.suffix.lower() not in supported_formats:
            print(f"Warning: {path} is not a supported format, skipping...")
            continue
        
        file_paths.append(path)

    # 确保至少提供了一个有效的文件
    if not file_paths:
        print("Error: No valid PDF or image files provided")
        sys.exit(1)

    return file_paths


def prepare_upload_data(file_paths):
    """
    准备上传数据配置

    将文件路径列表转换为MinerU API所需的上传请求格式

    Args:
        file_paths (list[Path]): PDF或图片文件路径列表

    Returns:
        dict: 包含files数组和model_version的上传配置字典
    """
    files_config = []
    for path in file_paths:
        # 将文件名转换为data_id：转小写，空格和连字符替换为下划线
        data_id = path.stem.lower().replace(' ', '_').replace('-', '_')
        files_config.append({
            "name": path.name,           # 原始文件名
            "data_id": data_id,          # 唯一标识符
            "file_type": path.suffix.lower()  # 文件类型（用于API识别）
        })
        
    return {
        "files": files_config,
        "model_version": "vlm"          # 使用VLM模型版本进行提取
    }


# 代理配置：设置为None表示不使用代理，直接连接
proxies = {"http": None, "https": None}


def upload_files(urls):
    """
    将PDF文件上传至预先获取的存储URL

    使用PUT请求将本地文件二进制内容上传到云存储

    Args:
        urls (list[str]): 与file_paths一一对应的上传目标URL列表

    Raises:
        RuntimeError: 当HTTP状态码不是200时抛出异常
    """
    # 使用zip将文件路径和URL配对处理
    for file_path, url in zip(file_paths, urls):
        # 以二进制读取模式打开文件
        with file_path.open("rb") as file:
            # 发送PUT请求上传文件内容
            response = requests.put(url, data=file, timeout=120, proxies=proxies)
        # 检查HTTP响应状态
        if response.status_code != 200:
            raise RuntimeError(f"{file_path.name} upload failed: {response.status_code}")
        print(f"{file_path.name} upload success")


def get_batch_results(batch_id):
    """
    查询指定批次的文档提取结果

    向MinerU API发送GET请求获取当前处理状态

    Args:
        batch_id (str): 批次唯一标识符

    Returns:
        list: 提取结果列表，每个元素包含单个文档的处理状态和结果URL

    Raises:
        RuntimeError: 当API返回错误码时抛出异常
    """
    # 使用格式化字符串插入batch_id
    response = requests.get(
        result_url_template.format(batch_id=batch_id),
        headers=header,           # 携带认证头
        timeout=30,               # 请求超时30秒
        proxies=proxies,
    )
    response.raise_for_status()   # 对非200状态码抛出异常
    result = response.json()      # 解析JSON响应

    # 检查业务逻辑错误码
    if result["code"] != 0:
        raise RuntimeError(f'query result failed: {result["msg"]}')

    # 返回提取结果列表
    return result["data"].get("extract_result", [])


def wait_until_done(batch_id):
    """
    轮询等待所有文档处理完成

    持续查询批次状态，直到所有文档处理完毕或发生错误/超时

    Args:
        batch_id (str): 批次唯一标识符

    Returns:
        list: 所有文档的提取结果

    Raises:
        RuntimeError: 当任一文档处理失败时抛出异常
        TimeoutError: 当轮询超过预设时间限制时抛出异常
    """
    start_time = time.time()      # 记录开始时间
    # 持续轮询直到超时
    while time.time() - start_time < poll_timeout:
        # 获取当前批次结果
        extract_results = get_batch_results(batch_id)
        if extract_results:
            # 提取所有文档的当前状态
            states = [item["state"] for item in extract_results]
            print(f"current states: {states}")

            # 检查是否存在处理失败的文档
            if any(state == "failed" for state in states):
                # 收集失败文档的详细信息
                failed_items = [item for item in extract_results if item["state"] == "failed"]
                raise RuntimeError(f"extract failed: {failed_items}")

            # 检查是否所有文档都已处理完成
            if all(state == "done" for state in states):
                return extract_results

        # 等待指定间隔后再次查询
        time.sleep(poll_interval)

    # 超出设定的超时时间
    raise TimeoutError(f"poll timeout after {poll_timeout} seconds")


def download_results(extract_results):
    """
    下载并处理提取结果

    从提取结果中获取ZIP包下载链接，下载后解压，
    只保留content_list.json文件，清理其他临时文件

    Args:
        extract_results (list): wait_until_done返回的提取结果列表
    """
    # 确保输出目录存在
    output_dir.mkdir(exist_ok=True)

    # 遍历每个文档的提取结果
    for item in extract_results:
        zip_url = item["full_zip_url"]              # ZIP包下载地址
        file_stem = Path(item["file_name"]).stem     # 提取文件名（不含扩展名）
        zip_path = output_dir / f"{file_stem}.zip"    # 本地ZIP文件保存路径
        extract_dir = output_dir / file_stem         # 解压目标目录

        try:
            # 流式下载ZIP文件，避免大文件占用过多内存
            response = requests.get(zip_url, stream=True, timeout=120, proxies=proxies)
            response.raise_for_status()

            # 分块写入文件，每块8KB
            with zip_path.open("wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            print(f"downloaded: {zip_path}")

            # 创建解压目录
            extract_dir.mkdir(exist_ok=True)

            # 打开ZIP文件并查找content_list.json
            with zipfile.ZipFile(zip_path, "r") as zip_file:
                content_list_json = None

                # 优先查找以_content_list.json结尾的文件
                for file_info in zip_file.filelist:
                    if file_info.filename.endswith('_content_list.json'):
                        zip_file.extract(file_info, extract_dir)
                        content_list_json = extract_dir / file_info.filename
                        break

                # 如果没找到，回退查找任意.json文件
                if not content_list_json:
                    for file_info in zip_file.filelist:
                        if file_info.filename.endswith('.json'):
                            zip_file.extract(file_info, extract_dir)
                            content_list_json = extract_dir / file_info.filename
                            break

            # 如果成功找到JSON文件
            if content_list_json:
                print(f"extracted content_list.json to: {extract_dir}")

                # 删除ZIP压缩包
                zip_path.unlink()

                # 删除除content_list.json外的所有文件
                for file in extract_dir.iterdir():
                    if file.name != content_list_json.name:
                        file.unlink()

                print(f"cleaned up unnecessary files, kept: {content_list_json.name}")
            else:
                print(f"No content_list.json found in {extract_dir}")

        # 捕获下载或处理过程中的任何异常
        except Exception as err:
            # 将下载URL保存到文本文件，供手动下载
            url_path = output_dir / f"{file_stem}_download_url.txt"
            url_path.write_text(zip_url, encoding="utf-8")
            print(f"download failed: {err}")
            print(f"saved download url to: {url_path}")
            print(f"Direct JSON URL: {zip_url}")


# ==================== 主程序入口 ====================
if __name__ == "__main__":
    try:
        # 步骤1：获取并验证命令行指定的PDF文件
        file_paths = get_file_paths()

        # 步骤2：准备上传数据配置
        data = prepare_upload_data(file_paths)
        print(f"Processing files: {[p.name for p in file_paths]}")

        # 步骤3：向MinerU API申请批量上传URL
        response = requests.post(upload_url, headers=header, json=data, timeout=30, proxies=proxies)
        response.raise_for_status()
        result = response.json()
        print("response success. result:{}".format(result))

        # 检查API响应错误
        if result["code"] != 0:
            raise RuntimeError('apply upload url failed,reason:{}'.format(result["msg"]))

        # 提取批次ID和文件上传URL
        batch_id = result["data"]["batch_id"]
        urls = result["data"]["file_urls"]
        print("batch_id:{},urls:{}".format(batch_id, urls))

        # 步骤4：上传PDF文件到云存储
        upload_files(urls)

        # 步骤5：轮询等待文档提取处理完成
        extract_results = wait_until_done(batch_id)

        # 步骤6：下载并整理提取结果
        download_results(extract_results)

    except Exception as err:
        # 捕获并输出任何异常信息
        print(err)
