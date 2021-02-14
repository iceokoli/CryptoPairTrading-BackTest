# CryptoPairTrading
Backtesting a strategy to pair trade BTC and ETH on a daily timeframe

## Initial Analysis

BTC returns and ETH returns have a correlation of 0.86 between 2019-09-18 and 2020-10-31 (training data)

## Training - Results

Period: 2019-09-18 and 2020-10-31

For more details checkout the "Training Pyfolio Analysis.ipynb" notebook


|  |  |
|---|---|
Threshold |  1.0 std 
Period | 20.0
Sell Threshold | 0.1
Starting Value | £10000.00
Ending   Value | £15772.11
Return | 68%
Annual Return | 38%


![image](training_overview.png)

## Testing - Results

Period: 2020-11-01 to 2021-02-08

For more details checkout the "Testing Pyfolio Analysis.ipynb" notebook


|  |  |
|---|---|
Threshold |  1.0 std 
Period | 20.0
Sell Threshold | 0.1
Starting Value | £10000.00
Ending   Value | £10836.02
Return | 8%
Annual Return | 22.7%

![image](testing_overview.png)