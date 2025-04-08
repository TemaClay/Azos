@echo off
setlocal

curl -X POST http://127.0.0.1:8000/api/equipment/ ^
--data-binary "@temp.json" ^
-H "Content-Type: application/json; charset=utf-8"

endlocal