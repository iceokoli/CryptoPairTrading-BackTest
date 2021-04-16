import yfinance as yf
from pathlib import Path
from argparse import ArgumentParser


def get_args():
    """ Handle Argument parsing"""

    parser = ArgumentParser()
    parser.add_argument("--tickers", required=True)
    parser.add_argument("--save-location", required=True)
    parser.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end-date", required=True, help="YYYY-MM-DD")

    args = parser.parse_args()

    return args.tickers.split(","), args.save_location, args.start_date, args.end_date


def grab_data(ticker, s, e):
    """ Get Data from Yahoo Finance"""

    t = yf.Ticker(ticker)

    return t.info["name"], t.history(start=s, end=e)


if __name__ == "__main__":

    tickers, save_location, start, end = get_args()

    for ticker in tickers:
        name, data = grab_data(ticker, start, end)
        out_dir = Path(__file__).parent / save_location / f"{name}.csv"
        data.to_csv(out_dir)
