@echo off
echo ===================================
echo CryptoMarket 一键推送工具
echo ===================================
echo.

cd /d C:\Users\jared\.openclaw\workspace\CryptoMarket

echo [1/3] 添加文件...
git add .

echo [2/3] 提交更改...
git commit -m "添加 ETH 数据、实时价格显示"

echo [3/3] 推送到 GitHub...
git push origin main

echo.
echo ===================================
echo 推送完成！
echo 等待 Railway 自动部署（约 1-2 分钟）
echo 访问: https://cryptomarket-production.up.railway.app
echo ===================================
pause
