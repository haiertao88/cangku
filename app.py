import streamlit as st
import streamlit.components.v1 as components

# 设置页面标题
st.set_page_config(page_title="3D 智能堆码专家 V8.3", layout="wide")

# --- 侧边栏：参数输入 ---
st.sidebar.header("📦 外箱配置")
col1, col2, col3 = st.sidebar.columns(3)
with col1:
    box_l = st.number_input("外箱长 (L)", value=400)
with col2:
    box_w = st.number_input("外箱宽 (W)", value=300)
with col3:
    box_h = st.number_input("外箱高 (H)", value=300)

st.sidebar.header("🍱 内装物配置")
icol1, icol2, icol3 = st.sidebar.columns(3)
with icol1:
    item_l = st.number_input("物料长", value=180)
with icol2:
    item_w = st.number_input("物料宽", value=120)
with icol3:
    item_h = st.number_input("物料高", value=100)

bulge = st.sidebar.slider("膨胀值 (mm)", 0, 20, 0)

# --- 核心算法逻辑 (Python 实现) ---
def calculate_stacking(L, W, H, l, w, h, bulge_val):
    # 简单的堆码计算示例（你可以把之前的 Guillotine 算法写在这里）
    nx = int((L + bulge_val) // l)
    ny = int((W + bulge_val) // w)
    nz = int((H + bulge_val) // h)
    total = nx * ny * nz
    efficiency = (total * l * w * h) / (L * W * H) * 100
    return total, efficiency

total_pcs, eff = calculate_stacking(box_l, box_w, box_h, item_l, item_w, item_h, bulge)

# --- 展示统计数据 ---
st.title("📦 3D 智能堆码专家 V8.3 - Python 版")
m1, m2 = st.columns(2)
m1.metric("装载总量", f"{total_pcs} pcs")
m2.metric("空间利用率", f"{eff:.2f}%")

# --- 3D 渲染部分 ---
# 这里我们直接嵌入你之前的 Three.js 代码，但数据由 Python 传入
three_js_code = f"""
<div id="container" style="width: 100%; height: 600px; background: #f0f2f6;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
    // 这里放入你之前的 Three.js 初始化代码
    // 将 Python 的变量传给 JS
    const boxL = {box_l};
    const boxW = {box_w};
    const boxH = {box_h};
    const itemL = {item_l};
    // ... 渲染逻辑
</script>
"""

# 在页面中渲染 3D 视图
components.html(three_js_code, height=650)