@echo off
setlocal

echo Installing dependencies...
call npm install
if %ERRORLEVEL% neq 0 (
  echo Failed to install dependencies. Please make sure Node.js is installed.
  pause
  exit /b 1
)

echo Starting server...
start "" http://localhost:3000
node src\server.js

endlocal
