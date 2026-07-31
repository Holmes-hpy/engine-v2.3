# API规范

## 通用信息
- **基础URL**: https://api.example.com/v1
- **数据格式**: JSON
- **认证方式**: Bearer Token
- **请求头**:
  - Content-Type: application/json
  - Authorization: Bearer {token}

## 响应格式
### 成功响应
```json
{
  "success": true,
  "data": {
    // 响应数据
  },
  "message": "操作成功"
}
```

### 错误响应

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  },
  "message": "操作失败"
}
```

## 状态码

- 200 OK: 请求成功
- 201 Created: 资源创建成功
- 400 Bad Request: 请求参数错误
- 401 Unauthorized: 未认证
- 403 Forbidden: 权限不足
- 404 Not Found: 资源不存在
- 500 Internal Server Error: 服务器内部错误

## 核心 API 示例

### 获取用户信息

- **URL**: GET /users/{id}
- **参数**: id (路径参数)
- **响应**:

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "created_at": "2023-01-01T00:00:00Z"
  }
}
```

