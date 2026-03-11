from scraper import scrape_farside_etf_with_playwright, get_crypto_prices

print("=== 测试BTC ETF (Playwright) ===")
btc = scrape_farside_etf_with_playwright('btc')
if btc:
    print(f"成功获取 {len(btc.get('daily_data', []))} 条数据")
    if btc.get('daily_data'):
        print("最新数据:", btc['daily_data'][0])
else:
    print("获取失败")

print("\n=== 测试ETH ETF (Playwright) ===")
eth = scrape_farside_etf_with_playwright('eth')
if eth:
    print(f"成功获取 {len(eth.get('daily_data', []))} 条数据")
else:
    print("获取失败")
