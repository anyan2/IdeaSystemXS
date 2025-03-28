@echo off
REM PyInstaller����ű� - Windows�汾
REM �˽ű����ڽ�ideaSystemXS�����Windows��ִ�г���

echo ====================================================
echo        ideaSystemXS ����ű� (Windows)
echo ====================================================
echo.

REM ������⻷��
if not exist venv (
    echo ����: δ�ҵ����⻷������������ setup-env.bat �ű���
    exit /b 1
)

REM �������⻷��
echo �������⻷��...
call venv\Scripts\activate.bat

REM ���PyInstaller
echo ���PyInstaller...
pip show pyinstaller >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ��װPyInstaller...
    pip install pyinstaller
    if %ERRORLEVEL% neq 0 (
        echo ����: ��װPyInstallerʧ��
        exit /b 1
    )
)

REM �������Ŀ¼
if not exist dist (
    mkdir dist
)

REM ����ɵĹ����ļ�
echo ����ɵĹ����ļ�...
if exist build rmdir /s /q build
if exist dist\ideaSystemXS rmdir /s /q dist\ideaSystemXS

REM ����PyInstaller
echo ��ʼ���Ӧ�ó���...
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
    echo ����: PyInstaller���ʧ��
    exit /b 1
)

REM ���ƶ����ļ�
echo ���ƶ����ļ�...
copy README.md dist\ideaSystemXS\
copy LICENSE dist\ideaSystemXS\
mkdir dist\ideaSystemXS\data
mkdir dist\ideaSystemXS\config

REM ���������ű�
echo ���������ű�...
echo @echo off > dist\ideaSystemXS\start_ideaSystemXS.bat
echo start ideaSystemXS.exe >> dist\ideaSystemXS\start_ideaSystemXS.bat

REM ����ZIPѹ����
echo ����ZIPѹ����...
cd dist
powershell Compress-Archive -Path ideaSystemXS -DestinationPath ideaSystemXS.zip -Force
cd ..

echo.
echo ====================================================
echo        ������!
echo ====================================================
echo.
echo ��ִ�г���λ��: dist\ideaSystemXS\ideaSystemXS.exe
echo ZIPѹ����λ��: dist\ideaSystemXS.zip
echo.
echo �뽫ZIPѹ�������͸��û����û���ѹ���ֱ�����С�
echo.

REM �˳����⻷��
call deactivate
