import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 页面配置
st.set_page_config(page_title="智能照明系统分析", layout="wide", page_icon="💡")

# ========== 自定义CSS（微信排版风格 - 白底黑字） ==========
st.markdown("""
<style>
/* 恢复白底黑字 */
.stApp {
    background-color: #ffffff !important;
}

/* 主容器内边距优化 */
.main > div {
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* 标题样式 - 精致适中 */
h1 {
    font-size: 1.8rem !important;
    font-weight: 600 !important;
    color: #1a1a1a !important;
    text-align: left !important;
    margin-bottom: 0.5rem !important;
    padding-bottom: 0.25rem !important;
    border-bottom: 3px solid #e6e6e6 !important;
    letter-spacing: -0.3px !important;
}

/* 副标题样式 */
h2 {
    font-size: 1.3rem !important;
    font-weight: 500 !important;
    color: #2c3e50 !important;
    margin-top: 1.5rem !important;
    margin-bottom: 1rem !important;
    padding-left: 0.5rem !important;
    border-left: 4px solid #4CAF50 !important;
}

h3 {
    font-size: 1.1rem !important;
    font-weight: 500 !important;
    color: #34495e !important;
    margin-top: 1rem !important;
    margin-bottom: 0.75rem !important;
}

/* 卡片指标样式 - 精致卡片 */
.element-container:has(.stMetric) {
    background: #f8f9fa !important;
    border-radius: 16px !important;
    padding: 12px 8px !important;
    text-align: center !important;
    transition: all 0.2s ease !important;
    border: 1px solid #eef2f6 !important;
}

.stMetric {
    background: transparent !important;
}

.stMetric label {
    font-size: 0.8rem !important;
    color: #6c757d !important;
    font-weight: 500 !important;
}

.stMetric .stMetricValue {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: #2c3e50 !important;
}

/* 侧边栏样式 - 清新 */
.css-1d391kg, .stSidebar {
    background-color: #f8f9fa !important;
    border-right: 1px solid #e9ecef !important;
}

.stSidebar .stMarkdown, .stSidebar header {
    color: #495057 !important;
}

/* 分割线 */
hr {
    margin: 1.5rem 0 !important;
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, #e0e0e0 0%, #e0e0e0 100%) !important;
}

/* 引用文字样式（描述语） */
.block-container .stMarkdown em, .block-container .stMarkdown blockquote {
    color: #6c757d !important;
    font-size: 0.85rem !important;
    border-left: 3px solid #4CAF50 !important;
    padding-left: 1rem !important;
    margin: 0.5rem 0 1rem 0 !important;
}

/* 优化建议卡片 */
.element-container:has(.stAlert) {
    margin: 0.75rem 0 !important;
}

.stAlert {
    border-radius: 12px !important;
    border-left: 4px solid !important;
    padding: 0.75rem 1rem !important;
}

/* 按钮样式 */
.stButton button {
    background-color: #4CAF50 !important;
    color: white !important;
    border-radius: 30px !important;
    padding: 0.5rem 1.2rem !important;
    font-weight: 500 !important;
    border: none !important;
    transition: all 0.2s ease !important;
}

.stButton button:hover {
    background-color: #45a049 !important;
    transform: translateY(-1px) !important;
}

/* 表格样式 */
.stDataFrame {
    border-radius: 12px !important;
    border: 1px solid #e9ecef !important;
}

/* 展开组件 */
.streamlit-expanderHeader {
    background-color: #f8f9fa !important;
    border-radius: 12px !important;
    font-weight: 500 !important;
    color: #2c3e50 !important;
}

.streamlit-expanderContent {
    border-radius: 0 0 12px 12px !important;
    border: 1px solid #e9ecef !important;
    border-top: none !important;
}

/* 手机适配 */
@media only screen and (max-width: 600px) {
    h1 {
        font-size: 1.4rem !important;
    }
    h2 {
        font-size: 1.1rem !important;
    }
    .stMetric .stMetricValue {
        font-size: 1.2rem !important;
    }
    .main > div {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown("# 💡 智能照明数据分析系统")
st.markdown("> 基于真实用户数据的照明行为分析与优化建议")
st.markdown("---")

# 读取数据
@st.cache_data
def load_data():
    df = pd.read_excel("智能照明系统数据集.xlsx")
    df.columns = ["时间戳", "用户", "亮度", "色温", "场景", "响应时间"]
    df["时间戳"] = pd.to_datetime(df["时间戳"])
    df["小时"] = df["时间戳"].dt.hour
    def get_time_period(hour):
        if 6 <= hour < 12:
            return "🌅 上午"
        elif 12 <= hour < 18:
            return "☀️ 下午"
        elif 18 <= hour < 24:
            return "🌙 夜间"
        else:
            return "🌃 深夜"
    df["时段"] = df["小时"].apply(get_time_period)
    return df

df = load_data()

# 侧边栏筛选
st.sidebar.header("🎛️ 筛选条件")
st.sidebar.markdown("---")

all_users = sorted(df["用户"].unique())
all_scenes = sorted(df["场景"].unique())
all_periods = sorted(df["时段"].unique())

selected_users = st.sidebar.multiselect("选择用户", all_users, default=all_users[:3] if len(all_users) > 3 else all_users)
selected_scenes = st.sidebar.multiselect("选择场景模式", all_scenes, default=all_scenes)
selected_periods = st.sidebar.multiselect("选择时段", all_periods, default=all_periods)

filtered_df = df[
    df["用户"].isin(selected_users) & 
    df["场景"].isin(selected_scenes) & 
    df["时段"].isin(selected_periods)
]

if len(filtered_df) == 0:
    st.warning("⚠️ 没有符合筛选条件的数据，请调整筛选条件")
    st.stop()

# ========== 核心指标卡片 ==========
st.markdown("### 📊 核心指标")

col1, col2, col3, col4, col5 = st.columns(5)

avg_brightness = filtered_df["亮度"].mean()
avg_colortemp = filtered_df["色温"].mean()
avg_response = filtered_df["响应时间"].mean()
total_records = len(filtered_df)
unique_users = filtered_df["用户"].nunique()

col1.metric("📝 数据记录数", f"{total_records}")
col2.metric("👥 活跃用户", f"{unique_users}")
col3.metric("💡 平均亮度", f"{avg_brightness:.0f} lux")
col4.metric("🎨 平均色温", f"{avg_colortemp:.0f} K")
col5.metric("⏱️ 平均响应", f"{avg_response:.2f}s")

st.markdown("---")

# ========== 场景分析 ==========
st.markdown("### 🎯 场景模式分析")

col_left, col_right = st.columns(2)

with col_left:
    fig1 = px.box(filtered_df, x="场景", y="亮度", color="场景",
                  title="亮度分布范围", color_discrete_sequence=px.colors.qualitative.Pastel)
    fig1.update_layout(showlegend=False, plot_bgcolor="white", height=400)
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    fig2 = px.violin(filtered_df, x="场景", y="色温", color="场景",
                     title="色温分布密度", color_discrete_sequence=px.colors.qualitative.Pastel)
    fig2.update_layout(showlegend=False, plot_bgcolor="white", height=400)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ========== 响应时间分析 ==========
st.markdown("### ⏱️ 性能分析")

col_resp_left, col_resp_right = st.columns(2)

with col_resp_left:
    response_by_scene = filtered_df.groupby("场景")["响应时间"].mean().sort_values()
    fig3 = px.bar(x=response_by_scene.values, y=response_by_scene.index, 
                  orientation='h', color=response_by_scene.values,
                  color_continuous_scale='Greens',
                  title="各场景平均响应时间", text_auto='.2f')
    fig3.update_layout(coloraxis_showscale=False, plot_bgcolor="white", height=350)
    st.plotly_chart(fig3, use_container_width=True)

with col_resp_right:
    fig4 = px.histogram(filtered_df, x="响应时间", nbins=20,
                        title="响应时间分布", color_discrete_sequence=['#4CAF50'])
    fig4.add_vline(x=avg_response, line_dash="dash", line_color="#2c3e50",
                   annotation_text=f"平均 {avg_response:.2f}s")
    fig4.update_layout(plot_bgcolor="white", height=350)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ========== 时段分析 ==========
st.markdown("### 🕐 时段趋势")

period_analysis = filtered_df.groupby("时段").agg({
    "亮度": "mean",
    "色温": "mean"
}).reset_index()

period_order = ["🌅 上午", "☀️ 下午", "🌙 夜间", "🌃 深夜"]
period_analysis["时段"] = pd.Categorical(period_analysis["时段"], categories=period_order, ordered=True)
period_analysis = period_analysis.sort_values("时段")

col_time_left, col_time_right = st.columns(2)

with col_time_left:
    fig5 = px.line(period_analysis, x="时段", y="亮度", markers=True,
                   title="亮度变化趋势", color_discrete_sequence=['#4CAF50'])
    fig5.update_layout(plot_bgcolor="white", height=300)
    st.plotly_chart(fig5, use_container_width=True)

with col_time_right:
    fig6 = px.line(period_analysis, x="时段", y="色温", markers=True,
                   title="色温变化趋势", color_discrete_sequence=['#2196F3'])
    fig6.update_layout(plot_bgcolor="white", height=300)
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

# ========== 优化建议 ==========
st.markdown("### 💡 优化建议")

suggestions = []

slow_scenes = filtered_df.groupby("场景")["响应时间"].mean().sort_values(ascending=False)
slowest_scene = slow_scenes.index[0] if len(slow_scenes) > 0 else None
slowest_time = slow_scenes.values[0] if len(slow_scenes) > 0 else 0

if slowest_time > 0.5:
    suggestions.append(f"⚠️ **{slowest_scene}** 场景响应最慢（{slowest_time:.2f}秒），建议优化网络或算法")

if avg_brightness < 30:
    suggestions.append("💡 整体亮度偏低，建议提升至50-70之间")
elif avg_brightness > 80:
    suggestions.append("⚠️ 整体亮度过高，建议降至40-60范围")

night_data = filtered_df   将streamlit导入为st[filtered_df["时段"].isin(["🌙 夜间", "🌃 深夜"])]
if len(night_data) > 0:
    night_ct = night_data["色温"].mean()
    if night_ct > 3500:
        suggestions.append(f"🌙 夜间色温偏高（{night_ct:.0f}K），建议切换至2700-3000K暖光")

scene_counts = filtered_df["场景"].value_counts()
if len(scene_counts) > 0:
    least_used = scene_counts.index[-1]
    suggestions.append(f"📱 **{least_used}** 场景使用频率较低，建议优化体验")

if len(suggestions) == 0:
    suggestions.append("✅ 当前照明系统运行良好")

for s in suggestions:
    if s.startswith("✅"):
        st.success(s)
    elif s.startswith("⚠️"):
        st.warning(s)
    else:
        st.info(s)

st.markdown("---")

# ========== 关系分析 ==========
st.markdown("### 🔍 亮度 vs 色温")
fig7 = px.scatter(filtered_df, x="亮度", y="色温", color="场景", 
                  size="响应时间", hover_data=["用户", "时段"],
                  title="亮度与色温关系（点越大=响应时间越长）",
                  color_discrete_sequence=px.colors.qualitative.Pastel)
fig7.update_layout(plot_bgcolor="white", height=450)
st.plotly_chart(fig7, use_container_width=True)

st.markdown("---")

# ========== 数据表格 ==========
with st.expander("📄 查看原始数据"):
    st.dataframe(filtered_df, use_container_width=True)

# ========== 下载 ==========
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 下载数据 (CSV)",
    data=csv,
    file_name="照明数据.csv",
    mime="text/csv"
)

# 页脚
st.markdown("---")
st.caption("智能照明数据分析系统 · 数据驱动优化决策")
