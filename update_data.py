import yfinance as yf
import json
from datetime import datetime
import pandas as pd

# 1. Конфигурация групп, тикеров и их соответствующих бенчмарков
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
    # Собираем уникальный список всех тикеров для загрузки за один раз
    all_req_tickers = set()
    for group in config.values():
        all_req_tickers.update(group["tickers"])
        all_req_tickers.add(group["benchmark"])
    
    print(f"Загрузка данных для {len(all_req_tickers)} тикеров...")
    
    # Загружаем данные за последние 60 дней (чтобы точно хватило на 21 торговый день)
    raw_data = yf.download(list(all_req_tickers), period="60d", progress=False)['Close']
    
    # Очищаем данные от пустых строк и берем последние 21 день (для расчета 20 изменений)
    clean_data = raw_data.dropna(how='all').tail(21)
    
    output = {}

    for group_name, params in config.items():
        group_results = {}
        bench_ticker = params["benchmark"]
        
        # Проверяем наличие бенчмарка в данных
        if bench_ticker not in clean_data.columns:
            print(f"Предупреждение: Бенчмарк {bench_ticker} не найден в данных.")
            continue

        for ticker in params["tickers"]:
            if ticker not in clean_data.columns:
                print(f"Пропуск {ticker}: данные отсутствуют.")
                continue
                
            rs_values = []
            ticker_series = clean_data[ticker]
            bench_series = clean_data[bench_ticker]
            
            # Рассчитываем относительную силу (RS) за 20 дней
            for i in range(1, len(ticker_series)):
                # Процентное изменение тикера за день
                t_ret = ticker_series.iloc[i] / ticker_series.iloc[i-1]
                # Процентное изменение бенчмарка за день
                b_ret = bench_series.iloc[i] / bench_series.iloc[i-1]
                
                # RS = Доходность актива / Доходность рынка
                rs = round(t_ret / b_ret, 4)
                rs_values.append(rs)
            
            # Сохраняем только если набралось полных 20 дней
            if len(rs_values) >= 20:
                group_results[ticker] = rs_values[-20:]
            
        output[group_name] = group_results
    
    return output

if __name__ == "__main__":
    try:
        data_payload = get_rolling_rs()
        
        final_json = {
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "payload": data_payload
        }
        
        with open('data.json', 'w') as f:
            json.dump(final_json, f)
            
        print(f"Успешно! Файл data.json обновлен: {final_json['last_update']}")
        
    except Exception as e:
        print(f"Критическая ошибка при выполнении скрипта: {e}")
        exit(1)
