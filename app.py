from textual import events, on
from textual.app import App, ComposeResult, RenderResult
from textual.widgets import Footer, Header, Label, Input, LoadingIndicator
import roster

class RosterGet(App):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield LoadingIndicator()
        yield Input(placeholder="enter path to excel file here...")
    
    def on_mount(self) -> None:
        self.title = "rosterget"
        self.sub_title = "v0.1"
    
    @on(Input.Submitted)
    def load_excel(self) -> roster.RosterTable:
        self.loaded_table = roster.RosterTable(Input.value)
        print("Loaded table successfully.")

if __name__ == "__main__":
    app = RosterGet()
    app.run()