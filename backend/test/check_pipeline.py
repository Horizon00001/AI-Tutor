import requests
import time

pipeline_id = '17b1017d-3aa5-47a3-9b37-7611565e1221'
url = f'http://localhost:8080/api/v1/pipeline/{pipeline_id}'

print('查询 Pipeline 状态...')
for i in range(15):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f'\n第 {i+1} 次查询:')
            print(f"Pipeline ID: {data['pipeline_id']}")
            print(f"所有阶段完成: {data['all_completed']}")
            print('阶段状态:')
            for stage_name, stage_info in data['stages'].items():
                if isinstance(stage_info, dict) and 'status' in stage_info:
                    print(f"  - {stage_name}: {stage_info['status']}")
                    if 'result_file' in stage_info:
                        print(f"    结果文件: {stage_info['result_file']}")
                    if 'pptx_file' in stage_info:
                        print(f"    PPT文件: {stage_info['pptx_file']}")
            
            if data['all_completed']:
                print('\n✓ Pipeline 处理完成!')
                break
        else:
            print(f'查询失败: {response.status_code}')
    except Exception as e:
        print(f'查询出错: {e}')
    
    time.sleep(3)
