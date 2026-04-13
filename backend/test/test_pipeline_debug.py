import asyncio
import json
from pathlib import Path
from services.task_manager import task_manager, TaskType
from services.mineru_service import mineru_service
from services.deepseek_service import deepseek_service

async def test_pipeline():
    # 测试图片路径
    image_path = Path(r'f:\大二下学期\杂项\ai教育\试卷讲解demo\uploads\4d8e8039-fd73-4a86-a6f7-0d0340192980_test.png')
    
    print("=== 测试 Pipeline ===")
    print(f"图片路径: {image_path}")
    print(f"图片存在: {image_path.exists()}")
    
    # 1. 创建 MinerU 任务
    mineru_task = task_manager.create_task(TaskType.MINERU, source_id='test')
    print(f"\n1. 创建 MinerU 任务: {mineru_task.task_id}")
    
    # 2. 执行 MinerU 提取
    print("2. 执行 MinerU 提取...")
    try:
        result = await mineru_service.extract(image_path, mineru_task.task_id)
        if result:
            print(f"   ✓ MinerU 提取成功: {result}")
            
            # 3. 创建 DeepSeek 任务
            deepseek_task = task_manager.create_task(TaskType.DEEPSEEK, source_id=mineru_task.task_id)
            print(f"\n3. 创建 DeepSeek 任务: {deepseek_task.task_id}")
            
            # 4. 执行 DeepSeek 修复
            print("4. 执行 DeepSeek 修复...")
            try:
                fixed_result = await deepseek_service.fix_json(result, deepseek_task.task_id)
                if fixed_result:
                    print(f"   ✓ DeepSeek 修复成功: {fixed_result}")
                    
                    # 读取结果
                    with open(fixed_result, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"\n处理结果:")
                    print(json.dumps(data, ensure_ascii=False, indent=2))
                else:
                    print(f"   ✗ DeepSeek 修复失败")
                    task = task_manager.get_task(deepseek_task.task_id)
                    if task:
                        print(f"   错误: {task.error}")
            except Exception as e:
                print(f"   ✗ DeepSeek 异常: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"   ✗ MinerU 提取失败")
    except Exception as e:
        print(f"   ✗ MinerU 异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pipeline())
