# CryptoMarket

实时加密货币市场数据展示平台

## 快速开始

### 本地运行
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

访问 http://localhost:8000

### Railway 部署
1. Fork 本仓库到你的 GitHub
2. 登录 https://railway.app（用 GitHub 账号）
3. 创建 New Project → Deploy from GitHub repo
4. 选择本仓库，自动部署

## 项目结构
```
CryptoMarket/
├── backend/
│   ├── main.py           # FastAPI 后端
│   ├── scraper.py        # 数据抓取
│   └── btc_etf_data.json # 数据文件
├── frontend/             # 前端文件
├── requirements.txt      # Python 依赖
├── railway.json          # Railway 配置
└── README.md
```

## 数据来源
- Farside BTC ETF Flow: https://farside.co.uk/btc/

## 技术栈
- 后端: Python + FastAPI
- 前端: HTML + CSS + JavaScript
- 部署: Railway (免费)
