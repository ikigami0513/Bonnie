import os
import json
import mimetypes
from http.server import BaseHTTPRequestHandler
from http.cookies import SimpleCookie
from urllib.parse import urlparse, parse_qs
from typing import Type, Any
from Bonnie.settings import load_settings


class HttpRequest:
    def __init__(self, path: str, method: str, client_address: tuple[str, int], headers: dict, GET: dict[str, Any] = {}, POST: dict[str, Any] = {}):
        self.path = path
        self.method = method
        self.client_address = client_address
        self.GET = GET
        self.POST = POST
        self.headers = headers
        self.cookies = self.parse_cookies(headers.get("Cookie", ""))

    def parse_cookies(self, cookie_header: str) -> dict:
        cookies = {}
        if cookie_header:
            cookie = SimpleCookie(cookie_header)
            for key, morsel in cookie.items():
                cookies[key] = morsel.value
        return cookies


class HttpResponse:
    def __init__(self, request: HttpRequest, status_code: int = 200, headers: dict[str, str] = {}, html: str = ""):
        self.request = request
        self.status_code = status_code
        self.headers = headers
        self.html = html

    def response(self, request_handler: 'HTTPRequestHandler') -> None:
        request_handler.send_response(self.status_code)
        for key, value in self.headers.items():
            request_handler.send_header(key, value)
        request_handler.end_headers()
        request_handler.wfile.write(self.html.encode("utf-8"))


class Middleware:
    def before(self, request: HttpRequest):
        pass

    def after(self, request: HttpRequest, response: HttpResponse):
        pass


class DebugMiddleware(Middleware):
    def before(self, request: HttpRequest):
        print("===== DEBUG REQUEST BEFORE HANDLE =====")
        print(f"    method : {request.method}")
        print(f"    path : {request.path}")
        print(f"    client address : {request.client_address}")
        print(f"    GET : {request.GET}")
        print(f"    POST : {request.POST}")
        print(f"    headers : {request.headers}")
        print(f"    cookies : {request.cookies}")

    def after(self, request: HttpRequest, response: HttpResponse):
        print("===== DEBUG RESPONSE AFTER HANDLE =====")
        print(f"    status code : {response.status_code}")
        print(f"    headers : {response.headers}")


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        settings = load_settings()
        file_path = self.get_static_file_path(parsed_url.path)
        if file_path:
            self.serve_static_file(file_path)
        else:
            view = settings.URLS.get(parsed_url.path, None)
            if view:
                request = HttpRequest(
                    parsed_url.path, self.command, self.client_address,
                    headers=self.headers, GET=query_params
                )
                self.handle_before_middlewares(request, settings.MIDDLEWARES)

                response = view(self).get(request)

                self.handle_after_middlewares(request, response, settings.MIDDLEWARES)
                response.response(self)
            else:
                self.send_error(404, "Page not found")

    def handle_before_middlewares(self, request: HttpRequest, middlewares: list[Type[Middleware]]):
        for middleware_cls in middlewares:
            middleware_cls().before(request)

    def handle_after_middlewares(self, request: HttpRequest, response: HttpResponse, middlewares: list[Type[Middleware]]):
        for middleware_cls in middlewares:
            middleware_cls().after(request, response)

    def get_static_file_path(self, path: str) -> str:
        """Retourne le chemin du fichier statique si le fichier existe."""
        # Nettoie le chemin et empêche les accès non autorisés (par ex., "../")
        normalized_path = os.path.normpath(path.lstrip("/"))
        file_path = os.path.join(load_settings().STATIC_DIR, normalized_path)

        # Vérifie si le fichier existe et est accessible
        if os.path.isfile(file_path):
            return file_path
        return None
    
    def serve_static_file(self, file_path) -> None:
        """Servez un fichier statique."""
        try:
            # Devine le MIME du fichier
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = "application/octet-stream"

            # Lit le contenu du fichier
            with open(file_path, "rb") as f:
                content = f.read()

            # Réponse HTTP
            self.send_response(200)
            self.send_header("Content-type", mime_type)
            self.send_header("Content-Length", len(content))
            self.end_headers()

            # Envoie le contenu du fichier
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Erreur lors de la lecture du fichier : {e}")

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8")

        try:
            parsed_data = json.loads(post_data)
        except json.JSONDecodeError:
            parsed_data = post_data

        view = load_settings().URLS.get(self.path, None)
        if view:
            request = HttpRequest(
                self.path, self.command, self.client_address,
                POST=parsed_data
            )
            response = view(self).post(request)
            response.response(self)

    def do_PUT(self) -> None:
        view = load_settings().URLS.get(self.path, None)
        if view:
            view(self).put()

    def do_DELETE(self) -> None:
        view = load_settings().URLS.get(self.path, None)
        if view:
            view(self).delete()
