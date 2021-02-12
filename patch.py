""" Patched Function so that pyfolio can handle mulptiple postions """
import pandas
from pandas import DataFrame as DF
from backtrader.utils.py3 import items, iteritems


def patched_get_pf_items(self):
    """Returns a tuple of 4 elements which can be used for further processing with
        ``pyfolio``
        returns, positions, transactions, gross_leverage
    Because the objects are meant to be used as direct input to ``pyfolio``
    this method makes a local import of ``pandas`` to convert the internal
    *backtrader* results to *pandas DataFrames* which is the expected input
    by, for example, ``pyfolio.create_full_tear_sheet``
    The method will break if ``pandas`` is not installed
    """

    #
    # Returns
    cols = ["index", "return"]
    returns = DF.from_records(
        iteritems(self.rets["returns"]), index=cols[0], columns=cols
    )
    returns.index = pandas.to_datetime(returns.index)
    returns.index = returns.index.tz_localize("UTC")
    rets = returns["return"]
    #
    # Positions
    pss = self.rets["positions"]
    ps = [[k] + v[:] for k, v in iteritems(pss)]  # patched item of code
    cols = ps.pop(0)  # headers are in the first entry
    positions = DF.from_records(ps, index=cols[0], columns=cols)
    positions.index = pandas.to_datetime(positions.index)
    positions.index = positions.index.tz_localize("UTC")

    #
    # Transactions
    txss = self.rets["transactions"]
    txs = list()
    # The transactions have a common key (date) and can potentially happend
    # for several assets. The dictionary has a single key and a list of
    # lists. Each sublist contains the fields of a transaction
    # Hence the double loop to undo the list indirection
    for k, v in iteritems(txss):
        for v2 in v:
            txs.append([k] + v2)

    cols = txs.pop(0)  # headers are in the first entry
    transactions = DF.from_records(txs, index=cols[0], columns=cols)
    transactions.index = pandas.to_datetime(transactions.index)
    transactions.index = transactions.index.tz_localize("UTC")

    # Gross Leverage
    cols = ["index", "gross_lev"]
    gross_lev = DF.from_records(
        iteritems(self.rets["gross_lev"]), index=cols[0], columns=cols
    )

    gross_lev.index = pandas.to_datetime(gross_lev.index)
    gross_lev.index = gross_lev.index.tz_localize("UTC")
    glev = gross_lev["gross_lev"]

    # Return all together
    return rets, positions, transactions, glev