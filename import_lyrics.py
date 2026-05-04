#!/usr/bin/env python3
"""批量导入歌词文件到 MySQL 数据库。用法: python3 import_lyrics.py /path/to/lrc/folder"""
import os, sys, pymysql

DB = {
    'host': '192.168.3.46', 'port': 3306,
    'user': 'song', 'password': 'ZPkj64YBaS7WfHzc',
    'database': 'song', 'charset': 'utf8mb4'
}

def import_folder(folder_path):
    conn = pymysql.connect(**DB)
    cur = conn.cursor()
    ok = dup = err = 0
    for fname in sorted(os.listdir(folder_path)):
        if not fname.endswith(('.lrc', '.txt')):
            continue
        fpath = os.path.join(folder_path, fname)
        name = fname[:-4] if fname.endswith('.lrc') else fname[:-4]
        parts = name.split(' - ', 1)
        artist, title = (parts[0].strip(), parts[1].strip()) if len(parts) == 2 else ('Unknown', name.strip())
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        if not content.strip():
            print(f'SKIP (empty): {fname}')
            continue
        try:
            cur.execute('INSERT INTO lyrics (title, artist, lyrics) VALUES (%s, %s, %s)', (title, artist, content))
            conn.commit()
            ok += 1
        except pymysql.err.IntegrityError:
            dup += 1
        except Exception as e:
            err += 1
    conn.close()
    print(f'Done: OK={ok} DUP={dup} ERR={err}')

if __name__ == '__main__':
    folder = sys.argv[1] if len(sys.argv) > 1 else '.'
    import_folder(folder)
