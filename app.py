import streamlit as st
import streamlit.components.v1 as components
import json

# 设置页面配置
st.set_page_config(page_title="3D 智能堆码专家 V8.3", layout="wide", initial_sidebar_state="expanded")

# --- 自定义 CSS 样式 ---
st.markdown("""
<style>
    .main { background-color: #f4f7f6; }
    .stNumberInput, .stSlider { margin-bottom: -10px; }
    .reportview-container .main .block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# --- 侧边栏 UI ---
st.sidebar.title("📦 堆码专家 V8.3")

with st.sidebar.expander("1. 外箱配置", expanded=True):
    size_mode = st.radio("尺寸模式", ["外径模式", "内径模式"], horizontal=True)
    c1, c2, c3 = st.columns(3)
    box_l = c1.number_input("长(L)", value=400)
    box_w = c2.number_input("宽(W)", value=300)
    box_h = c3.number_input("高(H)", value=300)
    
    c4, c5 = st.columns(2)
    wall_thick = c4.number_input("厚度(mm)", value=4)
    bulge_val = c5.number_input("膨胀(mm)", value=0)
    box_opacity = st.sidebar.slider("透明度", 10, 100, 100)

with st.sidebar.expander("2. 内装物配置", expanded=True):
    c6, c7, c8 = st.columns(3)
    item_l = c6.number_input("长", value=180)
    item_w = c7.number_input("宽", value=120)
    item_h = c8.number_input("高", value=100)
    
    item_gap = st.number_input("间隙(mm)", value=0)
    strategy = st.selectbox("算法策略", ["🚀 终极全排列", "📍 长度优先", "📌 宽度优先"])
    align = st.selectbox("对齐方式", ["🎯 居中对齐", "📐 靠角对齐"])

with st.sidebar.expander("3. 显示设置", expanded=False):
    show_edges = st.checkbox("显示线框", value=True)
    show_labels = st.checkbox("显示标注", value=True)
    layer_color = st.checkbox("🌈 分层着色", value=True)
    is_open = st.sidebar.checkbox("开启纸箱", value=False)

# --- 核心 Three.js 渲染引擎 (HTML/JS 注入) ---
# 将 Python 变量传递给 JavaScript
params = {
    "boxL": box_l, "boxW": box_w, "boxH": box_h,
    "wall": wall_thick, "bulge": bulge_val,
    "itemL": item_l, "itemW": item_w, "itemH": item_h,
    "gap": item_gap, "opacity": box_opacity / 100,
    "strategy": "ultra" if "终极" in strategy else ("l_first" if "长度" in strategy else "w_first"),
    "align": "center" if "居中" in align else "edge",
    "showEdges": show_edges, "showLabels": show_labels,
    "layerColor": layer_color, "isOpen": is_open,
    "sizeMode": "outer" if "外径" in size_mode else "inner"
}

# 这里是嵌入的 HTML/Three.js 代码
three_js_html = f"""
<div id="viewport" style="width: 100%; height: 80vh; background: #eef2f3; border-radius: 10px;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

<script>
    const p = {json.dumps(params)};
    let scene, camera, renderer, controls;
    let boxGroup, itemsGroup, labelGroup, flaps = [];
    const layerColors = [0x3498db, 0xe67e22, 0x2ecc71, 0xe74c3c, 0x9b59b6, 0x1abc9c];

    function init() {{
        const container = document.getElementById('viewport');
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0xeef2f3);
        
        camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 1, 10000);
        camera.position.set(600, 600, 600);
        
        renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);
        
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        scene.add(new THREE.AmbientLight(0xffffff, 0.7));
        const dl = new THREE.DirectionalLight(0xffffff, 0.8);
        dl.position.set(200, 500, 300);
        scene.add(dl);

        boxGroup = new THREE.Group();
        itemsGroup = new THREE.Group();
        scene.add(boxGroup, itemsGroup);

        renderLogic();
        animate();
    }}

    function renderLogic() {{
        // 计算逻辑与原 JS 相同
        let vL = p.boxL, vW = p.boxW, vH = p.boxH;
        let rL = vL - p.wall*2, rW = vW - p.wall*2, rH = vH - p.wall*2;
        if(p.sizeMode === 'inner') {{
            rL = p.boxL; rW = p.boxW; rH = p.boxH;
            vL = rL + p.wall*2; vW = rW + p.wall*2; vH = rH + p.wall*2;
        }}

        // 绘制外箱
        const bMat = new THREE.MeshPhongMaterial({{ color: 0xd2a679, transparent: p.opacity < 1, opacity: p.opacity, side: THREE.DoubleSide }});
        const addB = (geo, x, y, z) => {{
            const m = new THREE.Mesh(geo, bMat);
            m.position.set(x, y, z);
            if(p.showEdges) m.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({{color:0}})));
            boxGroup.add(m);
        }};
        
        addB(new THREE.BoxGeometry(vL, p.wall, vW), 0, 0, 0); // 底
        addB(new THREE.BoxGeometry(vL, vH, p.wall), 0, vH/2, -vW/2); // 后
        addB(new THREE.BoxGeometry(p.wall, vH, vW), -vL/2, vH/2, 0); // 左
        addB(new THREE.BoxGeometry(p.wall, vH, vW), vL/2, vH/2, 0);  // 右
        addB(new THREE.BoxGeometry(vL, vH, p.wall), 0, vH/2, vW/2);  // 前

        // 简化的堆码渲染逻辑 (演示用)
        const nX = Math.floor((rL + p.bulge) / (p.itemL + p.gap));
        const nZ = Math.floor((rW + p.bulge) / (p.itemW + p.gap));
        const nY = Math.floor((rH + p.bulge) / p.itemH);
        
        for(let y=0; y<nY; y++) {{
            const col = p.layerColor ? layerColors[y % 6] : 0x3498db;
            const iMat = new THREE.MeshPhongMaterial({{ color: col }});
            for(let x=0; x<nX; x++) {{
                for(let z=0; z<nZ; z++) {{
                    const geo = new THREE.BoxGeometry(p.itemL, p.itemH, p.itemW);
                    const m = new THREE.Mesh(geo, iMat);
                    m.position.set(-rL/2 + x*(p.itemL+p.gap) + p.itemL/2, y*p.itemH + p.itemH/2 + p.wall/2, -rW/2 + z*(p.itemW+p.gap) + p.itemW/2);
                    itemsGroup.add(m);
                }}
            }}
        }}
    }}

    function animate() {{
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }}

    init();
</script>
"""

# 在 Streamlit 中渲染 3D 画布
components.html(three_js_html, height=700)

# --- 统计面板 ---
st.write("---")
st.subheader("📊 装载统计")
col_s1, col_s2, col_s3 = st.columns(3)

# 简单后端计算用于显示
calc_nX = (box_l + bulge_val) // (item_l + item_gap)
calc_nZ = (box_w + bulge_val) // (item_w + item_gap)
calc_nY = (box_h + bulge_val) // item_h
total_pcs = int(calc_nX * calc_nZ * calc_nY)
efficiency = (total_pcs * item_l * item_w * item_h) / (box_l * box_w * box_h) * 100

col_s1.metric("装载总量", f"{total_pcs} pcs")
col_s2.metric("空间利用率", f"{efficiency:.1f}%")
col_s3.progress(min(efficiency / 100, 1.0))
