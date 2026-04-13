import requests

API_URL = "http://localhost:8080/api/v1/ai-chat/multi-turn"

test_messages = [
    {"role": "user", "content": "你好，请介绍一下你自己"}
]

payload = {
    "messages": test_messages,
    "model": "deepseek-chat"
}

try:
    print("测试带提示词的AI助手...")
    response = requests.post(API_URL, json=payload, timeout=30)

    if response.status_code == 200:
        result = response.json()
        print("✓ 请求成功!\n")
        print(f"AI回答:\n{result['answer']}")
    else:
        print(f"✗ 请求失败: {response.status_code}")
        print(f"错误信息: {response.text}")
except Exception as e:
    print(f"✗ 异常: {e}")
