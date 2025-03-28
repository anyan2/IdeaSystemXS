#!/bin/bash
# Windows版本的虚拟环境设置脚本

@echo off
REM 虚拟环境设置脚本
REM 此脚本用于创建Python虚拟环境并安装所需依赖

echo ====================================================
echo       ideaSystemXS 虚拟环境设置脚本
echo ====================================================
echo.

REM 检查Python版本
echo 检查Python版本...
python --version 2>nul
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Python。请安装Python 3.8或更高版本。
    exit /b 1
)

REM 检查pip
echo 检查pip...
pip --version 2>nul
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到pip。请确保pip已安装。
    exit /b 1
)

REM 检查venv模块
echo 检查venv模块...
python -c "import venv" 2>nul
if %ERRORLEVEL% neq 0 (
    echo 错误: venv模块未安装。请安装Python venv模块。
    exit /b 1
)

REM 创建虚拟环境
set VENV_DIR=venv
echo 创建虚拟环境 '%VENV_DIR%'...
if exist %VENV_DIR% (
    echo 虚拟环境目录已存在。是否要删除并重新创建? (y/n)
    set /p response=
    if /i "%response%"=="y" (
        echo 删除现有虚拟环境...
        rmdir /s /q %VENV_DIR%
    ) else (
        echo 使用现有虚拟环境
    )
)

if not exist %VENV_DIR% (
    python -m venv %VENV_DIR%
    if %ERRORLEVEL% neq 0 (
        echo 错误: 创建虚拟环境失败
        exit /b 1
    )
    echo 虚拟环境创建成功
)

REM 激活虚拟环境
echo 激活虚拟环境...
call %VENV_DIR%\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo 错误: 激活虚拟环境失败
    exit /b 1
)
echo 虚拟环境已激活

REM 升级pip
echo 升级pip...
pip install --upgrade pip
if %ERRORLEVEL% neq 0 (
    echo 警告: 升级pip失败，但将继续安装依赖
)

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo 错误: 安装依赖失败
    exit /b 1
)
echo 依赖安装成功

REM 完成
echo.
echo ====================================================
echo       虚拟环境设置完成!
echo ====================================================
echo.
echo 要激活此虚拟环境，请运行:
echo %VENV_DIR%\Scripts\activate.bat
echo.
echo 要退出虚拟环境，请运行:
echo deactivate
echo.

REM 保持窗口打开
pause
