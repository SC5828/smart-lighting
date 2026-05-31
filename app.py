import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 页面配置
st.set_page_config(page_title="智能照明系统分析", layout="wide", page_icon="💡")

# ========== 自定义CSS（包含手机字体优化） ==========
st.markdown("""
<style>
/* 渐变背景 */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
}
/* 卡片样式 */
.css-1r6slb0, .css-1v3fvcr {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 15px;
}
/* 标题美化 */
h1 {
    font-size: 2rem !important;
    background: linear-gradient(135deg, #fff 0%, #a0a0ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
}
h2, h3 {
    background: linear-gradient(135deg, #fff 0%, #a0a0ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
/* 手机屏幕适配 - 标题字体缩小一半 */
@media only screen and (max-width: 600px) {
    h1 {
        font-size: 1rem !important;
    }
    /* 让卡片在手机上变成一列 */
    .stColumn {
        width: 100% !important;
        margin-bottom: 10px;
    }
}
</style>
""", unsafe_allow_html=True)

# 标题（使用 markdown 方式，更易控制）
st.markdown("# 💡 智能照明数据分析系统")
st.markdown("> 基于真实用户数据的照明行为分析与优化建议")
st.markdown("---")

# 读取数据（适配你的Excel文件）
@st.cache_data
def load_data():
    df = pd.read_excel("智能照明系统数据集.xlsx")
    # 重命名列名（简化）
    df.columns = ["时间戳", "用户", "亮度", "色温", "场景", "响应时间"]
    # 转换时间戳为日期格式
    df["时间戳"] = pd.to_datetime(df["时间戳"])
    # 提取小时
    df["小时"] = df["时间戳"].dt.hour
    # 定义时段
    def get_time_period(hour):
        if 6 <= hour < 12:
            return "🌅 上午 (6-12点)"
        elif 12 <= hour < 18:
            return "☀️ 下午 (12-18点)"
        elif 18 <= hour < 24:
            return "🌙 夜间 (18-24点)"
        else:
            return "🌃 深夜 (0-6点)"
    df["时段"] = df["小时"].apply(get_time_period)
    return df

df = load_data()

# 侧边栏筛选
st.sidebar.header("🎛️ 筛选条件")

# 获取所有唯一值
all_users = sorted(df["用户"].unique())
all_scenes = sorted(df["场景"].unique())
all_periods = sorted(df["时段"].unique())

selected_users = st.sidebar.multiselect("选择用户", all_users, default=all_users[:3] if len(all_users) > 3 else all_users)
selected_scenes = st.sidebar.multiselect("选择场景模式", all_scenes, default=all_scenes)
selected_periods = st.sidebar.multiselect("选择时段", all_periods, default=all_periods)

# 筛选数据
filtered_df = df[
    df["用户"].isin(selected_users) & 
    df["场景"].isin(selected_scenes) & 
    df["时段"].isin(selected_periods)
]

if len(filtered_df) == 0:
    st.warning("⚠️ 没有符合筛选条件的数据，请调整筛选条件")
    st.stop()

# ========== 第一行：核心指标卡片 ==========
st.subheader("📊 核心指标概览")
col1, col2, col3, col4, col5 = st.columns(5)

avg_brightness = filtered_df["亮度"].mean()
avg_colortemp = filtered_df["色温"].mean()
avg_response = filtered_df["响应时间"].mean()
total_records = len(filtered_df)
unique_users = filtered_df["用户"].nunique()

col1.metric("📝 数据记录数", f"{total_records} 条")
col2.metric("👥 活跃用户", f"{unique_users} 人")
col3.metric("💡 平均亮度", f"{avg_brightness:.1f} lux")
col4.metric("🎨 平均色温", f"{avg_colortemp:.0f} K")
col5.metric("⏱️ 平均响应时间", f"{avg_response:.2f} 秒")

st.markdown("---")

# ========== 第二行：两个主要图表 ==========
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 不同场景的亮度分布")
    fig1 = px.box(filtered_df, x="场景", y="亮度", color="场景",
                  title="各场景模式下的亮度范围",
                  labels={"亮度": "光线亮度值 (0-100)", "场景": "使用场景"})
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("🎨 不同场景的色温分布")
    fig2 = px.violin(filtered_df, x="场景", y="色温", color="场景",
                     title="各场景模式下的色温分布",
                     labels={"色温": "色温值 (K)", "场景": "使用场景"})
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ========== 第三行：响应时间分析 ==========
st.subheader("⏱️ 响应时间分析")

col_resp_left, col_resp_right = st.columns(2)

