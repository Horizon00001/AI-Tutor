import requests
import json

API_URL = "http://localhost:8080/api/v1/ai-chat/multi-turn"

multi_turn_messages = [
    {"role": "user", "content": "什么是二次函数？"},
    {"role": "assistant", "content": "二次函数是形如 f(x) = ax² + bx + c（其中 a ≠ 0）的函数。\n\n它的图像是一条抛物线，\n- 当 a > 0 时，抛物线开口向上\n- 当 a < 0 时，抛物线开口向下\n\n二次函数在物理学、工程学、经济学等领域都有广泛应用。"},
    {"role": "user", "content": "能给我举个例子吗？"}
]

payload = {
    "messages": multi_turn_messages,
    "model": "deepseek-chat"
}

try:
    print("测试多轮对话（上下文记忆）...")
    response = requests.post(API_URL, json=payload, timeout=30)

    if response.status_code == 200:
        result = response.json()
        print("✓ 请求成功!")
        print(f"\n对话历史:")
        for i, msg in enumerate(multi_turn_messages):
            role = "用户" if msg['role'] == 'user' else "AI"
            content = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
            print(f"  {i+1}. [{role}]: {content}")

        print(f"\n最新AI回答: {result['answer']}")
        if result.get('usage'):
            print(f"\nToken使用: {result['usage']}")
    else:
        print(f"✗ 请求失败: {response.status_code}")
        print(f"错误信息: {response.text}")
except Exception as e:
    print(f"✗ 异常: {e}")
