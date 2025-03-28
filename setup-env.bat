#!/bin/bash
# Windows�汾�����⻷�����ýű�

@echo off
REM ���⻷�����ýű�
REM �˽ű����ڴ���Python���⻷������װ��������

echo ====================================================
echo       ideaSystemXS ���⻷�����ýű�
echo ====================================================
echo.

REM ���Python�汾
echo ���Python�汾...
python --version 2>nul
if %ERRORLEVEL% neq 0 (
    echo ����: δ�ҵ�Python���밲װPython 3.8����߰汾��
    exit /b 1
)

REM ���pip
echo ���pip...
pip --version 2>nul
if %ERRORLEVEL% neq 0 (
    echo ����: δ�ҵ�pip����ȷ��pip�Ѱ�װ��
    exit /b 1
)

REM ���venvģ��
echo ���venvģ��...
python -c "import venv" 2>nul
if %ERRORLEVEL% neq 0 (
    echo ����: venvģ��δ��װ���밲װPython venvģ�顣
    exit /b 1
)

REM �������⻷��
set VENV_DIR=venv
echo �������⻷�� '%VENV_DIR%'...
if exist %VENV_DIR% (
    echo ���⻷��Ŀ¼�Ѵ��ڡ��Ƿ�Ҫɾ�������´���? (y/n)
    set /p response=
    if /i "%response%"=="y" (
        echo ɾ���������⻷��...
        rmdir /s /q %VENV_DIR%
    ) else (
        echo ʹ���������⻷��
    )
)

if not exist %VENV_DIR% (
    python -m venv %VENV_DIR%
    if %ERRORLEVEL% neq 0 (
        echo ����: �������⻷��ʧ��
        exit /b 1
    )
    echo ���⻷�������ɹ�
)

REM �������⻷��
echo �������⻷��...
call %VENV_DIR%\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo ����: �������⻷��ʧ��
    exit /b 1
)
echo ���⻷���Ѽ���

REM ����pip
echo ����pip...
pip install --upgrade pip
if %ERRORLEVEL% neq 0 (
    echo ����: ����pipʧ�ܣ�����������װ����
)

REM ��װ����
echo ��װ����...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ����: ��װ����ʧ��
    exit /b 1
)
echo ������װ�ɹ�

REM ���
echo.
echo ====================================================
echo       ���⻷���������!
echo ====================================================
echo.
echo Ҫ��������⻷����������:
echo %VENV_DIR%\Scripts\activate.bat
echo.
echo Ҫ�˳����⻷����������:
echo deactivate
echo.

REM ���ִ��ڴ�
pause
