import streamlit as st
import pandas as pd
import altair as alt
import datetime
import time
from data.baostock_provider import data_provider
from core.engine import AnalysisEngine
from core.strategies_registry import get_strategy, get_all_strategy_keys

# Page Config
st.set_page_config(
    page_title="OmniAlpha 选股工作台",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- State Initialization ---
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'stock_pool' not in st.session_state:
    st.session_state.stock_pool = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'progress_text' not in st.session_state:
    st.session_state.progress_text = "准备就绪"

# Title and Intro
st.title("📈 OmniAlpha 智能选股工作台")
st.markdown("""
通过 **Baostock** 数据源，结合技术面与基本面策略，快速筛选 A 股优质标的。
支持 CSV 导入预选股票池，或直接全市场扫描。
""")

# --- Sidebar Configuration ---
st.sidebar.header("⚙️ 参数配置")

# 1. Date Selection
default_date = datetime.date.today()
selected_date = st.sidebar.date_input("📅 分析日期 (回测/复盘)", default_date)
date_str = selected_date.strftime("%Y-%m-%d")

# 2. Strategy Selection
st.sidebar.subheader("🛠 策略组合")
available_strategies = get_all_strategy_keys()
selected_strategy_keys = st.sidebar.multiselect(
    "选择要应用的策略 (取交集)",
    options=available_strategies,
    default=['ma'],
    help="同时满足所选所有策略的股票才会被选中"
)

with st.sidebar.expander("📖 策略说明指南"):
    st.markdown("""
    **技术面 (Technical)**
    - `ma`: **均线趋势** (收盘价 > MA20 & MA5金叉)
    - `vol`: **放量突破** (量比 > 1.5 & 涨幅 > 2%)
    - `turn`: **活跃资金** (换手 > 5% & 非ST)

    **基本面 (Fundamental)**
    - `pe`: **低估值** (0 < PE < 30)
    - `growth`: **高成长** (净利同比 > 20%)
    - `roe`: **高盈利** (ROE > 15%)
    - `debt`: **低负债** (资产负债率 < 50%)
    """)

# 3. Mode Selection
st.sidebar.subheader("🎯 扫描范围")
data_source_mode = st.sidebar.radio(
    "股票池来源",
    ("沪深300 (默认)", "CSV 文件导入", "快速测试 (前20只)")
)

with st.sidebar.expander("🛠 制作自定义股票池 CSV"):
    st.caption("输入代码用分号 ';' 隔开，如: sh.600000;sz.000001")
    user_input_codes = st.text_area("股票代码输入框", height=100)
    if user_input_codes:
        code_list = [c.strip() for c in user_input_codes.split(';') if c.strip()]
        if code_list:
            df_custom = pd.DataFrame({'code': code_list})
            csv_data = df_custom.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 生成并下载 CSV",
                data=csv_data,
                file_name="custom_pool.csv",
                mime='text/csv',
                key='dl_custom'
            )

# --- Market Overview (New) ---
st.subheader("📊 市场大盘 (上证指数)")
try:
    with st.spinner("正在加载大盘数据..."):
        data_provider.login()
        # Fetch SSE Composite Index Data (sh.000001)
        start_date_idx = (datetime.datetime.strptime(date_str, "%Y-%m-%d") - datetime.timedelta(days=90)).strftime("%Y-%m-%d")
        df_index = data_provider.get_daily_bars('sh.000001', start_date_idx, date_str)
        
        if df_index is not None and not df_index.empty:
            last_idx = df_index.iloc[-1]
            prev_idx = df_index.iloc[-2] if len(df_index) > 1 else last_idx
            
            change = last_idx['close'] - prev_idx['close']
            pct_change = (change / prev_idx['close']) * 100
            
            # Metric
            col_idx_1, col_idx_2 = st.columns([1, 3])
            with col_idx_1:
                st.metric(
                    label=f"上证指数 ({last_idx['date']})",
                    value=f"{last_idx['close']:.2f}",
                    delta=f"{change:.2f} ({pct_change:.2f}%)"
                )
            
            with col_idx_2:
                # Simple Area Chart
                chart_index = alt.Chart(df_index).mark_area(
                    line={'color':'darkblue'},
                    color=alt.Gradient(
                        gradient='linear',
                        stops=[alt.GradientStop(color='darkblue', offset=0),
                               alt.GradientStop(color='white', offset=1)],
                        x1=1, x2=1, y1=1, y2=0
                    )
                ).encode(
                    x=alt.X('date:T', title='日期'),
                    y=alt.Y('close:Q', scale=alt.Scale(zero=False), title='点位'),
                    tooltip=['date', 'close', 'pctChg']
                ).properties(height=150)
                st.altair_chart(chart_index, use_container_width=True)
        else:
            st.warning("暂无大盘数据，请检查日期或网络。")
