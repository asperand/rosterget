from textual.app import App, ComposeResult, ScreenStackError
from textual.widgets import Footer, Header, Input, LoadingIndicator, Label, Log, Static, RadioButton, RadioSet, Button
from textual.screen import Screen, ModalScreen
from textual.message import Message
from textual import work, on
from textual.worker import Worker
import roster
from pathlib import Path
from datetime import datetime

TITLE = "rosterget"
VERSION = "v0.2"

# Our message class for returning of values from the table
class QueryMsg(Static):
    class Send(Message):
        def __init__(self,send:str,option:int) -> None:
            self.send = send
            self.option = option
            super().__init__()
    class Recv(Message):
        def __init__(self,recv) -> None:
            self.recv = recv
            super().__init__()

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

    @work
    async def action_new_query(self):
        log = self.query_one(Log)
        if self.loaded == True:
            query_msg = await self.push_screen_wait(QueryScreen())
            self.parse_query(query_msg)
            self.push_screen(LoadingScreen())
        else:
            log.write_line(str(datetime.now().strftime("%H:%M:%S")) + " - No .xlsx File is loaded. Couldn't create a new Query.")
   
    @work(exclusive=True,thread=True)
    async def parse_query(self,query_msg:QueryMsg.Send):
        query_option = query_msg.option
        query_send = query_msg.send    
        match query_option:
            case 0:
                result = self.loaded_table.find_comms(query_send)
                self.post_message(QueryMsg.Recv(result))
            case 1:
                result = self.loaded_table.find_roster_info(query_send,"Name")
                self.post_message(QueryMsg.Recv(result))
            case 2:
                result = self.loaded_table.find_roster_info(query_send,"Email Address")
                self.post_message(QueryMsg.Recv(result))
            case 3:
                result = self.loaded_table.find_all_roster_names_from_name(query_send)
                self.post_message(QueryMsg.Recv(result))
            case 4:
                result = self.loaded_table.find_all_roster_emails_from_name(query_send)
                self.post_message(QueryMsg.Recv(result))

    @on(QueryMsg.Recv)
    def log_result(self,message:QueryMsg.Recv):
        self.pop_screen()
        log = self.query_one(Log)
        log.write_line(str(datetime.now().strftime("%H:%M:%S")) +  " - Got Query: ")
        log.write_lines(message.recv)

    # Called when the user submits input to the box
    async def on_input_submitted(self, message:Input.Submitted) -> None:
        input_box = self.query_one(Input)
        self.load_excel(input_box.value)
        self.push_screen(LoadingScreen())
    
    ### Our threaded work function to load the table into memory. Has error checking and logging to ensure there's no crash.
    ### TODO:   There are some crashes still on pop_screen related to the user spamming entries. 
    ###         Sometimes there will be an attempt to pop the main app screen, which causes crashing
    ###         Another issue is a RuntimeError that stems, I believe, from the same pop_screen call.
    @work(exclusive=True,thread=True)
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
class QueryScreen(ModalScreen[QueryMsg.Send]):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Input(placeholder="Enter search here...")
        yield Button(label="Submit Query")
        yield Log()
        with RadioSet():
            yield RadioButton("Get all Communities from Name")
            yield RadioButton("Get all Roster Names from Community")
            yield RadioButton("Get all Roster Emails from Community")
            yield RadioButton("Get all Roster Names from Name [bold italic red](Warning: Long)[/]")
            yield RadioButton("Get all Roster Emails from Name [bold italic red](Warning: Long)[/]")

    def on_radio_set_changed(self, event:RadioSet.Changed) -> None:
        self.querytype = event.radio_set.pressed_index

    def on_button_pressed(self, message:Button.Pressed):
        input_box = self.query_one(Input)
        if self.querytype == None or input_box.value == "":
            log = self.query_one(Log)
            log.write_line("No query selected or empty field. Please retry")
        else:
            self.dismiss(QueryMsg.Send(input_box.value,self.querytype))
            
if __name__ == "__main__":
    app = RosterApp()
    app.run()
