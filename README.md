# API 的使用方式
# 🎵 歌词 API —— 音流 (Stream Music) 自定义歌词服务

## ✨ 功能一览

| 模块 | 端口 | 说明 |
|------|------|------|
| 歌词 API | 4091 | 对接音流 APP，返回 LRC 歌词 |
| 歌词管理器 | 4092 | Web 管理界面，支持增删查 |
| 批量导入 | CLI | 一键导入整个文件夹的 .lrc / .txt |

- 完全兼容音流自定义 API 规范
- LRC 时间轴歌词支持
- MySQL 存储，模糊搜索
- WebUI 拖拽上传
- systemd 自启动，waitress 生产服务器

---

## 📦 环境要求

- Python 3.10 以上
- MySQL 8.x
- pip

---

## 🚀 快速开始

### 1. 克隆项目

git clone https://github.com/yourname/lyrics-api.git
cd lyrics-api/api

### 2. 安装依赖

pip install -r requirements.txt

### 3. 创建数据库

CREATE DATABASE IF NOT EXISTS song CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

程序首次运行会自动创建 lyrics 表。

### 4. 修改数据库配置

编辑 lyrics_api.py 和 lyrics_manager.py 中的 DB_CONFIG 字典，
填入你的 MySQL 地址、用户名和密码。

### 5. 批量导入已有歌词

python3 import_lyrics.py /你的歌词文件夹路径

文件名格式要求：歌手 - 歌名.lrc 或 歌手 - 歌名.txt

### 6. 启动服务

bash start.sh          # 同时启动 API + 管理器

# 或分别启动：
python3 lyrics_api.py      # 歌词 API → 端口 4091
python3 lyrics_manager.py  # 管理器   → 端口 4092


---

## API

### GET /lyrics - fetch lyrics as raw LRC text

Params: title, artist, album, path, duration, offset, limit

Example: curl "http://HOST:4091/lyrics?title=LYRICS_TITLE"

Returns plain text LRC content. HTTP 404 if not found.

### GET /jsonapi - fetch lyrics as JSON list (v1.1.6 format)

Same params as /lyrics. Returns JSON array with id, title, artist, lyrics fields.

### POST /lyrics/confirm - save confirmed lyrics (v1.2.0 format)

JSON body: path, title, artist, album, lyrics, lyricsId

### GET /ping - health check, returns pong

---

## Stream Music App Config

Set custom lyrics API URL to: http://SERVER_IP:4091/lyrics

Set confirm lyrics URL to: http://SERVER_IP:4091/lyrics/confirm

---

## Web Manager (port 4092)

Open http://SERVER_IP:4092 in browser.

Features:
- Browse all lyrics with pagination (20 per page)
- Search by title or artist
- Upload .lrc / .txt files via drag and drop
- View full lyrics in modal popup
- Delete lyrics from database

---

## Deploy as System Service

sudo systemctl enable --now lyrics-api.service
sudo systemctl enable --now lyrics-manager.service

---

## Project Structure

api/
  lyrics_api.py        Lyrics API (port 4091)
  lyrics_manager.py    Web Manager (port 4092)
  import_lyrics.py     Bulk import script
  requirements.txt     Python dependencies
  start.sh            Quick start script
  README.md           English docs
  README_CN.md        Chinese docs (this file)
  docs/
    API.md            Detailed API reference

---

## License

MIT License

## Credits

- Stream Music (音流): https://github.com/gitbobobo/StreamMusic
- LrcApi: https://github.com/HisAtri/LrcApi