except Exception as e:
    st.error(f"加载大盘数据失败: {e}")

# --- Main Logic ---

def load_stock_pool(mode, uploaded_file=None):
    """Helper to load stock pool based on mode"""
    try:
        data_provider.login()
        if mode == "CSV 文件导入":
            if uploaded_file is not None:
                df = pd.read_csv(uploaded_file)
                if 'code' in df.columns:
                    return df['code'].tolist()
                else:
                    st.error("CSV 文件必须包含 'code' 列")
                    return []
            else:
                st.warning("请上传 CSV 文件")
                return []
        elif mode == "快速测试 (前20只)":
            full_pool = data_provider.get_hs300_stocks(date_str)
            return full_pool[:20] if full_pool else []
        else: # 沪深300
            return data_provider.get_hs300_stocks(date_str)
    except Exception as e:
        st.error(f"获取股票池失败: {e}")
        return []

# File Uploader (Conditional)
uploaded_file = None
if data_source_mode == "CSV 文件导入":
    uploaded_file = st.file_uploader("📂 拖拽或选择 CSV 文件 (包含 'code' 列)", type=['csv'])

# Control Buttons
col_start, col_stop, col_status = st.columns([1, 1, 4])

with col_start:
    start_btn = st.button("🚀 开始分析", type="primary", disabled=st.session_state.is_running)

with col_stop:
    stop_btn = st.button("🛑 停止分析", type="secondary", disabled=not st.session_state.is_running)

# --- Start Logic ---
if start_btn:
    if not selected_strategy_keys:
        st.error("请至少选择一种策略！")
    else:
        with st.spinner(f"正在获取股票池 ({data_source_mode})..."):
            pool = load_stock_pool(data_source_mode, uploaded_file)
        
        if pool:
            st.session_state.stock_pool = pool
            st.session_state.current_index = 0
            st.session_state.analysis_results = [] # Reset results
            st.session_state.is_running = True
            st.session_state.progress_text = "开始扫描..."
            st.rerun()
        else:
            if data_source_mode != "CSV 文件导入":
                 st.warning("股票池为空，请检查日期或网络。")

# --- Stop Logic ---
if stop_btn:
    st.session_state.is_running = False
    st.session_state.progress_text = "已手动停止分析"
    st.rerun()

# --- Execution Loop (Batch Processing) ---
if st.session_state.is_running:
    pool = st.session_state.stock_pool
    idx = st.session_state.current_index
    total = len(pool)
    
    # Init Engine
    strategies = [get_strategy(k) for k in selected_strategy_keys]
    engine = AnalysisEngine(strategies)
    
    # Show Progress Bar
    progress_val = min(idx / total, 1.0)
    st.progress(progress_val)
    st.info(f"正在扫描: {idx}/{total} ({int(progress_val*100)}%) - {st.session_state.progress_text}")

    # Process a Batch (e.g., 5 stocks)
    BATCH_SIZE = 5
    end_idx = min(idx + BATCH_SIZE, total)
    
    try:
        data_provider.login()
        
        for i in range(idx, end_idx):
            code = pool[i]
            res = engine.scan_one(code, date_str)
            if res:
                st.session_state.analysis_results.append(res)
        
        # Update State
        st.session_state.current_index = end_idx
        
        if end_idx >= total:
            st.session_state.is_running = False
            st.session_state.progress_text = "分析完成！"
            st.rerun()
        else:
            # Continue Loop
            time.sleep(0.01) # Yield slightly
            st.rerun()
            
    except Exception as e:
        st.error(f"运行时错误: {e}")
        st.session_state.is_running = False

