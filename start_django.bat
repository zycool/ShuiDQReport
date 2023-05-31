@echo off

echo  flying...
call "./venv/Scripts/activate"
echo.

python manage.py runserver 192.168.100.2:80

echo.

pause