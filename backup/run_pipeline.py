import subprocess
import sys
from pathlib import Path

def main():
    # 支持的文件格式
    supported_formats = ['.pdf', '.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp']
    
    # 从命令行参数获取文件
    files = sys.argv[1:]
    
    # 验证命令行参数
    if not files:
        print("用法: python run_pipeline.py <file1.pdf|image.png> [file2.pdf] ...")
        print("\n示例:")
        print("  python run_pipeline.py upload/Exercises1.pdf")
        print("  python run_pipeline.py upload/Exercises1.pdf upload/Exercises2.pdf")
        print("\n支持的格式: pdf, png, jpg, jpeg, bmp, tiff, webp")
        return
    
    # 验证命令行参数中的文件是否存在
    valid_files = []
    for file_path in files:
        path = Path(file_path)
        if not path.exists():
            print(f"错误: 文件不存在: {file_path}")
            continue
        if path.suffix.lower() not in supported_formats:
            print(f"错误: 不支持的格式: {file_path}")
            continue
        valid_files.append(file_path)
    
    files = valid_files
    
    if not files:
        print("错误: 没有有效的文件")
        return
    
    print(f"处理 {len(files)} 个文件:")
    for f in files:
        print(f"  - {Path(f).name}")
    
    # 确保 raw_json 目录存在
    raw_json_dir = Path("output/raw_json")
    raw_json_dir.mkdir(parents=True, exist_ok=True)
    
    # 处理每个文件
    for file_path in files:
        file_name = Path(file_path).name
        print(f"\n处理文件: {file_name}")
        try:
            # 步骤1: 使用 pdf_extractor.py 处理文件
            subprocess.run([sys.executable, "pdf_extractor.py", file_path], check=True)
            
            # 步骤2: 查找并处理生成的 JSON 文件
            stem = Path(file_path).stem
            dir_path = raw_json_dir / stem
            if dir_path.exists():
                json_files = list(dir_path.glob("*_content_list.json"))
                if json_files:
                    print(f"处理 JSON 文件: {json_files[0].name}")
                    subprocess.run([sys.executable, "fix_with_deepseek.py", str(json_files[0])], check=True)
                    print(f"✓ {file_name} 处理完成")
                else:
                    print(f"✗ {file_name} 没有找到 JSON 文件")
            else:
                print(f"✗ {file_name} 没有找到输出目录")
            
        except subprocess.CalledProcessError as e:
            print(f"✗ {file_name} 处理失败: {e}")
            continue
    
    print(f"\n所有文件处理完成！")
    
if __name__ == "__main__":
    main()
