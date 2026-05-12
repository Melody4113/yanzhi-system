import os
import json
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# =====================================
# 活動名稱
# =====================================

ACTIVITY_NAME = "顏值從齒開始"

# =====================================
# 題目
# =====================================

QUESTIONS = {
    "第二組": "2. 你最近刷牙時牙齦會流血但不會痛，這可能是牙齦發炎嗎？請說明可能原因，並提出改善方法或是否需要就醫。",

    "第三組": "3. 智齒橫著長（水平智齒）但目前沒有疼痛或發炎，你會選擇拔除嗎？請說明你的判斷理由。",

    "第四組": "4. 每天都有刷牙但仍有口臭，朋友也有提醒。你認為可能原因是什麼？應該如何改善？",

    "第五組": "5. 常喝咖啡導致牙齒偏黃，想進行冷光美白。是否每個人都適合？有哪些注意事項？"
}

responses = []

# =====================================
# 學生頁面
# =====================================

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
}

body{

    margin:0;
    padding:20px;

    background:#f1f5f9;

    font-family:-apple-system,"Microsoft JhengHei",sans-serif;
}

.container{

    max-width:500px;
    margin:auto;
}

.card{

    background:white;

    border-radius:28px;

    padding:30px;

    box-shadow:0 10px 30px rgba(0,0,0,0.08);
}

h1{

    text-align:center;
    color:var(--primary);

    margin-bottom:35px;
}

.label{

    display:block;

    margin-bottom:12px;

    font-size:18px;
    font-weight:bold;

    color:#64748b;
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

.question-box{

    background:#eff6ff;

    border-left:6px solid var(--primary);

    padding:20px;

    border-radius:18px;

    line-height:1.8;

    margin-bottom:25px;

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

    background:#0f172a;

    display:flex;
    justify-content:center;
    align-items:center;

    color:white;

    font-size:30px;

    cursor:pointer;

    box-shadow:0 8px 20px rgba(0,0,0,0.3);
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

    box-shadow:0 8px 25px rgba(0,0,0,0.2);
}

.ai-link{

    display:block;

    text-decoration:none;

    color:white;

    padding:14px;

    border-radius:14px;

    margin-bottom:10px;

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

    const menu =
        document.getElementById("aiMenu");

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

    formData.append("name",name);
    formData.append("group",group);
    formData.append("answer",answer);

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

# =====================================
# 大螢幕頁面
# =====================================

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
    padding:30px;

    background:#071029;

    color:white;

    font-family:"Microsoft JhengHei";

    overflow:hidden;
}

.header{

    display:flex;
    justify-content:space-between;
    align-items:flex-start;

    margin-bottom:30px;
}

.title-wrap{

    display:flex;
    align-items:center;
}

.tooth{

    font-size:80px;

    margin-right:18px;

    filter:drop-shadow(0 0 18px rgba(255,255,255,0.8));
}

.main-title{

    font-size:72px;
    font-weight:900;

    color:#c9e2ff;

    text-shadow:
        0 0 15px rgba(173,216,255,0.8),
        0 0 30px rgba(173,216,255,0.4);

    letter-spacing:3px;
}

.qr-card{

    background:white;

    border-radius:28px;

    padding:18px;

    display:flex;
    align-items:center;

    box-shadow:0 0 25px rgba(255,255,255,0.2);
}

.qr-text{

    color:black;

    margin-left:15px;

    font-size:24px;
    font-weight:bold;

    line-height:1.8;
}

.grid{

    display:grid;

    grid-template-columns:1fr 1fr;

    gap:28px;
}

.group-card{

    background:rgba(255,255,255,0.06);

    border-radius:35px;

    padding:28px;

    min-height:310px;

    backdrop-filter:blur(10px);
}

.group-name{

    font-size:58px;
    font-weight:900;

    color:#ff8ea0;

    margin-bottom:20px;
}

.question{

    background:rgba(255,255,255,0.08);

    padding:22px;

    border-radius:24px;

    line-height:1.8;

    font-size:28px;

    margin-bottom:22px;
}

.entry{

    background:rgba(255,255,255,0.08);

    padding:20px;

    border-radius:22px;

    margin-bottom:15px;
}

.entry-name{

    color:#67c1ff;

    font-size:30px;
    font-weight:bold;

    margin-bottom:10px;
}

.entry-content{

    font-size:30px;

    line-height:1.8;

    word-break:break-word;
}

.wait{

    font-size:30px;

    color:#dbeafe;

    margin-top:20px;
}

</style>

</head>

<body>

<div class="header">

    <div class="title-wrap">

        <div class="tooth">
            🦷
        </div>

        <div class="main-title">
            {{TITLE}} 討論展示
        </div>

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

    width:150,
    height:150
});

const qs = {{QUESTIONS_JSON}};

async function updateBoard(){

    const res =
        await fetch("/get_data");

    const data =
        await res.json();

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

                        <div class="entry-content">
                            ${e.answer}
                        </div>

                    </div>

                `).join("")

                :

                `<div class="wait">
                    等待資料更新...
                </div>`
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

# =====================================
# API
# =====================================

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
            json.dumps(
                QUESTIONS,
                ensure_ascii=False
            )
        )

# =====================================

@app.get("/screen", response_class=HTMLResponse)
async def screen():

    return SCREEN_PAGE \
        .replace("{{TITLE}}", ACTIVITY_NAME) \
        .replace(
            "{{QUESTIONS_JSON}}",
            json.dumps(
                QUESTIONS,
                ensure_ascii=False
            )
        )

# =====================================

@app.get("/get_data")
async def get_data():

    return responses

# =====================================

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

# =====================================

if __name__ == "__main__":

    port =
        int(os.environ.get("PORT",10000))

    uvicorn.run(

        app,
        host="0.0.0.0",
        port=port
    )