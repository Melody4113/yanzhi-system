import os
import json
import socket
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# ================= 1. 核心配置 (已更新題目內容) =================
ACTIVITY_NAME = "顏值從齒開始"

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except: ip = '127.0.0.1'
    finally: s.close()
    return ip

LOCAL_IP = get_ip()

# 這裡更新了您提供的精確題目
QUESTIONS = {
    "第二組": "2. 你最近刷牙時牙齦會流血但不會痛，這可能是牙齦發炎嗎？請說明可能原因，並提出改善方法或是否需要就醫。",
    "第三組": "3. 智齒橫著長（水平智齒）但目前沒有疼痛或發炎，你會選擇拔除嗎？請說明你的判斷理由。",
    "第四組": "4. 每天都有刷牙但仍有口臭，朋友也有提醒。你認為可能原因是什麼？應該如何改善？",
    "第五組": "5. 常喝咖啡導致牙齒偏黃，想進行冷光美白。是否每個人都適合？有哪些注意事項？"
}

responses = []

# ================= 2. 學生手機端 HTML =================

STUDENT_PAGE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{{TITLE}}</title>
    <style>
        :root { --primary: #0ea5e9; --secondary: #10b981; --dark: #1e293b; --light: #f8fafc; }
        body { font-family: -apple-system, "Microsoft JhengHei", sans-serif; background: #f1f5f9; margin: 0; padding: 15px; color: var(--dark); }
        .container { width: 100%; max-width: 480px; margin: auto; }
        .card { background: white; padding: 25px; border-radius: 24px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-bottom: 20px; }
        h2 { text-align: center; color: var(--primary); margin: 0 0 20px; font-size: 22px; }
        .step-label { font-size: 14px; color: #64748b; font-weight: bold; margin-bottom: 8px; display: block; }
        input, select, textarea { width: 100%; padding: 12px; margin-bottom: 15px; border: 1.5px solid #e2e8f0; border-radius: 12px; font-size: 16px; box-sizing: border-box; outline: none; }
        input:focus, select:focus, textarea:focus { border-color: var(--primary); }
        .q-display { background: #fff1f2; padding: 15px; border-radius: 12px; color: #e11d48; font-size: 15px; margin-bottom: 20px; border-left: 6px solid #fb7185; line-height: 1.6; }
        .btn { width: 100%; color: white; border: none; padding: 16px; border-radius: 12px; font-size: 18px; font-weight: bold; cursor: pointer; transition: 0.3s; text-decoration: none; display: block; text-align: center; }
        .btn:disabled { background: #cbd5e1; cursor: not-allowed; }
        .btn-blue { background: var(--primary); }
        .btn-grad { background: linear-gradient(135deg, var(--primary), var(--secondary)); }
        
        #step2 { display: none; }
        
        #aiBall { position: fixed; bottom: 20px; right: 20px; width: 60px; height: 60px; background: #334155; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 28px; z-index: 1000; box-shadow: 0 4px 15px rgba(0,0,0,0.3); cursor: pointer; border: 2px solid white; }
        #aiPortal { position: fixed; bottom: 90px; right: 20px; width: 220px; background: white; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); display: none; flex-direction: column; z-index: 1000; border: 1px solid #e2e8f0; padding: 15px; }
        .portal-title { font-weight: bold; margin-bottom: 12px; text-align: center; color: #334155; font-size: 14px; }
        .ai-link { margin-bottom: 10px; padding: 12px; border-radius: 10px; display: flex; align-items: center; justify-content: center; text-decoration: none; color: white; font-weight: bold; transition: 0.2s; font-size: 15px; }
        .gpt { background: #10a37f; }
        .gemini { background: #1a73e8; }
        
        .back-link { width: 100%; background: none; border: none; margin-top: 15px; color: #94a3b8; font-size: 13px; cursor: pointer; text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div id="step1" class="card">
            <h2>🦷 {{TITLE}}</h2>
            <span class="step-label">請輸入您的姓名</span>
            <input type="text" id="uName" placeholder="例如：王小明">
            <span class="step-label">組別選擇</span>
            <select id="uGroup">
                <option value="">-- 請選擇您的討論組別 --</option>
                {{OPTIONS}}
            </select>
            <button class="btn btn-blue" id="nextBtn" onclick="toStep2()">開始討論</button>
        </div>

        <div id="step2" class="card">
            <h2 id="gTitle" style="margin-bottom:5px;"></h2>
            <p style="text-align:center; font-size:14px; color:#64748b; margin-bottom:15px;">填答者：<b id="nDisplay"></b></p>
            <div id="qText" class="q-display"></div>
            <span class="step-label">小組討論共識</span>
            <textarea id="ans" rows="5" placeholder="請在此輸入討論內容..."></textarea>
            <button id="sBtn" class="btn btn-grad" onclick="doSubmit()">確認送出</button>
            <button class="back-link" onclick="location.reload()">← 更換組別/姓名</button>
        </div>
    </div>

    <div id="aiBall" onclick="togglePortal()">✨</div>
    <div id="aiPortal">
        <div class="portal-title">開啟 AI 助手協作</div>
        <a href="https://chat.openai.com" target="_blank" class="ai-link gpt">ChatGPT</a>
        <a href="https://gemini.google.com" target="_blank" class="ai-link gemini">Google Gemini</a>
        <div style="font-size:11px; color:#94a3b8; text-align:center; margin-top:5px;">點擊將開啟新視窗</div>
    </div>

    <script>
        const qs = {{QUESTIONS_JSON}};
        
        function toStep2() {
            const n = document.getElementById('uName').value.trim();
            const g = document.getElementById('uGroup').value;
            if(!n || !g) {
                alert("請填寫姓名並選擇組別！");
                return;
            }
            document.getElementById('nDisplay').innerText = n;
            document.getElementById('gTitle').innerText = g;
            document.getElementById('qText').innerText = qs[g];
            document.getElementById('step1').style.display='none';
            document.getElementById('step2').style.display='block';
        }

        function togglePortal() {
            const p = document.getElementById('aiPortal');
            p.style.display = p.style.display === 'flex' ? 'none' : 'flex';
        }

        async function doSubmit() {
            const n = document.getElementById('uName').value.trim();
            const g = document.getElementById('uGroup').value;
            const a = document.getElementById('ans').value.trim();
            
            if(a.length === 0) {
                alert("討論內容不能是空的喔！");
                return;
            }

            const btn = document.getElementById('sBtn');
            btn.disabled = true;
            btn.innerText = "正在傳送...";

            try {
                const p = new URLSearchParams();
                p.append('name', n);
                p.append('group', g);
                p.append('answer', a);
                
                const response = await fetch('/submit', { method: 'POST', body: p });
                if(response.ok) {
                    alert("🎉 提交成功！點擊確定返回初始頁面。");
                    location.reload();
                } else {
                    throw new Error();
                }
            } catch(e) {
                alert("❌ 連線出錯，請再試一次。");
                btn.disabled = false;
                btn.innerText = "確認送出";
            }
        }
    </script>
</body>
</html>
"""

# ================= 3. 大螢幕展示牆 HTML =================

SCREEN_PAGE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>討論展示牆</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <style>
        body { 
            font-family: "PingFang TC", "Microsoft JhengHei", sans-serif; 
            background: #0f172a; color: white; margin: 0; padding: 40px; overflow: hidden;
        }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        .main-title { 
            font-size: 3.5em; font-weight: bold; 
            color: #9cdcfe; text-shadow: 0 0 15px rgba(156, 220, 254, 0.8);
            letter-spacing: 3px;
        }
        .qr-card { 
            background: white; padding: 12px; border-radius: 18px; 
            display: flex; align-items: center; box-shadow: 0 0 25px rgba(156, 220, 254, 0.4);
        }
        .qr-label { color: #0f172a; font-weight: bold; margin-left: 15px; font-size: 1.1em; line-height: 1.3; }
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 25px; height: 78vh; }
        .group-card { 
            background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px);
            border-radius: 30px; padding: 25px; 
            border: 1px solid rgba(255,255,255,0.1);
            display: flex; flex-direction: column; position: relative;
        }
        .group-name { font-size: 2.2em; color: #fb7185; font-weight: bold; margin-bottom: 12px; }
        .question-box { 
            background: rgba(15, 23, 42, 0.5); padding: 18px; border-radius: 15px; 
            font-size: 1.1em; color: #cbd5e1; border-left: 4px solid #fb7185; line-height: 1.5;
        }
        .responses-list { flex: 1; overflow-y: auto; margin-top: 15px; }
        .entry { 
            background: rgba(255,255,255,0.06); padding: 15px; border-radius: 15px; margin-bottom: 12px;
            border-left: 4px solid #38bdf8;
        }
        .entry-name { color: #38bdf8; font-weight: bold; font-size: 1.1em; margin-bottom: 5px; }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="main-title">🦷 {{TITLE}} 討論展示</div>
        <div class="qr-card">
            <div id="qrcode"></div>
            <div class="qr-label">手機掃描<br>加入討論</div>
        </div>
    </div>
    <div id="board" class="grid"></div>
    <script>
        new QRCode(document.getElementById("qrcode"), { text: "http://{{IP}}:8000", width: 100, height: 100 });
        const qs = {{QUESTIONS_JSON}};
        async function update() {
            try {
                const res = await fetch('/get_data');
                const data = await res.json();
                let html = '';
                ["第二組", "第三組", "第四組", "第五組"].forEach(g => {
                    const entries = data.filter(d => d.group === g);
                    html += `
                        <div class="group-card">
                            <div class="group-name">${g}</div>
                            <div class="question-box">${qs[g]}</div>
                            <div class="responses-list">
                                ${entries.length > 0 ? entries.map(e => `
                                    <div class="entry">
                                        <div class="entry-name">${e.name}：</div>
                                        <div style="line-height:1.6;">${e.answer}</div>
                                    </div>
                                `).join('') : '<div style="text-align:center; color:#475569; margin-top:40px;">等待資料更新...</div>'}
                            </div>
                        </div>`;
                });
                document.getElementById('board').innerHTML = html;
            } catch(e) {}
        }
        setInterval(update, 3000); update();
    </script>
</body>
</html>
"""

# ================= 4. 後端應用邏輯 =================

@app.get("/", response_class=HTMLResponse)
async def index():
    opts = "".join([f'<option value="{g}">{g}</option>' for g in QUESTIONS.keys()])
    return STUDENT_PAGE.replace("{{TITLE}}", ACTIVITY_NAME).replace("{{OPTIONS}}", opts).replace("{{QUESTIONS_JSON}}", json.dumps(QUESTIONS, ensure_ascii=False))

@app.get("/screen", response_class=HTMLResponse)
async def screen():
    return SCREEN_PAGE.replace("{{TITLE}}", ACTIVITY_NAME).replace("{{IP}}", LOCAL_IP).replace("{{QUESTIONS_JSON}}", json.dumps(QUESTIONS, ensure_ascii=False))

@app.get("/get_data")
async def get_all_data(): 
    return responses

@app.post("/submit")
async def handle_submit(name: str = Form(...), group: str = Form(...), answer: str = Form(...)):
    existing = next((i for i in responses if i["name"] == name and i["group"] == group), None)
    if existing:
        existing["answer"] = answer
    else:
        responses.append({"name": name, "group": group, "answer": answer})
    return {"status": "ok"}

if __name__ == "__main__":
    print(f"✅ 系統啟動中...")
    print(f"📱 填寫頁面: http://{LOCAL_IP}:8000")
    print(f"📺 大螢幕牆: http://{LOCAL_IP}:8000/screen")
    uvicorn.run(app, host="0.0.0.0", port=8000)