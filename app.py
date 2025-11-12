from textual.app import App, ComposeResult, RenderResult
from textual.widgets import Footer, Header
from textual.widget import Widget

class RosterGet(App):
    BINDINGS = [("q", "newquery", "New Query")]
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

if __name__ == "__main__":
    app = RosterGet()
    app.run()