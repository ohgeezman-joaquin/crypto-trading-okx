import okx.Account as Account
from datetime import datetime


def get_account_balance(accountAPI, ccy):

    # 查看帳戶餘額
    result = accountAPI.get_account_balance(
        ccy = ccy
    )
    with open("account_balance.txt", "w", encoding="utf-8") as f:
        if result["code"] == "0":
            f.write("您的帳戶餘額如下：\n\n")
            
            timestamp = int(result["data"][0]["uTime"])
            dt = datetime.fromtimestamp(timestamp / 1000.0)  # 將時間戳轉換為datetime對象
            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')  # 格式化為年月日時分秒

            for balance in result["data"][0]["details"]:
                f.write("時間: " + formatted_time + "\n")
                f.write("幣種：" + balance["ccy"] + "\n")
                f.write("餘額：" + balance["eq"] + "\n")
                f.write("可用餘額：" + balance["availBal"] + "\n")
                f.write("凍結餘額：" + balance["frozenBal"] + "\n")
                f.write("------------------------------------\n")
        else:
            f.write("獲取帳戶餘額失敗，錯誤代碼：" + result["code"])
            
    return result

def transfer_from_trading_to_funding(accountAPI, fundingAPI, ccy, remain):

    account_balance = get_account_balance(accountAPI, ccy)
    if account_balance["code"] == "0":
        for balance in account_balance["data"][0]["details"]:
                b_ccy = balance["ccy"]
                b_eq = balance["eq"]
                b_availBal = balance["availBal"]
                b_frozenBal = balance["frozenBal"]
    else:
        print("獲取帳戶餘額失敗，錯誤代碼：" + account_balance["data"])

    amount = float(b_eq) - remain
    if amount <= 0:
        print("餘額不足，無法劃轉")
        return 0

    try:
        transfer_from_trading_to_funding = fundingAPI.funds_transfer(
            # 定義劃轉參數
            ccy = "USDT",  # 幣種
            amt = str(amount),    # 金額
            from_ = "18",  # 轉出賬戶（交易賬戶）
            to = "6" # 轉入賬戶（資金賬戶）
        )

        if transfer_from_trading_to_funding["code"] == "0":
            for transfer in transfer_from_trading_to_funding["data"]:
                transId = transfer["transId"]
                b_ccy = transfer["ccy"]
        else:
            print("獲取帳戶餘額失敗，錯誤代碼：" , transfer_from_trading_to_funding["data"][0])


        # 資金劃轉結果
        result = fundingAPI.transfer_state(
            transId = transId
            )
        
        # 打印划转结果
        print("資金劃轉结果：", result["data"][0])
    
    except Exception as e:
        print("發生異常：", e)