with col_resp_left:
    # 各场景平均响应时间
    response_by_scene = filtered_df.groupby("场景")["响应时间"].mean().sort_values()
    fig3 = px.bar(x=response_by_scene.values, y=response_by_scene.index, 
                  orientation='h', color=response_by_scene.values,
                  color_continuous_scale='RdYlGn_r',
                  title="各场景平均响应时间（越小越好）",
                  labels={"x": "响应时间 (秒)", "y": "场景"})
    fig3.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

with col_resp_right:
    # 响应时间分布
    fig4 = px.histogram(filtered_df, x="响应时间", nbins=30,
                        title="响应时间分布直方图",
                        labels={"响应时间": "响应时间 (秒)"})
    fig4.add_vline(x=avg_response, line_dash="dash", line_color="red",
                   annotation_text=f"平均: {avg_response:.2f}s")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ========== 第四行：时段分析 ==========
st.subheader("🕐 时段行为分析")

# 按时段统计平均亮度和色温
period_analysis = filtered_df.groupby("时段").agg({
    "亮度": "mean",
    "色温": "mean",
    "响应时间": "mean"
}).reset_index()

# 时段顺序排序
period_order = ["🌅 上午 (6-12点)", "☀️ 下午 (12-18点)", "🌙 夜间 (18-24点)", "🌃 深夜 (0-6点)"]
period_analysis["时段"] = pd.Categorical(period_analysis["时段"], categories=period_order, ordered=True)
period_analysis = period_analysis.sort_values("时段")

col_time_left, col_time_right = st.columns(2)

with col_time_left:
    fig5 = px.line(period_analysis, x="时段", y="亮度", markers=True,
                   title="不同时段的平均亮度变化",
                   labels={"亮度": "平均亮度 (lux)"})
    st.plotly_chart(fig5, use_container_width=True)

with col_time_right:
    fig6 = px.line(period_analysis, x="时段", y="色温", markers=True,
                   title="不同时段的平均色温变化",
                   labels={"色温": "平均色温 (K)"})
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

# ========== 第五行：优化建议（基于真实数据） ==========
st.subheader("📋 智能优化建议")

suggestions = []

# 分析响应时间
slow_scenes = filtered_df.groupby("场景")["响应时间"].mean().sort_values(ascending=False)
slowest_scene = slow_scenes.index[0] if len(slow_scenes) > 0 else None
slowest_time = slow_scenes.values[0] if len(slow_scenes) > 0 else 0

if slowest_time > 0.5:
    suggestions.append(f"⚠️ **{slowest_scene}** 场景响应时间最慢（{slowest_time:.2f}秒），建议优化该场景的算法或网络连接")

# 分析亮度合理性
if avg_brightness < 30:
    suggestions.append("💡 整体亮度偏低（<30），建议在活动区域提高亮度至50-70之间")
elif avg_brightness > 80:
    suggestions.append("⚠️ 整体亮度过高，可能造成视觉疲劳，建议降低至40-60范围")

# 分析色温
night_data = filtered_df[filtered_df["时段"].str.contains("夜间|深夜")]
if len(night_data) > 0:
    night_ct = night_data["色温"].mean()
    if night_ct > 3500:
        suggestions.append(f"🌙 夜间色温偏高（{night_ct:.0f}K），建议切换至2700-3000K暖光，有助睡眠")

# 分析各场景使用频率
scene_counts = filtered_df["场景"].value_counts()
if len(scene_counts) > 0:
    least_used = scene_counts.index[-1] if len(scene_counts) > 0 else None
    if least_used:
        suggestions.append(f"📱 **{least_used}** 场景使用频率较低，可考虑优化该场景的用户体验或功能")

if len(suggestions) == 0:
    suggestions.append("✅ 当前照明系统运行良好，继续保持！")

for s in suggestions:
    if s.startswith("✅"):
        st.success(s)
    elif s.startswith("⚠️"):
        st.warning(s)
    else:
        st.info(s)

st.markdown("---")

# ========== 第六行：可视化增强 - 散点图 ==========
st.subheader("🔍 亮度 vs 色温 关系分析")
fig7 = px.scatter(filtered_df, x="亮度", y="色温", color="场景", 
                  size="响应时间", hover_data=["用户", "时段"],
                  title="亮度与色温的分布关系（点越大=响应时间越长）",
                  labels={"亮度": "亮度值", "色温": "色温值"})
st.plotly_chart(fig7, use_container_width=True)

st.markdown("---")

# ========== 第七行：原始数据表格 ==========
with st.expander("📊 查看原始数据（点击展开）"):
    st.dataframe(filtered_df, use_container_width=True)

# ========== 第八行：下载功能 ==========
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="⬇️ 下载筛选后的数据 (CSV格式)",
    data=csv,
    file_name="照明数据_筛选结果.csv",
    mime="text/csv"
)

# 页脚
st.markdown("---")
st.caption("💡 智能照明数据分析系统 | 基于真实用户数据生成优化建议")
