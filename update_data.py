import yfinance as yf
import json
from datetime import datetime

# Настройки групп и их бенчмарков
config = {
    "Core ETFs (vs IVE)": {
        "tickers": ['IJS', 'IJR', 'IJT', 'IJJ', 'IJH', 'IJK', 'IVV', 'IVW'],
        "benchmark": 'IVE'
    },
    "Equal Weight Sectors (vs RSP)": {
        "tickers": ['RSPT', 'RSPD', 'RSPC', 'RSPR', 'RSPH', 'RSPN', 'RSPF', 'RSPG', 'RSPM', 'RSPU', 'RSPS'],
        "benchmark": 'RSP'
    }
}

def get_rolling_rs():
    # Собираем абсолютно все нужные тикеры в один список для загрузки
    all_req_tickers = []
    for group in config.values():
        all_req_tickers.extend(group["tickers"])
        all_req_tickers.append(group["benchmark"])
    
    # Убираем дубликаты и скачиваем данные
    all_req_tickers = list(set(all_req_tickers))
    data = yf.download(all_req_tickers, period="60d")['Close'].dropna().tail(21)
    
    output = {}

    for group_name, params in config.items():
        group_results = {}
        bench_ticker = params["benchmark"]
        
        for ticker in params["tickers"]:
            rs_values = []
            for i in range(1, 21):
                # Доходность тикера за день
                t_ret = data[ticker].iloc[i] / data[ticker].iloc[i-1]
                # Доходность соответствующего бенчмарка за тот же день
                b_ret = data[bench_ticker].iloc[i] / data[bench_ticker].iloc[i-1]
                rs_values.append(round(t_ret / b_ret, 4))
            group_results[ticker] = rs_values
            
        output[group_name] = group_results
    
    return output

if __name__ == "__main__":
    try:
        results = {
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "payload": get_rolling_rs()
        }
        with open('data.json', 'w') as f:
            json.dump(results, f)
        print("Данные успешно обновлены.")
    except Exception as e:
        print(f"Ошибка: {e}")
