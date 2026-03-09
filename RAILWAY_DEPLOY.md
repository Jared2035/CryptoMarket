# CryptoMarket Railway 部署配置

## 部署步骤

### 1. 创建 Railway 账号
- 访问 https://railway.app
- 点击 "Login" → 选择 "Continue with GitHub"
- 授权完成即可

### 2. 创建新项目
- 点击 "New Project"
- 选择 "Deploy from GitHub repo"
- 选择你的 CryptoMarket 仓库（需要先 push 到 GitHub）

### 3. 配置环境变量
在项目 Settings → Variables 中添加：
```
PORT=8000
```

### 4. 部署完成
Railway 会自动检测 Python 项目并部署

### 5. 获取域名
- 部署完成后，点击项目 → Settings → Domains
- 自动生成 `xxx.up.railway.app` 域名
- 或绑定自定义域名

## 注意事项

1. **免费额度**: 每月 $5 或 500 小时运行时间
2. **休眠机制**: 15 分钟无访问会休眠，下次访问需等待唤醒（约 10-30 秒）
3. **数据持久化**: 免费版重启后数据会丢失，建议：
   - 使用 Railway 的 Volume（付费）
   - 或定期手动更新数据文件

## 本地开发

```bash
cd backend
pip install -r requirements.txt
python main.py
```

访问 http://localhost:8000
