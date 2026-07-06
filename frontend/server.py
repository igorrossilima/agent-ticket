import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).resolve().parent
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
PORT = int(os.getenv("FRONTEND_PORT", "5500"))


class FrontendHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/"):
            self._proxy()
            return

        self._serve_static()

    def do_POST(self):
        self._proxy()

    def do_PATCH(self):
        self._proxy()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS")
        self.end_headers()

    def _serve_static(self):
        path = self.path.split("?", 1)[0]
        relative_path = "index.html" if path in ("", "/") else path.lstrip("/")
        file_path = (ROOT_DIR / relative_path).resolve()

        if not str(file_path).startswith(str(ROOT_DIR)) or not file_path.is_file():
            self.send_error(404)
            return

        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        content = file_path.read_bytes()

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _proxy(self):
        if not self.path.startswith("/api/"):
            self._send_json(404, {"detail": "Rota do proxy nao encontrada."})
            return

        api_path = self.path.removeprefix("/api")
        url = f"{API_BASE_URL}{api_path}"
        body = self._read_body()
        headers = self._proxy_headers()

        try:
            request = Request(
                url=url,
                data=body if body else None,
                headers=headers,
                method=self.command,
            )

            with urlopen(request, timeout=120) as response:
                response_body = response.read()
                self._send_proxy_response(
                    status=response.status,
                    body=response_body,
                    content_type=response.headers.get("Content-Type", "application/json"),
                )
        except HTTPError as error:
            self._send_proxy_response(
                status=error.code,
                body=error.read(),
                content_type=error.headers.get("Content-Type", "application/json"),
            )
        except URLError as error:
            self._send_json(
                502,
                {
                    "detail": "Nao foi possivel conectar na API.",
                    "api_base_url": API_BASE_URL,
                    "error": str(error.reason),
                },
            )

    def _read_body(self):
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        return self.rfile.read(content_length) if content_length else None

    def _proxy_headers(self):
        headers = {}

        for key in ("Authorization", "Content-Type", "Accept"):
            value = self.headers.get(key)
            if value:
                headers[key] = value

        return headers

    def _send_proxy_response(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), FrontendHandler)
    print(f"Frontend: http://localhost:{PORT}")
    print(f"API proxy: {API_BASE_URL}")
    server.serve_forever()


if __name__ == "__main__":
    main()
