@echo off
REM PyInstaller打包脚本 - Windows版本
REM 此脚本用于将ideaSystemXS打包成Windows可执行程序

echo ====================================================
echo        ideaSystemXS 打包脚本 (Windows)
echo ====================================================
echo.

REM 检查虚拟环境
if not exist venv (
    echo 错误: 未找到虚拟环境。请先运行 setup-env.bat 脚本。
    exit /b 1
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查PyInstaller
echo 检查PyInstaller...
pip show pyinstaller >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 安装PyInstaller...
    pip install pyinstaller
    if %ERRORLEVEL% neq 0 (
        echo 错误: 安装PyInstaller失败
        exit /b 1
    )
)

REM 创建输出目录
if not exist dist (
    mkdir dist
)

REM 清理旧的构建文件
echo 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist\ideaSystemXS rmdir /s /q dist\ideaSystemXS

REM 运行PyInstaller
echo 开始打包应用程序...
pyinstaller --noconfirm --clean ^
    --name="ideaSystemXS" ^
    --icon=src/ui/resources/icon.ico ^
    --add-data="src/ui/resources;src/ui/resources" ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=sqlite3 ^
    --hidden-import=chromadb ^
    --hidden-import=numpy ^
    --hidden-import=openai ^
    --windowed ^
    src/main.py

if %ERRORLEVEL% neq 0 (
    echo 错误: PyInstaller打包失败
    exit /b 1
)

REM 复制额外文件
echo 复制额外文件...
copy README.md dist\ideaSystemXS\
copy LICENSE dist\ideaSystemXS\
mkdir dist\ideaSystemXS\data
mkdir dist\ideaSystemXS\config

REM 创建启动脚本
echo 创建启动脚本...
echo @echo off > dist\ideaSystemXS\start_ideaSystemXS.bat
echo start ideaSystemXS.exe >> dist\ideaSystemXS\start_ideaSystemXS.bat

REM 创建ZIP压缩包
echo 创建ZIP压缩包...
cd dist
powershell Compress-Archive -Path ideaSystemXS -DestinationPath ideaSystemXS.zip -Force
cd ..

echo.
echo ====================================================
echo        打包完成!
echo ====================================================
echo.
echo 可执行程序位于: dist\ideaSystemXS\ideaSystemXS.exe
echo ZIP压缩包位于: dist\ideaSystemXS.zip
echo.
echo 请将ZIP压缩包发送给用户，用户解压后可直接运行。
echo.

REM 退出虚拟环境
call deactivate
