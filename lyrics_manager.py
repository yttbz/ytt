import os, pymysql
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

DB = {
    "host": "192.168.3.46", "port": 3306,
    "user": "song", "password": "ZPkj64YBaS7WfHzc",
    "database": "song", "charset": "utf8mb4"
}

def db():
    return pymysql.connect(**DB)

HTML = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>歌词管理器</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#0f0f0f;color:#e0e0e0;min-height:100vh}
.header{background:#1a1a2e;padding:16px 24px;display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #6c63ff}
.header h1{font-size:20px;color:#6c63ff}
.header span{color:#888;font-size:14px}
.container{max-width:1100px;margin:0 auto;padding:24px}
.toolbar{display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap;align-items:center}
.toolbar input[type=text]{flex:1;min-width:200px;padding:10px 16px;background:#1a1a2e;border:1px solid #333;border-radius:8px;color:#e0e0e0;font-size:14px}
.toolbar input[type=text]:focus{outline:none;border-color:#6c63ff}
.btn{padding:10px 20px;border:none;border-radius:8px;font-size:14px;cursor:pointer;font-weight:600;transition:.2s}
.btn-primary{background:#6c63ff;color:#fff}
.btn-primary:hover{background:#5a52e0}
.btn-danger{background:#e74c3c;color:#fff}
.btn-danger:hover{background:#c0392b}
.btn-outline{background:transparent;border:1px solid #444;color:#ccc}
.btn-outline:hover{border-color:#6c63ff;color:#fff}
.btn-sm{padding:6px 12px;font-size:12px}
table{width:100%;border-collapse:collapse;background:#1a1a2e;border-radius:12px;overflow:hidden}
th{text-align:left;padding:12px 16px;background:#16162a;color:#888;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.5px}
td{padding:12px 16px;border-bottom:1px solid #222;font-size:14px}
tr:hover td{background:#1f1f3a}
.lyrics-preview{max-width:300px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#888;font-size:12px;font-family:monospace}
.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);z-index:1000;justify-content:center;align-items:center}
.modal.active{display:flex}
.modal-content{background:#1a1a2e;border-radius:12px;padding:24px;max-width:600px;width:90%;max-height:80vh;overflow-y:auto;border:1px solid #333}
.modal-content h2{margin-bottom:16px;color:#6c63ff}
.modal-content pre{background:#0d0d1a;padding:16px;border-radius:8px;overflow-x:auto;font-size:12px;max-height:50vh;overflow-y:auto;white-space:pre-wrap;word-break:break-all;color:#b0b0b0}
.upload-zone{border:2px dashed #333;border-radius:12px;padding:32px;text-align:center;margin-bottom:20px;transition:.2s;cursor:pointer}
.upload-zone:hover,.upload-zone.dragover{border-color:#6c63ff;background:#1a1a3e}
.upload-zone p{color:#888;margin-top:8px}
.upload-zone .icon{font-size:40px}
.file-item{display:flex;justify-content:space-between;align-items:center;padding:8px 12px;background:#0d0d1a;border-radius:6px;margin-bottom:6px;font-size:13px}
.file-item .remove-file{color:#e74c3c;cursor:pointer;font-weight:bold}
.toast{position:fixed;bottom:24px;right:24px;padding:12px 24px;border-radius:8px;font-size:14px;z-index:2000;animation:fadeIn .3s}
.toast-success{background:#27ae60;color:#fff}
.toast-error{background:#e74c3c;color:#fff}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.pagination{display:flex;gap:8px;margin-top:16px;justify-content:center}
.pagination a{padding:8px 14px;background:#1a1a2e;border:1px solid #333;border-radius:6px;color:#ccc;text-decoration:none;font-size:13px}
.pagination a:hover{border-color:#6c63ff}
.pagination .current{background:#6c63ff;border-color:#6c63ff;color:#fff}
.stats{color:#888;font-size:13px;margin-left:auto}
</style>
</head>
<body>
<div class="header">
  <h1>🎵 歌词管理器</h1>
  <span>数据库: song.lyrics | 共 {{ total }} 首</span>
</div>
<div class="container">
  <form class="toolbar" method="get" action="/">
    <input type="text" name="q" placeholder="搜索歌名 / 歌手..." value="{{ query }}">
    <button type="submit" class="btn btn-primary">🔍 搜索</button>
    <a href="/" class="btn btn-outline">↻ 显示全部</a>
    <button type="button" class="btn btn-primary" onclick="showUpload()">📤 上传歌词</button>
    <span class="stats">第 {{ page }} / {{ total_pages }} 页</span>
  </form>
  <table>
    <thead>
      <tr><th>ID</th><th>歌手</th><th>歌名</th><th>歌词预览</th><th>操作</th></tr>
    </thead>
    <tbody>
    {% for row in rows %}
      <tr>
        <td>{{ row.id }}</td>
        <td>{{ row.artist }}</td>
        <td>{{ row.title }}</td>
        <td><div class="lyrics-preview">{{ row.lyrics[:120] }}</div></td>
        <td>
          <button class="btn btn-outline btn-sm" onclick="viewLyrics({{ row.id }})">👁 查看</button>
          <button class="btn btn-danger btn-sm" onclick="deleteLyrics({{ row.id }})">🗑 删除</button>
        </td>
      </tr>
    {% endfor %}
    {% if not rows %}
      <tr><td colspan="5" style="text-align:center;padding:40px;color:#888">暂无歌词数据</td></tr>
    {% endif %}
    </tbody>
  </table>
  <div class="pagination">
    {% if page > 1 %}
      <a href="?q={{ query }}&page={{ page-1 }}">‹ 上一页</a>
    {% endif %}
    {% for p in page_range %}
      <a href="?q={{ query }}&page={{ p }}" class="{{ 'current' if p == page else '' }}">{{ p }}</a>
    {% endfor %}
    {% if page < total_pages %}
      <a href="?q={{ query }}&page={{ page+1 }}">下一页 ›</a>
    {% endif %}
  </div>
</div>
<div class="modal" id="viewModal">
  <div class="modal-content">
    <h2 id="viewTitle"></h2>
    <pre id="viewLyrics"></pre>
    <button class="btn btn-outline" onclick="closeModal('viewModal')" style="margin-top:12px">关闭</button>
  </div>
</div>
<div class="modal" id="uploadModal">
  <div class="modal-content">
    <h2>📤 上传歌词文件</h2>
    <p style="color:#888;margin-bottom:16px">支持 .lrc / .txt，文件名格式: <b>歌手 - 歌名.lrc</b></p>
    <form id="uploadForm" enctype="multipart/form-data">
      <div class="upload-zone" id="dropZone">
        <div class="icon">📁</div>
        <p>点击选择文件 或 拖拽到此处</p>
        <input type="file" id="fileInput" name="files" multiple accept=".lrc,.txt" style="display:none">
      </div>
      <div id="file-list"></div>
      <div style="display:flex;gap:8px;margin-top:16px">
        <button type="submit" class="btn btn-primary">上传到数据库</button>
        <button type="button" class="btn btn-outline" onclick="closeModal('uploadModal')">取消</button>
      </div>
    </form>
  </div>
</div>
<script>
var dz = document.getElementById('dropZone');
var fi = document.getElementById('fileInput');
dz.onclick = function(){ fi.click(); };
dz.ondragover = function(e){ e.preventDefault(); dz.classList.add('dragover'); };
dz.ondragleave = function(){ dz.classList.remove('dragover'); };
dz.ondrop = function(e){
  e.preventDefault(); dz.classList.remove('dragover');
  fi.files = e.dataTransfer.files; updateFileList();
};
fi.onchange = updateFileList;

var selectedFiles = [];
function updateFileList(){
  selectedFiles = Array.from(fi.files);
  var list = document.getElementById('file-list');
  list.innerHTML = selectedFiles.map(function(f,i){
    return '<div class="file-item"><span>📄 '+f.name+' ('+(f.size/1024).toFixed(1)+' KB)</span><span class="remove-file" onclick="removeFile('+i+')">✕</span></div>';
  }).join('');
}

function removeFile(i){ selectedFiles.splice(i,1); updateFileList(); }

document.getElementById('uploadForm').onsubmit = async function(e){
  e.preventDefault();
  if(!selectedFiles.length) return toast('请选择文件', 'error');
  var fd = new FormData();
  selectedFiles.forEach(function(f){ fd.append('files', f); });
  var res = await fetch('/upload', {method:'POST', body:fd});
  var data = await res.json();
  toast(data.message, data.status);
  if(data.status==='success') setTimeout(function(){ location.reload(); }, 800);
};

function showUpload(){ document.getElementById('uploadModal').classList.add('active'); }
function closeModal(id){ document.getElementById(id).classList.remove('active'); }

async function viewLyrics(id){
  var res = await fetch('/get/'+id);
  var data = await res.json();
  document.getElementById('viewTitle').textContent = data.artist + ' - ' + data.title;
  document.getElementById('viewLyrics').textContent = data.lyrics;
  document.getElementById('viewModal').classList.add('active');
}

async function deleteLyrics(id){
  if(!confirm('确定删除这条歌词吗？')) return;
  var res = await fetch('/delete/'+id, {method:'POST'});
  var data = await res.json();
  toast(data.message, data.status);
  if(data.status==='success') location.reload();
}

function toast(msg, type){
  var t = document.createElement('div');
  t.className = 'toast toast-'+(type==='success'?'success':'error');
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(function(){ t.remove(); }, 2500);
}
</script>
</body>
</html>"""

@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 20

    conn = db()
    cur = conn.cursor(pymysql.cursors.DictCursor)

    if q:
        cur.execute(
            "SELECT COUNT(*) as cnt FROM lyrics WHERE title LIKE %s OR artist LIKE %s",
            (f"%{q}%", f"%{q}%")
        )
    else:
        cur.execute("SELECT COUNT(*) as cnt FROM lyrics")
    total = cur.fetchone()["cnt"]

    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    offset = (page - 1) * per_page

    if q:
        cur.execute(
            "SELECT id, title, artist, lyrics FROM lyrics WHERE title LIKE %s OR artist LIKE %s ORDER BY id DESC LIMIT %s OFFSET %s",
            (f"%{q}%", f"%{q}%", per_page, offset)
        )
    else:
        cur.execute(
            "SELECT id, title, artist, lyrics FROM lyrics ORDER BY id DESC LIMIT %s OFFSET %s",
            (per_page, offset)
        )
    rows = cur.fetchall()
    conn.close()

    start = max(1, page - 3)
    end = min(total_pages, page + 3)
    page_range = list(range(start, end + 1))

    return render_template_string(HTML, rows=rows, total=total, page=page,
                                   total_pages=total_pages, query=q, page_range=page_range)


@app.route("/get/<int:lid>")
def get_lyrics(lid):
    conn = db()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("SELECT id, title, artist, lyrics FROM lyrics WHERE id=%s", (lid,))
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify(row)
    return jsonify({"error": "Not found"}), 404


@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")
    if not files:
        return jsonify({"status": "error", "message": "未选择文件"})

    conn = db()
    cur = conn.cursor()
    ok = dup = err = 0

    for f in files:
        fname = f.filename
        if not fname.endswith((".lrc", ".txt")):
            err += 1
            continue

        name = fname[:-4] if fname.endswith(".lrc") else fname[:-4]
        parts = name.split(" - ", 1)
        if len(parts) == 2:
            artist, title = parts[0].strip(), parts[1].strip()
        else:
            artist, title = "Unknown", name.strip()

        try:
            content = f.read().decode("utf-8")
        except:
            try:
                f.seek(0)
                content = f.read().decode("gbk")
            except:
                err += 1
                continue

        if not content.strip():
            err += 1
            continue

        try:
            cur.execute(
                "INSERT INTO lyrics (title, artist, lyrics) VALUES (%s, %s, %s)",
                (title, artist, content)
            )
            conn.commit()
            ok += 1
        except pymysql.err.IntegrityError:
            dup += 1
        except Exception as e:
            err += 1

    conn.close()

    msg = f"成功 {ok} 首"
    if dup: msg += f"，重复跳过 {dup} 首"
    if err: msg += f"，失败 {err} 首"
    return jsonify({"status": "success", "message": msg})


@app.route("/delete/<int:lid>", methods=["POST"])
def delete_lyrics(lid):
    conn = db()
    cur = conn.cursor()
    cur.execute("DELETE FROM lyrics WHERE id=%s", (lid,))
    conn.commit()
    affected = cur.rowcount
    conn.close()
    if affected:
        return jsonify({"status": "success", "message": "已删除"})
    return jsonify({"status": "error", "message": "未找到"}), 404


if __name__ == "__main__":
    from waitress import serve
    print("歌词管理器运行在 http://0.0.0.0:4092")
    serve(app, host="0.0.0.0", port=4092, threads=4)
