import os
import json
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# =========================
# 活動名稱
# =========================

ACTIVITY_NAME = "顏值從齒開始"

# =========================
# 題目設定
# =========================

QUESTIONS = {
    "第二組": "2. 你最近刷牙時牙齦會流血但不會痛，這可能是牙齦發炎嗎？請說明可能原因，並提出改善方法或是否需要就醫。",
    
    "第三組": "3. 智齒橫著長（水平智齒）但目前沒有疼痛或發炎，你會選擇拔除嗎？請說明你的判斷理由。",
    
    "第四組": "4. 每天都有刷牙但仍有口臭，朋友也有提醒。你認為可能原因是什麼？應該如何改善？",
    
    "第五組": "5. 常喝咖啡導致牙齒偏黃，想進行冷光美白。是否每個人都適合？有哪些注意事項？"
}

responses = []

# =========================
# 學生手機頁面
# =========================

STUDENT_PAGE = """
<!DOCTYPE html>
<html lang="zh-TW">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>{{TITLE}}</title>

    <style>

        :root{
            --primary:#60a5fa;
            --secondary:#38bdf8;
            --bg:#f1f5f9;
        }

        body{
            margin:0;
            padding:20px;
            background:var(--bg);
            font-family:-apple-system,"Microsoft JhengHei",sans-serif;
        }

        .container{
            max-width:500px;
            margin:auto;
        }

        .card{
            background:white;
            padding:30px;
            border-radius:28px;
            box-shadow:0 10px 25px rgba(0,0,0,0.05);
        }

        h1{
            text-align:center;
            color:var(--primary);
            margin-bottom:35px;
        }

        .label{
            font-size:18px;
            font-weight:bold;
            color:#64748b;
            margin-bottom:12px;
            display:block;
        }

        input,select,textarea{

            width:100%;
            padding:18px;
            border-radius:18px;
            border:2px solid #dbeafe;
            box-sizing:border-box;
            font-size:18px;
            margin-bottom:25px;
            outline:none;
        }

        textarea{
            resize:none;
        }

        input:focus,
        select:focus,
        textarea:focus{
            border-color:var(--primary);
        }

        .btn{

            width:100%;
            padding:18px;
            border:none;
            border-radius:20px;
            font-size:24px;
            font-weight:bold;
            color:white;
            cursor:pointer;
            background:linear-gradient(
                135deg,
                var(--primary),
                var(--secondary)
            );
        }

        .btn:hover{
            opacity:0.9;
        }

        .question-box{

            background:#eff6ff;
            border-left:6px solid var(--primary);
            padding:20px;
            border-radius:18px;
            line-height:1.8;
            margin-bottom:25px;
            color:#1e293b;
            font-size:18px;
        }

        #step2{
            display:none;
        }

        #aiBall{

            position:fixed;
            right:20px;
            bottom:20px;

            width:65px;
            height:65px;

            border-radius:50%;
            background:#334155;

            display:flex;
            justify-content:center;
            align-items:center;

            color:white;
            font-size:30px;

            cursor:pointer;

            box-shadow:0 5px 15px rgba(0,0,0,0.3);
        }

        #aiMenu{

            position:fixed;
            right:20px;
            bottom:95px;

            width:220px;

            background:white;
            border-radius:20px;

            padding:15px;

            display:none;

            box-shadow:0 5px 20px rgba(0,0,0,0.2);
        }

        .ai-link{

            display:block;

            text-decoration:none;
            color:white;

            padding:14px;
            margin-bottom:10px;

            border-radius:14px;
            text-align:center;

            font-weight:bold;
        }

        .gpt{
            background:#10a37f;
        }

        .gemini{
            background:#4285f4;
        }

    </style>

</head>

<body>

<div class="container">

    <div class="card" id="step1">

        <h1>🦷 {{TITLE}}</h1>

        <label class="label">
            請輸入您的姓名
        </label>

        <input
            type="text"
            id="uName"
            placeholder="例如：王小明"
        >

        <label class="label">
            組別選擇
        </label>

        <select id="uGroup">

            <option value="">
                -- 請選擇您的討論組別 --
            </option>

            {{OPTIONS}}

        </select>

        <button
            class="btn"
            onclick="toStep2()"
        >
            開始討論
        </button>

    </div>

    <div class="card" id="step2">

        <h1 id="groupTitle"></h1>

        <div
            id="questionText"
            class="question-box"
        ></div>

        <textarea
            id="answer"
            rows="6"
            placeholder="請輸入討論內容..."
        ></textarea>

        <button
            class="btn"
            onclick="submitData()"
        >
            確認送出
        </button>

    </div>

</div>

<div id="aiBall" onclick="toggleAI()">
✨
</div>

<div id="aiMenu">

    <a
        href="https://chat.openai.com"
        target="_blank"
        class="ai-link gpt"
    >
        ChatGPT
    </a>

    <a
        href="https://gemini.google.com"
        target="_blank"
        class="ai-link gemini"
    >
        Gemini
    </a>

</div>

<script>

const qs = {{QUESTIONS_JSON}};

function toggleAI(){

    const menu = document.getElementById("aiMenu");

    if(menu.style.display === "block"){
        menu.style.display = "none";
    }else{
        menu.style.display = "block";
    }
}

function toStep2(){

    const name =
        document.getElementById("uName").value.trim();

    const group =
        document.getElementById("uGroup").value;

    if(!name || !group){

        alert("請填寫姓名與組別");

        return;
    }

    document.getElementById("step1").style.display = "none";

    document.getElementById("step2").style.display = "block";

    document.getElementById("groupTitle").innerText = group;

    document.getElementById("questionText").innerText = qs[group];
}

async function submitData(){

    const name =
        document.getElementById("uName").value.trim();

    const group =
        document.getElementById("uGroup").value;

    const answer =
        document.getElementById("answer").value.trim();

    if(answer.length === 0){

        alert("請輸入內容");

        return;
    }

    const formData = new URLSearchParams();

    formData.append("name", name);
    formData.append("group", group);
    formData.append("answer", answer);

    const res = await fetch("/submit",{
        method:"POST",
        body:formData
    });

    if(res.ok){

        alert("提交成功");

        location.reload();

    }else{

        alert("提交失敗");
    }
}

</script>

</body>
</html>
"""