# --- Result Display ---
if st.session_state.analysis_results is not None and not st.session_state.is_running:
    results = st.session_state.analysis_results
    if results:
        st.success(f"{st.session_state.progress_text} 共筛选出 {len(results)} 只股票")
        st.divider()
        
        df_results = pd.DataFrame(results)
        
        # Reorder cols
        cols = ['code', 'strategy'] + [c for c in df_results.columns if c not in ['code', 'strategy', 'date']]
        df_results = df_results[cols]
        
        # Interactive Table
        st.dataframe(df_results, use_container_width=True)
        
        # Download
        csv = df_results.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 下载结果 CSV",
            data=csv,
            file_name=f"omnialpha_selection_{date_str}.csv",
            mime='text/csv',
        )
        
        # --- Visual Analysis Section ---
        st.divider()
        st.subheader("📈 优选股特征分布与统计")
        
        # Tabs for better organization
        tab1, tab2 = st.tabs(["估值分布 (基本面)", "量价特征 (技术面)"])
        
        with tab1:
            col_val_1, col_val_2 = st.columns(2)
            
            with col_val_1:
                if 'peTTM' in df_results.columns:
                    st.markdown("**市盈率 (PE-TTM) 分布**")
                    st.caption("反映股票估值高低，通常 <30 为合理或低估区间。")
                    chart_pe = alt.Chart(df_results).mark_bar(color='#4c78a8').encode(
                        x=alt.X('peTTM', bin=alt.Bin(maxbins=20), title='PE TTM'),
                        y=alt.Y('count()', title='股票数量'),
                        tooltip=['count()', alt.Tooltip('peTTM', bin=True, title='PE区间')]
                    ).interactive()
                    st.altair_chart(chart_pe, use_container_width=True)
                else:
                    st.info("结果中不包含 PE 数据，无法展示分布图。")

            with col_val_2:
                if 'pbMRQ' in df_results.columns:
                    st.markdown("**市净率 (PB-MRQ) 分布**")
                    st.caption("反映资产溢价情况，<3 通常被认为安全边际较高。")
                    chart_pb = alt.Chart(df_results).mark_bar(color='#e45756').encode(
                        x=alt.X('pbMRQ', bin=alt.Bin(maxbins=20), title='PB MRQ'),
                        y=alt.Y('count()', title='股票数量'),
                        tooltip=['count()', alt.Tooltip('pbMRQ', bin=True, title='PB区间')]
                    ).interactive()
                    st.altair_chart(chart_pb, use_container_width=True)
                else:
                    st.info("结果中不包含 PB 数据，无法展示分布图。")

        with tab2:
            col_tech_1, col_tech_2 = st.columns(2)
            
            with col_tech_1:
                if 'turn' in df_results.columns and 'pctChg' in df_results.columns:
                    st.markdown("**换手率 vs 涨跌幅**")
                    st.caption("展示活跃度与短期表现的关系。右上角代表高活跃高涨幅。")
                    chart_scatter = alt.Chart(df_results).mark_circle(size=60).encode(
                        x=alt.X('turn', title='换手率 (%)'),
                        y=alt.Y('pctChg', title='涨跌幅 (%)'),
                        color=alt.Color('strategy', title='策略来源'),
                        tooltip=['code', 'turn', 'pctChg', 'price']
                    ).interactive()
                    st.altair_chart(chart_scatter, use_container_width=True)
                else:
                    st.info("缺少换手率或涨跌幅数据。")
            
            with col_tech_2:
                if 'price' in df_results.columns:
                    st.markdown("**股价分布**")
                    st.caption("筛选出股票的价格区间分布。")
                    chart_price = alt.Chart(df_results).mark_bar(color='#f58518').encode(
                        x=alt.X('price', bin=True, title='收盘价'),
                        y=alt.Y('count()', title='股票数量'),
                        tooltip=['count()']
                    ).interactive()
                    st.altair_chart(chart_price, use_container_width=True)
                else:
                    st.info("缺少价格数据。")

        # Detail View
        st.subheader("🔍 个股深度透视 & 对比")
        
        col_sel_1, col_sel_2 = st.columns([1, 3])
        with col_sel_1:
            selected_stock = st.selectbox("选择一只股票查看详情", df_results['code'].tolist())
        
        if selected_stock:
            # Pre-calculate averages for comparison
            avg_pe = df_results['peTTM'].mean() if 'peTTM' in df_results.columns else 0
            avg_pb = df_results['pbMRQ'].mean() if 'pbMRQ' in df_results.columns else 0
            avg_turn = df_results['turn'].mean() if 'turn' in df_results.columns else 0

            with st.spinner("加载K线与历史指标..."):
                try:
                    data_provider.login()
                    start_date_k = (datetime.datetime.strptime(date_str, "%Y-%m-%d") - datetime.timedelta(days=250)).strftime("%Y-%m-%d")
                    df_k = data_provider.get_daily_bars(selected_stock, start_date_k, date_str)
                except Exception as e:
                    st.error(f"加载数据失败: {e}")
                    df_k = None
                finally:
                    data_provider.logout()

                if df_k is not None and len(df_k) > 0:
                    # Current metrics
                    curr_pe = df_k.iloc[-1].get('peTTM', 0)
                    curr_pb = df_k.iloc[-1].get('pbMRQ', 0)
                    curr_turn = df_k.iloc[-1].get('turn', 0)
                    
                    # --- Comparison Metrics Row ---
                    st.markdown("##### 📊 个股 vs 选股池均值对比")
                    m_col1, m_col2, m_col3 = st.columns(3)
                    
                    with m_col1:
                        st.metric(
                            label="PE-TTM (市盈率)", 
                            value=f"{curr_pe:.2f}", 
                            delta=f"{curr_pe - avg_pe:.2f} (vs 均值 {avg_pe:.2f})",
                            delta_color="inverse" # Lower PE is usually better (green)
                        )
                    with m_col2:
                        st.metric(
                            label="PB-MRQ (市净率)", 
                            value=f"{curr_pb:.2f}", 
                            delta=f"{curr_pb - avg_pb:.2f} (vs 均值 {avg_pb:.2f})",
                            delta_color="inverse"
                        )
                    with m_col3:
                        st.metric(
                            label="换手率 (%)", 
                            value=f"{curr_turn:.2f}%", 
                            delta=f"{curr_turn - avg_turn:.2f}% (vs 均值 {avg_turn:.2f}%)"
                        )
                    
                    st.divider()

                    # --- Indicator Calculation ---
                    df_k['MA5'] = df_k['close'].rolling(window=5).mean()
                    df_k['MA20'] = df_k['close'].rolling(window=20).mean()
                    df_k['MA60'] = df_k['close'].rolling(window=60).mean()
                    
                    # RSI Calculation (Simple 14-day)
                    delta = df_k['close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    df_k['RSI'] = 100 - (100 / (1 + rs))
                    
                    # Fill NaN for plotting
                    df_plot = df_k.tail(100).fillna(0) # Show last 100 days
                    
                    # --- Charts ---
                    base = alt.Chart(df_plot).encode(x=alt.X('date:T', axis=alt.Axis(title='日期')))
                    
                    # 1. Price & MA Chart
                    line_close = base.mark_line(color='black', strokeWidth=2).encode(
                        y=alt.Y('close:Q', scale=alt.Scale(zero=False), title='价格'),
                        tooltip=['date', 'close', 'open', 'high', 'low']
                    )
                    line_ma5 = base.mark_line(color='#ff7f0e', strokeDash=[2,2]).encode(y='MA5', tooltip=['MA5'])
                    line_ma20 = base.mark_line(color='#2ca02c').encode(y='MA20', tooltip=['MA20'])
                    line_ma60 = base.mark_line(color='#1f77b4').encode(y='MA60', tooltip=['MA60'])
                    
                    chart_price = (line_close + line_ma5 + line_ma20 + line_ma60).properties(
                        height=300, 
                        title=f"📈 股价趋势与均线 ({selected_stock})"
                    )
                    
                    # 2. Volume Chart
                    chart_vol = base.mark_bar(color='#9467bd').encode(
                        y=alt.Y('volume:Q', axis=alt.Axis(title='成交量')),
                        tooltip=['volume']
                    ).properties(height=100)
                    
                    # 3. Valuation Trends (PE & PB) - NEW
                    chart_pe_line = base.mark_line(color='#17becf').encode(
                        y=alt.Y('peTTM:Q', title='PE TTM'),
                        tooltip=['peTTM']
                    )
                    chart_pb_line = base.mark_line(color='#bcbd22').encode(
                        y=alt.Y('pbMRQ:Q', title='PB MRQ'),
                        tooltip=['pbMRQ']
                    )
                    
                    chart_valuation = alt.layer(chart_pe_line, chart_pb_line).resolve_scale(
                        y='independent'
                    ).properties(height=150, title="估值走势 (左轴:PE, 右轴:PB)")

                    # 4. RSI Chart
                    chart_rsi = base.mark_line(color='#d62728').encode(
                        y=alt.Y('RSI:Q', scale=alt.Scale(domain=[0, 100]), title='RSI')
                    ).properties(height=100, title="RSI 相对强弱指标")
                    
                    rsi_rule_top = base.mark_rule(color='gray', strokeDash=[4,4]).encode(y=alt.datum(70))
                    rsi_rule_bot = base.mark_rule(color='gray', strokeDash=[4,4]).encode(y=alt.datum(30))
                    
                    chart_rsi_final = chart_rsi + rsi_rule_top + rsi_rule_bot

                    # Combine all
                    final_chart = alt.vconcat(
                        chart_price, 
                        chart_vol, 
                        chart_valuation, 
                        chart_rsi_final
                    ).resolve_scale(x='shared')
                    
                    st.altair_chart(final_chart, use_container_width=True)
                    
                    with st.expander("📊 查看详细历史数据表格"):
                        st.dataframe(df_k.tail(20))
    else:
        st.warning(f"{st.session_state.progress_text}，但未找到符合条件的股票。")

# Footer
st.markdown("---")
st.caption("OmniAlpha Strategy Engine v1.2 | Powered by Baostock & Streamlit | 此工具仅供学习研究，不构成投资建议")
