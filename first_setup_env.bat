@echo off
rem �ű�Ŀ�ģ��������⻷������������Ȼ��װ requirements.txt �е�����

rem ������ĿĿ¼���������ű��� requirements.txt �ļ���ͬһĿ¼
set "project_dir=%~dp0"

rem �������⻷��
python -m venv %project_dir%venv

rem �������⻷��
call %project_dir%venv\Scripts\activate.bat

rem ��װ requirements.txt �е�����
python -m pip install -r %project_dir%requirements1.txt

rem �����ʾ��Ϣ
echo ������װ��ɣ�����Կ�ʼ��������

rem ���������д��ڴ�
pause    