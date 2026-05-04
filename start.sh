#!/bin/bash
cd /home/ytt/music/api
echo "=== Lyrics API (port 4091) ==="
source /home/ytt/music/venv/bin/activate
python3 lyrics_api.py &
sleep 1
echo "=== Lyrics Manager (port 4092) ==="
python3 lyrics_manager.py &
sleep 1
echo ""
echo "API:     http://0.0.0.0:4091/lyrics"
echo "Manager: http://0.0.0.0:4092"
echo ""
wait
