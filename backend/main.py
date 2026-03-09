from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import asyncio
from scraper import get_all_data, get_global_markets, get_crypto_prices, auto_update_etf

app = FastAPI(title="GlobalMarket API")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# 全局数据缓存
cached_data = {}


@app.on_event("startup")
async def startup_event():
    """启动时加载数据"""
    global cached_data
    cached_data = get_all_data()
    print(f"启动完成，数据加载成功")


@app.get("/")
@app.head("/")
async def root():
    """返回前端页面"""
    return FileResponse("../frontend/index.html")


@app.get("/api/data")
async def get_data(background_tasks: BackgroundTasks):
    """获取所有数据"""
    global cached_data
    
    # 后台更新市场数据
    background_tasks.add_task(background_update)
    
    # 刷新实时数据
    cached_data['markets'] = get_global_markets()
    cached_data['crypto'] = get_crypto_prices()
    
    return {
        'data': cached_data,
        'server_time': datetime.now().isoformat()
    }


async def background_update():
    """后台自动更新"""
    try:
        # 更新 ETF 数据（工作日）
        weekday = datetime.now().weekday()
        if weekday < 5:  # 周一到周五
            for coin in ['btc', 'eth', 'sol', 'xrp']:
                success, msg = auto_update_etf(coin)
                print(f"[{datetime.now()}] {msg}")
    except Exception as e:
        print(f"[{datetime.now()}] 自动更新失败: {e}")


@app.get("/api/health")
@app.head("/api/health")
async def health_check():
    """健康检查"""
    return {
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
