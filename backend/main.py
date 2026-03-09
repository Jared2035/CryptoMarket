from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import asyncio
from scraper import auto_update, get_all_data, get_crypto_prices

app = FastAPI(title="CryptoMarket API")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# 全局数据缓存
cached_data = {'btc': None, 'eth': None, 'prices': None}


@app.on_event("startup")
async def startup_event():
    """启动时加载数据"""
    global cached_data
    from scraper import load_data
    cached_data['btc'] = load_data('btc')
    cached_data['eth'] = load_data('eth')
    cached_data['prices'] = get_crypto_prices()
    print(f"启动完成，BTC: {cached_data['btc'] is not None}, ETH: {cached_data['eth'] is not None}")


@app.get("/")
@app.head("/")
async def root():
    """返回前端页面"""
    return FileResponse("../frontend/index.html")


@app.get("/api/data")
async def get_data(background_tasks: BackgroundTasks):
    """
    获取所有数据（BTC + ETH + 价格）
    后台自动检查是否需要更新
    """
    global cached_data
    
    # 后台触发自动更新检查
    background_tasks.add_task(background_auto_update)
    
    # 获取最新价格（每次访问都刷新）
    cached_data['prices'] = get_crypto_prices()
    
    return {
        'data': cached_data,
        'server_time': datetime.now().isoformat()
    }


@app.get("/api/prices")
async def get_prices():
    """获取实时价格"""
    prices = get_crypto_prices()
    if prices:
        return prices
    raise HTTPException(status_code=503, detail="价格数据暂时不可用")


async def background_auto_update():
    """后台自动更新任务"""
    global cached_data
    try:
        # 更新 BTC
        success, msg = auto_update('btc')
        if success:
            from scraper import load_data
            cached_data['btc'] = load_data('btc')
            print(f"[{datetime.now()}] BTC: {msg}")
        
        # 更新 ETH
        success, msg = auto_update('eth')
        if success:
            from scraper import load_data
            cached_data['eth'] = load_data('eth')
            print(f"[{datetime.now()}] ETH: {msg}")
            
    except Exception as e:
        print(f"[{datetime.now()}] 自动更新失败: {e}")


@app.post("/api/update")
async def manual_update():
    """手动触发更新"""
    global cached_data
    
    results = {}
    from scraper import load_data
    
    # 更新 BTC
    success, msg = auto_update('btc')
    results['btc'] = {'success': success, 'message': msg}
    if success:
        cached_data['btc'] = load_data('btc')
    
    # 更新 ETH
    success, msg = auto_update('eth')
    results['eth'] = {'success': success, 'message': msg}
    if success:
        cached_data['eth'] = load_data('eth')
    
    return {
        'results': results,
        'timestamp': datetime.now().isoformat()
    }


@app.get("/api/health")
@app.head("/api/health")
async def health_check():
    """健康检查"""
    return {
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'btc_loaded': cached_data['btc'] is not None,
        'eth_loaded': cached_data['eth'] is not None
    }
