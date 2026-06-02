---
sidebar_position: 1
---

# Authentication

All API endpoints require a API key in the Authorization header.

## Register
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

## Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Response:**
```json
{
  "access_token": "autodoc_xxxx...",
  "token_type": "bearer"
}
```
