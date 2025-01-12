from Bonnie.html_ import View
from views import IndexView

HOST = "localhost"
PORT = 2306

STATIC_DIR = "static"

URLS: dict[str, View] = {
    "": IndexView,
    "/": IndexView,
    "/index": IndexView
}
