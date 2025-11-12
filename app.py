from textual.app import App, ComposeResult, RenderResult
from textual.widgets import Footer, Header, Label, Input

class RosterGet(App):
    BINDINGS = [("q", "newquery", "New Query")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
    
    def on_mount(self) -> None:
        self.title = "rosterget"
        self.sub_title = "v0.1"

if __name__ == "__main__":
    app = RosterGet()
    app.run()