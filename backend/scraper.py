"""
Farside BTC ETF 数据抓取模块（自动更新版本）
"""

import json
import os
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

DATA_FILE = os.path.join(os.path.dirname(__file__), 'btc_etf_data.json')

def parse_value(value_str):
    """解析数值，处理括号和逗号"""
    if not value_str or value_str == '-' or value_str == '':
        return 0
    cleaned = value_str.replace('(', '-').replace(')', '').replace(',', '')
    try:
        return float(cleaned)
    except ValueError:
        return 0


def scrape_btc_etf_flow():
    """
    尝试抓取 Farside BTC ETF Flow 数据
    如果失败返回 None
    """
    url = 'https://farside.co.uk/btc/'
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
                            result['daily_data'].append({
                                'date': date_str,
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
                        except (IndexError, ValueError):
                            continue
        
        result['last_updated'] = datetime.now().isoformat()
        return result
        
    except Exception as e:
        print(f"抓取失败: {e}")
        return None


def load_cached_data():
    """加载缓存数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_data(data):
    """保存数据到 JSON 文件"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def should_update_data():
    """
    判断是否应该更新数据
    规则：
    1. 工作日（周一到周五）
    2. 北京时间 10:00-12:00 或 12:00-14:00
    3. 数据不是今天的
    """
    now = datetime.now()
    weekday = now.weekday()  # 0=周一, 6=周日
    
    # 周末不更新
    if weekday >= 5:  # 周六或周日
        return False, "周末休市"
    
    # 加载现有数据
    data = load_cached_data()
    if not data or 'daily_data' not in data or len(data['daily_data']) == 0:
        return True, "无数据，需要抓取"
    
    # 检查最新数据日期
    latest_date_str = data['daily_data'][0]['date']
    
    # 解析日期（格式如 "06 Mar 2026"）
    try:
        latest_date = datetime.strptime(latest_date_str, '%d %b %Y')
    except:
        return True, "日期解析失败，尝试更新"
    
    # 如果最新数据就是今天，不需要更新
    if latest_date.date() == now.date():
        return False, "数据已是最新"
    
    # 北京时间 10:00 后允许更新
    hour = now.hour
    if hour >= 10:
        return True, f"需要更新（当前最新数据: {latest_date_str}）"
    
    return False, "未到更新时间"


def auto_update():
    """
    自动更新数据
    返回: (成功/失败, 消息)
    """
    should_update, reason = should_update_data()
    
    if not should_update:
        return False, f"跳过更新: {reason}"
    
    # 尝试抓取
    new_data = scrape_btc_etf_flow()
    
    if new_data and len(new_data['daily_data']) > 0:
        # 检查是否抓到了新数据
        latest_new = new_data['daily_data'][0]['date']
        
        # 加载旧数据对比
        old_data = load_cached_data()
        if old_data and len(old_data['daily_data']) > 0:
            latest_old = old_data['daily_data'][0]['date']
            
            if latest_new == latest_old:
                # 数据相同，只更新时间戳
                old_data['last_updated'] = datetime.now().isoformat()
                save_data(old_data)
                return True, f"数据未变化（最新: {latest_new}），已刷新时间戳"
        
        # 保存新数据
        save_data(new_data)
        return True, f"更新成功！最新数据: {latest_new}"
    
    return False, "抓取失败，保持现有数据"


# 兼容旧接口
def get_data():
    """获取数据（优先缓存）"""
    data = load_cached_data()
    if data:
        return data
    
    # 尝试抓取
    new_data = scrape_btc_etf_flow()
    if new_data:
        save_data(new_data)
        return new_data
    
    return None


if __name__ == '__main__':
    # 测试自动更新
    success, msg = auto_update()
    print(f"结果: {success}, 消息: {msg}")
