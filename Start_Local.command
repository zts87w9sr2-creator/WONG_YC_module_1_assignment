#!/bin/bash
cd -- "$(dirname -- "$0")" || exit 1
preview_python="$(command -v python3 2>/dev/null)"
if [ -z "$preview_python" ]; then
 for candidate in /Applications/QGIS.app/Contents/MacOS/bin/python3 /Applications/QGIS.app/Contents/MacOS/python3 /Applications/QGIS-LTR.app/Contents/MacOS/bin/python3; do
  if [ -x "$candidate" ]; then preview_python="$candidate"; break; fi
 done
fi
if [ -z "$preview_python" ]; then
 echo '找不到 Python 3。請把這個訊息告訴我。'
 read -r -p '按 Return 關閉。'
 exit 1
fi
"$preview_python" start_preview.py
preview_result=$?
if [ "$preview_result" -ne 0 ]; then
 read -r -p '按 Return 關閉。'
fi
exit "$preview_result"
