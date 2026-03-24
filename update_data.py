import yfinance as yf
import json
from datetime import datetime

tickers = ['IJS', 'IJR', 'IJT', 'IJJ', 'IJH', 'IJK', 'IVV', 'IVW']
benchmark = 'IVE'

def get_rolling_rs():
    all_tickers = tickers + [benchmark]
    # Скачиваем с запасом (60 дней), чтобы гарантированно иметь 20+ рабочих дней
    data = yf.download(all_tickers, period="60d")['Close']
    
    # Очищаем от пустых значений (NaN)
    data = data.dropna()
    
    # Берем последние 21 день (чтобы получить 20 изменений "день к дню")
    # Или 20 последних дней для сравнения баз
    data = data.tail(21)
    
    history_rs = {}

    for ticker in tickers:
        rs_values = []
        # Считаем относительную силу для каждой из 20 последних дат
        for i in range(1, 21):
            # Доходность ETF за конкретный день i
            t_ret = data[ticker].iloc[i] / data[ticker].iloc[i-1]
            # Доходность IVE за тот же день i
            b_ret = data[benchmark].iloc[i] / data[benchmark].iloc[i-1]
            
            # Относительная сила дня
            rs = round(t_ret / b_ret, 4)
            rs_values.append(rs)
        
        history_rs[ticker] = rs_values
    
    return history_rs

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