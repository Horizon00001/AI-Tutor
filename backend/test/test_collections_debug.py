import requests
import json

BASE_URL = 'http://localhost:8080/api/v1'

def test_collect_question_validation():
    """测试收藏接口的请求验证"""

    print("=== 测试收藏接口验证 ===\n")

    print("测试1: 正常请求（包含所有必需字段）")
    valid_request = {
        "teacher_id": "test_teacher_123",
        "question_id": "test_question_456",
        "difficulty_note": "中等难度",
        "teach_note": "这是一个测试",
        "tags": ["测试", "自动生成"]
    }

    resp = requests.post(f"{BASE_URL}/collections", json=valid_request)
    print(f"状态码: {resp.status_code}")
    if resp.status_code != 200:
        print(f"错误详情: {resp.text}")
        try:
            error_detail = resp.json()
            print(f"JSON 错误: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
        except:
            pass
    else:
        print(f"成功: {resp.json()}")
    print()

    print("测试2: 缺少 teacher_id")
    invalid_request_1 = {
        "question_id": "test_question_456"
    }
    resp = requests.post(f"{BASE_URL}/collections", json=invalid_request_1)
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 422:
        print("✓ 正确触发 422 验证错误")
        try:
            error_detail = resp.json()
            print(f"验证错误详情:")
            if 'detail' in error_detail:
                for err in error_detail['detail']:
                    print(f"  - 字段: {err.get('loc')}, 原因: {err.get('msg')}")
        except:
            pass
    print()

    print("测试3: 缺少 question_id")
    invalid_request_2 = {
        "teacher_id": "test_teacher_123"
    }
    resp = requests.post(f"{BASE_URL}/collections", json=invalid_request_2)
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 422:
        print("✓ 正确触发 422 验证错误")
        try:
            error_detail = resp.json()
            print(f"验证错误详情:")
            if 'detail' in error_detail:
                for err in error_detail['detail']:
                    print(f"  - 字段: {err.get('loc')}, 原因: {err.get('msg')}")
        except:
            pass
    print()

    print("测试4: 空对象")
    invalid_request_3 = {}
    resp = requests.post(f"{BASE_URL}/collections", json=invalid_request_3)
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 422:
        print("✓ 正确触发 422 验证错误")
        try:
            error_detail = resp.json()
            print(f"验证错误详情:")
            if 'detail' in error_detail:
                for err in error_detail['detail']:
                    print(f"  - 字段: {err.get('loc')}, 原因: {err.get('msg')}")
        except:
            pass
    print()

    print("测试5: 无效的 tags 类型（传入字符串而不是列表）")
    invalid_request_4 = {
        "teacher_id": "test_teacher_123",
        "question_id": "test_question_456",
        "tags": "测试"  # 应该是列表，而不是字符串
    }
    resp = requests.post(f"{BASE_URL}/collections", json=invalid_request_4)
    print(f"状态码: {resp.status_code}")
    if resp.status_code == 422:
        print("✓ 正确触发 422 验证错误（tags 应该是列表）")
        try:
            error_detail = resp.json()
            print(f"验证错误详情:")
            if 'detail' in error_detail:
                for err in error_detail['detail']:
                    print(f"  - 字段: {err.get('loc')}, 原因: {err.get('msg')}")
        except:
            pass
    print()

if __name__ == "__main__":
    test_collect_question_validation()
