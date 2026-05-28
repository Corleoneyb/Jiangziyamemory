#!/usr/bin/env python3
"""软件脸语音 API：浏览器录音 POST → 转写 → 脑 → JSON。

用法:
  python3 scripts/voice_dialog_api.py
  python3 scripts/voice_dialog_api.py --port 8766

验收:
  curl -s http://127.0.0.1:8766/api/health
  curl -s -X POST http://127.0.0.1:8766/api/dialog \\
    -H 'Content-Type: application/json' -d '{"text":"你好"}'
"""

from __future__ import annotations

import argparse
import cgi
import json
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from voice_common import append_inbox, transcribe  # noqa: E402
from voice_dialog_brain import brain_reply, load_dotenv, write_last_reply  # noqa: E402

DEFAULT_PORT = 8766


def cors_headers(handler: BaseHTTPRequestHandler) -> None:
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")


class DialogAPIHandler(BaseHTTPRequestHandler):
    server_version = "JiangziyaVoiceAPI/1.0"

    def log_message(self, fmt: str, *args) -> None:
        print(f"[voice_api] {self.address_string()} - {fmt % args}")

    def _send_json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        cors_headers(self)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        cors_headers(self)
        self.end_headers()

    def do_GET(self) -> None:
        if self.path.rstrip("/") == "/api/health":
            self._send_json(200, {"ok": True, "service": "voice_dialog_api"})
            return
        self._send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path.rstrip("/") != "/api/dialog":
            self._send_json(404, {"error": "not_found"})
            return
        ctype = self.headers.get("Content-Type", "")
        try:
            if "application/json" in ctype:
                n = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(n) if n else b"{}"
                data = json.loads(raw.decode("utf-8") or "{}")
                text = (data.get("text") or "").strip()
                if not text:
                    self._send_json(400, {"error": "empty_text"})
                    return
            elif "multipart/form-data" in ctype:
                text = self._transcribe_multipart()
                if not text:
                    self._send_json(400, {"error": "no_speech"})
                    return
            else:
                text = self._transcribe_raw(ctype)
                if not text:
                    self._send_json(400, {"error": "no_speech"})
                    return
            reply = brain_reply(text)
            append_inbox(text, "软件脸语音", notify=False)
            write_last_reply(text, reply)
            self._send_json(200, {"text": text, "reply": reply})
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _transcribe_multipart(self) -> str:
        n = int(self.headers.get("Content-Length", 0))
        env = {
            "REQUEST_METHOD": "POST",
            "CONTENT_TYPE": self.headers.get("Content-Type", ""),
            "CONTENT_LENGTH": str(n),
        }
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ=env)
        item = form.get("audio") or form.get("file")
        if item is None or not getattr(item, "file", None):
            return ""
        raw = item.file.read()
        fname = getattr(item, "filename", "") or "clip.webm"
        ext = Path(fname).suffix or ".webm"
        return self._transcribe_bytes(raw, ext)

    def _transcribe_raw(self, ctype: str) -> str:
        n = int(self.headers.get("Content-Length", 0))
        if n <= 0:
            return ""
        raw = self.rfile.read(n)
        ext = ".webm"
        if "wav" in ctype:
            ext = ".wav"
        elif "ogg" in ctype:
            ext = ".ogg"
        elif "mpeg" in ctype or "mp3" in ctype:
            ext = ".mp3"
        return self._transcribe_bytes(raw, ext)

    def _transcribe_bytes(self, raw: bytes, ext: str) -> str:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            path = Path(tmp.name)
            tmp.write(raw)
        try:
            return transcribe(path)
        finally:
            path.unlink(missing_ok=True)


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), DialogAPIHandler)
    print(f"姜子牙语音 API · http://127.0.0.1:{args.port}")
    print("  GET  /api/health")
    print("  POST /api/dialog  (JSON text 或 multipart audio)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
