import os
from Bonnie.http_ import HttpRequest, HttpResponse
from Bonnie.html_ import Component


def render(request: HttpRequest, component: Component, status_code: int = 200) -> HttpResponse:
    response = HttpResponse(request)
    response.status_code = status_code
    response.headers = {
        "Content-type": "text/html; charset=utf-8"
    }
    response.html = component.render()
    return response
