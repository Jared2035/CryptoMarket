from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import asyncio
from scraper import get_data, auto_update, load_cached_data

app = FastAPI(title="CryptoMarket API")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# 全局数据缓存
cached_data = None
last_check = None


@app.on_event("startup")
async def startup_event():
    """启动时加载数据"""
    global cached_data
    cached_data = load_cached_data()
    print(f"启动完成，数据加载: {cached_data is not None}")


@app.get("/")
async def root():
    """返回前端页面"""
    return FileResponse("../frontend/index.html")


@app.get("/api/btc-etf-flow")
async def get_btc_etf_flow(background_tasks: BackgroundTasks):
    """
    获取 BTC ETF Flow 数据
    后台自动检查是否需要更新
    """
    global cached_data, last_check
    
    # 后台触发自动更新检查（不阻塞响应）
    background_tasks.add_task(background_auto_update)
    
    # 返回当前数据
    if cached_data is None:
        cached_data = load_cached_data()
    
    if cached_data is None:
        raise HTTPException(status_code=503, detail="数据暂时不可用")
    
    return {
        "data": cached_data,
        "last_updated": cached_data.get('last_updated'),
        "server_time": datetime.now().isoformat()
    }


async def background_auto_update():
    """后台自动更新任务"""
    global cached_data
    try:
        success, msg = auto_update()
        if success:
            # 重新加载数据
            cached_data = load_cached_data()
            print(f"[{datetime.now()}] 自动更新: {msg}")
    except Exception as e:
        print(f"[{datetime.now()}] 自动更新失败: {e}")


@app.post("/api/update")
async def manual_update():
    """手动触发更新"""
    global cached_data
    success, msg = auto_update()
    
    if success:
        cached_data = load_cached_data()
    
    return {
        "success": success,
        "message": msg,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "data_loaded": cached_data is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
