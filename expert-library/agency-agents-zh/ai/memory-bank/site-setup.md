# 网站配置

## 域名信息
- **主域名**: example.com
- **开发环境**: dev.example.com
- **测试环境**: test.example.com
- **生产环境**: example.com
- **管理后台**: admin.example.com
- **API域名**: api.example.com

## 服务器配置
### 开发环境
- **服务器**: [服务器IP]
- **操作系统**: Ubuntu 22.04 LTS
- **SSH端口**: 22
- **用户名**: ubuntu
- **部署目录**: /var/www/dev.example.com

### 生产环境
- **服务器**: [服务器IP]
- **操作系统**: Ubuntu 22.04 LTS
- **SSH端口**: 22
- **用户名**: ubuntu
- **部署目录**: /var/www/example.com

## 环境变量
### 通用环境变量
- NODE_ENV: development | test | production
- PORT: 3000
- API_BASE_URL: https://api.example.com

### 数据库环境变量
- DB_HOST: localhost
- DB_PORT: 5432
- DB_NAME: [数据库名]
- DB_USER: [数据库用户名]
- DB_PASSWORD: [数据库密码]

### 第三方服务
- SENDGRID_API_KEY: [SendGrid API Key]
- AWS_ACCESS_KEY_ID: [AWS Access Key]
- AWS_SECRET_ACCESS_KEY: [AWS Secret Key]
- STRIPE_PUBLIC_KEY: [Stripe公钥]
- STRIPE_SECRET_KEY: [Stripe私钥]

## SSL证书
- 证书提供商: Let's Encrypt
- 自动续期: 是
- 证书路径: /etc/letsencrypt/live/example.com/

## Nginx配置
- 配置文件路径: /etc/nginx/sites-available/example.com
- 日志路径: /var/log/nginx/
