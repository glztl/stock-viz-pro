import yfinance as yf
import pandas as pd
import time
from typing import Optional

def _clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    清洗 yfinance 返回的列名
    处理 MultiIndex 情况：('Close', 'AAPL') -> 'Close'
    """
    # 复制避免修改原始数据
    df_clean = df.copy()
    
    # 检查是否是 MultiIndex
    if isinstance(df_clean.columns, pd.MultiIndex):
        # 取第一级列名：('Close', 'AAPL') -> 'Close'
        df_clean.columns = df_clean.columns.get_level_values(0)
    
    # 移除可能的空格
    df_clean.columns = df_clean.columns.str.strip()
    
    return df_clean

def get_stock_data(ticker: str, start_date: str, end_date: str, retries: int = 3) -> Optional[pd.DataFrame]:
    """
    获取股票历史数据（带重试机制和列名清洗）
    """
    for attempt in range(retries):
        try:
            # 下载数据
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if data is None or data.empty:
                return None
            
            # 清洗列名 处理 MultiIndex
            data = _clean_column_names(data)
            
            # 速率限制
            time.sleep(1)
            
            return data.reset_index()
            
        except Exception as e:
            if attempt == retries - 1:
                print(f"Error after {retries} attempts: {e}")
                return None
            time.sleep(2 ** attempt)  # 指数退避
    
    return None