# =========================
# 大螢幕展示頁
# =========================

SCREEN_PAGE = """
<!DOCTYPE html>
<html lang="zh-TW">

<head>

<meta charset="UTF-8">

<title>討論展示牆</title>

<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>

<style>

body{

    margin:0;
    padding:40px;

    background:#0f172a;
    color:white;

    font-family:"Microsoft JhengHei";
}

.header{

    display:flex;
    justify-content:space-between;
    align-items:center;

    margin-bottom:30px;
}

.main-title{

    font-size:55px;
    color:#93c5fd;
    font-weight:bold;
}

.qr-card{

    background:white;
    padding:15px;
    border-radius:20px;

    display:flex;
    align-items:center;
}

.qr-text{

    color:black;
    margin-left:15px;
    font-weight:bold;
    line-height:1.6;
}

.grid{

    display:grid;

    grid-template-columns:1fr 1fr;

    gap:25px;
}

.group-card{

    background:rgba(255,255,255,0.05);

    border-radius:30px;

    padding:25px;
}

.group-name{

    color:#fb7185;

    font-size:35px;
    font-weight:bold;

    margin-bottom:15px;
}

.question{

    background:rgba(255,255,255,0.08);

    padding:18px;

    border-radius:18px;

    line-height:1.7;

    margin-bottom:20px;
}

.entry{

    background:rgba(255,255,255,0.08);

    padding:15px;

    border-radius:15px;

    margin-bottom:12px;
}

.entry-name{

    color:#38bdf8;
    font-weight:bold;

    margin-bottom:8px;
}

</style>

</head>

<body>

<div class="header">

    <div class="main-title">
        🦷 {{TITLE}} 討論展示
    </div>

    <div class="qr-card">

        <div id="qrcode"></div>

        <div class="qr-text">
            手機掃描<br>
            加入討論
        </div>

    </div>

</div>

<div id="board" class="grid"></div>

<script>

const BASE_URL = window.location.origin;

new QRCode(document.getElementById("qrcode"),{

    text:BASE_URL,
    width:120,
    height:120
});

const qs = {{QUESTIONS_JSON}};

async function updateBoard(){

    const res = await fetch("/get_data");

    const data = await res.json();

    let html = "";

    ["第二組","第三組","第四組","第五組"].forEach(group=>{

        const entries =
            data.filter(d=>d.group===group);

        html += `

        <div class="group-card">

            <div class="group-name">
                ${group}
            </div>

            <div class="question">
                ${qs[group]}
            </div>

            ${
                entries.length > 0

                ?

                entries.map(e=>`

                    <div class="entry">

                        <div class="entry-name">
                            ${e.name}
                        </div>

                        <div>
                            ${e.answer}
                        </div>

                    </div>

                `).join("")

                :

                "<div>等待資料更新...</div>"
            }

        </div>
        `;
    });

    document.getElementById("board").innerHTML = html;
}

setInterval(updateBoard,3000);

updateBoard();

</script>

</body>
</html>
"""

# =========================
# API
# =========================

@app.get("/", response_class=HTMLResponse)
async def home():

    options = "".join([
        f'<option value="{g}">{g}</option>'
        for g in QUESTIONS.keys()
    ])

    return STUDENT_PAGE \
        .replace("{{TITLE}}", ACTIVITY_NAME) \
        .replace("{{OPTIONS}}", options) \
        .replace(
            "{{QUESTIONS_JSON}}",
            json.dumps(QUESTIONS, ensure_ascii=False)
        )

# =========================

@app.get("/screen", response_class=HTMLResponse)
async def screen():

    return SCREEN_PAGE \
        .replace("{{TITLE}}", ACTIVITY_NAME) \
        .replace(
            "{{QUESTIONS_JSON}}",
            json.dumps(QUESTIONS, ensure_ascii=False)
        )

# =========================

@app.get("/get_data")
async def get_data():

    return responses

# =========================

@app.post("/submit")
async def submit(

    name:str = Form(...),
    group:str = Form(...),
    answer:str = Form(...)
):

    existing = next(

        (
            i for i in responses
            if i["name"] == name
            and i["group"] == group
        ),

        None
    )

    if existing:

        existing["answer"] = answer

    else:

        responses.append({

            "name":name,
            "group":group,
            "answer":answer
        })

    return {"status":"ok"}

# =========================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    uvicorn.run(

        app,
        host="0.0.0.0",
        port=port
    )