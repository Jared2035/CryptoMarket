# GlobalMarket

全球金融市场实时监控平台

## 功能

- **核心指标**：美元指数、VIX恐慌指数、原油、黄金、美债10年
- **全球股指**：标普500、道指、纳指、日经225、韩国KOSPI、恒生、上证、德国DAX、英国FTSE、法国CAC
- **加密货币**：BTC、ETH、SOL、XRP 实时价格
- **ETF数据**：BTC、ETH、SOL、XRP ETF 资金流向

## 数据源

- Yahoo Finance（全球股指、大宗商品）
- CoinGecko（加密货币价格）
- Farside（BTC/ETH/SOL ETF）
- SosoValue（XRP ETF）

## 本地运行

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

访问 http://localhost:8000

## 部署

Railway 自动部署
