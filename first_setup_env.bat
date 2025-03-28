@echo off
rem 脚本目的：创建虚拟环境，激活它，然后安装 requirements.txt 中的依赖

rem 定义项目目录，这里假设脚本和 requirements.txt 文件在同一目录
set "project_dir=%~dp0"

rem 创建虚拟环境
python -m venv %project_dir%venv

rem 激活虚拟环境
call %project_dir%venv\Scripts\activate.bat

rem 安装 requirements.txt 中的依赖
python -m pip install -r %project_dir%requirements1.txt

rem 输出提示信息
echo 依赖安装完成，你可以开始开发啦！

rem 保持命令行窗口打开
pause    