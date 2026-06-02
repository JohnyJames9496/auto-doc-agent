---
sidebar_position: 2
---

# Documentation API

## Request Documentation
```http
POST /api/v1/documentation
Authorization: Bearer <token>
Content-Type: application/json

{
  "file_path": "src/utils.py",
  "function_name": "calculate_area",
  "code_snippet": "def calculate_area(radius):\n    return 3.14 * radius * radius",
  "language": "python",
  "project_id": "your-project-id"
}
```

**Response:**
```json
{
  "task_id": "abc123",
  "status": "queued"
}
```

## Poll Task Result
```http
GET /api/v1/documentation/task/{task_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "function_name": "calculate_area",
  "documentation": "### `calculate_area`\n\nCalculates area of a circle...",
  "status": "complete"
}
```
