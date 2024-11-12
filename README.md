
# Crypto Trading Bot

此專案是用於加密貨幣交易的自動化交易機器人，基於 Python 實現，包含資產查詢、交易決策、技術指標分析等功能。

使用okx交易所 以及是基於永續合約所寫的

## 專案結構

- **main.py**：主執行檔案，負責整合並執行交易流程。
- **account_balance.py**：查詢帳戶餘額的模組，提供目前帳戶資金狀態。
- **buy_or_sell.py**：交易決策模組，根據指定的策略判斷是否進行買入或賣出操作。
- **draw_line.py**：圖表繪製模組，用於生成技術分析圖表。
- **Position.py**：記錄並管理倉位的模組，追蹤每筆交易的狀態。
- **strategy_kdj.py**：KDJ 指標策略模組，根據 KDJ 技術指標進行交易信號判斷。

## 安裝依賴項

安裝所有依賴項：
   ```bash
   pip install -r requirements.txt
   ```
要記得安裝TA-Lib 如果有使用到的話

## 使用方法

1. 編輯 **main.py** 以設定您要使用的交易策略或參數。
2. 運行主程式：
   ```bash
   python main.py
   ```

## 功能說明

### 1. 帳戶資產查詢 - `account_balance.py`
   查詢並返回目前帳戶的餘額資訊，便於了解資金狀態。

### 2. 交易決策 - `buy_or_sell.py`
   根據指定的策略生成交易信號，判斷是否執行買入或賣出操作。

### 3. 技術分析圖表 - `draw_line.py`
   使用 Matplotlib 繪製 KDJ 等技術指標圖表，提供視覺化的技術分析支援。

### 4. 倉位管理 - `Position.py`
   追蹤每筆交易的狀態，包括倉位大小、進出場價格等，便於資金管理。

### 5. KDJ 指標策略 - `strategy_kdj.py`
   以 KDJ 技術指標為基礎的策略，生成交易信號供 `buy_or_sell.py` 使用。

## 注意事項

- 請確保在運行程式前已配置好交易所 API 金鑰（若需要），以便程式能夠成功查詢帳戶餘額或執行交易。
- 請謹慎使用此交易機器人並先在模擬帳戶上測試，避免不必要的資金損失。

