from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from scraper import scrape_btc_etf_flow, load_cached_data
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = FastAPI(title="CryptoMarket API")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# 缓存数据
cached_data = None
last_update = None
executor = ThreadPoolExecutor(max_workers=1)


@app.get("/")
async def root():
    """返回前端页面"""
    return FileResponse("../frontend/index.html")


@app.get("/api/btc-etf-flow")
async def get_btc_etf_flow():
    """
    获取 BTC ETF Flow 数据
    如果缓存过期，自动重新抓取
    """
    global cached_data, last_update
    
    # 检查是否需要更新（每5分钟）
    need_update = True
    if last_update:
        elapsed = (datetime.now() - last_update).total_seconds()
        if elapsed < 300:  # 5分钟
            need_update = False
    
    if need_update or cached_data is None:
        # 使用线程池运行同步的抓取函数
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(executor, scrape_btc_etf_flow)
        
        if data:
            cached_data = data
            last_update = datetime.now()
        else:
            # 如果抓取失败，尝试使用缓存数据
            cached_data = load_cached_data()
            if cached_data is None:
                raise HTTPException(status_code=503, detail="数据暂时不可用")
    
    return {
        "data": cached_data,
        "last_update": last_update.isoformat() if last_update else None,
        "next_update_in": max(0, 300 - (datetime.now() - last_update).total_seconds()) if last_update else 0
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
