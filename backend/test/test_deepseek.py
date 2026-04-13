import asyncio
import json
from pathlib import Path
from services.deepseek_service import deepseek_service
from services.task_manager import task_manager, TaskType

async def test_deepseek():
    json_file_path = Path(r'f:\大二下学期\杂项\ai教育\试卷讲解demo\output\raw_json\60eb2c76-e05f-4348-a8c9-9a34607aa467_test_network_question\fad9b72e-79f3-42d8-bce4-e6a5f12d1af8_content_list.json')
    
    # 创建任务
    task = task_manager.create_task(TaskType.DEEPSEEK, source_id='test')
    print(f"创建任务: {task.task_id}")
    
    try:
        result = await deepseek_service.fix_json(json_file_path, task.task_id)
        if result:
            print(f"✓ 处理成功!")
            print(f"  结果文件: {result}")
            
            # 读取结果
            with open(result, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"\n处理结果:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"✗ 处理失败")
            task = task_manager.get_task(task.task_id)
            if task:
                print(f"  错误: {task.error_message}")
    except Exception as e:
        print(f"✗ 异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_deepseek())
