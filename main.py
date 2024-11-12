import draw_line
import okx.Trade as Trade
import okx.PublicData as PublicData
import okx.MarketData as MarketData
import okx.Account as Account
import okx.Funding as Funding
import json
import time
import requests
import Position
import account_balance
import strategy_kdj



# 設置API密鑰和密碼,以及主機地址和賬戶信息
# real
api_key = ""
secret_key = ""
passphrase = ""

# instId = "BTC-USDT-SWAP"
# instId = "DOGE-USDT-SWAP"
# instId = "ETH-USDT-SWAP"
instId = "AIDOGE-USDT-SWAP"
# instId = "NOT-USDT-SWAP"
# instId = "CEL-USDT-SWAP"

bar = "1H"
limit_for_data = "300"

# number_transactions = '1'#這裡不同幣別要調整 以張數為單位 #BTC
# number_transactions = '0.1' #PEPE
# number_transactions = '100' #DOGE
# number_transactions = '200' #NOT
number_transactions = '30' 

lever_num = '10'
balance_ccy = 'USDT'
num_closes_buy = 3
num_closes_sell = 3
take_profit = 2
stop_loss = 0.25
remain = 50

draw_line_date = 'last' #datetime.datetime(2023, 11, 30, 0, 0) # 起始時間 最新設定last'last'
# draw_line_date = datetime.datetime(2024, 3, 9, 0, 0) # 起始時間 最新設定last'last'


# 建立TradeAPI物件
# flag = "1"  # demo trading模式
flag = "0"  # real trading模式

tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)
accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
marketDataAPI = MarketData.MarketAPI(flag=flag)
fundingAPI = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag)

account_balance.get_account_balance(accountAPI, balance_ccy)
# account_balance.transfer_from_trading_to_funding(accountAPI, fundingAPI, balance_ccy, remain)

# 調用策略

strategy_kdj.kdj(   instId,
                    accountAPI,
                    tradeAPI,
                    bar,
                    limit_for_data,
                    number_transactions,
                    lever_num,
                    flag,
                    num_closes_buy,
                    num_closes_sell,
                    take_profit,
                    stop_loss,
                    fundingAPI,
                    remain)



# draw_line.plot_bollinger_band(instId, bar, limit_for_data, flag, draw_line_date)