#!/bin/bash
# Test login script

echo "Testing login endpoint..."
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@anwalts.ai",
    "password": "Test1234"
  }' | python3 -m json.tool

echo -e "\n\nLogin test complete"
