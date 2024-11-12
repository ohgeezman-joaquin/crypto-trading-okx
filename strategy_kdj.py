import numpy as np
import talib
import datetime
from datetime import timedelta
import time
import buy_or_sell
import Position
import draw_line
import okx.MarketData as MarketData
import account_balance

def dynamic_stop_loss_long(buy_price, current_price, highest_price, lowest_price, num_grids=20):
    # 計算每格的大小
    grid_size = (highest_price - lowest_price) / num_grids
    
    # 初始止損位
    initial_stop_loss = buy_price - 4 * grid_size
    
    # 計算當前價格所處的格子位置
    current_grid = (current_price - lowest_price) // grid_size
    
    # 計算最新價格所處的格子位置
    buy_grid = (buy_price - lowest_price) // grid_size
    
    # 如果價格上漲超過一格，則上調止損位
    if current_price > buy_price:
        new_stop_loss = buy_price + (current_grid - buy_grid) * grid_size - 4 * grid_size
    else:
        new_stop_loss = initial_stop_loss

    # 止損位不能低於初始止損位
    stop_loss = max(new_stop_loss, initial_stop_loss)
    
    return stop_loss

def dynamic_stop_loss_short(sell_price, current_price, highest_price, lowest_price, num_grids=20):
    # 計算每格的大小
    grid_size = (highest_price - lowest_price) / num_grids
    
    # 初始止損位
    initial_stop_loss = sell_price + 4 * grid_size
    
    # 計算當前價格所處的格子位置
    current_grid = (current_price - lowest_price) // grid_size
    
    # 計算賣出價格所處的格子位置
    sell_grid = (sell_price - lowest_price) // grid_size
    
    # 如果價格下跌超過一格，則下調止損位
    if current_price < sell_price:
        new_stop_loss = sell_price - (sell_grid - current_grid) * grid_size + 4 * grid_size
    else:
        new_stop_loss = initial_stop_loss

    # 止損位不能高於初始止損位
    stop_loss = min(new_stop_loss, initial_stop_loss)
    
    return stop_loss

def fixed_stop_loss_take_profit_long(buy_price, highest_price, lowest_price, num_grids):
    grid_size = (highest_price - lowest_price) / num_grids
    stop_loss = buy_price - 3 * grid_size
    take_profit = buy_price + 6 * grid_size
    
    return stop_loss, take_profit, grid_size

def fixed_stop_loss_take_profit_short(sell_price, highest_price, lowest_price, num_grids):
    grid_size = (highest_price - lowest_price) / num_grids
    stop_loss = sell_price + 3 * grid_size
    take_profit = sell_price - 6 * grid_size
    
    return stop_loss, take_profit, grid_size



def bcwsma(data, length, m):
    bcwsma_vals = np.zeros(len(data))
    for i in range(len(data)):
        if i == 0:
            bcwsma_vals[i] = data[i]
        else:
            bcwsma_vals[i] = (m * data[i] + (length - m) * bcwsma_vals[i - 1]) / length
    return bcwsma_vals

def calculate_kdj(closes, highs, lows, ilong=9, isig=3):
    h = np.array([np.max(highs[i - ilong + 1:i + 1]) if i >= ilong - 1 else np.max(highs[:i + 1]) for i in range(len(highs))])
    l = np.array([np.min(lows[i - ilong + 1:i + 1]) if i >= ilong - 1 else np.min(lows[:i + 1]) for i in range(len(lows))])
    RSV = 100 * ((closes - l) / (h - l))
    
    pK = bcwsma(RSV, isig, 1)
    pD = bcwsma(pK, isig, 1)
    pJ = 3 * pK - 2 * pD
    
    return pK, pD, pJ


def wait_time():

    # 設置等待時間為15小時
    wait_time_minutes = 3

    # 獲取當前時間
    start_time = datetime.datetime.now()

    # 計算等待結束的時間
    end_time = start_time + timedelta(minutes=wait_time_minutes)

    # 檢查是否已經到達等待結束時間
    while datetime.datetime.now() < end_time:
        # 計算距離等待結束還有多長時間
        remaining_time = end_time - datetime.datetime.now()
        print("等待中，剩餘時間: ", remaining_time)
        # 暫停執行
        time.sleep(10)

