from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Virat Page Token Fetcher & Checker</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
body { font-family: 'Poppins', sans-serif; margin:0; padding:0; background: linear-gradient(135deg,#e0f7fa,#ede7f6); color:#333; text-align:center; }
h1 { background: linear-gradient(to right,#4f46e5,#9333ea); color:#fff; padding:15px; margin:0; font-size:22px; border-radius:0 0 15px 15px; box-shadow:0 3px 10px rgba(0,0,0,0.2);}
form { background:#fff; margin:20px auto; padding:20px; border-radius:12px; width:90%; max-width:500px; box-shadow:0 4px 12px rgba(0,0,0,0.1);}
textarea { width:100%; padding:10px; border-radius:8px; border:1px solid #ccc; font-family: monospace; resize:none; }
button { margin-top:10px; padding:10px 20px; border-radius:8px; border:none; font-weight:bold; cursor:pointer; background:#4f46e5; color:#fff; transition:0.3s;}
button:hover { background:#4338ca; }
.table-container { width:95%; margin:20px auto;}
.page-card { background:#fff; border-radius:12px; padding:15px; margin-bottom:20px; box-shadow:0 4px 12px rgba(0,0,0,0.1); word-break: break-word; transition:0.3s;}
.page-card:hover { box-shadow:0 6px 18px rgba(0,0,0,0.2);}
.page-card div { margin:5px 0;}
.token-box { background:#f3f4f6; padding:6px 8px; border-radius:6px; font-size:12px; white-space:pre-wrap; word-break:break-word;}
.copy-btn, .check-btn { background:#22c55e; color:#fff; border:none; padding:6px 10px; border-radius:6px; cursor:pointer; font-size:12px; transition:0.3s;}
.copy-btn:hover, .check-btn:hover { background:#16a34a; }
.toast { visibility:hidden; min-width:200px; background-color:#333; color:#fff; text-align:center; border-radius:6px; padding:10px; position:fixed; z-index:1; bottom:30px; left:50%; transform:translateX(-50%); font-size:14px; opacity:0; transition:opacity 0.5s, visibility 0.5s;}
.toast.show { visibility:visible; opacity:1;}
footer { margin-top:30px; background:#fff; padding:15px; border-top:2px solid #ddd; box-shadow:0 -2px 8px rgba(0,0,0,0.1);}
.contact { font-weight:600; margin-bottom:10px;}
.icons a { margin:0 10px; font-size:24px; color:#4f46e5; text-decoration:none;}
.icons a:hover { color:#9333ea; transform:scale(1.1);}
@media(max-width:600px){ h1{font-size:18px;} .token-box{font-size:10px;} button{width:100%; margin-top:5px;} }
</style>
</head>
<body>

<h1>🏏 Virat Page Token Fetcher & Checker</h1>

<!-- Fetch Pages Form -->
<form method="POST" action="/fetch">
<label><strong>Enter Facebook User Access Token:</strong></label><br><br>
<textarea name="token" placeholder="Paste your token here..."></textarea><br>
<button type="submit">Fetch Page Tokens</button>
</form>

{% if error %}<h3 style="color:red;">Error: {{ error }}</h3>{% endif %}

{% if pages %}
<div class="table-container">
{% for p in pages %}
<div class="page-card">
    <div style="color:#4f46e5;"><b>Page Name:</b> {{ p.name }}</div>
    <div style="color:#9333ea;"><b>Page ID:</b> {{ p.id }}</div>
    <div class="token-box" id="token{{ loop.index }}"><b>Access Token:</b> {{ p.access_token }}</div>
    <button class="copy-btn" onclick="copyToken('token{{ loop.index }}')">Copy Token</button>
    <button class="check-btn" onclick="checkToken('{{ p.access_token }}', {{ loop.index }})">Check Token</button>
    <div id="status{{ loop.index }}" style="margin-top:5px;font-weight:bold;"></div>
</div>
{% endfor %}
</div>
{% endif %}

<!-- Manual Token Checker -->
<div style="background:#fff; margin:20px auto; padding:20px; border-radius:12px; width:90%; max-width:500px; box-shadow:0 4px 12px rgba(0,0,0,0.1);">
<h3>Manual Token Checker</h3>
<textarea id="manualToken" placeholder="Paste token to check"></textarea><br>
<button onclick="manualCheck()">Check Token</button>
<div id="manualStatus" style="margin-top:5px;font-weight:bold;"></div>
</div>

<div id="toast" class="toast">Token copied successfully!</div>

<footer>
<div class="contact">📞 Contact for Post Tool / Convo etc</div>
<div class="icons">
<a href="https://www.facebook.com/profile.php?id=100092380041881" target="_blank"><i class="fab fa-facebook"></i></a>
<a href="https://wa.me/6352569270" target="_blank"><i class="fab fa-whatsapp"></i></a>
</div>
</footer>

<script>
function copyToken(id){
    var tokenText = document.getElementById(id).innerText;
    navigator.clipboard.writeText(tokenText).then(function(){
        showToast("✅ Token copied!");
    });
}

function showToast(message){
    var toast = document.getElementById("toast");
    toast.innerText = message;
    toast.className = "toast show";
    setTimeout(function(){ toast.className = toast.className.replace("show",""); }, 2500);
}

function checkToken(token, index){
    var statusDiv = document.getElementById("status"+index);
    statusDiv.innerHTML = "Checking...";
    fetch("/check_token", {
        method: "POST",
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({token: token})
    })
    .then(response => response.json())
    .then(data => {
        if(data.valid){
            statusDiv.innerHTML = "✅ Token is live!";
            statusDiv.style.color = "green";
            statusDiv.innerHTML += "<br>ID: "+data.id+"<br>Name: "+data.name+"<br>Token: "+token;
        }else{
            statusDiv.innerHTML = "❌ Token is expired or invalid!";
            statusDiv.style.color = "red";
        }
    })
    .catch(err => {
        statusDiv.innerHTML = "❌ Error checking token";
        statusDiv.style.color = "red";
    });
}

function manualCheck(){
    var token = document.getElementById("manualToken").value.trim();
    var statusDiv = document.getElementById("manualStatus");
    if(!token){ statusDiv.innerHTML="❌ Enter a token"; statusDiv.style.color="red"; return; }
    statusDiv.innerHTML="Checking...";
    fetch("/check_token", {
        method:"POST",
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({token: token})
    })
    .then(res => res.json())
    .then(data => {
        if(data.valid){
            statusDiv.innerHTML = "✅ Token is live!";
            statusDiv.style.color = "green";
            statusDiv.innerHTML += "<br>ID: "+data.id+"<br>Name: "+data.name+"<br>Token: "+token;
        }else{
            statusDiv.innerHTML = "❌ Token is expired or invalid!";
            statusDiv.style.color = "red";
        }
    })
    .catch(err => {
        statusDiv.innerHTML="❌ Error checking token"; statusDiv.style.color="red";
    });
}
</script>

</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/fetch", methods=["POST"])
def fetch_pages():
    token = request.form.get("token","").strip()
    if not token:
        return render_template_string(HTML_TEMPLATE,error="Access Token is required")
    url=f"https://graph.facebook.com/v17.0/me/accounts?access_token={token}"
    try:
        res = requests.get(url).json()
        if "error" in res:
            return render_template_string(HTML_TEMPLATE,error=res["error"]["message"])
        pages = res.get("data",[])
        return render_template_string(HTML_TEMPLATE,pages=pages)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE,error=str(e))

@app.route("/check_token", methods=["POST"])
def check_token():
    data = request.get_json()
    token = data.get("token","").strip()
    if not token:
        return {"valid": False}
    url = f"https://graph.facebook.com/v17.0/me?access_token={token}"
    try:
        res = requests.get(url).json()
        if "error" in res:
            return {"valid": False}
        else:
            return {"valid": True, "id": res.get("id","N/A"), "name": res.get("name","N/A")}
    except:
        return {"valid": False}

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
