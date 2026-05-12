import os
import json
import socket
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# ================= 1. 核心配置 =================
ACTIVITY_NAME = "顏值從齒開始"

# 如果有使用 LocalTunnel，請將網址填入下方 (例如 "https://xxxxx.loca.lt")
EXTERNAL_URL = "" 

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except: ip = '127.0.0.1'
    finally: s.close()
    return ip

LOCAL_IP = get_ip()

# 衛教活動題目設定
QUESTIONS = {
    "第二組": "2. 你最近刷牙時牙齦會流血但不會痛，這可能是牙齦發炎嗎？請說明可能原因，並提出改善方法或是否需要就醫。",
    "第三組": "3. 智齒橫著長（水平智齒）但目前沒有疼痛或發炎，你會選擇拔除嗎？請說明你的判斷理由。",
    "第四組": "4. 每天都有刷牙但仍有口臭，朋友也有提醒。你認為可能原因是什麼？應該如何改善？",
    "第五組": "5. 常喝咖啡導致牙齒偏黃，想進行冷光美白。是否每個人都適合？有哪些注意事項？"
}

# 儲存回應的清單與 ID 計數器
responses = []
response_id_counter = 0

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
        .q-display { background: #fff1f2; padding: 15px; border-radius: 12px; color: #e11d48; font-size: 15px; margin-bottom: 20px; border-left: 6px solid #fb7185; line-height: 1.6; }
        .btn { width: 100%; color: white; border: none; padding: 16px; border-radius: 12px; font-size: 18px; font-weight: bold; cursor: pointer; text-decoration: none; display: block; text-align: center; }
        .btn-grad { background: linear-gradient(135deg, var(--primary), var(--secondary)); }
        #step2 { display: none; }
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
            <button class="btn btn-grad" onclick="toStep2()">開始討論</button>
        </div>
        <div id="step2" class="card">
            <h2 id="gTitle" style="margin-bottom:5px;"></h2>
            <p style="text-align:center; font-size:14px; color:#64748b; margin-bottom:15px;">填答者：<b id="nDisplay"></b></p>
            <div id="qText" class="q-display"></div>
            <span class="step-label">小組討論共識</span>
            <textarea id="ans" rows="5" placeholder="請在此輸入討論內容..."></textarea>
            <button class="btn btn-grad" onclick="doSubmit()">確認送出</button>
        </div>
    </div>
    <script>
        const qs = {{QUESTIONS_JSON}};
        function toStep2() {
            const n = document.getElementById('uName').value.trim();
            const g = document.getElementById('uGroup').value;
            if(!n || !g) { alert("請填寫姓名並選擇組別！"); return; }
            document.getElementById('nDisplay').innerText = n;
            document.getElementById('gTitle').innerText = g;
            document.getElementById('qText').innerText = qs[g];
            document.getElementById('step1').style.display='none';
            document.getElementById('step2').style.display='block';
        }
        async function doSubmit() {
            const n = document.getElementById('uName').value.trim();
            const g = document.getElementById('uGroup').value;
            const a = document.getElementById('ans').value.trim();
            if(!a) { alert("內容不能為空！"); return; }
            const p = new URLSearchParams();
            p.append('name', n); p.append('group', g); p.append('answer', a);
            await fetch('/submit', { method: 'POST', body: p });
            alert("🎉 提交成功！");
            location.reload();
        }
    </script>
</body>
</html>
"""

# ================= 3. 大螢幕展示牆 HTML (含管理功能) =================

SCREEN_PAGE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>展示牆</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <style>
        body { font-family: "Microsoft JhengHei", sans-serif; background: #0f172a; color: white; margin: 0; padding: 20px; overflow: hidden; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .main-title { font-size: 2.5em; font-weight: bold; color: #9cdcfe; cursor: pointer; }
        .qr-card { background: white; padding: 10px; border-radius: 12px; display: flex; align-items: center; }
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; height: 78vh; }
        .group-card { background: rgba(30, 41, 59, 0.7); border-radius: 20px; padding: 20px; display: flex; flex-direction: column; border: 1px solid rgba(255,255,255,0.1); }
        .group-name { font-size: 1.8em; color: #fb7185; font-weight: bold; margin-bottom: 10px; }
        .responses-list { flex: 1; overflow-y: auto; }
        .entry { background: rgba(255,255,255,0.06); padding: 12px; border-radius: 12px; margin-bottom: 10px; border-left: 4px solid #38bdf8; position: relative; }
        .del-btn { position: absolute; right: 10px; top: 10px; background: #ef4444; color: white; border: none; border-radius: 4px; padding: 2px 8px; cursor: pointer; display: none; font-size: 12px; }
        .admin-mode .del-btn { display: block; }
    </style>
</head>
<body id="mainBody">
    <div class="header">
        <div class="main-title" onclick="toggleAdmin()">🦷 {{TITLE}} 討論展示牆</div>
        <div class="qr-card">
            <div id="qrcode"></div>
            <div style="color: black; margin-left: 10px; font-size: 12px; font-weight: bold;">掃碼加入</div>
        </div>
    </div>
    <div id="board" class="grid"></div>
    <script>
        let adminActive = false;
        const finalUrl = "{{EXTERNAL_URL}}" || "http://{{IP}}:8000";
        new QRCode(document.getElementById("qrcode"), { text: finalUrl, width: 80, height: 80 });

        function toggleAdmin() {
            adminActive = !adminActive;
            document.getElementById('mainBody').classList.toggle('admin-mode', adminActive);
            if(adminActive) alert("管理模式啟動：現在可以點擊紅色的 [刪除] 按鈕清理留言。");
        }

        async function deleteResp(id) {
            if(!confirm("確定要刪除這條留言嗎？")) return;
            await fetch(`/delete/${id}`, { method: 'DELETE' });
            update();
        }

        async function update() {
            try {
                const res = await fetch('/get_data');
                const data = await res.json();
                let html = '';
                ["第二組", "第三組", "第四組", "第五組"].forEach(g => {
                    const entries = data.filter(d => d.group === g);
                    html += `<div class="group-card">
                        <div class="group-name">${g}</div>
                        <div class="responses-list">
                            ${entries.map(e => `
                                <div class="entry">
                                    <button class="del-btn" onclick="deleteResp(${e.id})">刪除</button>
                                    <b style="color:#38bdf8">${e.name}：</b>
                                    <div style="margin-top:5px;">${e.answer}</div>
                                </div>`).join('')}
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
    return SCREEN_PAGE.replace("{{TITLE}}", ACTIVITY_NAME).replace("{{IP}}", LOCAL_IP).replace("{{EXTERNAL_URL}}", EXTERNAL_URL).replace("{{QUESTIONS_JSON}}", json.dumps(QUESTIONS, ensure_ascii=False))

@app.get("/get_data")
async def get_all_data(): 
    return responses

@app.post("/submit")
async def handle_submit(name: str = Form(...), group: str = Form(...), answer: str = Form(...)):
    global response_id_counter
    # 如果同名同組則更新，否則新增
    existing = next((i for i in responses if i["name"] == name and i["group"] == group), None)
    if existing:
        existing["answer"] = answer
    else:
        responses.append({"id": response_id_counter, "name": name, "group": group, "answer": answer})
        response_id_counter += 1
    return {"status": "ok"}

@app.delete("/delete/{resp_id}")
async def delete_entry(resp_id: int):
    global responses
    responses = [i for i in responses if i["id"] != resp_id]
    return {"status": "success"}

if __name__ == "__main__":
    print(f"✅ 系統啟動成功！")
    uvicorn.run(app, host="0.0.0.0", port=8000)