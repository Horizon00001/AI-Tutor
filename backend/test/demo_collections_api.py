"""
收藏API实际演示
"""
import requests
import random
import string
import json

BASE_URL = 'http://localhost:8080/api/v1'

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def demo_collections_api():
    print("=" * 70)
    print(" 🎯 收藏API功能演示")
    print("=" * 70)

    # 1. 注册登录
    print("\n📝 Step 1: 注册并登录...")
    username = f"demo_{generate_random_string()}"
    password = "demo123"

    reg_resp = requests.post(f"{BASE_URL}/auth/register", json={
        "username": username,
        "email": f"{username}@demo.com",
        "password": password
    })

    if reg_resp.status_code == 200:
        user_id = reg_resp.json()["user_id"]
        print(f"   ✅ 注册成功! user_id: {user_id}")
    else:
        print(f"   ❌ 注册失败: {reg_resp.text}")
        return

    login_resp = requests.post(f"{BASE_URL}/auth/login", data={
        "username": username,
        "password": password
    })

    if login_resp.status_code == 200:
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"   ✅ 登录成功!")
    else:
        print(f"   ❌ 登录失败")
        return

    # 2. 创建文件夹
    print("\n📁 Step 2: 创建收藏文件夹...")
    folder_resp = requests.post(f"{BASE_URL}/collections/folders", json={
        "teacher_id": user_id,
        "name": "期末复习资料",
        "color": "#1890ff"
    })

    if folder_resp.status_code == 200:
        folder_data = folder_resp.json()
        folder_id = folder_data.get("folder_id")
        print(f"   ✅ 创建文件夹成功!")
        print(f"   📂 folder_id: {folder_id}")
        print(f"   📝 文件夹名称: 期末复习资料")
    else:
        print(f"   ❌ 创建文件夹失败: {folder_resp.text}")
        folder_id = None

    # 3. 创建标签
    print("\n🏷️  Step 3: 创建收藏标签...")
    tags_data = [
        {"tag_name": "重要", "color": "#f5222d"},
        {"tag_name": "易错题", "color": "#faad14"},
        {"tag_name": "高频考点", "color": "#52c41a"}
    ]

    created_tags = []
    for tag_info in tags_data:
        tag_resp = requests.post(f"{BASE_URL}/collections/tags", json={
            "teacher_id": user_id,
            **tag_info
        })

        if tag_resp.status_code == 200:
            created_tags.append(tag_info["tag_name"])
            print(f"   ✅ 创建标签: {tag_info['tag_name']}")
        else:
            print(f"   ⚠️  标签 {tag_info['tag_name']} 已存在，跳过")

    # 4. 获取所有文件夹
    print("\n📂 Step 4: 获取文件夹列表...")
    folders_resp = requests.get(
        f"{BASE_URL}/collections/folders",
        params={"teacher_id": user_id}
    )

    if folders_resp.status_code == 200:
        folders = folders_resp.json()
        print(f"   ✅ 找到 {len(folders)} 个文件夹")
        for folder in folders:
            print(f"   📁 {folder['name']} (ID: {folder['folder_id'][:8]}...)")
    else:
        print(f"   ❌ 获取文件夹失败")

    # 5. 获取所有标签
    print("\n🏷️  Step 5: 获取标签列表...")
    tags_resp = requests.get(
        f"{BASE_URL}/collections/tags",
        params={"teacher_id": user_id}
    )

    if tags_resp.status_code == 200:
        tags = tags_resp.json()
        print(f"   ✅ 找到 {len(tags)} 个标签")
        for tag in tags:
            print(f"   🏷️  {tag['tag_name']} (使用次数: {tag['use_count']})")
    else:
        print(f"   ❌ 获取标签失败")

    # 6. 收藏题目（模拟）
    print("\n⭐ Step 6: 收藏题目...")
    print("   💡 由于没有真实题目，我们演示收藏接口的调用方式：")
    print("   📤 发送收藏请求...")

    # 尝试获取一个真实题目
    exams_resp = requests.get(f"{BASE_URL}/exams", headers=headers)
    question_id = None

    if exams_resp.status_code == 200:
        exams = exams_resp.json()
        if isinstance(exams, dict):
            exams = exams.get("exams", [])
        if isinstance(exams, list) and len(exams) > 0:
            exam_id = exams[0].get("exam_id") if isinstance(exams[0], dict) else exams[0]
            if exam_id:
                questions_resp = requests.get(
                    f"{BASE_URL}/exams/{exam_id}/questions",
                    headers=headers
                )
                if questions_resp.status_code == 200:
                    questions = questions_resp.json().get("questions", [])
                    if questions:
                        question_id = questions[0].get("question_id")

    if question_id:
        print(f"   ✅ 找到真实题目: {question_id[:20]}...")

        # 收藏真实题目
        collect_resp = requests.post(
            f"{BASE_URL}/collections",
            json={
                "teacher_id": user_id,
                "question_id": str(question_id),
                "folder_id": folder_id,
                "tags": ["重要", "高频考点"],
                "difficulty_note": "中等难度",
                "teach_note": "这道题目考查了基本概念的理解",
                "common_errors": "学生容易混淆概念",
                "teach_points": "重点讲解解题思路和方法"
            },
            headers=headers
        )

        if collect_resp.status_code == 200:
            print(f"   ✅ 收藏真实题目成功!")
            collection_id = collect_resp.json().get("collection_id")
            print(f"   🔖 collection_id: {collection_id}")
        else:
            print(f"   ⚠️  收藏失败: {collect_resp.text}")
            collection_id = None
    else:
        print("   ⚠️  没有找到真实题目，跳过实际收藏")
        print("   💡 收藏请求格式示例：")
        print("   ```json")
        print("   {")
        print('       "teacher_id": "{}",'.format(user_id))
        print('       "question_id": "真实题目UUID",')
        print('       "folder_id": "{}",'.format(folder_id))
        print('       "tags": ["重要", "高频考点"],')
        print('       "difficulty_note": "中等难度",')
        print('       "teach_note": "教学备注"')
        print("   }")
        print("   ```")
        collection_id = None

    # 7. 获取收藏列表
    print("\n📋 Step 7: 获取收藏列表...")
    list_resp = requests.get(
        f"{BASE_URL}/collections",
        params={"teacher_id": user_id}
    )

    if list_resp.status_code == 200:
        result = list_resp.json()
        total = result.get("total", 0)
        collections = result.get("collections", [])
        print(f"   ✅ 共 {total} 条收藏")

        if collections:
            print("   📚 收藏详情:")
            for coll in collections[:3]:  # 只显示前3条
                title = coll.get('title', '无标题')
                if len(title) > 40:
                    title = title[:40] + "..."
                print(f"   - {title}")
                if coll.get('tags'):
                    print(f"     🏷️  标签: {', '.join(coll.get('tags', []))}")
    else:
        print(f"   ❌ 获取收藏列表失败")

    # 8. 获取统计信息
    print("\n📊 Step 8: 获取收藏统计...")
    stats_resp = requests.get(
        f"{BASE_URL}/collections/stats/summary",
        params={"teacher_id": user_id}
    )

    if stats_resp.status_code == 200:
        stats = stats_resp.json()
        print(f"   ✅ 统计信息:")
        print(f"   📦 总收藏数: {stats.get('total_count', 0)}")
        print(f"   📁 文件夹数: {stats.get('folder_count', 0)}")
        print(f"   🏷️  标签数: {stats.get('tag_count', 0)}")
        print(f"   📅 本周新增: {stats.get('this_week_count', 0)}")
    else:
        print(f"   ❌ 获取统计失败")

    # 9. 测试查询功能
    print("\n🔍 Step 9: 测试查询功能...")
    print("   📂 按文件夹查询...")

    if folder_id:
        folder_list_resp = requests.get(
            f"{BASE_URL}/collections",
            params={
                "teacher_id": user_id,
                "folder_id": folder_id
            }
        )
        if folder_list_resp.status_code == 200:
            folder_colls = folder_list_resp.json()
            print(f"   ✅ 文件夹 '{folder_id[:8]}...' 中有 {folder_colls.get('total', 0)} 条收藏")

    print("   🏷️  按标签查询...")
    if created_tags:
        tag_list_resp = requests.get(
            f"{BASE_URL}/collections",
            params={
                "teacher_id": user_id,
                "tag": created_tags[0]
            }
        )
        if tag_list_resp.status_code == 200:
            tag_colls = tag_list_resp.json()
            print(f"   ✅ 标签 '{created_tags[0]}' 下有 {tag_colls.get('total', 0)} 条收藏")

    # 总结
    print("\n" + "=" * 70)
    print(" 🎉 演示完成!")
    print("=" * 70)
    print("\n📌 关键API总结:")
    print("   1. POST   /api/v1/collections           收藏题目")
    print("   2. GET    /api/v1/collections           获取收藏列表")
    print("   3. POST   /api/v1/collections/folders   创建文件夹")
    print("   4. GET    /api/v1/collections/folders   获取文件夹列表")
    print("   5. POST   /api/v1/collections/tags      创建标签")
    print("   6. GET    /api/v1/collections/tags      获取标签列表")
    print("   7. GET    /api/v1/collections/stats/summary  获取统计")
    print("\n💡 收藏题目必需字段: teacher_id, question_id")
    print("💡 tags 必须是数组格式: ['标签1', '标签2']")
    print("=" * 70)

if __name__ == "__main__":
    demo_collections_api()
