from Bonnie.html_ import View
from Bonnie.http_ import DebugMiddleware
from views import IndexView

HOST = "localhost"
PORT = 2306

STATIC_DIR = "static"

MIDDLEWARES = [
    DebugMiddleware
]

URLS: dict[str, View] = {
    "": IndexView,
    "/": IndexView,
    "/index": IndexView
}
