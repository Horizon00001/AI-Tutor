# 获取提交信息，默认为 "sync: update project"
param (
    [string]$Message = "sync: update project"
)

Write-Host "--- 🚀 开始同步到 GitHub ---" -ForegroundColor Cyan

# 1. 添加更改
Write-Host "📦 正在暂存更改..."
git add .

# 2. 检查是否有更改需要提交
$status = git status --porcelain
if (-not $status) {
    Write-Host "✅ 没有发现任何更改，无需提交。" -ForegroundColor Green
} else {
    # 3. 提交更改
    Write-Host "💾 正在提交: $Message"
    git commit -m "$Message"
    
    # 4. 推送
    Write-Host "📤 正在推送到远程仓库..." -ForegroundColor Yellow
    git push
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "🎉 同步完成！" -ForegroundColor Green
    } else {
        Write-Host "❌ 推送失败，请检查网络或冲突。" -ForegroundColor Red
    }
}
