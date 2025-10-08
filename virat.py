from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Virat Page Token Fetcher</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
body {
    font-family: 'Poppins', sans-serif;
    margin: 0;
    padding: 0;
    background: linear-gradient(135deg,#e0f7fa,#ede7f6);
    color: #333;
    text-align: center;
}
h1 {
    background: linear-gradient(to right,#4f46e5,#9333ea);
    color: #fff;
    padding: 15px;
    margin: 0;
    font-size: 22px;
    border-radius: 0 0 15px 15px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.2);
}
form {
    background: #fff;
    margin: 20px auto;
    padding: 20px;
    border-radius: 12px;
    width: 90%;
    max-width: 500px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
textarea {
    width: 100%;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #ccc;
    font-family: monospace;
    resize: none;
}
button {
    margin-top: 10px;
    padding: 10px 20px;
    border-radius: 8px;
    border: none;
    font-weight: bold;
    cursor: pointer;
    background: #4f46e5;
    color: #fff;
}
button:hover { background: #4338ca; }

.table-container {
    width: 95%;
    margin: 20px auto;
    overflow-x: auto;
}
table {
    width: 100%;
    border-collapse: collapse;
    background: #fff;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
th, td {
    padding: 10px;
    border-bottom: 1px solid #eee;
    font-size: 14px;
    text-align: left;
    vertical-align: middle;
}
th {
    background: linear-gradient(to right,#6366f1,#9333ea);
    color: #fff;
}
tr:nth-child(even) { background: #f9f9ff; }

/* Page Name & ID single line */
.name-id, .copy-cell {
    white-space: nowrap;
    display: inline-block;
    vertical-align: middle;
}

/* Token multi-line wrap */
.token-box {
    display: block;
    background: #f3f4f6;
    padding: 6px 8px;
    border-radius: 6px;
    font-size: 12px;
    width: 100%;
    white-space: pre-wrap; /* preserve line breaks */
    word-wrap: break-word;
}

.copy-btn {
    background: #22c55e;
    color: #fff;
    border: none;
    padding: 6px 10px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 12px;
}
.copy-btn:hover { background: #16a34a; }

footer {
    margin-top: 30px;
    background: #fff;
    padding: 15px;
    border-top: 2px solid #ddd;
    box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
}
.contact { font-weight: 600; margin-bottom: 10px; }
.icons a {
    margin: 0 10px;
    font-size: 24px;
    color: #4f46e5;
    text-decoration: none;
}
.icons a:hover { color: #9333ea; transform: scale(1.1); }

@media(max-width:600px){
    h1 { font-size: 18px; }
    table, th, td { font-size: 12px; }
    .token-box { font-size: 10px; }
    button { width: 100%; margin-top: 5px; }
}
</style>
</head>
<body>

<h1>🏏 Virat Page Token Fetcher</h1>

<form method="POST" action="/fetch">
<label><strong>Enter Facebook User Access Token:</strong></label><br><br>
<textarea name="token" placeholder="Paste your token here..."></textarea><br>
<button type="submit">Fetch Page Tokens</button>
</form>

{% if error %}
<h3 style="color:red;">Error: {{ error }}</h3>
{% endif %}

{% if pages %}
<div class="table-container">
<table>
<tr>
<th>#</th>
<th>Page Name</th>
<th>Page ID</th>
<th>Access Token</th>
<th>Copy</th>
</tr>
{% for p in pages %}
<tr>
<td>{{ loop.index }}</td>
<td class="name-id" style="color:#4f46e5;"><b>{{ p.name }}</b></td>
<td class="name-id" style="color:#9333ea;">{{ p.id }}</td>
<td><div class="token-box" id="token{{ loop.index }}">{{ p.access_token }}</div></td>
<td class="copy-cell"><button class="copy-btn" onclick="copyToken('token{{ loop.index }}')">Copy</button></td>
</tr>
{% endfor %}
</table>
</div>
{% endif %}

<footer>
<div class="contact">📞 Contact for Post Tool / Convo etc</div>
<div class="icons">
<a href="https://www.facebook.com/profile.php?id=100092380041881" target="_blank"><i class="fab fa-facebook"></i></a>
<a href="https://wa.me/6352569270" target="_blank"><i class="fab fa-whatsapp"></i></a>
</div>
</footer>

<script>
function copyToken(id){
    var text = document.getElementById(id).innerText;
    navigator.clipboard.writeText(text);
    alert("✅ Token copied!");
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

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
