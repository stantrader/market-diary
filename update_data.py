import yfinance as yf
import json
import math
import os
from datetime import datetime

# Словарь имен
NAMES_MAP = {
    'IJS': 'Small Cap Value', 'IJR': 'Small Cap Core', 'IJT': 'Small Cap Growth',
    'IJJ': 'Mid Cap Value', 'IJH': 'Mid Cap Core', 'IJK': 'Mid Cap Growth',
    'IVV': 'S&P 500 Core', 'IVW': 'S&P 500 Growth', 'IVE': 'S&P 500 Value',
    'RSPT': 'Tech', 'RSPD': 'Cons Discretionary', 'RSPC': 'Communication',
    'RSPR': 'Real Estate', 'RSPH': 'Healthcare', 'RSPN': 'Industrials',
    'RSPF': 'Financials', 'RSPG': 'Cons Staples', 'RSPM': 'Materials',
    'RSPU': 'Utilities', 'RSPS': 'Energy', 'RSP': 'S&P 500 EW',
    'FXI': 'China Large Cap', 'GXC': 'China All Shares', 'FFTY': 'IBD 50',
    'XHB': 'Homebuilders', 'CIBR': 'Cybersecurity', 'PBJ': 'Food & Beverage',
    'XRT': 'Retail', 'IBUY': 'Online Retail', 'DRIV': 'Autonomous & EV',
    'WCLD': 'Cloud Computing', 'PEJ': 'Leisure & Ent', 'XTL': 'Telecom',
    'XSW': 'Software', 'KIE': 'Insurance', 'QQQE': 'Nasdaq 100 EW',
    'IPAY': 'Mobile Payments', 'USO': 'Oil (WTI)', 'KCE': 'Capital Markets',
    'ROBO': 'Robotics & AI', 'GNR': 'Natural Resources', 'BOAT': 'Shipping',
    'XOP': 'Oil & Gas Expl', 'FCG': 'Natural Gas', 'BUZZ': 'Social Sentiment',
    'XHS': 'Health Services', 'PAVE': 'Infrastructure', 'MOD': 'Momentum',
    'KBE': 'Banks', 'GBTC': 'Bitcoin Trust', 'XTN': 'Transportation',
    'XBI': 'Biotech', 'BLOK': 'Blockchain', 'XSD': 'Semiconductors',
    'IWM': 'Russell 2000', 'XHE': 'Health Equipment', 'XPH': 'Pharmaceuticals',
    'KRE': 'Regional Banking', 'XAR': 'Aerospace & Defense', 'XES': 'Oil Services',
    'COPX': 'Copper Miners', 'PBW': 'Clean Energy', 'XME': 'Metals & Mining',
    'SLX': 'Steel', 'JETS': 'Airlines', 'SPY': 'S&P 500'
}

config = {
    "Core ETFs (vs IVE)": {
        "tickers": ['IJS', 'IJR', 'IJT', 'IJJ', 'IJH', 'IJK', 'IVV', 'IVW'],
        "benchmark": 'IVE'
    },
    "Equal Weight Sectors (vs RSP)": {
        "tickers": ['RSPT', 'RSPD', 'RSPC', 'RSPR', 'RSPH', 'RSPN', 'RSPF', 'RSPG', 'RSPM', 'RSPU', 'RSPS'],
        "benchmark": 'RSP'
    },
    "Thematic & Industry (vs SPY)": {
        "tickers": [
            'FXI', 'GXC', 'FFTY', 'XHB', 'CIBR', 'PBJ', 'XRT', 'IBUY', 'DRIV', 
            'WCLD', 'PEJ', 'XTL', 'XSW', 'KIE', 'QQQE', 'IPAY', 'USO', 'KCE', 
            'ROBO', 'GNR', 'BOAT', 'XOP', 'FCG', 'BUZZ', 'XHS', 'PAVE', 'MOD', 
            'KBE', 'GBTC', 'XTN', 'XBI', 'BLOK', 'XSD', 'IWM', 'XHE', 'XPH', 
            'KRE', 'XAR', 'XES', 'COPX', 'PBW', 'XME', 'SLX', 'JETS'
        ],
        "benchmark": 'SPY'
    }
}

def get_rolling_rs():
    all_req_tickers = set()
    for group in config.values():
        all_req_tickers.update(group["tickers"])
        all_req_tickers.add(group["benchmark"])
    
    # Загрузка цен
    try:
        data = yf.download(list(all_req_tickers), period="60d", progress=False)['Close']
        data = data.ffill() # Заполняем пустоты
        clean_data = data.tail(21)
    except Exception as e:
        print(f"Ошибка загрузки yfinance: {e}")
        return {}

    output = {}
    for group_name, params in config.items():
        group_results = {}
        bench_ticker = params["benchmark"]
        
        for ticker in params["tickers"]:
            if ticker not in clean_data.columns or bench_ticker not in clean_data.columns:
                continue
                
            rs_values = []
            t_series = clean_data[ticker]
            b_series = clean_data[bench_ticker]
            
            for i in range(1, len(t_series)):
                t_ret = t_series.iloc[i] / t_series.iloc[i-1]
                b_ret = b_series.iloc[i] / b_series.iloc[i-1]
                
                res = t_ret / b_ret
                if math.isnan(res) or math.isinf(res):
                    res = 1.0
                rs_values.append(round(res, 4))
            
            if len(rs_values) >= 20:
                group_results[ticker] = {
                    "name": NAMES_MAP.get(ticker, ticker),
                    "data": rs_values[-20:]
                }
        output[group_name] = group_results
    return output

if __name__ == "__main__":
    results = get_rolling_rs()
    final_json = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "payload": results
    }
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_json, f, ensure_ascii=False, allow_nan=False)
    print("Update successful.")
