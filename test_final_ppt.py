import sys
import os
from pathlib import Path

# 将 backend 目录添加到 sys.path 以便导入 services
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from services.ppt_generator import ppt_generator

test_data = [
    { 
     "title": "9", 
     "source": "2024～2025学年第一学期期末考试试卷《计算机软件技术基础2》（C++、64学时）（B卷共6页）", 
     "content": "具有10个叶子节点的二叉树至少有多少层（层的数量）（ ）。\nA) 4\nB) 3\nC) 2\nD) 1", 
     "answer": "A", 
     "analysis": "知识点：二叉树性质。满二叉树时叶子节点最多，但求最小层数：第k层最多$2^{k-1}$个叶子，$2^{k-1} \\geq 10$，k最小为5层？计算：$2^{3}=8<10$，$2^{4}=16\\geq10$，所以至少4层。" 
   }
]

output_dir = Path("output/ppt")
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "final_test_output.pptx"

print(f"正在生成 PPT 到: {output_path}")
ppt_generator.generate(test_data, output_path, title="最终修复测试")
print("PPT 生成完成！")
