import os
import mimetypes
from http.server import BaseHTTPRequestHandler
from Bonnie.settings import load_settings


class HttpRequest:
    def __init__(self, path: str, method: str, client_address: tuple[str, int]):
        self.path = path
        self.method = method
        self.client_address = client_address


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


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        settings = load_settings()
        file_path = self.get_static_file_path(self.path)
        if file_path:
            self.serve_static_file(file_path)
        else:
            view = settings.URLS.get(self.path, None)
            if view:
                request = HttpRequest(self.path, self.command, self.client_address)
                response = view(self).get(request)
                response.response(self)
            else:
                self.send_error(404, "Page not found")

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
        view = load_settings().URLS.get(self.path, None)
        if view:
            view(self).post()
        # content_length = int(self.headers.get("Content-Length", 0))
        # post_data = self.rfile.read(content_length).decode("utf-8")
        # self.send_response(200)
        # self.send_header("Content-type", "application/json")
        # self.end_headers()
        # response = {
        #     "message": "Données reçues avec succès!",
        #     "data": post_data
        # }
        # self.wfile.write(json.dumps(response).encode("utf-8"))

    def do_PUT(self) -> None:
        view = load_settings().URLS.get(self.path, None)
        if view:
            view(self).put()

    def do_DELETE(self) -> None:
        view = load_settings().URLS.get(self.path, None)
        if view:
            view(self).delete()
