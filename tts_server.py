from __future__ import annotations

import asyncio
import base64
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

try:
    import edge_tts
except ImportError:  # pragma: no cover
    edge_tts = None


HOST = "127.0.0.1"
PORT = 5000
VOICE = "en-US-JennyNeural"
ORIGIN_ALLOWLIST = {
    "http://localhost:8000",
    "http://127.0.0.1:8000",
}


async def synthesize_audio(text: str) -> str:
    if edge_tts is None:
        raise RuntimeError("Missing dependency: edge-tts. Run: py -m pip install edge-tts")

    communicate = edge_tts.Communicate(text, VOICE)
    audio_chunks: list[bytes] = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_chunks.append(chunk["data"])

    audio_bytes = b"".join(audio_chunks)
    encoded = base64.b64encode(audio_bytes).decode("ascii")
    return f"data:audio/mpeg;base64,{encoded}"


class TTSHandler(BaseHTTPRequestHandler):
    server_version = "LocalEdgeTTSServer/1.0"

    def _origin(self) -> str:
        request_origin = self.headers.get("Origin", "")
        if request_origin.endswith(".github.io") or request_origin in ORIGIN_ALLOWLIST:
            return request_origin
        return request_origin or "*"

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", self._origin())
        self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/tts":
            self._send_json(404, {"error": "Not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            payload = json.loads(raw_body.decode("utf-8"))
            text = str(payload.get("text", "")).strip()

            if not text:
                self._send_json(400, {"error": "Missing text"})
                return
            if len(text) > 4000:
                self._send_json(413, {"error": "Text is too long"})
                return

            audio = asyncio.run(synthesize_audio(text))
            self._send_json(200, {"audio": audio})
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON"})
        except Exception as exc:  # pragma: no cover
            self._send_json(500, {"error": str(exc)})

    def log_message(self, format: str, *args: Any) -> None:
        print(f"{self.address_string()} - {format % args}")


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), TTSHandler)
    print(f"Local Edge TTS server running at http://{HOST}:{PORT}/tts")
    print("Install dependency if needed: py -m pip install edge-tts")
    server.serve_forever()


if __name__ == "__main__":
    main()
