@echo off
REM AI Novel Generator 启动脚本
REM 使用虚拟环境中的Python运行

echo Starting AI Novel Generator...
echo.

REM 激活虚拟环境并运行主程序
call venv\Scripts\activate.bat
python main.py

pause
