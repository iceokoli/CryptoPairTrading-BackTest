import backtrader as bt
import backtrader.indicators as btind


class Spread(bt.Indicator):
    params = (("period", 30),)
    lines = ("signal",)

    def __init__(self):
        first, second = self.datas[0], self.datas[1]
        beta = btind.SMA(first, period=self.p.period) / btind.SMA(
            second, period=self.p.period
        )
        spread = first - (beta * second)
        self.lines.signal = (
            spread - btind.SMA(spread, period=self.p.period)
        ) / btind.StdDev(spread, period=self.p.period)


class PairTrading(bt.Strategy):

    params = (
        ("printout", True),
        ("period", 30),
        ("trigger", 1),
        ("sell_mul", 1),
    )

    def __init__(self):

        self.spread = Spread(*self.datas, period=self.p.period)

    def log(self, txt, dt=None):
        if self.p.printout:
            dt = dt or self.data.datetime[0]
            dt = bt.num2date(dt)
            print("%s, %s" % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
            return  # Await further notifications

        if order.status == order.Completed:
            if order.isbuy():
                buytxt = "BUY %s COMPLETE, £%.2f" % (
                    order.data._name,
                    order.executed.price,
                )
                extxt = ", Executed, {} ".format(
                    order.executed.size * order.executed.price
                )
                self.log(buytxt + extxt, order.executed.dt)
            else:
                selltxt = "SELL %s COMPLETE, £%.2f" % (
                    order.data._name,
                    order.executed.price,
                )
                extxt = ", Executed, {} ".format(
                    order.executed.size * order.executed.price
                )
                self.log(selltxt + extxt, order.executed.dt)
        elif order.status in [order.Expired, order.Canceled, order.Margin]:
            self.log("%s, %s ," % (order.data._name, order.Status[order.status]))

    def next(self):
        btc_size = 0.475 * self.broker.getvalue() / self.getdatabyname("Bitcoin")
        eth_size = 0.475 * self.broker.getvalue() / self.getdatabyname("Ethereum")
        upper_threshold = self.p.trigger
        lower_threshold = -self.p.trigger

        if self.position:
            # if self.spread < upper_threshold and self.spread > lower_threshold:
            if abs(self.spread) < (self.p.sell_mul * abs(upper_threshold)):
                txt = "CLOSE POSTION, Indicator: {:.4f}".format(self.spread[0])
                self.log(txt)
                self.close(data=self.getdatabyname("Bitcoin"))
                self.close(data=self.getdatabyname("Ethereum"))
                p_txt = "Profit: {:.2f}".format(
                    self.broker.getvalue() - self.broker.startingcash
                )
                self.log(p_txt)
            elif (
                self.spread > abs(upper_threshold) and self.spread * self.spread[-1] < 0
            ):
                txt = "CLOSE POSTION, Indicator: {:.4f}".format(self.spread[0])
                self.log(txt)
                self.close(data=self.getdatabyname("Bitcoin"))
                self.close(data=self.getdatabyname("Ethereum"))
                p_txt = "Profit: {:.2f}".format(
                    self.broker.getvalue() - self.broker.startingcash
                )
                self.log(p_txt)
        else:
            if self.spread > upper_threshold:
                # Sell Btc and buy Eth
                txt = "OPEN POSTION, Indicator: {:.4f}".format(self.spread[0])
                self.log(txt)
                self.buy(data=self.getdatabyname("Ethereum"), size=eth_size)
                self.sell(data=self.getdatabyname("Bitcoin"), size=btc_size)
            elif self.spread < lower_threshold:
                # Buy Btc and Sell Eth
                txt = "OPEN POSTION, Indicator: {:.4f}".format(self.spread[0])
                self.log(txt)
                self.sell(data=self.getdatabyname("Ethereum"), size=eth_size)
                self.buy(data=self.getdatabyname("Bitcoin"), size=btc_size)

    def stop(self):
        contr = self.broker.startingcash
        value = self.broker.getvalue()
        rtr = (value / contr) - 1
        print("==================================================")
        print("Threshold      - {:.1f} std".format(self.p.trigger))
        print("Period         - {:.1f}".format(self.p.period))
        print("Sell Multiplier- {:.1f}".format(self.p.sell_mul))
        print("Starting Value - £%.2f" % contr)
        print("Ending   Value - £%.2f" % value)
        print("Return         - " + "{:.0%}".format(rtr))
        print("==================================================")
        # with open("results/training/optimisation.csv", "r") as f:
        #     output = f.readlines()
        # output.append(
        #     "{:.1f},{:.1f},{:.1f},{:.3f}\n".format(
        #         self.p.trigger, self.p.period, self.p.sell_mul, rtr
        #     )
        # )
        # with open("results/training/optimisation.csv", "w") as f:
        #     f.writelines(output)
