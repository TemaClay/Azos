@echo off
setlocal

set "json_data={"
set "json_data=%json_data% \"action\": \"insert\","
set "json_data=%json_data% \"equipment\": {"
set "json_data=%json_data% \"article\": \"001\","
set "json_data=%json_data% \"inventory_number\": \"000\","
set "json_data=%json_data% \"name\": \"Новое оборудование8\","
set "json_data=%json_data% \"location\": 2,"
set "json_data=%json_data% \"status\": 2,"
set "json_data=%json_data% \"commissioning_date\": \"2024-01-01\","
set "json_data=%json_data% \"Equipment_manager\": \"Иванов И.И.\""
set "json_data=%json_data% }"
set "json_data=%json_data% }"

curl -v -X POST http://127.0.0.1:8000/api/equipment/ ^
-H "Content-Type: application/json" ^
-H "Authorization: Bearer your_actual_token_here" ^
--data-binary "%json_data%"

endlocal