from http.server import HTTPServer
from Bonnie.settings import load_settings
from Bonnie.http_ import HTTPRequestHandler
from Bonnie.exceptions import *


class BonnieHTTPServer:
    def __init__(self, settings_path="settings") -> None:
        settings = load_settings(settings_path)
        self.server_address = (settings.HOST, settings.PORT)
        self.httpd = HTTPServer(self.server_address, HTTPRequestHandler)

    def start(self) -> None:
        print(f"Démarrage du serveur sur {self.server_address[0]}:{self.server_address[1]}")
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nArrêt du serveur...")

    def stop(self) -> None:
        self.httpd.server_close()
        print("Serveur arrêté.")
