curl -X POST http://127.0.0.1:8000/api/equipment/ \
-H "Content-Type: application/json" \
-H "Authorization: Bearer your_token" \
-d '{"action": "insert", "equipment": {"article": "TEST-001"}}'