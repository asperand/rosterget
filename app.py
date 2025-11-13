from textual.app import App, ComposeResult, ScreenStackError
from textual.widgets import Footer, Header, Input, LoadingIndicator, Label, Log, Static
from textual.screen import Screen, ModalScreen
from textual.message import Message
from textual import work, on
from textual.worker import Worker
import roster
from pathlib import Path
from datetime import datetime

TITLE = "rosterget"
VERSION = "v0.1"

# Our message class for the Loader functionality.
class Loader(Static):
    class LoadError(Message):
        def __init__(self,error:str) -> None:
            self.error = error
            super().__init__()

    class LoadSuccess(Message):
        def __init__(self,loaded:bool) -> None:
            self.loaded = loaded
            super().__init__()

class RosterApp(App):
    CSS_PATH = "roster.tcss"
    BINDINGS = [ ("q", "new_query", "New Query")
    ]
    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Enter path to .xlsx file...")
        yield Footer()
        yield Log()
    
    def on_mount(self) -> None:
        self.title = TITLE
        self.sub_title = VERSION
        self.loaded = False
    
    # Logging of a successful load.
    @on(Loader.LoadSuccess)
    def log_loadsuccess(self, message:Loader.LoadSuccess):
        log = self.query_one(Log)
        log.write_line(str(datetime.now().strftime("%H:%M:%S")) + " - Loaded " + str(self.loaded_table.get_row_count()) + " Rows")

    # Logging of errors from the loader.
    @on(Loader.LoadError)
    def log_loaderror(self, message:Loader.LoadError):
        log = self.query_one(Log)
        log.write_line(str(datetime.now().strftime("%H:%M:%S")) + " - Error loading file : " + message.error)

    # New query menu. We will make this screen modal.
    def action_new_query(self):
        log = self.query_one(Log)
        if self.loaded == True:
            self.push_screen(QueryScreen())
        else:
            log.write_line(str(datetime.now().strftime("%H:%M:%S")) + " - No .xlsx File is loaded. Couldn't create a new Query.")

    # Called when the user submits input to the box
    async def on_input_submitted(self, message:Input.Submitted) -> None:
        input_box = self.query_one(Input)
        self.load_excel(input_box.value)
        self.push_screen(LoadingScreen())
    
    ### Our threaded work function to load the table into memory. Has error checking and logging to ensure there's no crash.
    ### TODO:   There are some crashes still on pop_screen related to the user spamming entries. 
    ###         Sometimes there will be an attempt to pop the main app screen, which causes crashing
    ###         Another issue is a RuntimeError that stems, I believe, from the same pop_screen call.
    @work(exclusive=True, thread=True)
    def load_excel(self,path:str):
        try:
            self.loaded_table = roster.RosterTable(Path(path))
            self.loaded = True
            self.post_message(Loader.LoadSuccess(True))
        except FileNotFoundError:
            self.post_message(Loader.LoadError("File Not Found"))
        except FileExistsError:
            self.post_message(Loader.LoadError("File Does Not Exist"))
        except PermissionError:
            self.post_message(Loader.LoadError("Permission Denied"))
        except RuntimeError:
            self.post_message(Loader.LoadError("Be careful, I'm fragile!"))
        except:
            self.post_message(Loader.LoadError("Couldn't Load"))
        finally:
            self.call_from_thread(self.pop_screen())

# Loading indicator while the Excel file is working to ensure the user understands work is happening in the background.
class LoadingScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield LoadingIndicator()

# Let's make this a modalscreen.
class QueryScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
       
if __name__ == "__main__":
    app = RosterApp()
    app.run()
