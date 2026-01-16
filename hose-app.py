import streamlit as st
import pandas as pd

# 设置页面
st.set_page_config(page_title="工业软管智能选型助手", layout="wide")

# 加载数据
@st.cache_data
def load_data():
    # 文件名必须与 GitHub 仓库中的文件名完全一致
    file_path = "hose-catalog.xlsx - 橡胶软管.csv"
    try:
        # 使用 utf-8-sig 处理 Excel CSV 的 BOM 头问题
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        # 去除列名可能存在的空格
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return None

df = load_data()

if df is not None:
    st.title("🛠️ 工业软管智能选型系统")
    st.sidebar.header("📋 工况参数输入")

    # --- 侧边栏交互 ---
    # 1. 介质搜索（通过名称关键词）
    search_keyword = st.sidebar.text_input("1. 输入介质关键词 (如: 食品, 绝缘, 燃油)", "")
    
    # 2. 通径筛选
    all_dn = sorted(df['通径'].unique().tolist())
    target_dn = st.sidebar.selectbox("2. 选择通径 (DN)", all_dn, index=all_dn.index('DN25') if 'DN25' in all_dn else 0)
    
    # 3. 压力和温度
    req_press = st.sidebar.slider("3. 额定工作压力需求 (Bar)", 0, 80, 10)
    req_temp = st.sidebar.slider("4. 最高工作温度需求 (℃)", 0, 200, 80)

    # --- 核心筛选逻辑 ---
    # 注意：这里的列名必须与您 CSV 文件第一行完全一致
    mask = (df['通径'] == target_dn) & \
           (df['工作压力（Bar）'] >= req_press) & \
           (df['最高温度（℃）'] >= req_temp)
    
    if search_keyword:
        mask = mask & (df['名称'].str.contains(search_keyword, case=False, na=False))

    res = df[mask]

    # --- 结果展示 ---
    if not res.empty:
        # 智能推荐：按弯曲半径从小到大排序，取第一个
        recommend = res.sort_values(by="弯曲半径（mm）").iloc[0]
        
        st.success(f"✅ 根据您的工况，为您匹配到 {len(res)} 款适用型号")
        
        # 顶部指标卡
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("推荐编号", recommend['编号'])
        col2.metric("最大耐压", f"{recommend['工作压力（Bar）']} Bar")
        col3.metric("最高耐温", f"{recommend['最高温度（℃）']} ℃")
        col4.metric("弯曲半径", f"{recommend['弯曲半径（mm