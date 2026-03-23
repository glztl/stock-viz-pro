import pandas as pd
from typing import Optional, Tuple


def calculate_moving_averages(df: pd.DataFrame, short_window: int, long_window: int) -> pd.DataFrame:
    """
    计算简单移动平均线 (SMA)
    最近 N 天收盘价的平均值，每天滚动计算
    """
    df_strategy = df.copy()

    # 确保日期是索引，方便计算，然后再恢复
    # 为了滚动计算，确保数据是按日期排序的
    df_strategy = df_strategy.sort_values('Date')

    # 计算 SMA
    df_strategy['SMA_Short'] = df_strategy['Close'].rolling(window=short_window).mean()
    df_strategy['SMA_Long'] = df_strategy['Close'].rolling(window=long_window).mean()

    return df_strategy

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    生成交易信号:
    1 = 买入(金叉: 短均线 > 长均线)
    0 = 卖出/持有(死叉: 短均线 < 长均线)
    """
    df_signal = df.copy()
    df_signal['Signal'] = 0.0

    # 当短均线大于长均线时，标记为1
    df_signal.loc[df_signal['SMA_Short'] > df_signal['SMA_Long'], 'Signal'] = 1.0

    # 生成交易订单 (1 代表买入, -1 代表卖出)
    # 计算信号的差分, 1 -> 0 是卖出, 0 -> 1 是买入
    df_signal['Position'] = df_signal['Signal'].diff()

    return df_signal

def get_strategy_data(df: pd.DataFrame, short_window: int, long_window: int) -> Optional[pd.DataFrame]:
    """
    策略主入口：整合计算和信号生成
    """
    if len(df) < long_window:
        return None
    
    df = calculate_moving_averages(df, short_window, long_window)
    df = generate_signals(df)

    # 去除因计算均线产生的 NaN 值
    df = df.dropna()

    return df