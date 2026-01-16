import streamlit as st
import pandas as pd

# 设置页面
st.set_page_config(page_title="工业软管智能选型助手", layout="wide")

# 加载数据
@st.cache_data
def load_data():
    # 自动读取您的 CSV 文件
    try:
        df = pd.read_csv("hose-catalog.xlsx - 橡胶软管.csv")
        return df
    except:
        st.error("找不到数据文件，请确保 CSV 文件已上传并命名正确。")
        return None

df = load_data()

if df is not None:
    st.title("🛠️ 工业软管自主选型系统")
    st.info("请在左侧输入工况参数，系统将自动为您匹配最安全的软管型号。")

    # 侧边栏输入
    st.sidebar.header("📋 工况输入")
    
    # 介质分类建议逻辑
    all_names = df['名称'].unique().tolist()
    selected_name = st.sidebar.multiselect("1. 筛选特定系列 (可选)", all_names)
    
    target_dn = st.sidebar.selectbox("2. 选择通径 (DN)", sorted(df['通径'].unique().tolist()))
    
    req_press = st.sidebar.number_input("3. 工作压力需求 (Bar)", min_value=0, value=10)
    req_temp = st.sidebar.number_input("4. 最高温度需求 (℃)", min_value=-40, value=80)

    # 执行过滤
    mask = (df['通径'] == target_dn) & \
           (df['工作压力（Bar）'] >= req_press) & \
           (df['最高温度（℃）'] >= req_temp)
    
    if selected_name:
        mask = mask & (df['名称'].isin(selected_name))
        
    res = df[mask]

    # 结果展示
    if not res.empty:
        # 自动推荐：弯曲半径最小的
        recommend = res.sort_values(by="弯曲半径（mm）").iloc[0]
        
        st.success(f"✅ 为您找到 {len(res)} 个匹配型号")
        
        # 突出显示推荐项
        c1, c2, c3 = st.columns(3)
        c1.metric("最佳推荐编号", recommend['编号'])
        c2.metric("工作压力", f"{recommend['工作压力（Bar）']} Bar")
        c3.metric("弯曲半径", f"{recommend['弯曲半径（mm）']} mm")
        
        st.write("---")
        st.write("### 📋 匹配清单明细")
        # 格式化表格显示
        st.dataframe(res[['名称', '编号', '通径', '工作压力（Bar）', '最高温度（℃）', '弯曲半径（mm）', '真空压力（Bar）']], use_container_width=True)
    else:
        st.error("❌ 抱歉，当前参数组合下未找到匹配型号。请尝试降低压力/温度要求，或联系技术支持。")

# 页脚
st.sidebar.markdown("---")
st.sidebar.caption("Powered by 智能选型助手 v1.0")