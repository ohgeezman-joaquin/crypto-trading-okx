import okx.Account as Account

def get_account_positions(accountAPI):
    """
    查詢帳戶持倉信息的函式

    Args:
        apikey (str): 您的API金鑰
        secretkey (str): 您的Secret金鑰
        passphrase (str): 您的passphrase
        flag (str): 實盤(0) 或 模擬盤(1)

    Returns:
        dict: 持倉信息的字典
    """
    # 查詢持倉信息
    result = accountAPI.get_positions()
    # print_positions_info(result)

    return result

def print_positions_info(positions):
    """
    印出持倉信息的函式

    Args:
        positions (dict): 持倉信息的字典
    """
    if positions["code"] == "0":
        if positions["data"]:
            print("\n您的持倉信息如下：")
            for position in positions["data"]:
                print("持倉方向：", position["posSide"])
                print("產品類型：", position["instType"])
                print("產品ID：", position["instId"])
                print("持倉數量：", position["pos"])
                print("開倉平均價：", position["avgPx"])
                print("未實現收益：", position["upl"])
                print("未實現收益率：", position["uplRatio"])
                print("創建時間：", position["cTime"])
                print("------------------------------------")
        else:
            print("\n您目前沒有持倉。")
    else:
        print("查詢持倉信息失敗，錯誤碼：", positions["data"])


def check_long_and_execute_trades(accountAPI, flag):
    positions = get_account_positions(accountAPI)
    """
    檢查持倉狀況並執行交易操作

    Args:
        positions (dict): 持倉信息的字典
    """
    has_long_position = 0

    if positions["code"] == "0":
        if positions["data"]:
            for position in positions["data"]:
                if position["posSide"] == "long":
                    has_long_position = True
    else:
        print("查詢持倉信息失敗，錯誤碼：", positions["data"])

        #####################################################################
        import time
        time.sleep(10000)
        has_long_position = True

    return has_long_position

def check_short_and_execute_trades(accountAPI, flag):
    positions = get_account_positions(accountAPI)
    """
    檢查持倉狀況並執行交易操作

    Args:
        positions (dict): 持倉信息的字典
    """
    has_short_position = 0

    if positions["code"] == "0":
        if positions["data"]:
            for position in positions["data"]:
                if position["posSide"] == "short":
                    has_short_position = True
    else:
        print("查詢持倉信息失敗，錯誤碼：", positions["data"])
        import time
        time.sleep(10000)
        has_short_position = True
    return has_short_position
