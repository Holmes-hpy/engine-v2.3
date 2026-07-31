# 数据库设计

## 核心表结构

### users (用户表)
| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PRIMARY KEY | 用户ID |
| email | VARCHAR(255) | UNIQUE NOT NULL | 邮箱 |
| username | VARCHAR(50) | UNIQUE NOT NULL | 用户名 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 |
| is_verified | BOOLEAN | DEFAULT false | 是否验证 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

### roles (角色表)
| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | UUID | PRIMARY KEY | 角色ID |
| name | VARCHAR(50) | UNIQUE NOT NULL | 角色名称 |
| description | TEXT | | 角色描述 |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW() | 更新时间 |

### user_roles (用户角色关联表)
| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| user_id | UUID | FOREIGN KEY | 用户ID |
| role_id | UUID | FOREIGN KEY | 角色ID |
| created_at | TIMESTAMP | DEFAULT NOW() | 创建时间 |
| PRIMARY KEY | (user_id, role_id) | | |

## 索引
- users(email)
- users(username)
- user_roles(user_id)
- user_roles(role_id)
