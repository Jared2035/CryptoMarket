"""
Farside ETF 数据抓取模块（支持 BTC 和 ETH）
"""

import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

DATA_DIR = os.path.dirname(__file__)


def parse_value(value_str):
    """解析数值，处理括号和逗号"""
    if not value_str or value_str == '-' or value_str == '':
        return 0
    cleaned = value_str.replace('(', '-').replace(')', '').replace(',', '')
    try:
        return float(cleaned)
    except ValueError:
        return 0


def scrape_etf_flow(coin='btc'):
    """
    抓取 Farside ETF Flow 数据
    
    Args:
        coin: 'btc' 或 'eth'
    
    Returns:
        dict: ETF 数据
    """
    url = f'https://farside.co.uk/{coin}/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        tables = soup.find_all('table')
        
        if len(tables) < 2:
            return None
        
        target_table = tables[1]
        result = {'headers': [], 'daily_data': [], 'summary': {}}
        
        # 获取表头
        header_row = target_table.find('thead')
        if header_row:
            headers = header_row.find_all('th')
            result['headers'] = [h.get_text(strip=True) for h in headers]
        
        # 获取数据行
        tbody = target_table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) > 0:
                    row_data = [c.get_text(strip=True) for c in cells]
                    date_str = row_data[0]
                    
                    if date_str in ['Total', 'Average', 'Maximum', 'Minimum']:
                        result['summary'][date_str] = row_data
                    else:
                        try:
                            # 动态解析列数（BTC 和 ETH 列数不同）
                            data_row = {'date': date_str}
                            
                            # 根据 coin 类型解析不同的列
                            if coin == 'btc':
                                data_row.update({
                                    'blackrock': parse_value(row_data[1]),
                                    'fidelity': parse_value(row_data[2]),
                                    'bitwise': parse_value(row_data[3]),
                                    'ark': parse_value(row_data[4]),
                                    'invesco': parse_value(row_data[5]),
                                    'franklin': parse_value(row_data[6]),
                                    'valkyrie': parse_value(row_data[7]),
                                    'vaneck': parse_value(row_data[8]),
                                    'wtree': parse_value(row_data[9]),
                                    'grayscale_gb': parse_value(row_data[10]),
                                    'grayscale_btc': parse_value(row_data[11]),
                                    'total': parse_value(row_data[12])
                                })
                            elif coin == 'eth':
                                data_row.update({
                                    'blackrock': parse_value(row_data[1]),
                                    'fidelity': parse_value(row_data[2]),
                                    'bitwise': parse_value(row_data[3]),
                                    'shares21': parse_value(row_data[4]),
                                    'vaneck': parse_value(row_data[5]),
                                    'invesco': parse_value(row_data[6]),
                                    'franklin': parse_value(row_data[7]),
                                    'grayscale_et': parse_value(row_data[8]),
                                    'grayscale_eth': parse_value(row_data[9]),
                                    'total': parse_value(row_data[10])
                                })
                            
                            result['daily_data'].append(data_row)
                        except (IndexError, ValueError):
                            continue
        
        result['last_updated'] = datetime.now().isoformat()
        return result
        
    except Exception as e:
        print(f"抓取 {coin.upper()} 失败: {e}")
        return None


def get_crypto_prices():
    """
    获取 BTC 和 ETH 实时价格（CoinGecko 免费 API）
    """
    try:
        url = 'https://api.coingecko.com/api/v3/simple/price'
        params = {
            'ids': 'bitcoin,ethereum',
            'vs_currencies': 'usd',
            'include_24hr_change': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            'btc': {
                'price': data['bitcoin']['usd'],
                'change_24h': data['bitcoin'].get('usd_24h_change', 0)
            },
            'eth': {
                'price': data['ethereum']['usd'],
                'change_24h': data['ethereum'].get('usd_24h_change', 0)
            },
            'last_updated': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"获取价格失败: {e}")
        return None


def load_data(coin='btc'):
    """加载缓存数据"""
    filepath = os.path.join(DATA_DIR, f'{coin}_etf_data.json')
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_data(data, coin='btc'):
    """保存数据到 JSON 文件"""
    filepath = os.path.join(DATA_DIR, f'{coin}_etf_data.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def auto_update(coin='btc'):
    """
    自动更新数据
    返回: (成功/失败, 消息)
    """
    now = datetime.now()
    weekday = now.weekday()
    
    # 周末不更新
    if weekday >= 5:
        return False, f"{coin.upper()}: 周末休市"
    
    # 加载现有数据
    old_data = load_data(coin)
    
    # 尝试抓取
    new_data = scrape_etf_flow(coin)
    
    if new_data and len(new_data['daily_data']) > 0:
        latest_new = new_data['daily_data'][0]['date']
        
        if old_data and len(old_data['daily_data']) > 0:
            latest_old = old_data['daily_data'][0]['date']
            
            if latest_new == latest_old:
                # 数据相同，只更新时间戳
                old_data['last_updated'] = datetime.now().isoformat()
                save_data(old_data, coin)
                return True, f"{coin.upper()}: 数据未变化（{latest_new}）"
        
        # 保存新数据
        save_data(new_data, coin)
        return True, f"{coin.upper()}: 更新成功（{latest_new}）"
    
    return False, f"{coin.upper()}: 抓取失败"


def get_all_data():
    """获取所有数据（BTC + ETH + 价格）"""
    return {
        'btc': load_data('btc'),
        'eth': load_data('eth'),
        'prices': get_crypto_prices()
    }


if __name__ == '__main__':
    # 测试
    print("测试 BTC 抓取...")
    result = auto_update('btc')
    print(result)
    
    print("\n测试 ETH 抓取...")
    result = auto_update('eth')
    print(result)
    
    print("\n测试价格获取...")
    prices = get_crypto_prices()
    print(prices)
