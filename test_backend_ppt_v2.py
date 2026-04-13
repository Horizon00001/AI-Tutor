import sys
sys.path.insert(0, 'backend')

from pathlib import Path
from services.ppt_generator import ppt_generator

test_data = {
    "content": "具有10个叶子节点的二叉树至少有多少层（层的数量）（ ）。\nA) 4\nB) 3\nC) 2\nD) 1",
    "source": "2024～2025学年第一学期期末考试试卷《计算机软件技术基础2》（C++、64学时）（B卷共6页）",
    "answer": "A",
    "analysis": "知识点：二叉树性质。满二叉树时叶子节点最多，但求最小层数：第k层最多$2^{k-1}$个叶子，$2^{k-1} \\geq 10$，k最小为5层？计算：$2^{3}=8<10$，$2^{4}=16\\geq10$，所以至少4层。"
}

output_path = Path("output/ppt/test_backend_v2.pptx")
result = ppt_generator.generate([test_data], output_path, title="测试PPT生成-V2")
print(f"PPT生成成功: {result}")
