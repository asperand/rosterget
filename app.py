from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Input, LoadingIndicator, Label
from textual.screen import Screen
from textual.message import Message
import roster
from pathlib import Path
import time

TITLE = "rosterget"
VERSION = "v0.1"

class RosterApp(App):
    CSS_PATH = "roster.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Enter path to .xlsx file...")
    
    def on_mount(self) -> None:
        self.title = TITLE
        self.sub_title = VERSION
    
    async def on_input_submitted(self, message:Input.Submitted) -> None:
        input_box = self.query_one(Input)
        self.run_worker(self.load_excel(input_box.value),exclusive=True,thread=True)
        # Spawned our worker thread. Switch the UI over to our loading screen.
        self.push_screen(LoadingScreen())
        # This loading screen works while the background work is going.

    async def load_excel(self,path:str):
        self.loaded_table = roster.RosterTable(Path(path))
        self.title = "Loaded " + str(self.loaded_table.get_row_count()) + " Rows"
        self.sub_title = TITLE + " " + VERSION
        # Since work is done, I'd like to switch to the next screen.
        # I've tried screen_push(), which causes the app to close.
        # I've tried screen_switch(), which causses the app to freeze.
        # Would I have to do this in the above async function?
        
class LoadingScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield LoadingIndicator()

class QueryScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Finished!")

if __name__ == "__main__":
    app = RosterApp()
    app.run()
