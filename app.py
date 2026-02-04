import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="3D 智能堆码专家 V8.3 Pro")

st.markdown("""
    <style>
        .block-container { padding: 0rem; max-width: 100%; }
        iframe { display: block; border: none; }
    </style>
""", unsafe_allow_html=True)

v83_source_code = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <style>
        html, body { margin: 0; padding: 0; width: 100%; height: 100vh; overflow: hidden; }
        body { font-family: "PingFang SC", "Segoe UI", sans-serif; display: flex; background-color: #f4f7f6; }
        #sidebar { width: 340px; height: 100vh; background: #ffffff; border-right: 1px solid #d1d9e6; padding: 18px; box-sizing: border-box; z-index: 100; display: flex; flex-direction: column; gap: 10px; box-shadow: 4px 0 15px rgba(0,0,0,0.05); overflow-y: auto; }
        #viewport { flex-grow: 1; height: 100vh; position: relative; background: #eef2f3; cursor: crosshair; }
        .stats-card { background: #2c3e50; color: #ecf0f1; padding: 12px; border-radius: 8px; flex-shrink: 0; }
        .stats-item { display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px; }
        .efficiency-bar { height: 6px; background: #444; border-radius: 3px; overflow: hidden; }
        .efficiency-fill { height: 100%; background: #2ecc71; width: 0%; transition: 0.5s; }
        .group-title { font-size: 12px; font-weight: 700; color: #34495e; margin-top: 5px; border-left: 4px solid #3498db; padding-left: 8px; }
        .input-row { display: flex; gap: 8px; align-items: center; width: 100%; }
        .input-item { flex: 1; display: flex; flex-direction: column; gap: 2px; }
        .input-item span { font-size: 10px; color: #7f8c8d; }
        input[type="number"], select { width: 100%; padding: 6px; border: 1px solid #e0e0e0; border-radius: 4px; font-size: 12px; outline: none; background: white; }
        .mode-toggle { display: flex; background: #eee; border-radius: 6px; padding: 2px; margin-bottom: 5px; }
        .mode-btn { flex: 1; padding: 5px; font-size: 11px; border: none; background: transparent; cursor: pointer; border-radius: 4px; color: #666; transition: 0.3s; }
        .mode-btn.active { background: #fff; color: #3498db; box-shadow: 0 2px 5px rgba(0,0,0,0.1); font-weight: bold; }
        button { flex: 1; padding: 8px; cursor: pointer; border: none; border-radius: 6px; font-weight: bold; font-size: 11px; }
        .btn-update { background: #e74c3c; color: #fff; margin-top: 5px; }
        .btn-toggle { background: #95a5a6; color: #fff; }
        .btn-hide { background: #ecf0f1; color: #7f8c8d; border: 1px solid #d1d9e6; }
        .btn-hide.active { background: #3498db; color: white; border-color: #2980b9; }
        #mini-container { position: absolute; bottom: 20px; right: 20px; display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }
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
    <div class="group-title">1. 外箱配置</div>
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
        <div class="input-item"><span>厚度</span><input type="number" id="wallThick" value="4" class="calc-trigger"></div>
        <div class="input-item"><span>膨胀</span><input type="number" id="bulgeVal" value="0" class="bulge-input calc-trigger"></div>
    </div>
    <div class="group-title">2. 内装物</div>
    <div class="input-row">
        <div class="input-item"><span>长</span><input type="number" id="itemL" value="180" class="calc-trigger"></div>
        <div class="input-item"><span>宽</span><input type="number" id="itemW" value="120" class="calc-trigger"></div>
        <div class="input-item"><span>高</span><input type="number" id="itemH" value="100" class="calc-trigger"></div>
    </div>
    <div class="input-row">
        <div class="input-item"><span>算法</span>
            <select id="stackStrategy" onchange="updateAndRender()">
                <option value="ultra">🚀 终极全排列</option>
                <option value="l_first">📍 长度优先</option>
            </select>
        </div>
        <div class="input-item"><span>对齐</span>
            <select id="alignStrategy" onchange="updateAndRender()">
                <option value="center">🎯 居中</option>
                <option value="edge">📐 靠角</option>
            </select>
        </div>
    </div>
    <div class="group-title">3. 显示控制</div>
    <div class="input-row" style="flex-wrap: wrap; gap: 8px;">
        <label class="checkbox-item"><input type="checkbox" id="showEdges" checked onchange="updateAndRender()"> 线框</label>
        <label class="checkbox-item"><input type="checkbox" id="layerColor" checked onchange="updateAndRender()"> 分层</label>
    </div>
    <button class="btn-update" onclick="updateAndRender()">执行计算 (Enter)</button>
    <button class="btn-toggle" id="toggleBtn">开启/关闭纸箱</button>
</div>
<div id="viewport">
    <div id="mini-container">
        <div id="mini-viewport"></div>
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/TransformControls.js"></script>
<script>
    let scene, camera, renderer, controls, tfControls, raycaster, mouse;
    let targetGroup, boxGroup, itemsGroup, labelGroup, flaps = [];
    let isOpen = false;
    const edgeMat = new THREE.LineBasicMaterial({ color: 0x000000 });
    const layerColors = [0x3498db, 0xe67e22, 0x2ecc71, 0xe74c3c, 0x9b59b6, 0x1abc9c];

    function updateAndRender() {
        const inputL=parseFloat(document.getElementById('boxL').value), inputW=parseFloat(document.getElementById('boxW').value), inputH=parseFloat(document.getElementById('boxH').value);
        const wall=parseFloat(document.getElementById('wallThick').value), bulge=parseFloat(document.getElementById('bulgeVal').value)||0;
        const iL=parseFloat(document.getElementById('itemL').value), iW=parseFloat(document.getElementById('itemW').value), iH=parseFloat(document.getElementById('itemH').value);
        const showE=document.getElementById('showEdges').checked, useLayerColor=document.getElementById('layerColor').checked;
        const align=document.getElementById('alignStrategy').value;

        boxGroup.clear(); itemsGroup.clear(); flaps=[];
        let vL=inputL, vW=inputW, vH=inputH, rL=vL-wall*2, rW=vW-wall*2, rH=vH-wall*2;
        
        const bMat=new THREE.MeshPhongMaterial({color:0xd2a679, side:THREE.DoubleSide});
        const addB=(geo,x,y,z)=>{ const m=new THREE.Mesh(geo,bMat); m.position.set(x,y,z); if(showE) m.add(new THREE.LineSegments(new THREE.EdgesGeometry(geo),edgeMat)); boxGroup.add(m); return m; };
        
        addB(new THREE.BoxGeometry(vL,wall,vW),0,0,0);
        addB(new THREE.BoxGeometry(vL,vH,wall),0,vH/2,-vW/2);
        addB(new THREE.BoxGeometry(wall,vH,vW),-vL/2,vH/2,0);
        addB(new THREE.BoxGeometry(wall,vH,vW),vL/2,vH/2,0);
        addB(new THREE.BoxGeometry(vL,vH,wall),0,vH/2,vW/2);

        const addF=(fw,fd,px,pz,axis,dir,type)=>{
            const p=new THREE.Group(); p.position.set(px,vH,pz);
            const m=new THREE.Mesh(new THREE.BoxGeometry(fw,wall/2,fd),bMat);
            m.position.z=(axis==='x')?fd/2*-dir:0; m.position.x=(axis==='z')?fw/2*-dir:0;
            if(showE) m.add(new THREE.LineSegments(new THREE.EdgesGeometry(m.geometry),edgeMat));
            p.add(m); boxGroup.add(p); flaps.push({pivot:p, axis, dir, currentAng:0, type});
        };
        addF(vL,vW/2,0,vW/2,'x',1,'long'); addF(vL,vW/2,0,-vW/2,'x',-1,'long');
        addF(vL/2,vW,vL/2,0,'z',1,'short'); addF(vL/2,vW,-vL/2,0,'z',-1,'short');

        const nX=Math.floor((rL+bulge)/iL), nZ=Math.floor((rW+bulge)/iW), nY=Math.floor((rH+bulge)/iH);
        document.getElementById('statCount').innerText=(nX*nZ*nY)+" pcs";
        
        let offX=(align==='center')?(rL-nX*iL)/2:0, offZ=(align==='center')?(rW-nZ*iW)/2:0;
        for(let y=0; y<nY; y++){
            const mat=new THREE.MeshPhongMaterial({color:useLayerColor?layerColors[y%6]:0x3498db});
            for(let x=0; x<nX; x++) for(let z=0; z<nZ; z++){
                const m=new THREE.Mesh(new THREE.BoxGeometry(iL,iH,iW),mat);
                m.position.set(-rL/2+offX+x*iL+iL/2, y*iH+iH/2+wall/2, -rW/2+offZ+z*iW+iW/2);
                if(showE) m.add(new THREE.LineSegments(new THREE.EdgesGeometry(m.geometry),edgeMat));
                itemsGroup.add(m);
            }
        }
    }

    function init(){
        const v=document.getElementById('viewport'); scene=new THREE.Scene(); scene.background=new THREE.Color(0xeef2f3);
        camera=new THREE.PerspectiveCamera(45,v.clientWidth/v.clientHeight,1,10000); camera.position.set(600,600,600);
        renderer=new THREE.WebGLRenderer({antialias:true}); renderer.setSize(v.clientWidth,v.clientHeight); v.appendChild(renderer.domElement);
        controls=new THREE.OrbitControls(camera, renderer.domElement);
        tfControls=new THREE.TransformControls(camera, renderer.domElement);
        tfControls.addEventListener('dragging-changed',e=>controls.enabled=!e.value); scene.add(tfControls);
        
        // 恢复鼠标交互 Raycaster
        raycaster=new THREE.Raycaster(); mouse=new THREE.Vector2();
        v.addEventListener('pointerdown', e=>{
            const rect=renderer.domElement.getBoundingClientRect();
            mouse.x=((e.clientX-rect.left)/rect.width)*2-1; mouse.y=-((e.clientY-rect.top)/rect.height)*2+1;
            raycaster.setFromCamera(mouse, camera);
            const intersects=raycaster.intersectObjects(boxGroup.children, true);
            const target=intersects.find(i=>i.object.userData.isInteractable);
            if(target) tfControls.attach(target.object); else if(!tfControls.dragging) tfControls.detach();
        });

        scene.add(new THREE.AmbientLight(0xffffff,0.7)); const dl=new THREE.DirectionalLight(0xffffff,0.8); dl.position.set(200,500,300); scene.add(dl);
        targetGroup=new THREE.Group(); boxGroup=new THREE.Group(); itemsGroup=new THREE.Group();
        targetGroup.add(boxGroup,itemsGroup); scene.add(targetGroup);
        document.getElementById('toggleBtn').onclick=()=>isOpen=!isOpen;
        updateAndRender(); animate();
    }

    function animate(){
        requestAnimationFrame(animate);
        const tA=isOpen?Math.PI*0.8:0;
        // 关键：恢复动画开启/关闭顺序逻辑
        const lF=flaps.filter(f=>f.type==='long'), sF=flaps.filter(f=>f.type==='short');
        flaps.forEach(f=>{
            let canMove=false;
            if(isOpen){
                if(f.type==='long') canMove=true;
                else if(f.type==='short' && lF[0].currentAng>0.4) canMove=true;
            } else {
                if(f.type==='short') canMove=true;
                else if(f.type==='long' && sF[0].currentAng<0.2) canMove=true;
            }
            if(canMove) f.currentAng+=(tA-f.currentAng)*0.1;
            if(f.axis==='x') f.pivot.rotation.x=f.currentAng*f.dir;
            else f.pivot.rotation.z=-f.currentAng*f.dir;
        });
        controls.update(); renderer.render(scene,camera);
    }
    init();
</script>
</body>
</html>
"""

components.html(v83_source_code, height=900)
