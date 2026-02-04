import streamlit as st
import streamlit.components.v1 as components

# 1. 设置 Streamlit 页面配置
st.set_page_config(
    page_title="3D 智能堆码专家 V8.3 - Python版",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 核心修复：注入 CSS 强制 iframe 全屏且不可滚动
st.markdown("""
    <style>
        /* 隐藏 Streamlit 所有原生 UI */
        #MainMenu, header, footer {visibility: hidden;}
        
        /* 移除 Streamlit 容器的所有内边距和滚动条 */
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
            overflow: hidden !important;
        }
        
        /* 禁止 Streamlit 主页面滚动 */
        .main {
            overflow: hidden !important;
        }

        /* 关键修复：强制 iframe 占满屏幕，脱离文档流 */
        iframe {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            border: none !important;
            z-index: 99999; /* 确保在最上层 */
            display: block;
        }
    </style>
""", unsafe_allow_html=True)

# 3. HTML 代码 (包含内部滚动逻辑)
html_code = r"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D 智能堆码专家 V8.3</title>
    <style>
        /* 全局重置：禁止 body 滚动 */
        html, body { 
            margin: 0; 
            padding: 0; 
            width: 100%; 
            height: 100vh; /* 强制视口高度 */
            overflow: hidden; /* 关键：防止整个页面出现滚动条 */
        }
        
        body { 
            font-family: "PingFang SC", "Segoe UI", sans-serif; 
            display: flex; 
            background-color: #f4f7f6; 
        }

        /* 侧边栏：允许独立滚动 */
        #sidebar { 
            width: 340px; 
            height: 100%; /* 继承 body 的 100vh */
            background: #ffffff; 
            border-right: 1px solid #d1d9e6; 
            padding: 18px; 
            box-sizing: border-box; 
            z-index: 100; 
            display: flex; 
            flex-direction: column; 
            gap: 10px; 
            box-shadow: 4px 0 15px rgba(0,0,0,0.05); 
            
            /* 关键：侧边栏独立滚动条 */
            overflow-y: auto; 
            flex-shrink: 0;
        }

        /* 视图区：禁止滚动 */
        #viewport { 
            flex-grow: 1; 
            height: 100%; /* 继承 body 的 100vh */
            position: relative; 
            background: #eef2f3; 
            cursor: crosshair; 
            
            /* 关键：防止视图区溢出导致滚动 */
            overflow: hidden; 
        }
        
        /* 美化滚动条 (Webkit) */
        #sidebar::-webkit-scrollbar { width: 6px; }
        #sidebar::-webkit-scrollbar-track { background: #f1f1f1; }
        #sidebar::-webkit-scrollbar-thumb { background: #ccc; border-radius: 3px; }
        #sidebar::-webkit-scrollbar-thumb:hover { background: #bbb; }

        /* 以下保持原有样式不变 */
        .stats-card { background: #2c3e50; color: #ecf0f1; padding: 12px; border-radius: 8px; flex-shrink: 0; }
        .stats-item { display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px; }
        .efficiency-bar { height: 6px; background: #444; border-radius: 3px; overflow: hidden; }
        .efficiency-fill { height: 100%; background: #2ecc71; width: 0%; transition: 0.5s; }

        .group-title { font-size: 12px; font-weight: 700; color: #34495e; margin-top: 5px; border-left: 4px solid #3498db; padding-left: 8px; }
        .input-row { display: flex; gap: 8px; align-items: center; width: 100%; }
        .input-item { flex: 1; display: flex; flex-direction: column; gap: 2px; }
        .input-item span { font-size: 10px; color: #7f8c8d; }
        
        input[type="number"], select { width: 100%; padding: 6px; border: 1px solid #e0e0e0; border-radius: 4px; font-size: 12px; outline: none; background: white; box-sizing: border-box; }
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

        #mini-container { position: absolute; bottom: 20px; right: 20px; display: flex; flex-direction: column; align-items: flex-end; gap: 8px; pointer-events: none; }
        #mini-container > * { pointer-events: auto; }
        #mini-viewport { width: 220px; height: 220px; background: #fff; border: 2px solid #3498db; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); overflow: hidden; }
        .checkbox-item { display: flex; align-items: center; gap: 6px; font-size: 11px; color: #444; cursor: pointer; }
        
        .bulge-input { background-color: #e8f8f5; border: 1px solid #2ecc71; color: #27ae60; font-weight: bold; }
    </style>
</head>
<body>

<div id="sidebar">
    <h2 style="margin:0; font-size: 18px; color: #2c3e50;">📦 堆码专家 V8.3</h2>
    
    <div class="stats-card">
        <div class="stats-item"><span>装载总量:</span><b id="statCount">0 pcs</b></div>
        <div class="stats-item"><span>空间利用率:</span><b id="statEff">0%</b></div>
        <div class="efficiency-bar"><div id="effFill" class="efficiency-fill"></div></div>
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
                <option value="ultra">🚀 终极全排列 (V8.1)</option>
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
    
    <button class="btn-update" onclick="updateAndRender()">执行计算 (或按回车)</button>
    <button class="btn-toggle" id="toggleBtn">开启/关闭纸箱</button>
    
    <div style="height: 50px;"></div>
</div>

<div id="viewport">
    <div id="mini-container">
        <button style="width: auto; padding: 4px 10px; background: #fff; border: 1px solid #ccc; font-size: 11px;" onclick="resetMiniView()">🔄 重置</button>
        <div id="mini-viewport"></div>
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/TransformControls.js"></script>

<script>
    let scene, camera, renderer, controls, tfControls, raycaster, mouse;
    let targetGroup, boxGroup, itemsGroup, labelGroup;
    let miniScene, miniCamera, miniRenderer, miniItemContainer, miniControls;
    let isOpen = false, labelTexture = null, logoTexture = null;
    let showL1 = true, showL2 = true, showLogo1 = true, showLogo2 = true;
    let sizeMode = 'outer', flaps = [];
    const edgeMat = new THREE.LineBasicMaterial({ color: 0x000000 });
    
    const layerColors = [0x3498db, 0xe67e22, 0x2ecc71, 0xe74c3c, 0x9b59b6, 0x1abc9c];

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

    function toggleMiniViewManual() {
        document.getElementById('mini-container').style.display = document.getElementById('showMiniView').checked ? 'flex' : 'none';
    }
    
    function resetMiniView() {
        if(miniControls) miniControls.reset();
    }

    function updateOpacity() {
        const val = parseInt(document.getElementById('boxOpacity').value);
        document.getElementById('val-op').innerText = val;
        const op = val / 100;
        boxGroup.traverse(c => {
            if(c.isMesh && !c.userData.isInteractable) {
                c.material.opacity = op;
                c.material.transparent = op < 1.0;
                c.material.needsUpdate = true;
            }
        });
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

    // --- Guillotine Algorithm ---
    const memo = {};
    function solveGuillotine(rectL, rectW, l, w) {
        const key = Math.round(rectL * 1000) + "x" + Math.round(rectW * 1000);
        if (memo[key] !== undefined) return memo[key];
        if (rectL < Math.min(l, w) - 0.001 || rectW < Math.min(l, w) - 0.001) return { n: 0, items: [] };

        let bestSol = { n: 0, items: [] };
        let n_lw = Math.floor(rectL / l) * Math.floor(rectW / w);
        if (n_lw > bestSol.n) {
            let its = []; for(let i=0;i<Math.floor(rectL/l);i++) for(let j=0;j<Math.floor(rectW/w);j++) its.push({x:i*l, z:j*w, w:l, d:w});
            bestSol = {n: n_lw, items: its};
        }
        let n_wl = Math.floor(rectL / w) * Math.floor(rectW / l);
        if (n_wl > bestSol.n) {
            let its = []; for(let i=0;i<Math.floor(rectL/w);i++) for(let j=0;j<Math.floor(rectW/l);j++) its.push({x:i*w, z:j*l, w:w, d:l});
            bestSol = {n: n_wl, items: its};
        }

        if (rectL >= l && rectW >= w) {
            let maxCols = Math.floor(rectL / l);
            for (let i = 1; i <= maxCols; i++) {
                let colWidth = i * l;
                let itemsPerCol = Math.floor(rectW / w);
                let currentN = i * itemsPerCol;
                let currentItems = [];
                for (let c = 0; c < i; c++) for (let r = 0; r < itemsPerCol; r++) currentItems.push({ x: c * l, z: r * w, w: l, d: w });
                let resRight = solveGuillotine(rectL - colWidth, rectW, l, w);
                if (currentN + resRight.n > bestSol.n) {
                    let shiftedRight = resRight.items.map(it => ({ ...it, x: it.x + colWidth }));
                    bestSol = { n: currentN + resRight.n, items: [...currentItems, ...shiftedRight] };
                }
            }
        }
        if (rectL >= w && rectW >= l) {
            let maxCols = Math.floor(rectL / w);
            for (let i = 1; i <= maxCols; i++) {
                let colWidth = i * w;
                let itemsPerCol = Math.floor(rectW / l);
                let currentN = i * itemsPerCol;
                let currentItems = [];
                for (let c = 0; c < i; c++) for (let r = 0; r < itemsPerCol; r++) currentItems.push({ x: c * w, z: r * l, w: w, d: l });
                let resRight = solveGuillotine(rectL - colWidth, rectW, l, w);
                if (currentN + resRight.n > bestSol.n) {
                    let shiftedRight = resRight.items.map(it => ({ ...it, x: it.x + colWidth }));
                    bestSol = { n: currentN + resRight.n, items: [...currentItems, ...shiftedRight] };
                }
            }
        }

        if (rectW >= w && rectL >= l) {
            let maxRows = Math.floor(rectW / w);
            for (let j = 1; j <= maxRows; j++) {
                let rowHeight = j * w;
                let itemsPerRow = Math.floor(rectL / l);
                let currentN = j * itemsPerRow;
                let currentItems = [];
                for (let r = 0; r < j; r++) for (let c = 0; c < itemsPerRow; c++) currentItems.push({ x: c * l, z: r * w, w: l, d: w });
                let resBottom = solveGuillotine(rectL, rectW - rowHeight, l, w);
                if (currentN + resBottom.n > bestSol.n) {
                    let shiftedBottom = resBottom.items.map(it => ({ ...it, z: it.z + rowHeight }));
                    bestSol = { n: currentN + resBottom.n, items: [...currentItems, ...shiftedBottom] };
                }
            }
        }
        if (rectW >= l && rectL >= w) {
            let maxRows = Math.floor(rectW / l);
            for (let j = 1; j <= maxRows; j++) {
                let rowHeight = j * l;
                let itemsPerRow = Math.floor(rectL / w);
                let currentN = j * itemsPerRow;
                let currentItems = [];
                for (let r = 0; r < j; r++) for (let c = 0; c < itemsPerRow; c++) currentItems.push({ x: c * w, z: r * l, w: w, d: l });
                let resBottom = solveGuillotine(rectL, rectW - rowHeight, l, w);
                if (currentN + resBottom.n > bestSol.n) {
                    let shiftedBottom = resBottom.items.map(it => ({ ...it, z: it.z + rowHeight }));
                    bestSol = { n: currentN + resBottom.n, items: [...currentItems, ...shiftedBottom] };
                }
            }
        }
        memo[key] = bestSol;
        return bestSol;
    }

    function solveUltra(L, W, l, w) {
        for (var member in memo) delete memo[member]; 
        return solveGuillotine(L, W, l, w);
    }

    function updateAndRender() {
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

        const effectiveRL = rL + bulgeVal;
        const effectiveRW = rW + bulgeVal;
        const effectiveRH = rH + bulgeVal;

        boxGroup.clear(); itemsGroup.clear(); labelGroup.clear(); flaps=[];
        const bMat=new THREE.MeshPhongMaterial({color:0xd2a679,side:THREE.DoubleSide}); 
        const hMat=new THREE.MeshPhongMaterial({map:getHandleTexture(),side:THREE.DoubleSide});

        const addB=(geo,x,y,z,h=false)=>{ 
            const m=new THREE.Mesh(geo,h&&showH?hMat:bMat); m.position.set(x,y,z); 
            if(showE) m.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo),edgeMat)); boxGroup.add(m); return m; 
        };
        addB(new THREE.BoxGeometry(vL,wall,vW),0,0,0); 
        addB(new THREE.BoxGeometry(vL,vH,wall),0,vH/2,-vW/2); 
        const sideL = addB(new THREE.BoxGeometry(wall,vH,vW),-vL/2,vH/2,0,true); 
        const sideR = addB(new THREE.BoxGeometry(wall,vH,vW),vL/2,vH/2,0,true);
        const front = addB(new THREE.BoxGeometry(vL,vH,wall),0,vH/2,vW/2);

        const lpMat = new THREE.MeshPhongMaterial({color:labelTexture?0xffffff:0xccaa88,map:labelTexture,transparent:true});
        const loMat = new THREE.MeshPhongMaterial({color:logoTexture?0xffffff:0xff0000,map:logoTexture,transparent:true});
        const addPI = (parent, geo, mat, face) => {
            const m = new THREE.Mesh(geo, mat); m.userData.isInteractable = true; m.userData.face = face; 
            parent.add(m); return m;
        };
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
        
        const calcRL = effectiveRL + gap; const calcRW = effectiveRW + gap;
        const effL = iL + gap; const effW = iW + gap;

        let layerResult;
        if (strat === 'ultra') {
            layerResult = solveUltra(calcRL, calcRW, effL, effW); 
        } else if (strat === 'l_first') {
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

        let bBoxL = 0, bBoxW = 0;
        layerResult.items.forEach(it => { bBoxL = Math.max(bBoxL, it.x + it.w); bBoxW = Math.max(bBoxW, it.z + it.d); });
        
        let offX = (align === 'center') ? (effectiveRL - bBoxL)/2 : 0;
        let offZ = (align === 'center') ? (effectiveRW - bBoxW)/2 : 0;
        const startX = -rL/2 + offX;
        const startZ = -rW/2 + offZ;

        for(let y=0; y<nY; y++) {
            const currentColor = useLayerColor ? layerColors[y % layerColors.length] : 0x3498db;
            const iMat = new THREE.MeshPhongMaterial({ color: currentColor });

            layerResult.items.forEach(it => {
                const realW = it.w - gap;
                const realD = it.d - gap;
                const geo = new THREE.BoxGeometry(realW, iH, realD); 
                const m = new THREE.Mesh(geo, iMat);
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
        updateOpacity();
        updateMiniView(iL, iW, iH);
    }

    function updateMiniView(l, w, h) {
        if(!miniItemContainer) return;
        miniItemContainer.clear();
        const mat = new THREE.MeshPhongMaterial({color: 0x3498db});
        const geo = new THREE.BoxGeometry(l, h, w);
        const m = new THREE.Mesh(geo, mat);
        m.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo), edgeMat));
        miniItemContainer.add(m);
        miniItemContainer.add(createDimLabel(l.toString(), new THREE.Vector3(-l/2,-h/2,w/2), new THREE.Vector3(l/2,-h/2,w/2), new THREE.Vector3(0,-1,0), 20, '#e67e22'));
        miniItemContainer.add(createDimLabel(w.toString(), new THREE.Vector3(l/2,-h/2,w/2), new THREE.Vector3(l/2,-h/2,-w/2), new THREE.Vector3(1,0,0), 20, '#e67e22'));
    }

    function init(){
        const v=document.getElementById('viewport'); scene=new THREE.Scene(); scene.background=new THREE.Color(0xeef2f3);
        camera=new THREE.PerspectiveCamera(45,v.clientWidth/v.clientHeight,1,10000); camera.position.set(600,600,600);
        renderer=new THREE.WebGLRenderer({antialias:true}); renderer.setSize(v.clientWidth,v.clientHeight); v.appendChild(renderer.domElement);
        controls = new THREE.OrbitControls(camera, renderer.domElement); controls.enableDamping = true;
        controls.mouseButtons = { LEFT: THREE.MOUSE.ROTATE, MIDDLE: THREE.MOUSE.PAN, RIGHT: THREE.MOUSE.DOLLY };
        tfControls = new THREE.TransformControls(camera, renderer.domElement);
        tfControls.addEventListener('dragging-changed', (e) => { controls.enabled = !e.value; });
        scene.add(tfControls);
        tfControls.addEventListener('objectChange', () => {
            const obj = tfControls.object; if(!obj) return;
            const wall = parseFloat(document.getElementById('wallThick').value);
            if(obj.userData.face === 'front') { obj.position.z = wall/2 + 0.5; obj.scale.z = 1; }
            else if(obj.userData.face === 'side') { obj.position.x = wall/2 + 0.5; obj.scale.x = 1; }
        });
        raycaster = new THREE.Raycaster(); mouse = new THREE.Vector2();
        renderer.domElement.addEventListener('pointerdown', (e) => {
            if (e.button !== 0) return;
            const rect = renderer.domElement.getBoundingClientRect();
            mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(targetGroup.children, true);
            const target = intersects.find(i => i.object.userData.isInteractable);
            if(target) {
                tfControls.attach(target.object);
                if(target.object.userData.face === 'front') { tfControls.showZ = false; tfControls.showX = true; tfControls.showY = true; }
                else { tfControls.showX = false; tfControls.showZ = true; tfControls.showY = true; }
            } else if(!tfControls.dragging) tfControls.detach();
        });
        window.addEventListener('keydown', (e) => {
            const k = e.key.toLowerCase();
            if(k === 'w') tfControls.setMode('translate');
            if(k === 'e') tfControls.setMode('scale');
        });
        
        document.querySelectorAll('.calc-trigger').forEach(input => {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    input.blur(); 
                    updateAndRender();
                }
            });
        });

        scene.add(new THREE.AmbientLight(0xffffff, 0.7));
        const dl=new THREE.DirectionalLight(0xffffff, 0.8); dl.position.set(200, 500, 300); scene.add(dl);
        targetGroup=new THREE.Group(); boxGroup=new THREE.Group(); itemsGroup=new THREE.Group(); labelGroup=new THREE.Group();
        targetGroup.add(boxGroup,itemsGroup,labelGroup); scene.add(targetGroup); initMini();
        document.getElementById('toggleBtn').onclick=()=>{isOpen=!isOpen; document.getElementById('toggleBtn').innerText=isOpen?"关闭纸箱":"开启纸箱";};
        
        // 关键修复：窗口调整时同步更新
        window.addEventListener('resize',()=>{
            camera.aspect=v.clientWidth/v.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(v.clientWidth,v.clientHeight);
        });
        
        updateAndRender(); animate();
    }

    function initMini(){
        const mv=document.getElementById('mini-viewport'); miniScene=new THREE.Scene(); miniScene.background=new THREE.Color(0xffffff);
        miniCamera=new THREE.PerspectiveCamera(45,1,1,2000); miniCamera.position.set(240,180,240);
        miniRenderer=new THREE.WebGLRenderer({antialias:true}); miniRenderer.setSize(220,220); mv.appendChild(miniRenderer.domElement);
        miniControls = new THREE.OrbitControls(miniCamera, miniRenderer.domElement);
        miniScene.add(new THREE.AmbientLight(0xffffff,0.9)); miniItemContainer=new THREE.Group(); miniScene.add(miniItemContainer);
    }

    function animate(){
        requestAnimationFrame(animate); 
        const tA=isOpen?Math.PI*0.8:0; 
        const lF=flaps.filter(f=>f.type==='long'), sF=flaps.filter(f=>f.type==='short');
        flaps.forEach(f=>{
            let m=false; if(isOpen){ if(f.type==='long') m=true; else if(f.type==='short'&&lF[0].currentAng>0.4) m=true; }
            else{ if(f.type==='short') m=true; else if(f.type==='long'&&sF[0].currentAng<0.2) m=true; }
            if(m) f.currentAng+=(tA-f.currentAng)*0.1;
            if(f.axis==='x')f.pivot.rotation.x=f.currentAng*f.dir; else f.pivot.rotation.z=-f.currentAng*f.dir;
        });
        controls.update(); if (miniControls) miniControls.update();
        renderer.render(scene,camera); miniRenderer.render(miniScene,miniCamera);
    }
    init();
</script>
</body>
</html>
"""

# 4. 在 Streamlit 中渲染 (Height 设置较大值以防止 Python 侧截断，实际由 CSS 控制)
components.html(html_code, height=1200, scrolling=False)
