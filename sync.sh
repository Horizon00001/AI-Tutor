#!/bin/bash

# 获取提交信息，默认为 "sync: update project"
MESSAGE=${1:-"sync: update project"}

echo "--- 🚀 开始同步到 GitHub ---"

# 1. 添加更改
echo "📦 正在暂存更改..."
git add .

# 2. 检查是否有更改需要提交
if git diff-index --quiet HEAD --; then
    echo "✅ 没有发现任何更改，无需提交。"
else
    # 3. 提交更改
    echo "💾 正在提交: $MESSAGE"
    git commit -m "$MESSAGE"
    
    # 4. 推送
    echo "📤 正在推送到远程仓库..."
    git push
    
    if [ $? -eq 0 ]; then
        echo "🎉 同步完成！"
    else
        echo "❌ 推送失败，请检查网络或冲突。"
    fi
fi
