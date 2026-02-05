import streamlit as st
import streamlit.components.v1 as components

# 1. 设置 Streamlit 页面配置
st.set_page_config(
    page_title="3D 智能堆码专家 V9.2 - 稳定修复版",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 注入 CSS 强制 iframe 全屏且不可滚动
st.markdown("""
    <style>
        #MainMenu, header, footer {visibility: hidden;}
        .block-container {
            padding: 0 !important; margin: 0 !important;
            max-width: 100% !important; overflow: hidden !important;
        }
        .main { overflow: hidden !important; }
        iframe {
            position: fixed !important; top: 0 !important; left: 0 !important;
            width: 100vw !important; height: 100vh !important;
            border: none !important; z-index: 99999; display: block;
        }
    </style>
""", unsafe_allow_html=True)

# 3. HTML 代码
html_code = r"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D 智能堆码专家 V9.2</title>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/TransformControls.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    
    <style>
        html, body { margin: 0; padding: 0; width: 100%; height: 100vh; overflow: hidden; }
        body { font-family: "PingFang SC", "Microsoft YaHei", sans-serif; display: flex; background-color: #f4f7f6; }

        /* 左侧设置栏 */
        #sidebar { 
            width: 340px; height: 100%; background: #ffffff; border-right: 1px solid #d1d9e6; 
            padding: 18px; box-sizing: border-box; z-index: 100; display: flex; flex-direction: column; 
            gap: 10px; box-shadow: 4px 0 15px rgba(0,0,0,0.05); overflow-y: auto; flex-shrink: 0;
        }
        #sidebar::-webkit-scrollbar { width: 6px; }
        #sidebar::-webkit-scrollbar-track { background: #f1f1f1; }
        #sidebar::-webkit-scrollbar-thumb { background: #ccc; border-radius: 3px; }

        /* 右侧 3D 视图 */
        #viewport { flex-grow: 1; height: 100%; position: relative; background: #eef2f3; cursor: crosshair; overflow: hidden; }
        
        /* UI 组件 */
        .stats-card { background: #2c3e50; color: #ecf0f1; padding: 12px; border-radius: 8px; flex-shrink: 0; }
        .stats-item { display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px; }
        .efficiency-bar { height: 6px; background: #444; border-radius: 3px; overflow: hidden; }
        .efficiency-fill { height: 100%; background: #2ecc71; width: 0%; transition: 0.5s; }

        .group-title { font-size: 12px; font-weight: 700; color: #34495e; margin-top: 5px; border-left: 4px solid #3498db; padding-left: 8px; }
        .input-row { display: flex; gap: 8px; align-items: center; width: 100%; }
        .input-item { flex: 1; display: flex; flex-direction: column; gap: 2px; }
        .input-item span { font-size: 10px; color: #7f8c8d; }
        
        input[type="number"], select, input[type="text"] { width: 100%; padding: 6px; border: 1px solid #e0e0e0; border-radius: 4px; font-size: 12px; outline: none; background: white; box-sizing: border-box; }
        input[type="range"] { width: 100%; cursor: pointer; height: 4px; background: #dfe6e9; border-radius: 2px; outline: none; }

        .upload-card { background: #f8faff; border: 1px solid #e1e8f0; border-radius: 6px; padding: 10px; display: flex; flex-direction: column; gap: 8px; }
        .upload-field { display: flex; flex-direction: column; gap: 4px; }
        .upload-field label { font-size: 10px; font-weight: bold; color: #4a5568; }

        .mode-toggle { display: flex; background: #eee; border-radius: 6px; padding: 2px; margin-bottom: 5px; }
        .mode-btn { flex: 1; padding: 5px; font-size: 11px; border: none; background: transparent; cursor: pointer; border-radius: 4px; color: #666; transition: 0.3s; }
        .mode-btn.active { background: #fff; color: #3498db; box-shadow: 0 2px 5px rgba(0,0,0,0.1); font-weight: bold; }

        button { flex: 1; padding: 8px; cursor: pointer; border: none; border-radius: 6px; font-weight: bold; font-size: 11px; }
        .btn-update { background: #e74c3c; color: #fff; margin-top: 5px; }
        .btn-toggle { background: #95a5a6; color: #fff; }
        .btn-hide { background: #ecf0f1; color: #7f8c8d; border: 1px solid #d1d9e6; }
        .btn-hide.active { background: #3498db; color: white; border-color: #2980b9; }
        
        .btn-anim { background: #9b59b6; color: white; }
        .btn-export { background: #27ae60; color: white; }
        .preset-row { display: flex; gap: 5px; margin-bottom: 10px; }

        #mini-container { position: absolute; bottom: 20px; right: 20px; display: flex; flex-direction: column; align-items: flex-end; gap: 8px; pointer-events: none; }
        #mini-container > * { pointer-events: auto; }
        #mini-viewport { width: 220px; height: 220px; background: #fff; border: 2px solid #3498db; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); overflow: hidden; }
        .checkbox-item { display: flex; align-items: center; gap: 6px; font-size: 11px; color: #444; cursor: pointer; }
        .bulge-input { background-color: #e8f8f5; border: 1px solid #2ecc71; color: #27ae60; font-weight: bold; }
        
        /* 遮罩层 */
        #loadingOverlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8); color: white; display: none;
            flex-direction: column; justify-content: center; align-items: center; z-index: 200;
        }
        .loader {
            border: 5px solid #f3f3f3; border-top: 5px solid #3498db; border-radius: 50%;
            width: 40px; height: 40px; animation: spin 1s linear infinite; margin-bottom: 15px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

        /* 隐藏的报告模板，用于 HTML2Canvas 截图 */
        #report-hidden-template {
            position: absolute; top: -9999px; left: -9999px;
            width: 794px; /* A4 宽度 approx */
            background: white; padding: 40px; box-sizing: border-box;
            color: #333;
        }
        .rpt-header { text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 20px; margin-bottom: 20px; }
        .rpt-title { font-size: 24px; font-weight: bold; color: #2c3e50; }
        .rpt-date { color: #7f8c8d; font-size: 12px; margin-top: 5px; }
        
        .rpt-stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 30px; background: #f8f9fa; padding: 15px; border-radius: 8px; }
        .rpt-stat-row { display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding: 5px 0; font-size: 14px; }
        
        .rpt-gallery { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
        .rpt-img-box { border: 1px solid #eee; padding: 5px; border-radius: 4px; }
        .rpt-img-box img { width: 100%; height: auto; display: block; }
        .rpt-img-label { text-align: center; font-size: 12px; font-weight: bold; color: #555; margin-top: 5px; background: #eee; padding: 4px; }
        
        .rpt-table { width: 100%; border-collapse: collapse; font-size: 12px; }
        .rpt-table th { background: #3498db; color: white; padding: 8px; text-align: left; }
        .rpt-table td { border-bottom: 1px solid #eee; padding: 6px; }
        .rpt-table tr:nth-child(even) { background: #f9f9f9; }
    </style>
</head>
<body>

<div id="loadingOverlay">
    <div class="loader"></div>
    <div id="loadingText">正在处理...</div>
</div>

<div id="sidebar">
    <h2 style="margin:0; font-size: 18px; color: #2c3e50;">📦 堆码专家 V9.2</h2>
    
    <div class="stats-card">
        <div class="stats-item"><span>装载总量:</span><b id="statCount">0 pcs</b></div>
        <div class="stats-item"><span>空间利用率:</span><b id="statEff">0%</b></div>
        <div class="efficiency-bar"><div id="effFill" class="efficiency-fill"></div></div>
    </div>

    <div class="group-title">💾 方案管理</div>
    <div class="preset-row">
        <select id="presetSelect" onchange="loadPreset()" style="flex:2;">
            <option value="">-- 选择预设 --</option>
        </select>
        <button class="btn-hide active" style="flex:1;" onclick="savePreset()">保存</button>
        <button class="btn-hide" style="flex:0.5; background:#e74c3c; color:white;" onclick="deletePreset()">X</button>
    </div>

    <div class="group-title">图片素材上传</div>
    <div class="upload-card">
        <div class="upload-field"><label>🖼️ 外箱 Logo</label><input type="file" id="logoInput" accept="image/*" onchange="loadLogo(this)"></div>
        <div class="upload-field"><label>🏷️ 产品标签</label><input type="file" id="labelInput" accept="image/*" onchange="loadLabel(this)"></div>
    </div>

    <div class="group-title">1. 外箱配置 (Enter 计算)</div>
    <div class="mode-toggle">
        <button id="mode-outer" class="mode-btn active" onclick="setSizeMode('outer')">外径模式</button>
        <button id="mode-inner" class="mode-btn" onclick="setSizeMode('inner')">内径模式</button>
    </div>
    <div class="input-row">
        <div class="input-item"><span>L</span><input type="number" id="boxL" value="400" class="calc-trigger"></div>
        <div class="input-item"><span>W</span><input type="number" id="boxW" value="300" class="calc-trigger"></div>
        <div class="input-item"><span>H</span><input type="number" id="boxH" value="300" class="calc-trigger"></div>
    </div>
    <div class="input-row">
        <div class="input-item"><span>厚度(mm)</span><input type="number" id="wallThick" value="4" class="calc-trigger"></div>
        <div class="input-item"><span>膨胀(mm)</span><input type="number" id="bulgeVal" value="0" min="0" class="bulge-input calc-trigger"></div>
    </div>
    <div class="input-row">
        <div class="input-item"><span>透明度 <b id="val-op">100</b>%</span><input type="range" id="boxOpacity" min="10" max="100" value="100" oninput="updateOpacity()"></div>
    </div>

    <div class="group-title">2. 内装物 (含间隙)</div>
    <div class="input-row">
        <div class="input-item"><span>长</span><input type="number" id="itemL" value="180" class="calc-trigger"></div>
        <div class="input-item"><span>宽</span><input type="number" id="itemW" value="120" class="calc-trigger"></div>
        <div class="input-item"><span>高</span><input type="number" id="itemH" value="100" class="calc-trigger"></div>
    </div>
    <div class="input-row">
        <div class="input-item" style="flex: 0.5;"><span>间隙</span><input type="number" id="itemGap" value="0" min="0" class="calc-trigger" style="background:#fff3e0;"></div>
        <div class="input-item" style="flex: 1.5;"><span>算法策略</span>
            <select id="stackStrategy" onchange="updateAndRender()">
                <option value="ultra">🚀 终极全排列</option>
                <option value="l_first">📍 长度优先</option>
                <option value="w_first">📌 宽度优先</option>
            </select>
        </div>
    </div>
    <div class="input-row" style="margin-top:5px;">
        <div class="input-item"><span>对齐方式</span>
            <select id="alignStrategy" onchange="updateAndRender()">
                <option value="center">🎯 居中对齐</option>
                <option value="edge">📐 靠角对齐</option>
            </select>
        </div>
    </div>

    <div class="group-title">3. 交互设置</div>
    <div class="btn-row" style="display:flex; gap:5px;">
        <button id="btn-logo-l1" class="btn-hide active" onclick="toggleLogoVisibility(1)">Logo正</button>
        <button id="btn-logo-l2" class="btn-hide active" onclick="toggleLogoVisibility(2)">Logo侧</button>
        <button id="btn-show-l1" class="btn-hide active" onclick="toggleLabelVisibility(1)">标签正</button>
        <button id="btn-show-l2" class="btn-hide active" onclick="toggleLabelVisibility(2)">标签侧</button>
    </div>

    <div class="group-title">4. 显示设置</div>
    <div class="input-row" style="flex-wrap: wrap; gap: 8px;">
        <label class="checkbox-item"><input type="checkbox" id="showEdges" checked onchange="updateAndRender()"> 线框</label>
        <label class="checkbox-item"><input type="checkbox" id="showLabels" checked onchange="updateAndRender()"> 标注</label>
        <label class="checkbox-item"><input type="checkbox" id="hasHandle" checked onchange="updateAndRender()"> 把手</label>
        <label class="checkbox-item"><input type="checkbox" id="layerColor" onchange="updateAndRender()"> 🌈 分层着色</label>
        <label class="checkbox-item"><input type="checkbox" id="showMiniView" checked onchange="toggleMiniViewManual()"> 视窗</label>
    </div>
    
    <button class="btn-update" onclick="updateAndRender()">执行计算 (Enter)</button>
    
    <div class="btn-row" style="display:flex; gap:5px; margin-top:5px;">
        <button class="btn-anim" onclick="playAnimation()">🎬 演示装载</button>
        <button class="btn-export" onclick="exportReportImage()">📄 导出中文报告</button>
    </div>

    <button class="btn-toggle" id="toggleBtn" style="margin-top:5px;">开启/关闭纸箱</button>
    <div style="height: 50px;"></div>
</div>

<div id="viewport">
    <div id="mini-container">
        <button style="width: auto; padding: 4px 10px; background: #fff; border: 1px solid #ccc; font-size: 11px;" onclick="resetMiniView()">🔄 重置</button>
        <div id="mini-viewport"></div>
    </div>
</div>

<div id="report-hidden-template">
    <div class="rpt-header">
        <div class="rpt-title">智能堆码装箱方案报告</div>
        <div class="rpt-date" id="rptDate">2023-01-01</div>
    </div>
    
    <div class="rpt-stats-grid">
        <div class="rpt-stat-row"><b>纸箱尺寸:</b> <span id="rptBoxDim"></span></div>
        <div class="rpt-stat-row"><b>内盒尺寸:</b> <span id="rptItemDim"></span></div>
        <div class="rpt-stat-row"><b>装箱总数:</b> <span id="rptCount"></span></div>
        <div class="rpt-stat-row"><b>体积利用率:</b> <span id="rptEff"></span></div>
        <div class="rpt-stat-row"><b>计算策略:</b> <span id="rptStrat"></span></div>
        <div class="rpt-stat-row"><b>对齐/间隙:</b> <span id="rptAlign"></span></div>
    </div>

    <div class="rpt-gallery">
        <div class="rpt-img-box">
            <img id="img-empty" src="" />
            <div class="rpt-img-label">1. 空箱示意图</div>
        </div>
        <div class="rpt-img-box">
            <img id="img-dim" src="" />
            <div class="rpt-img-label">2. 尺寸标注图</div>
        </div>
        <div class="rpt-img-box">
            <img id="img-full" src="" />
            <div class="rpt-img-label">3. 满装俯视图</div>
        </div>
        <div class="rpt-img-box">
            <img id="img-persp" src="" />
            <div class="rpt-img-label">4. 满装透视图</div>
        </div>
    </div>

    <h3>📦 装箱明细 (前200件)</h3>
    <table class="rpt-table" id="rptTable">
        <thead>
            <tr><th>序号</th><th>X (mm)</th><th>Y (mm)</th><th>Z (mm)</th><th>规格</th></tr>
        </thead>
        <tbody></tbody>
    </table>
</div>

<script>
    let scene, camera, renderer, controls, tfControls, raycaster, mouse;
    let targetGroup, boxGroup, itemsGroup, labelGroup;
    let miniScene, miniCamera, miniRenderer, miniItemContainer, miniControls;
    let isOpen = false, labelTexture = null, logoTexture = null;
    let showL1 = true, showL2 = true, showLogo1 = true, showLogo2 = true;
    let sizeMode = 'outer', flaps = [];
    const edgeMat = new THREE.LineBasicMaterial({ color: 0x000000 });
    const layerColors = [0x3498db, 0xe67e22, 0x2ecc71, 0xe74c3c, 0x9b59b6, 0x1abc9c];

    // 动画控制
    let isAnimating = false;
    let animQueue = [];
    let animIndex = 0;
    let animFrameCounter = 0;

    // --- 预设管理 ---
    function initPresets() { refreshPresetList(); }
    function refreshPresetList() {
        const sel = document.getElementById('presetSelect');
        const presets = JSON.parse(localStorage.getItem('stacking_presets') || '{}');
        sel.innerHTML = '<option value="">-- 选择预设 --</option>';
        for(let name in presets) {
            let opt = document.createElement('option'); opt.value = name; opt.innerText = name; sel.appendChild(opt);
        }
    }
    function savePreset() {
        const name = prompt("请输入方案名称:"); if(!name) return;
        const data = {
            boxL: document.getElementById('boxL').value, boxW: document.getElementById('boxW').value, boxH: document.getElementById('boxH').value,
            wall: document.getElementById('wallThick').value, itemL: document.getElementById('itemL').value, itemW: document.getElementById('itemW').value, itemH: document.getElementById('itemH').value,
            mode: sizeMode
        };
        const presets = JSON.parse(localStorage.getItem('stacking_presets') || '{}'); presets[name] = data;
        localStorage.setItem('stacking_presets', JSON.stringify(presets)); refreshPresetList(); alert("已保存");
    }
    function loadPreset() {
        const name = document.getElementById('presetSelect').value; if(!name) return;
        const presets = JSON.parse(localStorage.getItem('stacking_presets') || '{}'); const data = presets[name];
        if(data) {
            document.getElementById('boxL').value = data.boxL; document.getElementById('boxW').value = data.boxW; document.getElementById('boxH').value = data.boxH;
            document.getElementById('wallThick').value = data.wall; document.getElementById('itemL').value = data.itemL; document.getElementById('itemW').value = data.itemW; document.getElementById('itemH').value = data.itemH;
            setSizeMode(data.mode || 'outer'); updateAndRender();
        }
    }
    function deletePreset() {
        const name = document.getElementById('presetSelect').value; if(!name) return;
        if(confirm("删除 " + name + "?")) {
            const presets = JSON.parse(localStorage.getItem('stacking_presets') || '{}'); delete presets[name];
            localStorage.setItem('stacking_presets', JSON.stringify(presets)); refreshPresetList();
        }
    }

    // --- 高级截图函数 ---
    function captureView(opts) {
        const oldItems = itemsGroup.visible;
        const oldLabels = labelGroup.visible;
        const oldPos = camera.position.clone();
        const oldRot = camera.rotation.clone();

        if(opts.showItems !== undefined) itemsGroup.visible = opts.showItems;
        if(opts.showLabels !== undefined) labelGroup.visible = opts.showLabels;
        
        // 自动调整视角
        if(opts.view === 'top') {
            camera.position.set(0, 1000, 0); camera.lookAt(0,0,0);
        } else if (opts.view === 'persp') {
            camera.position.set(600, 600, 600); camera.lookAt(0,0,0);
        }

        renderer.render(scene, camera);
        const data = renderer.domElement.toDataURL('image/jpeg', 0.9);
        
        // 恢复
        itemsGroup.visible = oldItems;
        labelGroup.visible = oldLabels;
        camera.position.copy(oldPos);
        camera.rotation.copy(oldRot);
        return data;
    }

    // --- 导出 PDF (Canvas 截图方案) ---
    async function exportReportImage() {
        document.getElementById('loadingOverlay').style.display = 'flex';
        document.getElementById('loadingText').innerText = "正在生成快照...";

        // 1. 填充文本数据
        document.getElementById('rptDate').innerText = new Date().toLocaleString();
        document.getElementById('rptBoxDim').innerText = `${document.getElementById('boxL').value} x ${document.getElementById('boxW').value} x ${document.getElementById('boxH').value} mm`;
        document.getElementById('rptItemDim').innerText = `${document.getElementById('itemL').value} x ${document.getElementById('itemW').value} x ${document.getElementById('itemH').value} mm`;
        document.getElementById('rptCount').innerText = document.getElementById('statCount').innerText;
        document.getElementById('rptEff').innerText = document.getElementById('statEff').innerText;
        document.getElementById('rptStrat').innerText = document.getElementById('stackStrategy').options[document.getElementById('stackStrategy').selectedIndex].text;
        document.getElementById('rptAlign').innerText = document.getElementById('alignStrategy').value + " / " + document.getElementById('itemGap').value + "mm";

        // 2. 填充表格 (前200行)
        const tbody = document.querySelector('#rptTable tbody');
        tbody.innerHTML = "";
        let idx = 1;
        itemsGroup.children.forEach(mesh => {
            if(idx > 200) return;
            if(mesh.geometry) {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td>${idx++}</td><td>${Math.round(mesh.position.x)}</td><td>${Math.round(mesh.position.y)}</td><td>${Math.round(mesh.position.z)}</td><td>${Math.round(mesh.geometry.parameters.width)}x${Math.round(mesh.geometry.parameters.height)}x${Math.round(mesh.geometry.parameters.depth)}</td>`;
                tbody.appendChild(tr);
            }
        });

        // 3. 生成 4 张 3D 截图
        // 稍微延迟让 UI 渲染
        setTimeout(async () => {
            try {
                // A. 空箱图
                document.getElementById('img-empty').src = captureView({ showItems: false, showLabels: false, view: 'persp' });
                // B. 尺寸图
                document.getElementById('img-dim').src = captureView({ showItems: false, showLabels: true, view: 'persp' });
                // C. 满装俯视图
                document.getElementById('img-full').src = captureView({ showItems: true, showLabels: false, view: 'top' });
                // D. 满装透视图
                document.getElementById('img-persp').src = captureView({ showItems: true, showLabels: false, view: 'persp' });

                document.getElementById('loadingText').innerText = "正在渲染 PDF...";
                
                // 4. 将 HTML 模板转为 Canvas
                const element = document.getElementById('report-hidden-template');
                // 必须临时移动到可见区域截图，截完再移回去 (或者使用 cloning)
                // 这里我们使用 window.scrollTo 技巧或 html2canvas 的 clone 特性
                // 简单起见，利用 absolute 定位
                
                const canvas = await html2canvas(element, { scale: 2, useCORS: true });
                
                // 5. 生成 PDF
                const { jsPDF } = window.jspdf;
                const pdf = new jsPDF('p', 'mm', 'a4');
                const imgData = canvas.toDataURL('image/jpeg', 0.95);
                
                const pdfWidth = 210;
                const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
                
                pdf.addImage(imgData, 'JPEG', 0, 0, pdfWidth, pdfHeight);
                pdf.save('堆码方案报告.pdf');

            } catch (err) {
                alert("生成失败: " + err.message);
                console.error(err);
            } finally {
                document.getElementById('loadingOverlay').style.display = 'none';
            }
        }, 200);
    }

    // --- 动画逻辑修复版 ---
    function playAnimation() {
        if(!itemsGroup.children.length) return;
        
        // 1. 初始化队列
        animQueue = [];
        // 排序：Y轴(层) -> Z轴(里外) -> X轴(左右)
        const children = itemsGroup.children.slice().sort((a,b) => {
            if(Math.abs(a.position.y - b.position.y) > 1) return a.position.y - b.position.y;
            if(Math.abs(a.position.z - b.position.z) > 1) return a.position.z - b.position.z;
            return a.position.x - b.position.x;
        });
        
        children.forEach(c => {
            c.visible = false;
            c.userData.finalY = c.position.y; // 记录最终落地高度
            c.position.y += 250; // 抬高到空中
            c.userData.isSettled = false; // 标记是否落地
            animQueue.push(c);
        });

        isAnimating = true;
        animIndex = 0;
        animFrameCounter = 0;
        document.getElementById('toggleBtn').innerText = "关闭纸箱";
        isOpen = true; // 强制开箱
    }

    // --- Three.js 基础逻辑 ---
    function setSizeMode(m) {
        sizeMode = m;
        document.getElementById('mode-outer').classList.toggle('active', m === 'outer');
        document.getElementById('mode-inner').classList.toggle('active', m === 'inner');
        updateAndRender();
    }
    function toggleLabelVisibility(idx) {
        if(idx === 1) showL1 = !showL1; else showL2 = !showL2;
        document.getElementById('btn-show-l' + idx).classList.toggle('active', idx === 1 ? showL1 : showL2);
        updateAndRender();
    }
    function toggleLogoVisibility(idx) {
        if(idx === 1) showLogo1 = !showLogo1; else showLogo2 = !showLogo2;
        document.getElementById('btn-logo-l' + idx).classList.toggle('active', idx === 1 ? showLogo1 : showLogo2);
        updateAndRender();
    }
    function toggleMiniViewManual() { document.getElementById('mini-container').style.display = document.getElementById('showMiniView').checked ? 'flex' : 'none'; }
    function resetMiniView() { if(miniControls) miniControls.reset(); }
    function updateOpacity() {
        const val = parseInt(document.getElementById('boxOpacity').value);
        document.getElementById('val-op').innerText = val;
        const op = val / 100;
        boxGroup.traverse(c => { if(c.isMesh && !c.userData.isInteractable) { c.material.opacity = op; c.material.transparent = op < 1.0; c.material.needsUpdate = true; } });
    }
    function loadLabel(i) { if(i.files[0]) { let r=new FileReader(); r.onload=e=>{let m=new Image(); m.onload=()=>{labelTexture=new THREE.Texture(m); labelTexture.needsUpdate=true; updateAndRender();}; m.src=e.target.result;}; r.readAsDataURL(i.files[0]); } }
    function loadLogo(i) { if(i.files[0]) { let r=new FileReader(); r.onload=e=>{let m=new Image(); m.onload=()=>{logoTexture=new THREE.Texture(m); logoTexture.needsUpdate=true; updateAndRender();}; m.src=e.target.result;}; r.readAsDataURL(i.files[0]); } }
    function getHandleTexture() {
        const c = document.createElement('canvas'); c.width=256; c.height=256; const x=c.getContext('2d');
        x.fillStyle='#d2a679'; x.fillRect(0,0,256,256); x.fillStyle='#3e2723'; x.beginPath(); x.roundRect(68,108,120,40,20); x.fill();
        return new THREE.CanvasTexture(c);
    }
    function createDimLabel(txt, p1, p2, offD, dist, col='#ff3333') {
        const g=new THREE.Group(); const mat=new THREE.LineBasicMaterial({color:col});
        const d1=p1.clone().add(offD.clone().multiplyScalar(dist)); const d2=p2.clone().add(offD.clone().multiplyScalar(dist));
        g.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([d1,d2]),mat));
        g.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([p1,d1]),mat)); g.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([p2,d2]),mat));
        const c=document.createElement('canvas'); c.width=1024; c.height=256; const x=c.getContext('2d');
        x.fillStyle=col; x.font='bold 140px Arial'; x.textAlign='center'; x.fillText(txt, 512, 170);
        const tex = new THREE.CanvasTexture(c); tex.anisotropy = 16;
        const s=new THREE.Sprite(new THREE.SpriteMaterial({map:tex})); s.scale.set(70,18,1);
        s.position.copy(d1.clone().lerp(d2,0.5)).add(offD.clone().multiplyScalar(15)); g.add(s); return g;
    }

    // 核心算法
    const memo = {};
    function solveGuillotine(rectL, rectW, l, w) {
        const key = Math.round(rectL * 1000) + "x" + Math.round(rectW * 1000);
        if (memo[key] !== undefined) return memo[key];
        if (rectL < Math.min(l, w) - 0.001 || rectW < Math.min(l, w) - 0.001) return { n: 0, items: [] };
        let bestSol = { n: 0, items: [] };
        let n_lw = Math.floor(rectL / l) * Math.floor(rectW / w);
        if (n_lw > bestSol.n) { let its = []; for(let i=0;i<Math.floor(rectL/l);i++) for(let j=0;j<Math.floor(rectW/w);j++) its.push({x:i*l, z:j*w, w:l, d:w}); bestSol = {n: n_lw, items: its}; }
        let n_wl = Math.floor(rectL / w) * Math.floor(rectW / l);
        if (n_wl > bestSol.n) { let its = []; for(let i=0;i<Math.floor(rectL/w);i++) for(let j=0;j<Math.floor(rectW/l);j++) its.push({x:i*w, z:j*l, w:w, d:l}); bestSol = {n: n_wl, items: its}; }
        if (rectL >= l && rectW >= w) {
            let maxCols = Math.floor(rectL / l);
            for (let i = 1; i <= maxCols; i++) {
                let colWidth = i * l; let itemsPerCol = Math.floor(rectW / w); let currentN = i * itemsPerCol; let currentItems = [];
                for (let c = 0; c < i; c++) for (let r = 0; r < itemsPerCol; r++) currentItems.push({ x: c * l, z: r * w, w: l, d: w });
                let resRight = solveGuillotine(rectL - colWidth, rectW, l, w);
                if (currentN + resRight.n > bestSol.n) { let shiftedRight = resRight.items.map(it => ({ ...it, x: it.x + colWidth })); bestSol = { n: currentN + resRight.n, items: [...currentItems, ...shiftedRight] }; }
            }
        }
        if (rectL >= w && rectW >= l) {
            let maxCols = Math.floor(rectL / w);
            for (let i = 1; i <= maxCols; i++) {
                let colWidth = i * w; let itemsPerCol = Math.floor(rectW / l); let currentN = i * itemsPerCol; let currentItems = [];
                for (let c = 0; c < i; c++) for (let r = 0; r < itemsPerCol; r++) currentItems.push({ x: c * w, z: r * l, w: w, d: l });
                let resRight = solveGuillotine(rectL - colWidth, rectW, l, w);
                if (currentN + resRight.n > bestSol.n) { let shiftedRight = resRight.items.map(it => ({ ...it, x: it.x + colWidth })); bestSol = { n: currentN + resRight.n, items: [...currentItems, ...shiftedRight] }; }
            }
        }
        if (rectW >= w && rectL >= l) {
            let maxRows = Math.floor(rectW / w);
            for (let j = 1; j <= maxRows; j++) {
                let rowHeight = j * w; let itemsPerRow = Math.floor(rectL / l); let currentN = j * itemsPerRow; let currentItems = [];
                for (let r = 0; r < j; r++) for (let c = 0; c < itemsPerRow; c++) currentItems.push({ x: c * l, z: r * w, w: l, d: w });
                let resBottom = solveGuillotine(rectL, rectW - rowHeight, l, w);
                if (currentN + resBottom.n > bestSol.n) { let shiftedBottom = resBottom.items.map(it => ({ ...it, z: it.z + rowHeight })); bestSol = { n: currentN + resBottom.n, items: [...currentItems, ...shiftedBottom] }; }
            }
        }
        if (rectW >= l && rectL >= w) {
            let maxRows = Math.floor(rectW / l);
            for (let j = 1; j <= maxRows; j++) {
                let rowHeight = j * l; let itemsPerRow = Math.floor(rectL / w); let currentN = j * itemsPerRow; let currentItems = [];
                for (let r = 0; r < j; r++) for (let c = 0; c < itemsPerRow; c++) currentItems.push({ x: c * w, z: r * l, w: w, d: l });
                let resBottom = solveGuillotine(rectL, rectW - rowHeight, l, w);
                if (currentN + resBottom.n > bestSol.n) { let shiftedBottom = resBottom.items.map(it => ({ ...it, z: it.z + rowHeight })); bestSol = { n: currentN + resBottom.n, items: [...currentItems, ...shiftedBottom] }; }
            }
        }
        memo[key] = bestSol; return bestSol;
    }
    function solveUltra(L, W, l, w) { for (var member in memo) delete memo[member]; return solveGuillotine(L, W, l, w); }

    function updateAndRender() {
        isAnimating = false; // 停止旧动画
        const inputL=parseFloat(document.getElementById('boxL').value), inputW=parseFloat(document.getElementById('boxW').value), inputH=parseFloat(document.getElementById('boxH').value);
        const wall=parseFloat(document.getElementById('wallThick').value);
        const gap=parseFloat(document.getElementById('itemGap').value) || 0;
        const bulgeVal = parseFloat(document.getElementById('bulgeVal').value) || 0;
        const showE=document.getElementById('showEdges').checked, showH=document.getElementById('hasHandle').checked;
        const useLayerColor = document.getElementById('layerColor').checked;
        const strat=document.getElementById('stackStrategy').value, align=document.getElementById('alignStrategy').value;

        let vL, vW, vH, rL, rW, rH;
        if(sizeMode === 'outer') { vL = inputL; vW = inputW; vH = inputH; rL = vL - wall*2; rW = vW - wall*2; rH = vH - wall*2; }
        else { rL = inputL; rW = inputW; rH = inputH; vL = rL + wall*2; vW = rW + wall*2; vH = rH + wall*2; }
        const effectiveRL = rL + bulgeVal; const effectiveRW = rW + bulgeVal; const effectiveRH = rH + bulgeVal;

        boxGroup.clear(); itemsGroup.clear(); labelGroup.clear(); flaps=[];
        const bMat=new THREE.MeshPhongMaterial({color:0xd2a679,side:THREE.DoubleSide}); 
        const hMat=new THREE.MeshPhongMaterial({map:getHandleTexture(),side:THREE.DoubleSide});

        const addB=(geo,x,y,z,h=false)=>{ const m=new THREE.Mesh(geo,h&&showH?hMat:bMat); m.position.set(x,y,z); if(showE) m.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo),edgeMat)); boxGroup.add(m); return m; };
        addB(new THREE.BoxGeometry(vL,wall,vW),0,0,0); addB(new THREE.BoxGeometry(vL,vH,wall),0,vH/2,-vW/2); 
        const sideL = addB(new THREE.BoxGeometry(wall,vH,vW),-vL/2,vH/2,0,true); const sideR = addB(new THREE.BoxGeometry(wall,vH,vW),vL/2,vH/2,0,true);
        const front = addB(new THREE.BoxGeometry(vL,vH,wall),0,vH/2,vW/2);

        const lpMat = new THREE.MeshPhongMaterial({color:labelTexture?0xffffff:0xccaa88,map:labelTexture,transparent:true});
        const loMat = new THREE.MeshPhongMaterial({color:logoTexture?0xffffff:0xff0000,map:logoTexture,transparent:true});
        const addPI = (parent, geo, mat, face) => { const m = new THREE.Mesh(geo, mat); m.userData.isInteractable = true; m.userData.face = face; parent.add(m); return m; };
        if(showL1) addPI(front, new THREE.BoxGeometry(100,80,1), lpMat, 'front').position.set(80, 0, wall/2+0.5);
        if(showLogo1) addPI(front, new THREE.BoxGeometry(60,60,1), loMat, 'front').position.set(-100, 100, wall/2+0.5);
        if(showL2) addPI(sideR, new THREE.BoxGeometry(1,80,100), lpMat, 'side').position.set(wall/2+0.5, 0, 0);
        if(showLogo2) addPI(sideR, new THREE.BoxGeometry(1,60,60), loMat, 'side').position.set(wall/2+0.5, 100, 0);

        const addF=(fw,fd,px,pz,axis,dir,type)=>{
            const p=new THREE.Group(); p.position.set(px,vH+(type==='long'?0.4:0),pz);
            const m=new THREE.Mesh(new THREE.BoxGeometry(fw,wall/2,fd),bMat); m.position.z=axis==='x'?fd/2*-dir:0; m.position.x=axis==='z'?fw/2*-dir:0;
            if(showE) m.add(new THREE.LineSegments(new THREE.EdgesGeometry(m.geometry),edgeMat)); p.add(m); boxGroup.add(p); flaps.push({pivot:p,axis,dir,currentAng:0,type});
        };
        addF(vL,vW/2,0,vW/2,'x',1,'long'); addF(vL,vW/2,0,-vW/2,'x',-1,'long'); addF(vL/2,vW,vL/2,0,'z',1,'short'); addF(vL/2,vW,-vL/2,0,'z',-1,'short');

        const iL=parseFloat(document.getElementById('itemL').value), iW=parseFloat(document.getElementById('itemW').value), iH=parseFloat(document.getElementById('itemH').value);
        const calcRL = effectiveRL + gap; const calcRW = effectiveRW + gap; const effL = iL + gap; const effW = iW + gap;

        let layerResult;
        if (strat === 'ultra') layerResult = solveUltra(calcRL, calcRW, effL, effW); 
        else if (strat === 'l_first') {
            let nx = Math.floor(calcRL/effL), nz = Math.floor(calcRW/effW), items=[];
            for(let x=0; x<nx; x++) for(let z=0; z<nz; z++) items.push({x: x*effL, z: z*effW, w: effL, d: effW});
            layerResult = { n: items.length, items: items };
        } else {
            let nx = Math.floor(calcRL/effW), nz = Math.floor(calcRW/effL), items=[];
            for(let x=0; x<nx; x++) for(let z=0; z<nz; z++) items.push({x: x*effW, z: z*effL, w: effW, d: effL});
            layerResult = { n: items.length, items: items };
        }

        const nY = Math.floor(effectiveRH / iH);
        const total = layerResult.n * nY;
        document.getElementById('statCount').innerText=total+" pcs";
        document.getElementById('statEff').innerText=(total*iL*iW*iH/(vL*vW*vH)*100).toFixed(1)+"%";
        document.getElementById('effFill').style.width=Math.min(100, parseFloat(document.getElementById('statEff').innerText)) + "%";

        let bBoxL = 0, bBoxW = 0; layerResult.items.forEach(it => { bBoxL = Math.max(bBoxL, it.x + it.w); bBoxW = Math.max(bBoxW, it.z + it.d); });
        let offX = (align === 'center') ? (effectiveRL - bBoxL)/2 : 0; let offZ = (align === 'center') ? (effectiveRW - bBoxW)/2 : 0;
        const startX = -rL/2 + offX; const startZ = -rW/2 + offZ;

        for(let y=0; y<nY; y++) {
            const currentColor = useLayerColor ? layerColors[y % layerColors.length] : 0x3498db;
            const iMat = new THREE.MeshPhongMaterial({ color: currentColor });
            layerResult.items.forEach(it => {
                const realW = it.w - gap; const realD = it.d - gap;
                const geo = new THREE.BoxGeometry(realW, iH, realD); const m = new THREE.Mesh(geo, iMat);
                m.position.set(startX + it.x + realW/2, y*iH + iH/2 + wall/2, startZ + it.z + realD/2);
                if(showE) m.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo),edgeMat)); 
                itemsGroup.add(m);
            });
        }
        if(document.getElementById('showLabels').checked){
            labelGroup.add(createDimLabel(vL.toString(),new THREE.Vector3(-vL/2,0,vW/2),new THREE.Vector3(vL/2,0,vW/2),new THREE.Vector3(0,0,1),50));
            labelGroup.add(createDimLabel(vH.toString(),new THREE.Vector3(-vL/2,0,vW/2),new THREE.Vector3(-vL/2,vH,vW/2),new THREE.Vector3(-1,0,0),50));
            labelGroup.add(createDimLabel(vW.toString(),new THREE.Vector3(vL/2,0,-vW/2),new THREE.Vector3(vL/2,0,vW/2),new THREE.Vector3(1,0,0),50));
        }
        updateOpacity(); updateMiniView(iL, iW, iH);
    }

    function updateMiniView(l, w, h) {
        if(!miniItemContainer) return; miniItemContainer.clear();
        const mat = new THREE.MeshPhongMaterial({color: 0x3498db}); const geo = new THREE.BoxGeometry(l, h, w); const m = new THREE.Mesh(geo, mat); m.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo), edgeMat)); miniItemContainer.add(m);
        miniItemContainer.add(createDimLabel(l.toString(), new THREE.Vector3(-l/2,-h/2,w/2), new THREE.Vector3(l/2,-h/2,w/2), new THREE.Vector3(0,-1,0), 20, '#e67e22'));
        miniItemContainer.add(createDimLabel(w.toString(), new THREE.Vector3(l/2,-h/2,w/2), new THREE.Vector3(l/2,-h/2,-w/2), new THREE.Vector3(1,0,0), 20, '#e67e22'));
    }

    function init(){
        initPresets();
        const v=document.getElementById('viewport'); scene=new THREE.Scene(); scene.background=new THREE.Color(0xeef2f3);
        camera=new THREE.PerspectiveCamera(45,v.clientWidth/v.clientHeight,1,10000); camera.position.set(600,600,600);
        renderer=new THREE.WebGLRenderer({antialias:true, preserveDrawingBuffer: true}); renderer.setSize(v.clientWidth,v.clientHeight); v.appendChild(renderer.domElement);
        controls = new THREE.OrbitControls(camera, renderer.domElement); controls.enableDamping = true;
        controls.mouseButtons = { LEFT: THREE.MOUSE.ROTATE, MIDDLE: THREE.MOUSE.PAN, RIGHT: THREE.MOUSE.DOLLY };
        tfControls = new THREE.TransformControls(camera, renderer.domElement);
        tfControls.addEventListener('dragging-changed', (e) => { controls.enabled = !e.value; }); scene.add(tfControls);
        tfControls.addEventListener('objectChange', () => {
            const obj = tfControls.object; if(!obj) return; const wall = parseFloat(document.getElementById('wallThick').value);
            if(obj.userData.face === 'front') { obj.position.z = wall/2 + 0.5; obj.scale.z = 1; } else if(obj.userData.face === 'side') { obj.position.x = wall/2 + 0.5; obj.scale.x = 1; }
        });
        raycaster = new THREE.Raycaster(); mouse = new THREE.Vector2();
        renderer.domElement.addEventListener('pointerdown', (e) => {
            if (e.button !== 0) return;
            const rect = renderer.domElement.getBoundingClientRect();
            mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1; mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(targetGroup.children, true);
            const target = intersects.find(i => i.object.userData.isInteractable);
            if(target) { tfControls.attach(target.object); if(target.object.userData.face === 'front') { tfControls.showZ = false; tfControls.showX = true; tfControls.showY = true; } else { tfControls.showX = false; tfControls.showZ = true; tfControls.showY = true; } } else if(!tfControls.dragging) tfControls.detach();
        });
        window.addEventListener('keydown', (e) => { const k = e.key.toLowerCase(); if(k === 'w') tfControls.setMode('translate'); if(k === 'e') tfControls.setMode('scale'); });
        document.querySelectorAll('.calc-trigger').forEach(input => { input.addEventListener('keydown', (e) => { if (e.key === 'Enter') { input.blur(); updateAndRender(); } }); });
        scene.add(new THREE.AmbientLight(0xffffff, 0.7)); const dl=new THREE.DirectionalLight(0xffffff, 0.8); dl.position.set(200, 500, 300); scene.add(dl);
        targetGroup=new THREE.Group(); boxGroup=new THREE.Group(); itemsGroup=new THREE.Group(); labelGroup=new THREE.Group(); targetGroup.add(boxGroup,itemsGroup,labelGroup); scene.add(targetGroup); initMini();
        document.getElementById('toggleBtn').onclick=()=>{isOpen=!isOpen; document.getElementById('toggleBtn').innerText=isOpen?"关闭纸箱":"开启纸箱";};
        window.addEventListener('resize',()=>{ camera.aspect=v.clientWidth/v.clientHeight; camera.updateProjectionMatrix(); renderer.setSize(v.clientWidth,v.clientHeight); });
        
        updateAndRender(); animate();
    }
    function initMini(){
        const mv=document.getElementById('mini-viewport'); miniScene=new THREE.Scene(); miniScene.background=new THREE.Color(0xffffff);
        miniCamera=new THREE.PerspectiveCamera(45,1,1,2000); miniCamera.position.set(240,180,240);
        miniRenderer=new THREE.WebGLRenderer({antialias:true}); miniRenderer.setSize(220,220); mv.appendChild(miniRenderer.domElement);
        miniControls = new THREE.OrbitControls(miniCamera, miniRenderer.domElement); miniScene.add(new THREE.AmbientLight(0xffffff,0.9)); miniItemContainer=new THREE.Group(); miniScene.add(miniItemContainer);
    }

    function animate(){
        requestAnimationFrame(animate); 
        const tA=isOpen?Math.PI*0.8:0; 
        const lF=flaps.filter(f=>f.type==='long'), sF=flaps.filter(f=>f.type==='short');
        flaps.forEach(f=>{
            let m=false; if(isOpen){ if(f.type==='long') m=true; else if(f.type==='short'&&lF[0].currentAng>0.4) m=true; } else{ if(f.type==='short') m=true; else if(f.type==='long'&&sF[0].currentAng<0.2) m=true; }
            if(m) f.currentAng+=(tA-f.currentAng)*0.1;
            if(f.axis==='x')f.pivot.rotation.x=f.currentAng*f.dir; else f.pivot.rotation.z=-f.currentAng*f.dir;
        });

        // --- 核心修复：动画逻辑分离 ---
        // 1. 队列投放逻辑
        if(isAnimating && animQueue.length > 0) {
            if(animIndex < animQueue.length) {
                animFrameCounter++;
                if(animFrameCounter > 3) { // 投放速度
                    animFrameCounter = 0;
                    animQueue[animIndex].visible = true;
                    animIndex++;
                }
            }
        }

        // 2. 物理下落逻辑 (独立运行)
        // 只要有任何一个物体还没有“落地”，我们就继续执行下落逻辑，防止悬空
        let activeFalling = false;
        if(isAnimating || animIndex > 0) {
            // 遍历所有已经投放（可见）的物体
            for(let i=0; i<animIndex; i++) {
                const item = animQueue[i];
                if(item.userData.isSettled) continue; // 已经落地的跳过

                // 如果还没落地
                if(item.position.y > item.userData.finalY + 0.5) {
                    item.position.y += (item.userData.finalY - item.position.y) * 0.15; // 缓动下落
                    activeFalling = true; // 只要有一个在动，动画就没结束
                } else {
                    item.position.y = item.userData.finalY; // 强制归位
                    item.userData.isSettled = true;
                }
            }
        }

        // 只有当所有物体都投放完毕 AND 所有物体都落地了，才真正停止动画状态
        if(animIndex === animQueue.length && !activeFalling) {
            isAnimating = false;
        }

        controls.update(); if (miniControls) miniControls.update();
        renderer.render(scene,camera); miniRenderer.render(miniScene,miniCamera);
    }
    init();
</script>
</body>
</html>
"""

components.html(html_code, height=1200, scrolling=False)

