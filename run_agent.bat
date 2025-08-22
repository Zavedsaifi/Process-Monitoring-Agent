@echo off
echo Starting Process Monitor Agent...
echo.
echo This will collect system process information and send it to the backend.
echo Make sure the Django backend is running at http://localhost:8000
echo.
echo Press Ctrl+C to stop the agent.
echo.
pause

ProcessMonitorAgent.exe
pause
