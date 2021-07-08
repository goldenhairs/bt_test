# -*- coding:utf-8 -*-
# /usr/bin/env python
"""
Date: 2021/7/8 15:34
Desc: BackTrader-MACD 策略
注意事项
由于 BackTrader 自身原因，需要锁定 matplotlib 版本
pip install matplotlib==3.2.2

指数平滑异同移动平均线 MACD
买入与卖出算法：
当持有空仓时候且macd、signal、histo 都大于 0，买入
当持有仓位时候且macd、signal、histo 都小于等于 0，卖出

2.MACD 的应用
MACD 在应用上，是以 12 日为快速移动平均线（12 日 EMA），而以 26 日为慢速移动平均线（ 26 日 EMA），首先计算出此两条移动平均线数值，再
计算出两者数值间的差离值，即差离值 DIF＝ 12 日 EMA－26 日 EMA。然后根据此差离值，计算 9 日 EMA 值（即为 MACD 值）；将 DIF 与 MACD 值
分别绘出线条，然后依“交错分析法”分析，当 DIF 线向上突破 MACD 平滑线即为涨势确认之点，也就是买入信号。反之，当 DIF 线向下跌破 MACD 平滑
线时，即为跌势确认之点，也就是卖出信号。

3. MACD 指标的研判标准

a.DIF 和 MACD 的值及线的位置
当 DIF 和 MACD 均大于 0（即在图形上表示为它们处于零线以上）并向上移动时，一般表示为股市处于多头行情中，可以买入或持股；
当 DIF 和 MACD 均小于 0（即在图形上表示为它们处于零线以下）并向下移动时，一般表示为股市处于空头行情中，可以卖出股票或观望。
当 DIF 和 MACD 均大于 0（即在图形上表示为它们处于零线以上）但都向下移动时，一般表示为股票行情处于退潮阶段，股票将下跌，可以卖出股票和观望；
当 DIF 和 MACD 均小于 0（即在图形上表示为它们处于零线以下）但都向上移动时，一般表示为行情即将启动，股票将上涨，可以买进股票或持股待涨。

b.DIF 和 MACD 的交叉情况
当 DIF 与 MACD 都在零线以上，而 DIF 向上突破 MACD 时，表明股市处于一种强势之中，股价将再次上涨，可以加码买进股票或持股待涨，这就是 MACD 指标“黄金交叉”的一种形式。
当 DIF 和 MACD 都在零线以下，而 DIF 向上突破 MACD 时，表明股市即将转强，股价跌势已尽将止跌朝上，可以开始买进股票或持股，这是 MACD 指标“黄金交叉”的另一种形式。
当 DIF 与 MACD 都在零线以上，而 DIF 向下突破 MACD 时，表明股市即将由强势转为弱势，股价将大跌，这时应卖出大部分股票而不能买股票，这就是 MACD 指标的“死亡交叉”的一种形式。
当 DIF 和 MACD 都在零线以下，而 DIF 向下突破 MACD 时，表明股市将再次进入极度弱市中，股价还将下跌，可以再卖出股票或观望，这是 MACD 指标“死亡交叉”的另一种形式。

c.MACD 指标中的柱状图分析
在股市电脑分析软件中，通常采用 DIF 值减 MACD 值而绘制成柱状图，用红柱状和绿柱状表示，红柱表示正值，绿柱表示负值。用红绿柱状来分析行情，既直观明了又实用可靠。
当红柱状持续放大时，表明股市处于牛市行情中，股价将继续上涨，这时应持股待涨或短线买入股票，直到红柱无法再放大时才考虑卖出。
当绿柱状持续放大时，表明股市处于熊市行情之中，股价将继续下跌，这时应持币观望或卖出股票，直到绿柱开始缩小时才可以考虑少量买入股票。
当红柱状开始缩小时，表明股市牛市即将结束（或要进入调整期），股价将大幅下跌，这时应卖出大部分股票而不能买入股票。
当绿柱状开始收缩时，表明股市的大跌行情即将结束，股价将止跌向上（或进入盘整），这时可以少量进行长期战略建仓而不要轻易卖出股票。
当红柱开始消失、绿柱开始放出时，这是股市转市信号之一，表明股市的上涨行情（或高位盘整行情）即将结束，股价将开始加速下跌，这时应开始卖出大部分股票而不能买入股票。
当绿柱开始消失、红柱开始放出时，这也是股市转市信号之一，表明股市的下跌行情（或低位盘整）已经结束，股价将开始加速上升，这时应开始加码买入股票或持股待涨。
"""
import datetime

