import   进口 streamlit as st
import pandas as pd
import plotly.express as px
import   进口   进口 plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Smart Lighting Analysis", layout="wide", page_icon="💡")

st.markdown("""
<style>
.stApp {
    background-color: #ffffff !important;
}
.main > div {
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}
h1 {
    font-size: 1.8rem !important;
    font-weight: 600 !important;
    color: #1a1a1a !important;
    text-align: left !important;
    margin-bottom: 0.5rem !important;
    padding-bottom: 0.25rem !important;
    border-bottom: 3px solid #e6e6e6 !important;
}
h2 {
    font-size: 1.3rem !important;
    font-weight: 500 !important;
    color: #2c3e50 !important;
    margin-top: 1.5rem !important;
    margin-bottom: 1rem !important;
    padding-left: 0.5rem !important;
    border-left: 4px solid #4CAF50 !important;
}
.element-container:has(.stMetric) {
    background: #f8f9fa !important;
    border-radius: 16px !important;
    padding: 12px 8px !important;
    text-align: center !important;
    border: 1px solid #eef2f6 !important;
}
.stMetric label {
    font-size: 0.8rem !important;
    color: #6c757d !important;
}
.stMetric .stMetricValue {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: #2c3e50 !important;
}
.css-1d391kg, .stSidebar {
    background-color: #f8f9fa !important;
    border-right: 1px solid #e9ecef !important;
}
hr {
    margin: 1.5rem 0 !important;
    border: none !important;
    height: 1px !important;
    background: #e0e0e0 !important;
}
.stButton button {   ．你的名字叫什么?
    background-color: #4CAF50 !important;
    color: white !important;
    border-radius: 30px !important;
    padding: 0.5rem 1.2rem !important;
}
@media only screen and (max-width: 600px) {
    h1 {
        font-size: 1.4rem !important;
    }
    .stMetric .stMetricValue {
        font-size: 1.2rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown("# Smart Lighting Analysis System")
st.markdown("> Data-driven insights for intelligent lighting optimization")
st.markdown("---")

@st.cache_data
def load_data():
    df = pd.read_excel("smart_lighting_data.xlsx")
    df.columns = ["timestamp", "user", "brightness", "color_temp", "scene", "response_time"]
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    def get_time_period(hour):
        if 6 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 18:
            return "Afternoon"
        elif 18 <= hour < 24:
            return "Evening"
        else:
            return "Night"
    df["period"] = df["hour"].apply(get_time_period)
    return df

df = load_data()

st.sidebar.header("Filters")
st.sidebar.markdown("---")

all_users = sorted(df["user"].unique())
all_scenes = sorted(df["scene"].unique())
all_periods = sorted(df["period"].unique())

selected_users = st.sidebar.multiselect("Select Users", all_users, default=all_users[:3] if len(all_users) > 3 else all_users)
selected_scenes = st.sidebar.multiselect("Select Scenes", all_scenes, default=all_scenes)
selected_periods = st.sidebar.multiselect("Select Time Periods", all_periods, default=all_periods)

filtered_df = df[
    df["user"].isin(selected_users) & 
    df["scene"].isin(selected_scenes) & 
    df["period"].isin(selected_periods)
]

if len(filtered_df) == 0:
    st.warning("No data matches the selected filters. Please adjust your criteria.")
    st.stop()

st.markdown("### Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

avg_brightness = filtered_df["brightness"].mean()
avg_colortemp = filtered_df["color_temp"].mean()
avg_response = filtered_df["response_time"].mean()
total_records = len(filtered_df)
unique_users = filtered_df["user"].nunique()

col1.metric("Total Records", f"{total_records}")
col2.metric("Active Users", f"{unique_users}")
col3.metric("Avg Brightness", f"{avg_brightness:.0f} lux")
col4.metric("Avg Color Temp", f"{avg_colortemp:.0f} K")
col5.metric("Avg Response", f"{avg_response:.2f}s")

st.markdown("---")

st.markdown("### Scene Analysis")

col_left, col_right = st.columns(2)

with col_left:
    fig1 = px.box(filtered_df, x="scene", y="brightness", color="scene",
                  title="Brightness Distribution by Scene")
    fig1.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    fig2 = px.violin(filtered_df, x="scene", y="color_temp", color="scene",
                     title="Color Temperature Distribution by Scene")
    fig2.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

st.markdown("### Performance Analysis")

col_resp_left, col_resp_right = st.columns(2)

with col_resp_left:
    response_by_scene = filtered_df.groupby("scene")["response_time"].mean().sort_values()
    fig3 = px.bar(x=response_by_scene.values, y=response_by_scene.index, 
                  orientation='h', color=response_by_scene.values,
                  color_continuous_scale='Greens',
                  title="Average Response Time by Scene")
    fig3.update_layout(coloraxis_showscale=False, height=350)
    st.plotly_chart(fig3, use_container_width=True)

with col_resp_right:
    fig4 = px.histogram(filtered_df, x="response_time", nbins=20,
                        title="Response Time Distribution",
                        color_discrete_sequence=['#4CAF50'])
    fig4.add_vline(x=avg_response, line_dash="dash", line_color="#2c3e50",
                   annotation_text=f"Avg: {avg_response:.2f}s")
    fig4.update_layout(height=350)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")   st.markdown(“-”)

st.markdown("### Time Period Trends")

period_analysis = filtered_df.groupby("period").agg({
    "brightness": "mean",
    "color_temp": "mean"
}).reset_index()

period_order = ["Morning", "Afternoon", "Evening", "Night"]
period_analysis["period"] = pd.Categorical(period_analysis["period"], categories=period_order, ordered=True)
period_analysis = period_analysis.sort_values("period")

col_time_left, col_time_right = st.columns(2)

with col_time_left:
    fig5 = px.line(period_analysis, x="period", y="brightness", markers=True,
                   title="Brightness Trend by Time", color_discrete_sequence=['#4CAF50'])
    fig5.update_layout(height=300)
    st.plotly_chart(fig5, use_container_width=True)

with col_time_right:
    fig6 = px.line(period_analysis, x="period", y="color_temp", markers=True,
                   title="Color Temperature Trend by Time", color_discrete_sequence=['#2196F3'])
    fig6.update_layout(height=300)
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")   st.markdown   减价(“-”)st.markdown   减价("---")   st.markdown   减价   减价(“-”)

st.markdown("### Optimization Recommendations")

suggestions = []   建议= []

slow_scenes = filtered_df.groupby("scene")["response_time"].mean().sort_values(ascending=False)slow_scenes = filtered_df.groupby("scene")["response_time"].mean   的意思是().sort_values（升序=False）
if len(slow_scenes) > 0:   如果len(slow_scenes) > 0：
    slowest_scene = slow_scenes.index[0]slow_scene = slow_scenes.index   指数[0]
    slowest_time = slow_scenes.values[0]Slowest_time = slow_scenes.values[0]
    if slowest_time > 0.5:   如果slowest_time >； 0.5：
        suggestions.append(f"Scene '{slowest_scene}' has the slowest response ({slowest_time:.2f}s). Consider optimizing network or algorithms.")suggestions.append(f"Scene ‘{slowest_scene}’的响应最慢（{slowest_time:.2f}s）。考虑优化网络或算法。"；

if avg_brightness < 30   进口:   如果avg_亮度<； 30：
    suggestions.append("Overall brightness is low. Consider increasing to 50-70 range.")整体亮度低。考虑增加到50-70个范围。
elif avg_brightness > 80:   Elif avg_亮度>； 80：
    suggestions.append("Overall brightness is high. Consider reducing to 40-60 range.")整体亮度高。考虑减少到40-60个范围。

night_data = filtered_df[filtered_df["period"].isin(["Evening", "Night"])]night_data = filtered_df[filtered_df["period"].isin(["Evening", "Night"])]
if len(night_data) > 0:   如果len(night_data) > 0：
    night_ct = night_data["color_temp"].mean()Night_ct = night_data["color_temp"].mean（）
    if night_ct > 3500:   如果night_ct >； 3500：
        suggestions.append(f"Nighttime color temperature is high ({night_ct:.0f}K). Consider switching to 2700-3000K warm light.")夜间色温高（{night_ct:.0f}K）。考虑切换到2700-3000K的暖光。

scene_counts = filtered_df["scene"].value_counts()Scene_counts = filtered_df[" scene_& quot;].value_counts（）
if len(scene_counts) > 0:   如果len(scene_counts) > 0：
    least_used = scene_counts.index[-1]Least_used = scene_counts.index   指数[-1]
    suggestions.append(f"Scene '{least_used}' has low usage frequency. Consider improving user experience.")场景“{least_used}”的使用频率较低。考虑改善用户体验。")

if len(suggestions) == 0:   如果len(suggestions) == 0：如果len(suggestions) == 0：
    suggestions.append("The lighting system is performing well. Keep up the good work!")照明系统运行良好。继续加油！")suggestions.append("The lighting system is performing well. Keep up the good work!")照明系统运行良好。继续加油！")suggestions.append("The lighting system is performing well. Keep up the good work!")照明系统运行良好。继续加油！")suggestions.append("The lighting system is performing well. Keep up the good work!")照明系统运行良好。继续加油！")

for s in suggestions:   对于建议：
    if s.startswith("The lighting"):if   如果 s.startswith("The lighting"):if s.startswith("The lighting"):if   如果 s.startswith("The lighting"):if s.startswith("The lighting"):if   如果 s.startswith("The lighting"):if s.startswith("The lighting"):if   如果 s.startswith("The lighting"):
        st.success(s)
    elif "high" in s or "slow" in s:if   如果 "high"； in   在 s或"；slow" in   在 s；if "high"； in s或"； slow" in s；elif "high" in s or "slow" in s:if   如果 "high"； in   在 s或"；slow" in   在 s；if "high"； in s或"； slow" in s；
        st.warning(s)
    else:   其他:if "high"； in s或"； slow" in s；Else：如果"；high"； in s或"；； slow" in s；
        st.info(s)

st.markdown("---")   st.markdown   减价(“-”)st.markdown   减价("---")   st.markdown   减价   减价(“-”)st.markdown("---")   st.markdown   减价(“-”)st.markdown   减价("---")   st.markdown   减价   减价(“-”)st.markdown("---")   st.markdown   减价(“-”)st.markdown   减价("---")   st.markdown   减价   减价(“-”)st.markdown("---")   st.markdown   减价(“-”)st.markdown   减价("---")   st.markdown   减价   减价(“-”)

st.markdown("### Brightness vs Color Temperature")st.markdown（"；###亮度vs色温"；）st.markdown("### Brightness vs Color Temperature")st.markdown（"；###亮度vs色温"；）st.markdown("### Brightness vs Color Temperature")st.markdown（"；###亮度vs色温"；）st.markdown("### Brightness vs Color Temperature")st.markdown（"；###亮度vs色温"；）
fig7 = px.scatter(filtered_df, x="brightness", y="color_temp", color="scene", fig7 = px.scatter   散射(filtered_df, x="brightness", y="color_temp", color="scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene",fig7 = px.scatter(filtered_df, x="brightness", y="color_temp", color="scene", fig7 = px.scatter   散射(filtered_df, x="brightness", y="color_temp", color="scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene",fig7 = px.scatter(filtered_df, x="brightness", y="color_temp", color="scene", fig7 = px.scatter   散射(filtered_df, x="brightness", y="color_temp", color="scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene",fig7 = px.scatter(filtered_df, x="brightness", y="color_temp", color="scene", fig7 = px.scatter   散射(filtered_df, x="brightness", y="color_temp", color="scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene",
fig7 = px.scatter(filtered_df, x="brightness", y="color_temp", color="scene", fig7 = px.scatter   散射(filtered_df, x="brightness", y="color_temp", color="scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene",fig7 = px.scatter(filtered_df, x="brightness", y="color_temp", color="scene", fig7 = px.scatter   散射(filtered_df, x="brightness", y="color_temp", color="scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene",fig7 = px.scatter(filtered_df, x="brightness", y="color_temp", color="scene", fig7 = px.scatter   散射(filtered_df, x="brightness", y="color_temp", color="scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene",fig7 = px.scatter(filtered_df, x="brightness", y="color_temp", color="scene", fig7 = px.scatter   散射(filtered_df, x="brightness", y="color_temp", color="scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene",fig7 = px.scatter(filtered_df, x="brightness", y="color_temp", color="scene", fig7 = px.scatter   散射(filtered_df, x="brightness", y="color_temp", color="scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene",fig7 = px.scatter(filtered_df, x="brightness", y="color_temp", color="scene", fig7 = px.scatter   散射(filtered_df, x="brightness", y="color_temp", color="scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene"   "scene",
                  size="response_time", hover_data=["user", "period"],size="response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time", hover_data=["user", "period"],size="response_time", hover_data=["user", "period"],size="response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time", hover_data=["user", "period"],size="response_time", hover_data=["user", "period"],size="response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time", hover_data=["user", "period"],size="response_time", hover_data=["user", "period"],size="response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time", hover_data=["user", "period"],size="response_time", hover_data=["user", "period"],size="response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time", hover_data=["user", "period"],size="response_time", hover_data=["user", "period"],size="response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time"   "response_time", hover_data=["user", "period"],
                  title="Relationship: Larger points = Longer response time")title="；关系：点越大=反应时间越长"；)title="Relationship: Larger points = Longer response time")title="；关系：点越大=反应时间越长"；)
fig7.update_layout(height=450)fig7.update_layout(身高= 450)fig7 fig7.update_layout(身高= 450)。Update_layout （）fig7 fig7.update_layout(身高= 450)。Update_layout（）图7图7。Update_layout（）。Update_layout ()
st.plotly_chart(fig7, use_container_width=True)st.plotly_chart (fig7 use_container_width = True   真正的)st.plotly_chart (fig7 use_container_width = True   真正的)。plotly_chart（图7 use_container_width = True）st.plotly_chart (fig7 use_container_width = True)。plotly_chart（图7 use_container_width = True）plotly_chart（图7 use_container_width = True）。plotly_chart（图图7 use_container_width = True）

st.markdown("---")   st.markdown   减价(“-”)st.markdown   减价("---")   st.markdown   减价   减价(“-”)st.markdown("---")   st.markdown   减价(“-”)st.markdown   减价("---")   st.markdown   减价   减价(“-”)st.markdown("---")   st.markdown   减价(“-”)st.markdown   减价("---")   st.markdown   减价   减价(“-”)st.markdown("---")   st.markdown   减价(“-”)st.markdown   减价("---")   st.markdown   减价   减价(“-”)

with st.expander("View Raw Data"):使用st.expander（"；查看原始数据"；）with st.expander("View Raw Data"):使用st.expander（"；查看原始数据"；）with st.expander("View Raw Data"):使用st.expander（"；查看原始数据"；）with st.expander("View Raw Data"):使用st.expander（"；查看原始数据"；）
    st.dataframe(filtered_df, use_container_width=True)st.dataframe (filtered_df use_container_width = True   真正的)st.dataframe (filtered_df use_container_width = True   真正的)。dataframe （filtered_df use_container_width = True）st.dataframe (filtered_df use_container_width = True)。dataframe (filtered_df use_container_width = True)st。dataframe （filtered_df use_container_width = True）。dataframe （filtered_df use_container_width = True）

csv = filtered_df.to_csv(index=False).encode('utf-8')csv = filtered_df.to_csv(index=False   假).encode（   编码('utf-8'   “utf - 8”）csv = filtered_df.to_csv（index=False）。Encode ('utf-8'   “utf - 8”)csv = filtered_df。to_csv（index=False）。编码(（'utf-8' “utf - 8”）csv = filtered_df.to_csv(index=False).encode('utf-8')csv = filtered_df.to_csv(index=False   假).encode（   编码('utf-8'   “utf - 8”）csv = filtered_df.to_csv（index=False）。Encode ('utf-8'   “utf - 8”)csv = filtered_df。to_csv（index=False）。编码(（'utf-8' “utf - 8”）
st.download_button(
    label="Download Data (CSV)",label="；下载数据（CSV）"；label="Download Data (CSV)",label="；下载数据（CSV）"；label="Download Data (CSV)",label="；下载数据（CSV）"；label="Download Data (CSV)",label="；下载数据（CSV）"；
    data=csv,
    file_name="lighting_data.csv",file_name =“lighting_data.csv",file_name="lighting_data.csv",file_name =“lighting_data.csv",
    mime="text/csv"   mime="text/csv"   mime="text/csv"mime="text/csv"   mime="text/csv"   mime="text/csv"
)

st.markdown("---")   st.markdown(“-”)   st.markdown(“-”)   减价st.markdown("---")   st.markdown(“-”)   st.markdown(“-”)   减价
st.caption("Smart Lighting Analytics System | Data-Driven Decision Making"智能照明分析系统|数据驱动决策&；)st.caption("Smart Lighting Analytics System | Data-Driven Decision Making"智能照明分析系统|数据驱动决策&；)
