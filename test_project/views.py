from Bonnie.http_ import HttpRequest
from Bonnie.html_ import View, Component
from Bonnie.utils import render


class LayoutComponent(Component):
    def __init__(self, request: HttpRequest, content: str):
        super().__init__(request, "components/layout.html", {
            "content": content
        })
    

class IndexComponent(Component):
    def __init__(self, request: HttpRequest, props = {}):
        super().__init__(request, "components/index.html", props)

    def render(self) -> str:
        html = super().render()
        return LayoutComponent(self.request, content=html).render()


class IndexView(View):
    def get(self, request: HttpRequest):
        return render(request, IndexComponent(request))
        