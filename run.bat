@echo off
echo ========================================
echo   Instalando dependencias...
echo ========================================
venv\Scripts\pip install -r requirements.txt

echo.
echo ========================================
echo   Iniciando o servidor Flask...
echo ========================================
echo.
echo Acesse: http://127.0.0.1:5000
echo.
venv\Scripts\python app.py

pause
