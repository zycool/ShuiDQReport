@echo off

echo  flying...
call "./venv/Scripts/activate"
echo.
cd bokeh_app
python main.py
echo.

pause