import akshare as ak
import backtrader as bt
import pandas as pd


class StrategyClass(bt.Strategy):
    """
    平滑异同移动平均线 MACD

    DIF(MACD): 计算 12 天平均和 26 天平均的差，公式：EMA(C,12)-EMA(c,26)
    Signal(DEA) (红线): 计算 macd 9 天均值，公式：Signal(DEA)：EMA(MACD,9)
    Histogram(柱): 计算 macd 与 signal 的差值，公式：Histogram: MACD-Signal

    period_ma1=12
    period_ma2=26
    period_signal=9

    macd = ema(data, me1_period) - ema(data, me2_period)
    signal = ema(macd, signal_period)
    histo = macd - signal
    """

    def __init__(self):
        # sma源码位于indicators\macd.py
        # 指标必须要定义在策略类中的初始化函数中
        macd = bt.ind.MACD(self.datas[0].close)
        self.macd = macd.macd
        self.signal = macd.signal
        self.histo = bt.ind.MACDHisto()

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()}, {txt}")

    def next(self):
        size = self.getposition(self.datas[0]).size
        # self.data.close是表示收盘价
        # 收盘价大于histo，买入
        if size == 0 and self.macd > 0 and self.signal > 0 and self.histo > 0:
            self.order_target_value(self.datas[0], target=50000)

        # 收盘价小于等于histo，卖出
        if size > 0 and self.macd <= 0 and self.signal <= 0 and self.histo <= 0:
            self.close(self.datas[0])

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # order被提交和接受
            return
        if order.status == order.Rejected:
            self.log(
                f"order is rejected : order_ref:{order.ref}  order_info:{order.info}"
            )
        if order.status == order.Margin:
            self.log(
                f"order need more margin : order_ref:{order.ref}  order_info:{order.info}"
            )
        if order.status == order.Cancelled:
            self.log(
                f"order is concelled : order_ref:{order.ref}  order_info:{order.info}"
            )
        if order.status == order.Partial:
            self.log(
                f"order is partial : order_ref:{order.ref}  order_info:{order.info}"
            )
        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status == order.Completed:
            if order.isbuy():
                self.log(
                    "buy result : buy_price : {} , buy_cost : {} , commission : {}".format(
                        order.executed.price, order.executed.value, order.executed.comm
                    )
                )

            else:  # Sell
                self.log(
                    "sell result : sell_price : {} , sell_cost : {} , commission : {}".format(
                        order.executed.price, order.executed.value, order.executed.comm
                    )
                )

    def notify_trade(self, trade):
        # 一个trade结束的时候输出信息
        if trade.isclosed:
            self.log(
                "closed symbol is : {} , total_profit : {} , net_profit : {}".format(
                    trade.getdataname(), trade.pnl, trade.pnlcomm
                )
            )
        if trade.isopen:
            self.log(
                "open symbol is : {} , price : {} ".format(
                    trade.getdataname(), trade.price
                )
            )


if __name__ == "__main__":
    cerebro = bt.Cerebro()
    cerebro.addstrategy(StrategyClass)
    params = dict(
        fromdate=datetime.datetime(2006, 10, 27),
        todate=datetime.datetime(2021, 7, 6),
        timeframe=bt.TimeFrame.Days,
        compression=1,
        # dtformat=('%Y-%m-%d %H:%M:%S'),
        # tmformat=('%H:%M:%S'),
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=6,
    )
    df = ak.stock_zh_a_hist(symbol="601398", adjust="hfq")
    df = df[["日期", "开盘", "最高", "最低", "收盘", "成交量", "成交额"]]
    df.columns = ["datetime", "open", "high", "low", "close", "volume", "openinterest"]
    df = df.sort_values("datetime")
    df.index = pd.to_datetime(df["datetime"])
    df = df[["open", "high", "low", "close", "volume", "openinterest"]]
    feed = bt.feeds.PandasDirectData(dataname=df, **params)

    cerebro.adddata(feed, name="gsyh")
    cerebro.broker.setcommission(commission=0.0005)

    # 添加资金
    cerebro.broker.setcash(100000.0)

    cerebro.run()
    cerebro.plot()
