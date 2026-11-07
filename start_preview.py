#!/usr/bin/env python3
"""Open this archive through one loopback HTTP URL in Chrome or Safari."""
import argparse
import functools
import http.server
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request
import webbrowser

DEFAULT_PORT = 4173
REVISION = '20261105-r11'
ROOT = pathlib.Path(__file__).resolve().parent


def archive_revision(root=ROOT):
    try:
        text = (root / 'index.html').read_text(encoding='utf-8')
    except OSError:
        return None
    match = re.search(r'<meta name="b16-revision" content="([^"]+)"', text)
    return match.group(1) if match else 'previous'


class ArchiveHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        if self.path.split('?', 1)[0].endswith(('.html', '/')) or self.path.startswith('/__b16_status__'):
            self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def do_GET(self):
        if self.path.split('?', 1)[0] == '/__b16_status__':
            payload = json.dumps({'archive': 'B16', 'root': str(ROOT), 'revision': archive_revision()}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        else:
            super().do_GET()


def existing_archive(port):
    try:
        with urllib.request.urlopen('http://127.0.0.1:%d/__b16_status__' % port, timeout=2) as response:
            return json.load(response)
    except (OSError, ValueError, urllib.error.URLError):
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=DEFAULT_PORT)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    if not (ROOT / 'index.html').is_file() or not (ROOT / 'js' / 'leaflet.js').is_file():
        print('請將更新檔放進原本網站資料夾，與 images、tiles、data、css、js 並列，再啟動。')
        return 1
    url = 'http://127.0.0.1:%d/index.html?rev=%s' % (args.port, REVISION)
    running = existing_archive(args.port)
    if running and running.get('archive') == 'B16' and running.get('root') == str(ROOT):
        print('網站已啟動：' + url, flush=True)
        if not args.no_browser:
            webbrowser.open(url)
        return 0
    try:
        server = http.server.ThreadingHTTPServer(
            ('127.0.0.1', args.port), functools.partial(ArchiveHandler, directory=str(ROOT)))
    except OSError:
        print('4173埠正被另一個程式或另一份網站使用。請關閉舊的網站啟動視窗，再啟動本檔案。')
        return 1
    print('東涌影像檔案已啟動：' + url, flush=True)
    print('Chrome 和 Safari 都使用上面同一個網址。', flush=True)
    print('保留這個視窗；瀏覽結束後按 Control+C。', flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
