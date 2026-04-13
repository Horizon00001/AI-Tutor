import requests

API_URL = "http://localhost:8080/api/v1/ai-chat/multi-turn"

test_messages = [
    {"role": "user", "content": "我需要讲解一道二次函数的题目：已知抛物线y=ax²+bx+c经过点(0,0)、(1,0)、(2,3)，求a、b、c的值。怎么讲学生更容易理解？"}
]

payload = {
    "messages": test_messages,
    "model": "deepseek-chat"
}

try:
    print("测试教师教学场景...\n")
    response = requests.post(API_URL, json=payload, timeout=120)

    if response.status_code == 200:
        result = response.json()
        print("✓ 请求成功!\n")
        print(f"AI回答:\n{result['answer']}")
    else:
        print(f"✗ 请求失败: {response.status_code}")
        print(f"错误信息: {response.text}")
except requests.exceptions.Timeout:
    print("✗ 请求超时，可能是DeepSeek API响应较慢")
except Exception as e:
    print(f"✗ 异常: {e}")
