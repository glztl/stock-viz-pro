import streamlit as st
import plotly.graph_objects as go
from src.data_fetcher import get_stock_data
from src.strategy import get_strategy_data  # 导入新策略
from datetime import timedelta, date
import pandas as pd

# 1. 页面配置
st.set_page_config(page_title="Stock Viz Pro", layout="wide")
st.title("📈 股票策略回测可视化 (均线交叉)")

# 2. 侧边栏输入
st.sidebar.header("⚙️ 配置参数")
ticker = st.sidebar.text_input("股票代码 (如 AAPL, 600519.SS)", "AAPL")

# 日期选择
end_date = st.sidebar.date_input("结束日期", date.today())
start_date = st.sidebar.date_input("开始日期", end_date - timedelta(days=365))

# 策略参数
st.sidebar.subheader("📉 策略参数")
short_window = st.sidebar.number_input("短期均线 (日)", min_value=5, max_value=100, value=50)
long_window = st.sidebar.number_input("长期均线 (日)", min_value=50, max_value=300, value=200)

# 3. 获取数据
if st.sidebar.button("🚀 运行策略分析"):
    with st.spinner("正在获取数据并计算策略..."):
        # 获取原始数据
        df = get_stock_data(ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

        if df is not None and not df.empty:
            # 检查数据长度是否足够计算长均线
            if len(df) < long_window:
                st.error(f"❌ 数据长度 ({len(df)} 天) 不足以计算 {long_window} 日均线。请选择更长的时间范围。")
                st.stop()

            st.success("✅ 数据加载成功！")
            
            # 计算策略
            df_strategy = get_strategy_data(df, short_window, long_window)
            
            if df_strategy is None or df_strategy.empty:
                st.error("❌ 策略计算后无有效数据。")
                st.stop()

            # 绘制主图表 (K 线 + 均线 + 信号)
            fig = go.Figure()

            # 1. K 线图
            fig.add_trace(go.Candlestick(
                x=df_strategy['Date'],
                open=df_strategy['Open'],
                high=df_strategy['High'],
                low=df_strategy['Low'],
                close=df_strategy['Close'],
                name='Price',
                increasing_line_color='#26a69a',
                decreasing_line_color='#ef5350'
            ))

            # 2. 均线
            fig.add_trace(go.Scatter(
                x=df_strategy['Date'],
                y=df_strategy['SMA_Short'],
                mode='lines',
                name=f'SMA {short_window}',
                line=dict(color='orange', width=1)
            ))
            
            fig.add_trace(go.Scatter(
                x=df_strategy['Date'],
                y=df_strategy['SMA_Long'],
                mode='lines',
                name=f'SMA {long_window}',
                line=dict(color='blue', width=1)
            ))

            # 3. 买卖信号标记
            # 买入信号 (Position == 1)
            buy_signals = df_strategy[df_strategy['Position'] == 1]
            fig.add_trace(go.Scatter(
                x=buy_signals['Date'],
                y=buy_signals['Close'],
                mode='markers',
                name='买入信号',
                marker=dict(symbol='triangle-up', size=10, color='green')
            ))

            # 卖出信号 (Position == -1)
            sell_signals = df_strategy[df_strategy['Position'] == -1]
            fig.add_trace(go.Scatter(
                x=sell_signals['Date'],
                y=sell_signals['Close'],
                mode='markers',
                name='卖出信号',
                marker=dict(symbol='triangle-down', size=10, color='red')
            ))

            # 布局更新
            fig.update_layout(
                title=f"{ticker} 策略回测 ( {short_window}/{long_window} 均线 )",
                xaxis_title="日期",
                yaxis_title="价格",
                xaxis_rangeslider_visible=False,
                height=600,
                legend=dict(orientation="h", y=1.02)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 策略绩效摘要
            st.subheader("📊 策略信号统计")
            col1, col2, col3 = st.columns(3)
            buy_count = len(buy_signals)
            sell_count = len(sell_signals)
            # 如果最后持有信号是 1，说明当前持有
            current_position = df_strategy['Signal'].iloc[-1]
            
            col1.metric("买入次数", f"{buy_count} 次")
            col2.metric("卖出次数", f"{sell_count} 次")
            col3.metric("当前状态", "持有中 🟢" if current_position == 1 else "空仓 ⚪")

            # 显示原始数据
            with st.expander("查看策略数据表"):
                st.dataframe(df_strategy[['Date', 'Close', 'SMA_Short', 'SMA_Long', 'Signal', 'Position']])
        else:
            st.error("❌ 未找到数据，请检查股票代码是否正确。")