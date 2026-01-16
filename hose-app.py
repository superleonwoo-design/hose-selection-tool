import streamlit as st
import pandas as pd

st.set_page_config(page_title="工业软管智能选型助手", layout="wide")

@st.cache_data
def load_data():
    file_path = "hose-catalog.xlsx - 橡胶软管.csv"
    try:
        # 针对分号分隔符进行读取
        df = pd.read_csv(file_path, encoding='utf-8-sig', sep=';')
        df.columns = df.columns.str.strip().str.replace('\ufeff', '').str.replace('\n', '')
        # 统一列名
        df = df.rename(columns={'最高工作温度（℃）': '最高温度（℃）'})
        return df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return None

df = load_data()

if df is not None:
    # 检查核心列是否已识别
    required = ['通径', '工作压力（Bar）', '最高温度（℃）', '名称', '编号']
    missing = [col for col in required if col not in df.columns]
    
    if missing:
        st.error(f"识别失败！仍缺少: {missing}")
        st.write("当前列名:", df.columns.tolist())
    else:
        st.title("🛠️ 工业软管智能选型系统")
        st.sidebar.header("📋 工况参数输入")
        
        search_keyword = st.sidebar.text_input("1. 输入介质关键词", "")
        all_dn = sorted(df['通径'].unique().tolist())
        target_dn = st.sidebar.selectbox("2. 选择通径 (DN)", all_dn, index=0)
        req_press = st.sidebar.slider("3. 工作压力需求 (Bar)", 0, 80, 10)
        req_temp = st.sidebar.slider("4. 最高温度需求 (℃)", 0, 200, 80)

        mask = (df['通径'] == target_dn) & \
               (df['工作压力（Bar）'] >= req_press) & \
               (df['最高温度（℃）'] >= req_temp)
        
        if search_keyword:
            mask = mask & (df['名称'].str.contains(search_keyword, case=False, na=False))

        res = df[mask]

        if not res.empty:
            recommend = res.sort_values(by="弯曲半径（mm）").iloc[0]
            st.success(f"✅ 为您匹配到 {len(res)} 款适用型号")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("推荐编号", recommend['编号'])
            c2.metric("最大耐压", f"{recommend['工作压力（Bar）']} Bar")
            c3.metric("最高耐温", f"{recommend['最高温度（℃）']} ℃")
            c4.metric("弯曲半径", f"{recommend['弯曲半径（mm）']} mm")
            st.dataframe(res, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ 暂无匹配型号，请调整参数。")

st.sidebar.markdown("---")
st.sidebar.write("✉️ 技术咨询: 您的联系方式")
