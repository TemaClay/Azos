@echo off
setlocal
chcp 65001 > nul

:: Step 1: Get JWT token
echo Getting JWT token...
curl -X POST http://localhost:8000/api/token/ ^
     -H "Content-Type: application/json; charset=utf-8" ^
     -d "{\"username\": \"Наталия\", \"password\": \"#P21v0!D\"}" ^
     -o token_response.json 2>nul

:: Step 2: Parse JSON properly using PowerShell
for /f "delims=" %%i in ('powershell -command "(Get-Content -Raw token_response.json) | ConvertFrom-Json | Select-Object -ExpandProperty access"') do (
    set "access_token=%%i"
)

echo %access_token%

if "%access_token%"=="" (
    echo Failed to extract access token from response
    type token_response.json
    del token_response.json
    exit /b 1
)

del token_response.json

echo Successfully obtained access token: %access_token%

:: Step 3: Use the token in API request
echo Making API request with the token...
curl -X POST http://127.0.0.1:8000/api/equipment/ ^
     --data-binary "@temp.json" ^
     -H "Authorization: Bearer %access_token%" ^
     -H "Content-Type: application/json; charset=utf-8"

endlocal
pause