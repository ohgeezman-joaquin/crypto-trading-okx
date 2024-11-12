import matplotlib.pyplot as plt
import numpy as np
import talib
import okx.Trade as Trade
import okx.PublicData as PublicData
import okx.MarketData as MarketData
import okx.Account as Account
from matplotlib.dates import DateFormatter
import datetime
import time
import json

def get_market_data(instId, bar, limit, flag):

    marketDataAPI = MarketData.MarketAPI(flag=flag)
    result = marketDataAPI.get_candlesticks(instId=instId, bar=bar, limit=limit)

    return result

def get_ticker(instId, flag):

    marketDataAPI = MarketData.MarketAPI(flag=flag)
    ticker_data = marketDataAPI.get_ticker(instId)

    return ticker_data
    

    
def plot_bollinger_band(instId, bar, limit, flag, start_time):

    fig, ax = plt.subplots()  # 初始化图形和轴
    marketDataAPI = MarketData.MarketAPI(flag=flag)

    while True:       
        try:

            if start_time == 'last':
                # 獲得最新的K線數據
                data = get_market_data(instId, bar, limit, flag)

            else:
                # 將起始時間轉換為Unix時間戳的毫秒數格式
                start_ts = str(int(start_time.timestamp()) * 1000)

                # 設置要查詢的起始時間
                data = marketDataAPI.get_candlesticks(
                    instId=instId,
                    bar=bar, 
                    limit=limit,
                    after=start_ts
                )

            # 清除图表以进行更新
            ax.clear()

            data = np.array(data['data'])#重要 之後查為什麼

            timestamps = np.array(data[:, 0], dtype=float) / 1000
            opens = np.array(data[:, 1], dtype=float)
            highs = np.array(data[:, 2], dtype=float)
            lows = np.array(data[:, 3], dtype=float)
            closes = np.array(data[:, 4], dtype=float)

            sma20 = talib.SMA(closes, timeperiod=20)
            sma20_shifted = np.roll(sma20, -20)
            stddev = talib.STDDEV(closes, timeperiod=20)

            upper_band = sma20 + 2 * stddev
            lower_band = sma20 - 2 * stddev
            upper_band_shifted = np.roll(upper_band, -19)
            lower_band_shifted = np.roll(lower_band, -19)

            print("upper_band_shifted", upper_band_shifted[1], upper_band_shifted[2], upper_band_shifted[3], upper_band_shifted[4])

            date_times = [datetime.datetime.fromtimestamp(ts) for ts in timestamps]

            # 绘制K线图
            for i in range(len(date_times)):
                ax.plot([date_times[i], date_times[i]], [lows[i], highs[i]], color='black')
                ax.plot([date_times[i], date_times[i]], [opens[i], closes[i]], color='green' if opens[i] < closes[i] else 'red')

            # 绘制布林带和SMA20
            ax.plot(date_times, upper_band_shifted, label='upper_band', linestyle='--')
            ax.plot(date_times, lower_band_shifted, label='lower_band', linestyle='--')
            ax.plot(date_times, sma20_shifted, label='SMA20', linestyle='-', color='blue')

            ax.set_title(instId)
            ax.set_xlabel('time')
            ax.set_ylabel('price')

            n = 1
            ax.set_xticks(date_times[::n])
            ax.set_xticklabels([dt.strftime("%Y-%m-%d %H:%M") for dt in date_times[::n]], rotation=45)

            # 显示图表
            plt.legend()
            plt.pause(100)  # 暂停1秒钟

        except Exception as e:
            print("\nAn error occurred", e)
            time.sleep(10)
