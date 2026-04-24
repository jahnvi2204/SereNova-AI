@echo off
echo ========================================
echo Starting SeraNova AI Development Servers
echo ========================================
echo.

echo [1/2] Starting Flask Backend...
start "Flask Backend" cmd /k "cd backend && .\venv\Scripts\activate && python server.py"

timeout /t 3 /nobreak >nul

echo [2/2] Starting React Frontend...
<<<<<<< HEAD
start "React Frontend" cmd /k "cd frontend && npm start"
=======
start "React Frontend" cmd /k "cd frontend_1 && npm start"
>>>>>>> 9b714ecfe3f2dbb84015c29a62856b5d69863a63

echo.
echo ========================================
echo Both servers are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo ========================================
echo.
echo Press any key to exit (servers will continue running)...
pause >nul

