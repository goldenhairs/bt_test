# -*- coding:utf-8 -*-
# /usr/bin/env python
"""
Date: 2021/7/9 16:08
Desc: BackTrader-KDJ 策略
注意事项
由于 BackTrader 自身原因，需要锁定 matplotlib 版本
pip install matplotlib==3.2.2

策略：
当 J 值上穿K值的时候，是买入信号，此时买入。
当J值下穿K值的时候，是卖出信号，此时卖出。

计算方式：
RSV = (收盘价-N周期最低价) / (N周期最高价-N周期最低价) * 100
K值 = RSV的 N 周期加权移动平均值
D值 = K值的 N 周期加权移动平均值
J值 = 3 * K-2 * D
"""
import datetime

import akshare as ak
import backtrader as bt
import pandas as pd


class StrategyClass(bt.Strategy):
    """
    KDJ指标
    RSV = (收盘价-N周期最低价) / (N周期最高价-N周期最低价) * 100
    K值 = RSV的 N 周期加权移动平均值
    D值 = K值的 N 周期加权移动平均值
    J值 = 3 * K-2 * D
    """

    def __init__(self):
        # sma源码位于indicators\macd.py
        # 指标必须要定义在策略类中的初始化函数中
        # 9个交易日内最高价
        self.high_nine = bt.indicators.Highest(self.data.high, period=9)
        # 9个交易日内最低价
        self.low_nine = bt.indicators.Lowest(self.data.low, period=9)
        # 计算rsv值
        self.rsv = 100 * bt.DivByZero(
            self.data_close - self.low_nine, self.high_nine - self.low_nine, zero=None
        )
        # 计算rsv的3周期加权平均值，即K值
        self.K = bt.indicators.EMA(self.rsv, period=3)
        # D值=K值的3周期加权平均值
        self.D = bt.indicators.EMA(self.K, period=3)
        # J=3*K-2*D
        self.J = 3 * self.K - 2 * self.D

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()}, {txt}")

    def next(self):
        size = self.getposition(self.datas[0]).size
        condition1 = self.J[-1] - self.D[-1]
        condition2 = self.J[0] - self.D[0]
        if size == 0 and condition1 < 0 and condition2 > 0:
            self.order_target_value(self.datas[0], target=50000)
        else:
            condition1 = self.J[-1] - self.D[-1]
            condition2 = self.J[0] - self.D[0]
            if size != 0 and condition1 > 0 and condition2 < 0:
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