def kdj(instId, accountAPI, tradeAPI, bar, limit, number_transactions, lever_num, flag, num_closes_buy, num_closes_sell, take_profit, stop_loss, fundingAPI, remain):




    buy_or_sell.close_long(tradeAPI, instId)
    buy_or_sell.close_short(tradeAPI, instId)
    
    buy_price = None
    sell_price = None

    safty_loss = 10
    safty_profit = 10

    trade_buy_chack = False
    trade_sell_chack = False

    level_stop_loss_buy = stop_loss
    level_stop_loss_sell = stop_loss

    stop_loss_price_buy = None
    stop_loss_price_sell = None
    take_profit_price_buy = None
    take_profit_price_sell = None
    new_stop_loss_buy = None
    new_stop_loss_sell = None




    while True:

        try:

            print("\n")
            # Get the latest data
            # result = draw_line.get_market_data(instId, bar, limit, flag='0')
            result = draw_line.get_market_data(instId, bar, limit, flag='0')
            data = np.array(result['data'])
            closes = np.array(data[:, 4], dtype=float)
            opens = np.array(data[:, 1], dtype=float)
            low = np.array(data[:, 3], dtype=float)
            high = np.array(data[:, 2], dtype=float)
            # print('收盤價:', closes[0])


            # 獲取未成交訂單
            pending_orders = buy_or_sell.get_pending_orders(tradeAPI, "SWAP", instId, "live")

            # 獲取單一產品的最新數據
            ticker_data = draw_line.get_ticker(instId, flag='0')
            print("\n\n-----------------------------------------------")
            
            # 解析最新價格
            if ticker_data["code"] == "0":
                last_price = float(ticker_data["data"][0]["last"])  # 最新成交价
                print("\n最新成交價:", last_price, datetime.datetime.now())

            else:
                print("\n獲取最新價格失敗:", ticker_data["msg"])

            


            closes_10000 = closes * 10000
            high_10000 = high * 10000
            low_10000 = low * 10000

            close_reverse = closes_10000[::-1]
            high_reverse = high_10000[::-1]
            low_reverse = low_10000[::-1]

            #計算sma
            sma = talib.SMA(close_reverse, timeperiod=30)
            sma_reverse = sma[::-1]

            #計算rsi
            rsi = talib.RSI(close_reverse, timeperiod=14)
            rsi_reverse = rsi[::-1]

            rsi_ma = talib.SMA(rsi, timeperiod=14)
            rsi_ma = rsi_ma[::-1]

            print('rsi:', rsi_reverse[0:10])
            print('rsi_ma:', rsi_ma[0:10])
        
            #計算kdj
            pK, pD, pJ = calculate_kdj(close_reverse, high_reverse, low_reverse, 9, 3)

            k_reverse = pK[::-1]
            d_reverse = pD[::-1]
            j_reverse = pJ[::-1]

            print('k:', k_reverse[0:10])
            print('d:', d_reverse[0:10])
            print('j:', j_reverse[0:10])

                
####################################策略############################################

            if (
                rsi_ma[2] > rsi_reverse[2] and
                closes[1] > closes[2]
                ):
                    
                print('條件買觸發')
                signal = "Buy"

            else:
                signal = None

            if (
                  rsi_ma[2] < rsi_reverse[2] and
                  closes[1] < closes[2]
                 ):

                print('條件賣觸發')
                signal = "Sell"

            else:
                signal = None

            signal = None





            window_size = 100

            # 初始化最大值和最小值
            max_value = None
            min_value = None

            window = closes[0:window_size]  # 获取当前窗口的290个数值
            
            # 找出窗口内的最大值和最小值
            window_max = max(window)
            window_min = min(window)
            
            # 更新最大值和最小值
            if max_value is None or window_max > max_value:
                max_value = window_max
            if min_value is None or window_min < min_value:
                min_value = window_min

            max_value_str = format(max_value, '.15f')
            min_value_str = format(min_value, '.15f')

            print("最大值:", max_value_str)
            print("最小值:", min_value_str)


            # print("最大值:", max_value, '.20f')
            # print("最小值:", min_value, '.20f')

            increase = ((max_value - min_value) / min_value)


            if buy_price is not None:
                stop_loss_price_buy, take_profit_price_buy, grid_size = fixed_stop_loss_take_profit_long(buy_price, k_high, k_low, 20)

                # 如果價格上漲，則上調止損位
                if last_price > buy_price + 4 * grid_size:
                    new_stop_loss_buy = buy_price

                if new_stop_loss_buy is not None:
                    # 止損位不能低於初始止損位
                    stop_loss_price_buy = max(new_stop_loss_buy, stop_loss_price_buy)

            if sell_price is not None:
                stop_loss_price_sell, take_profit_price_sell, grid_size  = fixed_stop_loss_take_profit_short(sell_price, k_high, k_low, 20)

                # 如果價格下跌，則下調止損位
                if last_price < sell_price - 4 * grid_size:
                    new_stop_loss_sell = sell_price

                if new_stop_loss_sell is not None:
                    # 止損位不能高於初始止損位
                    stop_loss_price_sell = min(new_stop_loss_sell, stop_loss_price_sell)

            print('level_stop_loss_buy:', stop_loss_price_buy)
            print('level_take_profit_buy:', take_profit_price_buy)
            print('level_stop_loss_sell:', stop_loss_price_sell)
            print('level_take_profit_sell:', take_profit_price_sell)

