"""
Strategy signal generation. MVP scope: sma_cross only (per demo script and
acceptance criteria — 'a natural-language SMA strategy compiles').
"""
import pandas as pd

from models.strategy import Strategy


def compute_sma(close: pd.Series, window: int) -> pd.Series:
    return close.rolling(window=window, min_periods=window).mean()


def generate_signals(df: pd.DataFrame, strategy: Strategy) -> pd.DataFrame:
    """
    Adds 'position' column: 1 = long, 0 = flat, computed with NO look-ahead —
    a signal on day t's close can only be acted on at day t+1's open.

    df must have a 'close' and 'open' column, sorted ascending by date.
    """
    out = df.copy()

    entry_fast = compute_sma(out["close"], strategy.entry.fast)
    entry_slow = compute_sma(out["close"], strategy.entry.slow)
    exit_fast = compute_sma(out["close"], strategy.exit.fast)
    exit_slow = compute_sma(out["close"], strategy.exit.slow)

    entry_signal = (
        (entry_fast > entry_slow) if strategy.entry.direction == "above"
        else (entry_fast < entry_slow)
    )
    exit_signal = (
        (exit_fast > exit_slow) if strategy.exit.direction == "above"
        else (exit_fast < exit_slow)
    )

    # Cross detection: signal fires only on the bar the condition FLIPS true, not every bar it holds.
    entry_cross = entry_signal & ~entry_signal.shift(1).fillna(False).astype(bool)
    exit_cross = exit_signal & ~exit_signal.shift(1).fillna(False).astype(bool)

    position = pd.Series(0, index=out.index, dtype=int)
    in_position = False
    for i in range(len(out)):
        if not in_position and entry_cross.iloc[i]:
            in_position = True
        elif in_position and exit_cross.iloc[i]:
            in_position = False
        position.iloc[i] = 1 if in_position else 0

    out["position"] = position
    # Fill model: next_bar_open — the position decided at close of day t is
    # only ACTED ON at day t+1's open. Shift position forward one bar for fills.
    out["filled_position"] = out["position"].shift(1).fillna(0).astype(int)
    return out
