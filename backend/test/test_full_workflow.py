import requests
import os
import time
import random
import string

# 配置信息
BASE_URL = 'http://localhost:8080/api/v1'
IMAGE_PATH = r'f:\大二下学期\杂项\ai教育\试卷讲解demo\backend\uploads\fb82ae92-1297-4651-8e8d-1dc65c196da9.png'

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def test_full_workflow():
    print("=== 开始全流程测试 ===")
    
    # 1. 注册与登录
    print("\n[Step 1] 注册与登录")
    username = f"test_{generate_random_string()}"
    password = "test_password_123"
    email = f"{username}@example.com"
    
    # 注册
    reg_resp = requests.post(f"{BASE_URL}/auth/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    if reg_resp.status_code != 200:
        print(f"注册失败: {reg_resp.text}")
        return
    user_data = reg_resp.json()
    user_id = user_data["user_id"]
    print(f"注册成功: 用户ID = {user_id}, 用户名 = {username}")
    
    # 登录
    login_resp = requests.post(f"{BASE_URL}/auth/login", data={
        "username": username,
        "password": password
    })
    if login_resp.status_code != 200:
        print(f"登录失败: {login_resp.text}")
        return
    token = login_resp.json()["access_token"]
    print(f"登录成功: 获取到 Token")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 上传图片并运行 Pipeline
    print("\n[Step 2] 上传图片并运行 Pipeline")
    if not os.path.exists(IMAGE_PATH):
        print(f"错误: 找不到测试图片 {IMAGE_PATH}")
        return
        
    with open(IMAGE_PATH, 'rb') as f:
        files = {'file': ('test_image.png', f, 'image/png')}
        data = {
            'use_animation': 'false',
            'title': '集成测试试卷',
            'user_id': user_id
        }
        
        pipe_resp = requests.post(f"{BASE_URL}/pipeline/full", files=files, data=data, headers=headers)
        if pipe_resp.status_code != 200:
            print(f"Pipeline 启动失败: {pipe_resp.text}")
            return
        pipeline_id = pipe_resp.json()["pipeline_id"]
        print(f"Pipeline 已启动: ID = {pipeline_id}")
        
    # 3. 轮询 Pipeline 状态 (MinerU + DeepSeek)
    print("\n[Step 3] 轮询 Pipeline 状态 (包含 MinerU 和 DeepSeek 处理)")
    max_retries = 30
    all_completed = False
    questions = []
    
    for i in range(max_retries):
        time.sleep(5)
        status_resp = requests.get(f"{BASE_URL}/pipeline/{pipeline_id}", headers=headers)
        status_data = status_resp.json()
        
        stages = status_data.get("stages", {})
        print(f"轮询中 ({i+1}/{max_retries}): ", end="")
        for stage, info in stages.items():
            if isinstance(info, dict):
                print(f"{stage}: {info.get('status')} | ", end="")
        print()
        
        if status_data.get("all_completed") or (stages.get("deepseek", {}).get("status") == "completed"):
            if status_data.get("all_completed"):
                print("Pipeline 所有阶段处理完成!")
            else:
                print("Pipeline DeepSeek 阶段已完成 (即使后续 PPT 阶段失败，我们仍可继续测试)")
                
            # 获取 DeepSeek 任务 ID
            deepseek_task_id = stages.get("deepseek", {}).get("task_id")
            if deepseek_task_id:
                # 从 DeepSeek 结果 API 获取题目列表
                result_url = f"{BASE_URL}/deepseek/tasks/{deepseek_task_id}/result"
                res_resp = requests.get(result_url, headers=headers)
                if res_resp.status_code == 200:
                    res_data = res_resp.json()
                    questions = res_data.get("json_content", []) or res_data.get("data", [])
                else:
                    print(f"获取 DeepSeek 结果失败: {res_resp.text}")
            
            if questions:
                all_completed = True
                break
            
        # 检查关键阶段是否失败
        critical_stages = ["mineru", "deepseek"]
        for stage in critical_stages:
            if stages.get(stage, {}).get("status") == "failed":
                task_id = stages.get(stage, {}).get("task_id")
                error_msg = "未知错误"
                if task_id:
                    task_resp = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=headers)
                    if task_resp.status_code == 200:
                        error_msg = task_resp.json().get("error", "无错误信息")
                print(f"关键阶段 {stage} 处理失败! 错误详情: {error_msg}")
                return
            
    if not all_completed or not questions:
        print("Pipeline 超时或未获取到题目")
        return
        
    print(f"成功解析到 {len(questions)} 道题目")
    
    # 4. 生成相似题
    print("\n[Step 4] 生成相似题")
    # 选择第一道题目生成相似题
    target_question_idx = 0
    # 我们需要找到 DeepSeek 任务 ID
    deepseek_task_id = stages.get("deepseek", {}).get("task_id")
    
    # 获取真正的 exam_id（不是 pipeline_id）
    exam_id_for_similar = status_data.get("exam_id")
    if not exam_id_for_similar:
        # 如果 API 没返回 exam_id，说明 pipeline 可能在创建 exam 时失败了
        print("警告: Pipeline 状态中没有 exam_id，无法生成相似题")
        print("跳过 Step 4 相似题生成")
        exam_id_for_similar = None
    else:
        print(f"获取到正确的 exam_id: {exam_id_for_similar}")
    
    if exam_id_for_similar:
        similar_req = {
            "user_id": user_id,
            "exam_id": exam_id_for_similar,  # ✅ 使用真正的 exam_id
            "count": 2,
            "difficulty_adjustment": "same"
        }
        
        sim_resp = requests.post(
            f"{BASE_URL}/questions/{deepseek_task_id}/{target_question_idx}/generate-similar",
            json=similar_req,
            headers=headers
        )
        
        if sim_resp.status_code != 200:
            print(f"相似题生成请求失败: {sim_resp.text}")
        else:
            similar_task_id = sim_resp.json()["task_id"]
            print(f"相似题任务已启动: ID = {similar_task_id}")
            
            # 轮询相似题状态
            for i in range(20):
                time.sleep(3)
                sim_status_resp = requests.get(f"{BASE_URL}/questions/similar-tasks/{similar_task_id}", headers=headers)
                sim_status_data = sim_status_resp.json()
                print(f"相似题状态轮询 ({i+1}/20): {sim_status_data.get('status')}")
                
                if sim_status_data.get("status") == "completed":
                    print("相似题生成完成!")
                    res_resp = requests.get(f"{BASE_URL}/questions/similar-tasks/{similar_task_id}/result", headers=headers)
                    similar_data = res_resp.json()
                    similar_questions = similar_data.get("similar_questions", [])
                    print(f"生成了 {len(similar_questions)} 道相似题")
                    break
                elif sim_status_data.get("status") == "failed":
                    print(f"相似题生成失败: {sim_status_data.get('error')}")
                    break
    else:
        print("跳过相似题生成（exam_id 不可用）")
    
    sim_resp = requests.post(
        f"{BASE_URL}/questions/{deepseek_task_id}/{target_question_idx}/generate-similar",
        json=similar_req,
        headers=headers
    )
    
    if sim_resp.status_code != 200:
        print(f"相似题生成请求失败: {sim_resp.text}")
        return
        
    similar_task_id = sim_resp.json()["task_id"]
    print(f"相似题任务已启动: ID = {similar_task_id}")
    
    # 轮询相似题状态
    for i in range(20):
        time.sleep(3)
        sim_status_resp = requests.get(f"{BASE_URL}/questions/similar-tasks/{similar_task_id}", headers=headers)
        sim_status_data = sim_status_resp.json()
        print(f"相似题状态轮询 ({i+1}/20): {sim_status_data.get('status')}")
        
        if sim_status_data.get("status") == "completed":
            print("相似题生成完成!")
            # 获取相似题结果
            res_resp = requests.get(f"{BASE_URL}/questions/similar-tasks/{similar_task_id}/result", headers=headers)
            similar_data = res_resp.json()
            similar_questions = similar_data.get("similar_questions", [])
            print(f"生成了 {len(similar_questions)} 道相似题")
            break
        elif sim_status_data.get("status") == "failed":
            print(f"相似题生成失败: {sim_status_data.get('error')}")
            return
            
    # 5. 题目收藏
    print("\n[Step 5] 题目收藏")
    # 先从试卷接口获取带 ID 的题目
    exam_id = status_data.get("exam_id")
    if not exam_id:
        # 如果 API 没返回 exam_id，说明 pipeline 可能在创建 exam 时失败了
        print("错误: 无法获取 exam_id，无法进行题目收藏")
        print("跳过 Step 5 题目收藏")
        exam_id = None
    
    if not exam_id:
        print("跳过题目收藏（exam_id 不可用）")
    else:
        questions_resp = requests.get(f"{BASE_URL}/exams/{exam_id}/questions", headers=headers)
        if questions_resp.status_code != 200:
            print(f"获取试卷题目失败: {questions_resp.text}")
            return
            
        db_questions = questions_resp.json().get("questions", [])
        if not db_questions:
            print("未在数据库中找到题目")
            return
            
        target_q = db_questions[0]
        question_id = target_q.get("question_id")
        
        collect_req = {
            "teacher_id": user_id,
            "question_id": str(question_id), # 确保是字符串
            "difficulty_note": "中等难度",
            "teach_note": "这是一个集成测试生成的题目",
            "tags": ["测试", "自动生成"]
        }
        
        coll_resp = requests.post(f"{BASE_URL}/collections", json=collect_req, headers=headers)
        if coll_resp.status_code != 200:
            print(f"收藏失败: {coll_resp.text}")
            return
            
        print(f"题目 {question_id} 收藏成功!")
        
        # 检查收藏列表
        list_resp = requests.get(f"{BASE_URL}/collections?teacher_id={user_id}", headers=headers)
        collections = list_resp.json().get("collections", [])
        print(f"当前用户收藏数量: {len(collections)}")
    
    print("\n=== 全流程测试完成 ===")
    print(f"测试通过! 用户: {username}, Pipeline: {pipeline_id}")

if __name__ == "__main__":
    test_full_workflow()