####################################策略############################################
            
            if signal == "Buy" and trade_buy_chack == False:
                print("\多頭信號:", datetime.datetime.now())

                if not Position.check_long_and_execute_trades(accountAPI, flag) and not Position.check_short_and_execute_trades(accountAPI, flag):
                    if any(order["posSide"] == "long" for order in pending_orders["data"]) or any(order["posSide"] == "short" for order in pending_orders["data"]):
                        print('有委託，暫時無法再次買入')

                    else:
                        buy_price = last_price

                        profit = buy_price * (1 + safty_profit / 100)
                        loss = buy_price * (1 - safty_loss / 100)

                        okx_check = buy_or_sell.buy(accountAPI, tradeAPI, instId, last_price, number_transactions, lever_num, loss, profit)
                        
                        if okx_check == True:
                            trade_buy_chack = True 
                            k_high = max_value
                            k_low = min_value      
                        else:
                            buy_price = None        

                else:
                    print("\n已有持倉，不可以再次買入")

                    if (sell_price is not None and 
                        Position.check_short_and_execute_trades(accountAPI, flag)):

                        buy_price = None
                        sell_price = None
                        buy_or_sell.close_short(tradeAPI, instId)
                        trade_sell_chack = False
                        new_stop_loss_sell = None
                        take_profit_price_sell = None
                        stop_loss_price_sell = None

            elif signal == "Sell" and trade_sell_chack == False:

                print("\n空頭信號:", datetime.datetime.now())
                    
                if not Position.check_short_and_execute_trades(accountAPI, flag) and not Position.check_long_and_execute_trades(accountAPI, flag):
                    if any(order["posSide"] == "short" for order in pending_orders["data"]) or any(order["posSide"] == "long" for order in pending_orders["data"]):
                        print('有委託，暫時無法再次賣出')

                    else:
                        sell_price = last_price

                        profit = sell_price * (1 - safty_profit / 100)
                        loss = sell_price * (1 + safty_loss / 100)

                        okx_check = buy_or_sell.sell(accountAPI, tradeAPI, instId, last_price, number_transactions, lever_num, loss, profit)

                        if okx_check == True:
                            trade_sell_chack = True
                            k_high = max_value
                            k_low = min_value  
                        else:
                            sell_price = None

                else:
                    print("\n已有持倉，不可以再次賣出")

                    if (buy_price is not None and 
                        Position.check_long_and_execute_trades(accountAPI, flag)):

                        buy_price = None
                        sell_price = None
                        buy_or_sell.close_long(tradeAPI, instId)
                        trade_buy_chack = False
                        new_stop_loss_buy = None
                        take_profit_price_buy = None
                        stop_loss_price_buy = None

                    
            else:
                print('無信號')

                #做多止損止盈
                if (buy_price is not None and 
                        Position.check_long_and_execute_trades(accountAPI, flag)):

                    if last_price > take_profit_price_buy:
                    
                        buy_price = None
                        sell_price = None
                        buy_or_sell.close_long(tradeAPI, instId)
                        trade_buy_chack = False
                        new_stop_loss_buy = None
                        take_profit_price_buy = None
                        stop_loss_price_buy = None

                        wait_time()


                    elif ((last_price < stop_loss_price_buy) 
                          ):
                        
                        buy_price = None
                        sell_price = None
                        buy_or_sell.close_long(tradeAPI, instId)
                        trade_buy_chack = False
                        new_stop_loss_buy = None
                        take_profit_price_buy = None
                        stop_loss_price_buy = None

                        wait_time()


                #做空止損止盈
                elif (sell_price is not None and 
                        Position.check_short_and_execute_trades(accountAPI, flag)):

                    if last_price < take_profit_price_sell:

                        buy_price = None
                        sell_price = None
                        buy_or_sell.close_short(tradeAPI, instId)
                        trade_sell_chack = False
                        new_stop_loss_sell = None
                        take_profit_price_sell = None
                        stop_loss_price_sell = None

                        wait_time()
                    
                    elif ((last_price > stop_loss_price_sell)
                        ):

                        buy_price = None
                        sell_price = None
                        buy_or_sell.close_short(tradeAPI, instId)
                        trade_sell_chack = False
                        new_stop_loss_sell = None
                        take_profit_price_sell = None
                        stop_loss_price_sell = None

                        wait_time()


            #檢查是否有未成交訂單
            if (any(order["posSide"] == "long" for order in pending_orders["data"]) or
                any(order["posSide"] == "short" for order in pending_orders["data"])):

                print("\n有未成交的單")
                buy_or_sell.cancel_order_if_timeout(tradeAPI, "SWAP", instId, "buy01")
                buy_or_sell.cancel_order_if_timeout(tradeAPI, "SWAP", instId, "sel01")

            
            current_time = datetime.datetime.now()
            if current_time.minute == 0:
                print("\n整點，劃轉資金")
                account_balance.transfer_from_trading_to_funding(accountAPI, fundingAPI, "USDT", remain)


            print("\n\n###############################################")
            #time.sleep(0.1) 

        except Exception as e:
            print("\nAn error occurred:", e)
            time.sleep(10)
            # break