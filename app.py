import streamlit as st
import plotly.graph_objects as go
from src.data_fetcher import get_stock_data
from datetime import timedelta, date
import pandas as pd



# 1. 页面配置
st.set_page_config(page_title="Stock Viz Pro", layout="wide")
st.title("📈 股票数据可视化分析工具 MVP")

# 2. 侧边栏输入
st.sidebar.header("配置参数")
ticker = st.sidebar.text_input("股票代码 (如 AAPL, 600519.SS)", "AAPL")
end_date = st.sidebar.date_input("结束日期", date.today())
start_date = st.sidebar.date_input("开始日期", end_date - timedelta(days=365))

# 3. 获取数据
if st.sidebar.button("加载数据"):
    with st.spinner("正在从 Yahoo Finance 获取数据..."):
        df = get_stock_data(ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

        if df is not None and not df.empty:
            st.success("✅ 数据加载成功！")
            
            # 调试信息
            with st.expander("🔍 调试信息"):
                st.write(f"列名类型: {type(df.columns)}")
                st.write(f"列名: {df.columns.tolist()}")
                st.write(f"数据形状: {df.shape}")
                st.write(f"前 2 行:\n{df.head(2)}")
            
            # 检查必需列
            required_cols = ['Date', 'Open', 'High', 'Low', 'Close']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"❌ 数据缺少必要列: {missing_cols}")
                st.write(f"💡 实际列名: {df.columns.tolist()}")
                st.stop()
            
            # 绘制 K 线图
            try:
                fig = go.Figure(data=[go.Candlestick(
                    x=df['Date'],
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='Price'
                )])
                
                fig.update_layout(
                    title=f"{ticker} 股价走势",
                    xaxis_title="日期",
                    yaxis_title="价格",
                    xaxis_rangeslider_visible=False  # 隐藏范围滑块，让图表更简洁
                )
                
                st.plotly_chart(fig, width="stretch", key="candlestick_chart")
                
            except Exception as e:
                st.error(f"❌ 图表绘制失败: {str(e)}")
                st.write("💡 调试信息：")
                st.write(f"Date 列类型: {type(df['Date'])}")
                st.write(f"Close 列前 3 个值: {df['Close'].head(3).tolist()}")
                st.stop()
            
            # 基本统计
            st.subheader(" 基本统计")
            col1, col2, col3 = st.columns(3)
            
            def to_float(val):
                """安全转换为浮点数"""
                if hasattr(val, 'item'):
                    return val.item()
                return float(val)
            
            try:
                col1.metric("最新收盘价", f"{to_float(df['Close'].iloc[-1]):.2f}")
                col2.metric("期间最高价", f"{to_float(df['High'].max()):.2f}")
                col3.metric("期间最低价", f"{to_float(df['Low'].min()):.2f}")
            except Exception as e:
                st.error(f"❌ 统计计算失败: {str(e)}")