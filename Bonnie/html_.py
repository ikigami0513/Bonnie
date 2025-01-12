import os
from html.parser import HTMLParser
from abc import ABC
from Bonnie.http_ import HTTPRequestHandler, HttpRequest
from Bonnie.exceptions import MethodNotAllowed


class Component(ABC):
    def __init__(self, request: HttpRequest, path: str = "", props: dict = {}) -> None:
        self.request = request
        self.path = path
        self.props = props

    def render(self) -> str:
        with open(self.path, "rb") as f:
            html = f.read().decode("utf-8")

        for key in self.props.keys():
            html = html.replace(f"<{key} />", self.props.get(key))

        html = self.replace_remaining_tags(html)

        return html
    
    def replace_remaining_tags(self, html: str) -> str:
        """
        Parcourt les balises restantes dans le HTML et tente de les remplacer
        par le contenu d'un fichier HTML correspondant.
        """
        class TagParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.tags = set()

            def handle_starttag(self, tag, attrs):
                self.tags.add(tag)

        # Parse le HTML pour récupérer les balises restantes
        parser = TagParser()
        parser.feed(html)

        # Liste des balises HTML standard (simplifiée)
        standard_tags = {
            "html", "head", "body", "div", "span", "p", "h1", "h2", "h3", "h4", "h5", "h6",
            "a", "ul", "ol", "li", "table", "tr", "td", "th", "img", "form", "input", "button",
            "header", "footer", "main", "nav", "section", "article", "aside", "figure", "figcaption",
        }

        # Parcourir les balises et remplacer celles qui ne sont pas standard
        for tag in parser.tags:
            if tag not in standard_tags:
                tag_placeholder = f"<{tag} />"
                html_file = f"components/{tag}.html"

                # Vérifier si un fichier HTML correspondant existe
                if os.path.exists(html_file):
                    with open(html_file, "r", encoding="utf-8") as f:
                        replacement_content = f.read()
                    html = html.replace(tag_placeholder, replacement_content)

        return html

    def get(self) -> None:
        html_content = self.render()
        self._send_response(html_content)



class View(ABC):
    def __init__(self, request_handler: HTTPRequestHandler) -> None:
        self.request_handler = request_handler

    def get(self, request: HttpRequest) -> None:
        raise MethodNotAllowed("Method GET not allowed.")

    def post(self, request: HttpRequest) -> None:
        raise MethodNotAllowed("Method POST not allowed.")
    
    def put(self, request: HttpRequest) -> None:
        raise MethodNotAllowed("Method PUT not allowed.")
    
    def delete(self, request: HttpRequest) -> None:
        raise MethodNotAllowed("Method DELETE not allowed.")
    