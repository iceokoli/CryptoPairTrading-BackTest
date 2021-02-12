import glob
import datetime
from pathlib import Path
from argparse import ArgumentParser

import backtrader as bt
import backtrader.feeds as btfeeds

from pair_trading_strat import PairTrading
from patch import patched_get_pf_items


class CommInfoFractional(bt.CommissionInfo):
    def getsize(self, price, cash):
        """Returns fractional size for cash operation @price"""
        return self.p.leverage * (cash / price)


def get_args():
    """ Handle Argument parsing"""

    parser = ArgumentParser()
    parser.add_argument("--show-log", action="store_true")
    parser.add_argument("--show-plot", action="store_true")
    parser.add_argument("--show-pyfolio", action="store_true")
    parser.add_argument("--data-set", default="training")

    args = parser.parse_args()

    return args.show_log, args.show_plot, args.show_pyfolio, args.data_set


def run_strat(**kwargs):

    # Instatiates backtester
    cerebro = bt.Cerebro()

    # Set Cash & Commission
    cerebro.broker.setcash(10000)
    cerebro.broker.setcommission(commission=0.005)

    # Allow fractional shares
    cerebro.broker.addcommissioninfo(CommInfoFractional())

    # Adds DataFeeds for universe to the backtester
    if kwargs["data_set"] == "testing":
        from_dt = datetime.datetime(2020, 11, 1)
        to_dt = datetime.datetime(2021, 2, 8)
    else:
        from_dt = datetime.datetime(2019, 8, 19)
        to_dt = datetime.datetime(2020, 10, 31)

    dataPath = Path(__file__).parent / "data/*.csv"
    for file in glob.glob(str(dataPath)):
        data = btfeeds.GenericCSVData(
            dataname=file,
            fromdate=from_dt,
            todate=to_dt,
            datetime=0,
            open=1,
            high=2,
            low=3,
            close=4,
            volume=5,
            openinterest=-1,
            time=-1,
            dtformat=("%Y-%m-%d"),
        )
        cerebro.adddata(data)

    # cerebro.optstrategy(
    #     PairTrading,
    #     trigger=map(lambda x: x / 10, range(10, 40, 5)),
    #     period=range(10, 55, 5),
    #     printout=kwargs["show_log"],
    # )
    cerebro.addstrategy(PairTrading, trigger=1, period=25, printout=kwargs["show_log"])

    if kwargs["show_pyfolio"]:
        cerebro.addanalyzer(bt.analyzers.PyFolio, _name="pyfolio")

    results = cerebro.run()

    if kwargs["show_plot"]:
        cerebro.plot()

    if kwargs["show_pyfolio"]:
        pyfoliozer = results[0].analyzers.getbyname("pyfolio")
        returns, positions, transactions, _ = pyfoliozer.get_pf_items()
        returns.to_pickle(
            Path(__file__).parent / "results" / kwargs["data_set"] / "returns.pickle"
        )
        positions.to_pickle(
            Path(__file__).parent / "results" / kwargs["data_set"] / "positions.pickle"
        )
        transactions.to_pickle(
            Path(__file__).parent
            / "results"
            / kwargs["data_set"]
            / "transactions.pickle"
        )


if __name__ == "__main__":
    bt.analyzers.PyFolio.get_pf_items = patched_get_pf_items
    log, plot, s_pyfolio, data_set = get_args()
    run_strat(show_log=log, show_plot=plot, show_pyfolio=s_pyfolio, data_set=data_set)