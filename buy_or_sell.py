
import okx.Trade as Trade
import okx.PublicData as PublicData
import okx.MarketData as MarketData
import okx.Account as Account
import json
import time
import numpy as np
import requests


def buy(accountAPI, tradeAPI, instId, last_price, number, lever_num, loss, profit):

    last_price_str = str(last_price)
    # loss_str = str(loss)
    # profit_str = str(profit)

    loss_str = str(format(loss, '.15f'))
    profit_str = str(format(profit, '.15f'))

    leverage = accountAPI.set_leverage(
        instId = instId,
        lever = lever_num,
        mgnMode = "isolated",
        posSide="long"
    )
    # formatted_result = json.dumps(leverage, indent=4)
    # print('\n',formatted_result)

    order = tradeAPI.place_order(
        instId=instId,
        clOrdId = 'buy01',
        tdMode="isolated",
        side="buy",
        posSide="long",
        ordType="market",
        px = last_price_str,
        sz= number,
        attachAlgoOrds=[
        {
            "attachAlgoClOrdId": "stopbuy01", # 止盈止損訂單ID
            "tpTriggerPx": profit_str, # 止盈觸發價
            "tpOrdPx": "-1", # 止盈委托價 -1表示市價
            "slTriggerPx": loss_str, # 止損觸發價
            "slOrdPx": "-1" # 市價止損 
        }
    ]

    )

    if order["code"] == "0":
        print("下單成功：", order["data"])
        check_okx_buy = True

    else:
        print("下單失敗：", order["data"])
        check_okx_buy = False
    return check_okx_buy


def sell(accountAPI, tradeAPI, instId, last_price, number, lever_num, loss, profit):


    last_price_str = str(last_price)
    # loss_str = str(loss)
    # profit_str = str(profit)

    loss_str = str(format(loss, '.15f'))
    profit_str = str(format(profit, '.15f'))

    leverage = accountAPI.set_leverage(
        instId = instId,
        lever = lever_num,
        mgnMode = "isolated",
        posSide="short"
    )
    # formatted_result = json.dumps(leverage, indent=4)
    # print('\n',formatted_result)

    order = tradeAPI.place_order(
        instId=instId,
        clOrdId = 'sel01',
        tdMode="isolated",
        side="sell",
        posSide="short",
        ordType="market",
        px =   last_price_str,
        sz=number,
        attachAlgoOrds=[
        {
            "attachAlgoClOrdId": "stopsell01", # 止盈止損訂單ID
            "tpTriggerPx": profit_str, # 止盈觸發價
            "tpOrdPx": "-1", # 止盈委托價 -1表示市價
            "slTriggerPx": loss_str, # 止損觸發價
            "slOrdPx": "-1" # 市價止損 
        }
    ]
    )

    if order["code"] == "0":
        print("下單成功：", order["data"])
        check_okx_sell = True


    else:
        print("下單失敗：", order["data"])
        check_okx_sell = False
    
    return check_okx_sell



def close_long(tradeAPI, instId):
    #市價平倉
    close_pos = tradeAPI.close_positions(
        instId = instId,  # 产品ID
        posSide = "long",           # 持仓方向，做多
        mgnMode = "isolated"           # 保证金模式，竹仓模式
    )
    if close_pos["code"] == "0":
        print("市價平倉下單成功：", close_pos["data"])

    else:
        print("市價平倉下單失敗：", close_pos["data"])

def close_short(tradeAPI, instId):
    #市價平倉
    close_pos = tradeAPI.close_positions(
        instId = instId,  # 产品ID
        posSide = "short",           # 持仓方向，做空
        mgnMode = "isolated"           # 保证金模式，竹仓模式
    )
    if close_pos["code"] == "0":
        print("市價平倉下單成功：", close_pos["data"])

    else:
        print("市價平倉下單失敗：", close_pos["data"])


def get_pending_orders(tradeAPI, instType, instId, state):
    """
    取得未成交訂單列表的函式

    Args:
        instType (str): 產品類型
        uly (str): 標的指數
        instFamily (str): 交易品種
        instId (str): 產品ID
        ordType (str): 訂單類型
        state (str): 訂單狀態
        after (str): 請求此ID之前的分頁內容
        before (str): 請求此ID之後的分頁內容
        limit (str): 返回結果的數量

    Returns:
        dict: 未成交訂單列表資訊
    """
    try:
        # 查询所有未成交订单
        result = tradeAPI.get_order_list(
            instType=instType,
            instId=instId,
            state=state
        )

        print(result)

        # if pending_orders["code"] == "0":
        #     if pending_orders["data"]:
        #         print("\n您的未成交訂單如下：")
        #         for order in pending_orders["data"]:
        #             print("訂單ID：", order["ordId"])
        #             print("產品ID：", order["instId"])
        #             print("訂單類型：", order["ordType"])
        #             print("訂單狀態：", order["state"])
        #             print("委託價格：", order["px"])
        #             print("委託數量：", order["sz"])
        #             print("創建時間：", order["cTime"])
        #             print("------------------------------------")
        #     else:
        #         print("\n您目前沒有未成交訂單。") 

        return result
    except Exception as e:
        print("取得未成交訂單清單時發生錯誤:", e)
        return None
    

    
# 定義函式撤銷訂單
def cancel_order_if_timeout(tradeAPI, instType, instId, clOrdId):
    # 查詢訂單狀態
    result = get_pending_orders(tradeAPI, instType, instId, "live")

    if result["code"] == "0":
        # 檢查所有委託訂單
        for order in result["data"]:
            if order["clOrdId"] == clOrdId:
                # 獲取訂單創建時間
                inTime = int(order["cTime"]) / 1000  # 將毫秒轉換為秒
                # 獲取當前時間
                current_time = time.time()
                print("訂單創建時間:", inTime, "當前時間:", current_time)
                # 如果訂單超過15分鐘還未完成，則撤銷訂單
                if current_time - inTime > 15 * 60:
                    # 撤銷訂單
                    cancel_result = tradeAPI.cancel_order(instId=instId, clOrdId=clOrdId)
                    # cancel_bingx()

                    if cancel_result["code"] == "0":
                        print("訂單", clOrdId, "已撤銷")
                    else:
                        print("撤銷訂單失敗:", cancel_result["data"])
                else:
                    print("訂單未超時，繼續監控")
                break
            else:
                print("未找到指定的委託訂單:", clOrdId)
    else:
        print("獲取未完成的委託訂單失敗:", result["data"])