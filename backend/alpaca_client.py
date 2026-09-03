"""
Single point of contact with Alpaca. Every other module (backtest, crash tests,
trading) goes through this wrapper — never imports alpaca-py directly, and
never reaches into a private attribute of this class either.

This keeps three guarantees from the spec:
  - "Never fabricate market data / API responses" — one place to audit.
  - Paper-only enforcement lives here as a hard gate, not a convention.
  - Every Alpaca SDK call site is here, so a bad request shape only needs
    fixing once.
"""
from datetime import datetime, timedelta, timezone

from alpaca.data.enums import DataFeed
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest

from config import settings


class AlpacaClientError(RuntimeError):
    pass


class AlpacaClient:
    def __init__(self):
        problems = settings.validate()
        if problems:
            raise AlpacaClientError(f"Cannot start Alpaca client: {'; '.join(problems)}")

        try:
            self._feed = DataFeed(settings.ALPACA_DATA_FEED)
        except ValueError as e:
            raise AlpacaClientError(
                f"Invalid ALPACA_DATA_FEED '{settings.ALPACA_DATA_FEED}' — "
                f"must be one of: {[f.value for f in DataFeed]}"
            ) from e

        self._trading = TradingClient(
            settings.ALPACA_API_KEY,
            settings.ALPACA_SECRET_KEY,
            paper=True,  # hard-coded True regardless of config — belt and suspenders on FR "hard-block live trading"
        )
        self._data = StockHistoricalDataClient(
            settings.ALPACA_API_KEY,
            settings.ALPACA_SECRET_KEY,
        )

    def get_account(self) -> dict:
        """Account/buying-power check — also doubles as the 'verify SDK connection' smoke test."""
        try:
            acct = self._trading.get_account()
        except Exception as e:  # noqa: BLE001 — any auth/network failure must surface clearly, not as a stack trace deep in a route
            raise AlpacaClientError(f"Failed to fetch account: {e}") from e
        return {
            "account_number": acct.account_number,
            "buying_power": float(acct.buying_power),
            "portfolio_value": float(acct.portfolio_value),
            "status": str(acct.status),
        }

    def get_daily_bars(self, symbol: str, days_back: int = 400):
        """
        Historical daily bars — the FR-04 data source for the deterministic backtester.
        days_back=400 gives enough lookback for a 50-day SMA plus a real test window.
        Always returns a plain single-level-indexed DataFrame with lowercase
        OHLC columns, regardless of how many symbols were requested — callers
        never need to know about alpaca-py's multi-symbol MultiIndex shape.
        """
        req = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=datetime.now(timezone.utc) - timedelta(days=days_back),
            feed=self._feed,
        )
        try:
            bars = self._data.get_stock_bars(req)
        except Exception as e:  # noqa: BLE001 — surface Alpaca-side errors (bad symbol, entitlement, rate limit) verbatim
            raise AlpacaClientError(f"Failed to fetch bars for {symbol}: {e}") from e

        df = bars.df
        if df.empty:
            raise AlpacaClientError(f"No bars returned for {symbol} — check symbol/feed entitlement")

        df = df.rename(columns=str.lower)
        if hasattr(df.index, "nlevels") and df.index.nlevels > 1:
            df = df.droplevel(0)  # drop the symbol level of alpaca-py's MultiIndex — single point of truth for this
        return df

    def submit_market_order(self, symbol: str, notional: float, side: str):
        """
        The only place order submission happens. Callers pass a plain
        'buy'/'sell' string and a dollar notional; this owns translating
        that into the SDK's request shape.
        """
        if side not in ("buy", "sell"):
            raise ValueError(f"Invalid side: {side}")

        order_req = MarketOrderRequest(
            symbol=symbol,
            notional=round(notional, 2),
            side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
        )
        try:
            order = self._trading.submit_order(order_req)
        except Exception as e:  # noqa: BLE001 — surface any Alpaca-side rejection verbatim, never swallow it
            raise AlpacaClientError(f"Order submission failed: {e}") from e

        return {
            "order_id": str(order.id),
            "symbol": symbol,
            "side": side,
            "notional": round(notional, 2),
            "status": str(order.status),
        }


alpaca_client: AlpacaClient | None = None


def get_alpaca_client() -> AlpacaClient:
    """Lazy singleton so importing this module doesn't require env vars to already be set (e.g. in tests)."""
    global alpaca_client
    if alpaca_client is None:
        alpaca_client = AlpacaClient()
    return alpaca_client
