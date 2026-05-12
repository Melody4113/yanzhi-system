@echo off
title 顏值從齒開始 - ROG Strix 離線版啟動器
echo 正在啟動 ROG 離線 AI 系統...

:: 1. 偵測本機 IP
for /f "tokens=4 delims= " %%i in ('route print ^| findstr 0.0.0.0 ^| findstr /v "127.0.0.1"') do set localip=%%i

echo ========================================
echo 活動名稱：顏值從齒開始 (離線 AI 版)
echo 電腦 IP：%localip%
echo 學生掃碼網址：http://%localip%:8000
echo 大螢幕網址：http://localhost:8000/screen
echo ========================================

:: 2. 自動開啟大螢幕看板
start http://localhost:8000/screen

:: 3. 執行 Python 程式 (直接執行同資料夾下的 main.py)
python main.py

pause