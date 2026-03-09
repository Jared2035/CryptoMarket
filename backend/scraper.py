"""
Farside BTC ETF 数据抓取模块
由于网站有反爬，使用浏览器手动抓取后保存的数据
"""

import json
import os
from datetime import datetime


def scrape_btc_etf_flow():
    """
    加载已保存的 BTC ETF Flow 数据
    实际抓取通过 browser 工具手动完成，保存到 btc_etf_data.json
    """
    return load_cached_data()


def load_cached_data(filename='btc_etf_data.json'):
    """加载缓存数据"""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 更新最后更新时间
            data['last_updated'] = datetime.now().isoformat()
            return data
    return None


def save_data(data, filename='btc_etf_data.json'):
    """保存数据到 JSON 文件"""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存到 {filepath}")


if __name__ == '__main__':
    print("加载 BTC ETF 数据...")
    data = scrape_btc_etf_flow()
    
    if data:
        print(f"成功加载 {len(data['daily_data'])} 天数据")
        print(f"最新数据日期: {data['daily_data'][0]['date']}")
        print(f"最新总流入: ${data['daily_data'][0]['total']}M")
    else:
        print("数据加载失败")
