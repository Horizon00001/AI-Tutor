import requests
import os
import time

# 测试图片路径
image_path = r'f:\大二下学期\杂项\ai教育\试卷讲解demo\uploads\4d8e8039-fd73-4a86-a6f7-0d0340192980_test.png'

print(f'文件大小: {os.path.getsize(image_path)} bytes')

# 调用 pipeline API
url = 'http://localhost:8080/api/v1/pipeline/full'

with open(image_path, 'rb') as f:
    files = {'file': ('test_network_question.png', f, 'image/png')}
    data = {
        'use_animation': 'false',
        'title': '计算机网络测试题',
        'user_id': 'test_user'
    }
    
    response = requests.post(url, files=files, data=data, timeout=30)
    print(f'Status Code: {response.status_code}')
    if response.status_code != 200:
        print(f'Error Response: {response.text}')
        exit(1)
    result = response.json()
    print('Pipeline 启动成功!')
    print(f"Pipeline ID: {result['pipeline_id']}")
    
    # 轮询检查状态
    pipeline_id = result['pipeline_id']
    status_url = f'http://localhost:8080/api/v1/pipeline/{pipeline_id}'
    
    for i in range(15):
        time.sleep(3)
        status_resp = requests.get(status_url, timeout=10)
        status_data = status_resp.json()
        
        print(f'\n--- 第 {i+1} 次检查 ---')
        for stage_name, stage_info in status_data['stages'].items():
            if isinstance(stage_info, dict) and 'status' in stage_info:
                status = stage_info["status"]
                print(f'{stage_name}: {status}')
                if status == 'failed' and 'task_id' in stage_info:
                    # 获取任务详情以查看错误
                    task_id = stage_info['task_id']
                    task_url = f'http://localhost:8080/api/v1/tasks/{task_id}'
                    try:
                        task_resp = requests.get(task_url, timeout=5)
                        if task_resp.status_code == 200:
                            task_data = task_resp.json()
                            if task_data.get('error'):
                                print(f'  错误详情: {task_data["error"]}')
                    except Exception:
                        pass
        
        if status_data['all_completed']:
            print('\n✓ 所有阶段处理完成!')
            if 'ppt' in status_data['stages'] and 'pptx_file' in status_data['stages']['ppt']:
                print(f"PPT文件: {status_data['stages']['ppt']['pptx_file']}")
            break
        
        has_failed = any(
            stage_info.get('status') == 'failed'
            for stage_name, stage_info in status_data['stages'].items()
            if isinstance(stage_info, dict) and 'status' in stage_info
        )
        if has_failed:
            print('\n✗ 有阶段处理失败')
            break
