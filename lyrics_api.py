#!/usr/bin/env python3
"""Lyrics API for Stream Music (音流) — compatible with LrcApi format."""

import json
import os
import logging
import traceback
from flask import Flask, request, jsonify, Response
import pymysql

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

DB_CONFIG = {
    'host': '192.168.3.46',
    'port': 3306,
    'user': 'song',
    'password': 'ZPkj64YBaS7WfHzc',
    'database': 'song',
    'charset': 'utf8mb4'
}

MUSIC_DIR = '/home/ytt/music/gc'

def get_db():
    return pymysql.connect(**DB_CONFIG)


@app.before_request
def log_request():
    logger.info(f'{request.method} {request.path} ? {request.query_string.decode() if request.query_string else ""}')


@app.errorhandler(Exception)
def handle_error(e):
    logger.error(f'ERROR: {traceback.format_exc()}')
    return str(e), 500


def search_lyrics(title='', artist='', album='', path=''):
    """Search lyrics, returns (lyrics_text, title, artist) or (None, None, None)"""
    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    conditions = []
    params = []

    # 1. 优先按文件路径查找同名 lrc
    if path:
        basename = os.path.splitext(os.path.basename(path))[0]
        if ' - ' in basename:
            parts = basename.split(' - ', 1)
            conditions.append('(artist LIKE %s AND title LIKE %s)')
            params.extend([f'%{parts[0].strip()}%', f'%{parts[1].strip()}%'])
        else:
            conditions.append('(title LIKE %s OR artist LIKE %s)')
            params.extend([f'%{basename}%', f'%{basename}%'])

    if title:
        conditions.append('(title = %s OR title LIKE %s)')
        params.extend([title, f'%{title}%'])

    if artist:
        conditions.append('(artist = %s OR artist LIKE %s)')
        params.extend([artist, f'%{artist}%'])

    if not conditions:
        conn.close()
        return None, None, None

    where = ' OR '.join(conditions)
    query = f'SELECT id, title, artist, lyrics FROM lyrics WHERE {where} LIMIT 1'
    
    cursor.execute(query, params)
    row = cursor.fetchone()
    conn.close()

    if row:
        return row['lyrics'], row['title'], row['artist']
    return None, None, None


# === OLD API: /lyrics — returns raw LRC text (like LrcApi) ===
@app.route('/lyrics', methods=['GET'])
def get_lyrics():
    path = request.args.get('path', '').strip()
    title = request.args.get('title', '').strip()
    artist = request.args.get('artist', '').strip()
    album = request.args.get('album', '').strip()

    logger.info(f'  title="{title}" artist="{artist}" path="{path}"')

    # Also try local file lookup (like LrcApi)
    if path:
        lrc_path = os.path.splitext(path)[0] + '.lrc'
        if os.path.isfile(lrc_path):
            with open(lrc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f'  -> 200 (local file: {lrc_path})')
            return Response(content, mimetype='text/plain; charset=utf-8')

    lyrics, _, _ = search_lyrics(title=title, artist=artist, album=album, path=path)

    if lyrics is None:
        logger.info('  -> 404')
        return '', 404

    logger.info(f'  -> 200 ({len(lyrics)} chars)')
    return Response(lyrics, mimetype='text/plain; charset=utf-8')


# === NEW API: /jsonapi — returns JSON list (v1.1.6+) ===
@app.route('/jsonapi', methods=['GET'])
def get_lyrics_json():
    path = request.args.get('path', '').strip()
    title = request.args.get('title', '').strip()
    artist = request.args.get('artist', '').strip()
    album = request.args.get('album', '').strip()
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 10, type=int)

    logger.info(f'  title="{title}" artist="{artist}" path="{path}"')

    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    conditions = []
    params = []

    if path:
        basename = os.path.splitext(os.path.basename(path))[0]
        if ' - ' in basename:
            parts = basename.split(' - ', 1)
            conditions.append('(artist LIKE %s AND title LIKE %s)')
            params.extend([f'%{parts[0].strip()}%', f'%{parts[1].strip()}%'])
        else:
            conditions.append('(title LIKE %s OR artist LIKE %s)')
            params.extend([f'%{basename}%', f'%{basename}%'])

    if title:
        conditions.append('(title = %s OR title LIKE %s OR artist LIKE %s)')
        params.extend([title, f'%{title}%', f'%{title}%'])

    if artist:
        conditions.append('(artist = %s OR artist LIKE %s OR title LIKE %s)')
        params.extend([artist, f'%{artist}%', f'%{artist}%'])

    if not conditions:
        conn.close()
        return '', 404

    where = ' OR '.join(conditions)
    query = f'SELECT id, title, artist, lyrics FROM lyrics WHERE {where} LIMIT %s OFFSET %s'
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        logger.info('  -> 404')
        return '', 404

    result = []
    for row in rows:
        result.append({
            'id': str(row['id']),
            'title': row['title'],
            'artist': row['artist'],
            'lyrics': row['lyrics']
        })

    logger.info(f'  -> 200 ({len(result)} results)')
    resp = jsonify(result)
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp


# === POST /lyrics/confirm ===
@app.route('/lyrics/confirm', methods=['POST'])
def confirm_lyrics():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    title = data.get('title', '').strip()
    artist = data.get('artist', '').strip()
    lyrics = data.get('lyrics', '')
    lyrics_id = data.get('lyricsId', '')

    if not title or not artist or not lyrics:
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db()
    cursor = conn.cursor()

    if lyrics_id:
        cursor.execute(
            'UPDATE lyrics SET title=%s, artist=%s, lyrics=%s WHERE id=%s',
            (title, artist, lyrics, lyrics_id)
        )
        if cursor.rowcount == 0:
            cursor.execute(
                'INSERT INTO lyrics (title, artist, lyrics) VALUES (%s, %s, %s)',
                (title, artist, lyrics)
            )
    else:
        cursor.execute(
            'INSERT INTO lyrics (title, artist, lyrics) VALUES (%s, %s, %s) '
            'ON DUPLICATE KEY UPDATE lyrics=VALUES(lyrics)',
            (title, artist, lyrics)
        )

    conn.commit()
    conn.close()
    logger.info('  -> 200 OK')
    return jsonify({'status': 'ok'}), 200


@app.route('/ping', methods=['GET'])
def ping():
    return 'pong', 200


if __name__ == '__main__':
    from waitress import serve
    logger.info('Starting Lyrics API on http://0.0.0.0:4091')
    serve(app, host='0.0.0.0', port=4091, threads=4, channel_timeout=30)
