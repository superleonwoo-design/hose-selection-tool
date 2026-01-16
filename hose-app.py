import streamlit as st
import pandas as pd

# 设置页面
st.set_page_config(page_title="工业软管智能选型助手", layout="wide")

# 加载数据
@st.cache_data
def load_data():
    file_path = "hose-catalog.xlsx - 橡胶软管.csv"
    try:
        # 使用 utf-8-sig 处理编码，并去掉首尾空格
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        # 核心修复：清理列名（去除空格、换行符、不可见字符）
        df.columns = df.columns.str.strip().str.replace('\ufeff', '').str.replace('\n', '')
        return df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return None

df = load_data()

# 调试：如果在页面看到报错，请看这里打印出的实际列名
if df is not None:
    # 如果找不到关键列，打印出来方便排查
    required_columns = ['通径', '工作压力（Bar）', '最高温度（℃）', '名称', '编号']
    missing = [col for col in required_columns if col not in df.columns]
    
    if missing:
        st.error(f"表格中缺少以下列名: {missing}")
        st.write("当前检测到的列名为:", df.columns.tolist())
    else:
        st.title("🛠️ 工业软管智能选型系统")
        st.sidebar.header("📋 工况参数输入")

        # --- 侧边栏交互 ---
        search_keyword = st.sidebar.text_input("1. 输入介质关键词 (如: 食品, 绝缘, 燃油)", "")
        
        all_dn = sorted(df['通径'].unique().tolist())
        target_dn = st.sidebar.selectbox("2. 选择通径 (DN)", all_dn, index=0)
        
        req_press = st.sidebar.slider("3. 额定工作压力需求 (Bar)", 0, 80, 10)
        req_temp = st.sidebar.slider("4. 最高工作温度需求 (℃)", 0, 200, 80)

        # --- 核心筛选逻辑 ---
        mask = (df['通径'] == target_dn) & \
               (df['工作压力（Bar）'] >= req_press) & \
               (df['最高温度（℃）'] >= req_temp)
        
        if search_keyword:
            mask = mask & (df['名称'].str.contains(search_keyword, case=False, na=False))

        res = df[mask]

        # --- 结果展示 ---
        if not res.empty:
            recommend = res.sort_values(by="弯曲半径（mm）").iloc[0]
            st.success(f"✅ 为您匹配到 {len(res)} 款适用型号")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("推荐编号", recommend['编号'])
            c2.metric("最大耐压", f"{recommend['工作压力（Bar）']} Bar")
            c3.metric("最高耐温", f"{recommend['最高温度（℃）']} ℃")
            c4.metric("弯曲半径", f"{recommend['弯曲半径（mm）']} mm")

            st.write("### 📝 所有可选型号明细")
            st.dataframe(res, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ 暂无完全匹配的型号。请调整参数。")

# 侧边栏底部
st.sidebar.markdown("---")
st.sidebar.write("✉️ 技术咨询: 您的联系方式")