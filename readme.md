# Mean Reversion Strategy Backtest Report
## BTC/INR Trading Analysis
Date: December 25, 2024

### Executive Summary
This report analyzes the performance of a mean reversion trading strategy for BTC/INR across multiple timeframes, using an initial capital of 1,000,000 INR. The strategy was tested across 5 days, 1 month, 3 months, 6 months, 1 year, and 5 years periods.

> NOTE 
> The Bot Generates Both Signals But Only executes Longs.*


### Strategy Overview
- Type: Mean Reversion
- Initial Capital: 1,000,000 INR
- Instrument: BTC/INR
- Trading Style: Long-only positions
- Average Bars in Trades: 23-31 bars

### Performance Metrics by Timeframe

#### 5-Day Performance
- Net Profit: 974.69 USD (0.97%)
- Total Closed Trades: 141
- Percent Profitable: 67.38%
- Profit Factor: 1.029
- Maximum Drawdown: 10,408.61 USD (10.15%)
- Average Trade: 6.91 USD
![5d-data](./pics/5d.png) 

#### 1-Month Performance
- Net Profit: 36,404.27 USD (36.40%)
- Total Closed Trades: 343
- Percent Profitable: 70.85%
- Profit Factor: 1.179
- Maximum Drawdown: 38,424.23 USD (30.36%)
- Average Trade: 106.13 USD
![1month](./pics/241225_15h16m46s_screenshot.png)

#### 3-Month Performance
- Net Profit: 27,059.02 USD (27.06%)
- Total Closed Trades: 175
- Percent Profitable: 68.57%
- Profit Factor: 1.194
- Maximum Drawdown: 37,525.38 USD (29.21%)
- Average Trade: 154.62 USD
![3month](./pics/241225_15h17m54s_screenshot.png) 

#### 6-Month Performance
- Net Profit: 68,303.61 USD (68.30%)
- Total Closed Trades: 176
- Percent Profitable: 71.02%
- Profit Factor: 1.318
- Maximum Drawdown: 47,980.93 USD (26.71%)
- Average Trade: 388.09 USD
![6month](./pics/241225_15h18m44s_screenshot.png) 

#### 1-Year Performance
- Net Profit: -60,633.10 USD (-60.63%)
- Total Closed Trades: 76
- Percent Profitable: 60.53%
- Profit Factor: 0.775
- Maximum Drawdown: 98,750.05 USD (87.36%)
- Average Trade: -797.80 USD
![1year](./pics/241225_15h19m42s_screenshot.png) 

#### 5-Year Performance
- Net Profit: 90,246.74 USD (90.25%)
- Total Closed Trades: 67
- Percent Profitable: 66.67%
- Profit Factor: 1.425
- Maximum Drawdown: 162,768.75 USD (70.15%)
- Average Trade: 1,347.72 USD
![5year](./pics/241225_15h20m30s_screenshot.png) 

### Risk Analysis

#### Drawdown Analysis
The strategy shows varying levels of drawdown across timeframes:
- Shortest timeframe (5D): Lowest drawdown at 10.15%
- Medium timeframes (1M-6M): Moderate drawdowns between 26-30%
- Longer timeframes (1Y-5Y): Significant drawdowns up to 87.36%

#### Risk-Adjusted Returns
- Best risk-adjusted performance in 6-month timeframe (Profit Factor: 1.318)
- Poorest risk-adjusted performance in 1-year timeframe (Profit Factor: 0.775)
- Most consistent profitability in medium timeframes (1M-6M)

### Strategy Strengths
1. High win rate across most timeframes (60-71%)
2. Strong performance in medium-term trades (1M-6M)
3. Significant potential for long-term gains (90.25% in 5Y)

### Strategy Weaknesses
1. High maximum drawdown in longer timeframes
2. Inconsistent performance across different periods
3. Poor performance in 1-year timeframe

### Recommendations
1. Consider position sizing adjustments to reduce maximum drawdown
2. Implement stop-loss mechanisms for better risk management
3. Focus optimization on medium-term timeframes where strategy shows best consistency
4. Consider adding filters for volatile market conditions

### Conclusion
The mean reversion strategy shows promise with strong performance in medium timeframes but requires careful risk management for longer-term trading. The strategy performs best in 3-6 month periods, suggesting optimal use in these timeframes.

## CURRUNT STATUS OF TRADEBOT

Chatbot is online on aws ec2.
but due to low capital the long signal fails to execute ;(.


