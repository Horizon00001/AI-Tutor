"""
完整的收藏功能测试脚本
展示如何正确使用收藏API的所有接口
"""
import requests
import time
import random
import string
import json

BASE_URL = 'http://localhost:8080/api/v1'
IMAGE_PATH = r'f:\大二下学期\杂项\ai教育\试卷讲解demo\backend\uploads\fb82ae92-1297-4651-8e8d-1dc65c196da9.png'


def generate_random_string(length=8):
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def test_complete_collection_workflow():
    """完整的收藏工作流测试"""
    print("=" * 60)
    print("完整收藏功能测试")
    print("=" * 60)

    # 1. 注册和登录
    print("\n[Step 1] 注册和登录...")
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
        print(f"❌ 注册失败: {reg_resp.text}")
        return

    user_data = reg_resp.json()
    user_id = user_data["user_id"]
    print(f"✅ 注册成功: user_id = {user_id}")

    # 登录
    login_resp = requests.post(f"{BASE_URL}/auth/login", data={
        "username": username,
        "password": password
    })

    if login_resp.status_code != 200:
        print(f"❌ 登录失败: {login_resp.text}")
        return

    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ 登录成功")

    # 2. 创建文件夹
    print("\n[Step 2] 创建收藏文件夹...")
    folder_resp = requests.post(f"{BASE_URL}/collections/folders", json={
        "teacher_id": user_id,
        "name": "测试文件夹",
        "color": "#1890ff"
    })

    if folder_resp.status_code != 200:
        print(f"❌ 创建文件夹失败: {folder_resp.text}")
        folder_id = None
    else:
        folder_data = folder_resp.json()
        folder_id = folder_data.get("folder_id")
        print(f"✅ 创建文件夹成功: folder_id = {folder_id}")

    # 3. 创建标签
    print("\n[Step 3] 创建收藏标签...")
    tag_resp = requests.post(f"{BASE_URL}/collections/tags", json={
        "teacher_id": user_id,
        "tag_name": "重要",
        "color": "#f5222d"
    })

    if tag_resp.status_code != 200:
        print(f"❌ 创建标签失败: {tag_resp.text}")
        tag_name = None
    else:
        tag_data = tag_resp.json()
        print(f"✅ 创建标签成功: tag_name = {tag_data.get('tag_name', '重要')}")
        tag_name = "重要"

    # 4. 上传图片并运行Pipeline（简化版：使用已存在的题目）
    print("\n[Step 4] 准备测试题目...")
    print("💡 提示：为了简化测试，我们将使用数据库中已存在的题目")
    print("💡 如果没有题目，请先运行完整的工作流测试（test_full_workflow.py）")

    # 尝试获取已有的试卷题目
    exams_resp = requests.get(f"{BASE_URL}/exams", headers=headers)
    exam_id = None
    question_id = None

    if exams_resp.status_code == 200:
        exams = exams_resp.json()
        # 检查 exams 的结构
        if isinstance(exams, list) and len(exams) > 0:
            exam_id = exams[0].get("exam_id")
            print(f"✅ 找到试卷: exam_id = {exam_id}")
        elif isinstance(exams, dict):
            # exams 可能是一个包含 exams 键的字典
            exams_list = exams.get("exams", [])
            if exams_list and len(exams_list) > 0:
                exam_id = exams_list[0].get("exam_id")
                print(f"✅ 找到试卷: exam_id = {exam_id}")

            # 获取题目列表
            if exam_id:
                questions_resp = requests.get(
                    f"{BASE_URL}/exams/{exam_id}/questions",
                    headers=headers
                )
                if questions_resp.status_code == 200:
                    questions = questions_resp.json().get("questions", [])
                    if questions and len(questions) > 0:
                        question_id = questions[0].get("question_id")
                        print(f"✅ 找到题目: question_id = {question_id}")

    if not exam_id or not question_id:
        print("\n⚠️  没有找到现有的题目和试卷")
        print("请运行完整的测试流程来创建题目:")
        print("  python backend/test_full_workflow.py")
        print("\n或者，我可以使用模拟数据进行测试演示...")

        # 使用模拟数据进行演示
        question_id = "mock_question_001"
        print(f"✅ 使用模拟题目ID: {question_id}")

    # 5. 收藏题目（正确的请求格式）
    print("\n[Step 5] 收藏题目（正确的请求格式）...")
    print("📝 请求格式要求：")
    print("  - teacher_id: 必须（用户ID）")
    print("  - question_id: 必须（题目ID）")
    print("  - folder_id: 可选（文件夹ID）")
    print("  - tags: 可选，但必须是数组格式 ['标签1', '标签2']")
    print("  - difficulty_note: 可选（难度备注）")
    print("  - teach_note: 可选（教学备注）")

    # 构建正确的请求体
    collect_request = {
        "teacher_id": user_id,  # ✅ 必需：用户ID
        "question_id": str(question_id),  # ✅ 必需：题目ID
        "folder_id": folder_id,  # ✅ 可选：文件夹ID
        "tags": [tag_name] if tag_name else ["测试"],  # ✅ 可选，但必须是数组！
        "difficulty_note": "中等难度",
        "teach_note": "这道题目考查了基本概念",
        "common_errors": "容易忽略特殊情况",
        "teach_points": "需要重点讲解解题思路"
    }

    print(f"\n📤 发送收藏请求:")
    print(json.dumps(collect_request, indent=2, ensure_ascii=False))

    coll_resp = requests.post(
        f"{BASE_URL}/collections",
        json=collect_request,
        headers=headers
    )

    if coll_resp.status_code == 200:
        print(f"✅ 收藏成功！")
        print(f"📥 响应: {coll_resp.json()}")
        collection_id = coll_resp.json().get("collection_id")
    elif coll_resp.status_code == 400:
        print(f"⚠️  业务逻辑错误: {coll_resp.json()}")
        print("💡 这可能是因为题目不存在或已经收藏过")
        collection_id = None
    else:
        print(f"❌ 收藏失败: {coll_resp.text}")
        collection_id = None

    # 6. 获取收藏列表
    if collection_id or exam_id:
        print("\n[Step 6] 获取收藏列表...")
        list_resp = requests.get(
            f"{BASE_URL}/collections?teacher_id={user_id}",
            headers=headers
        )

        if list_resp.status_code == 200:
            result = list_resp.json()
            collections = result.get("collections", [])
            total = result.get("total", 0)
            print(f"✅ 获取收藏列表成功！共 {total} 条收藏")
            for i, coll in enumerate(collections[:3], 1):  # 只显示前3条
                print(f"  {i}. {coll.get('title', '无标题')[:50]}")
        else:
            print(f"❌ 获取收藏列表失败: {list_resp.text}")

    # 7. 测试错误场景
    print("\n[Step 7] 测试错误请求场景...")
    print("=" * 60)

    # 错误1: 缺少 teacher_id
    print("\n❌ 错误1: 缺少 teacher_id")
    error_resp1 = requests.post(f"{BASE_URL}/collections", json={
        "question_id": "test_q"
    })
    print(f"   状态码: {error_resp1.status_code}")
    if error_resp1.status_code == 422:
        print("   ✅ 正确触发 422 验证错误")
        errors = error_resp1.json().get("detail", [])
        for err in errors:
            print(f"   - {err.get('loc')}: {err.get('msg')}")

    # 错误2: 缺少 question_id
    print("\n❌ 错误2: 缺少 question_id")
    error_resp2 = requests.post(f"{BASE_URL}/collections", json={
        "teacher_id": user_id
    })
    print(f"   状态码: {error_resp2.status_code}")
    if error_resp2.status_code == 422:
        print("   ✅ 正确触发 422 验证错误")
        errors = error_resp2.json().get("detail", [])
        for err in errors:
            print(f"   - {err.get('loc')}: {err.get('msg')}")

    # 错误3: tags 不是数组
    print("\n❌ 错误3: tags 不是数组")
    error_resp3 = requests.post(f"{BASE_URL}/collections", json={
        "teacher_id": user_id,
        "question_id": "test_q",
        "tags": "测试"  # ❌ 错误：应该是 ["测试"]
    })
    print(f"   状态码: {error_resp3.status_code}")
    if error_resp3.status_code == 422:
        print("   ✅ 正确触发 422 验证错误")
        errors = error_resp3.json().get("detail", [])
        for err in errors:
            print(f"   - {err.get('loc')}: {err.get('msg')}")

    print("\n" + "=" * 60)
    print("✅ 完整测试流程结束")
    print("=" * 60)
    print("\n💡 关键要点：")
    print("   1. POST /api/v1/collections 请求体必须包含 teacher_id 和 question_id")
    print("   2. tags 字段必须是数组格式，即使只有一个标签")
    print("   3. 所有可选字段都是可选的，但不要传错误类型")
    print("   4. 如果收到 422 错误，检查请求体格式是否符合规范")


if __name__ == "__main__":
    test_complete_collection_workflow()
