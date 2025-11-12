### roster.py
### created by Ryan McMahon
### Serves as the "backend" for the rosterget app.
### Certified vibecode free :)

import petl as etl
import openpyxl as xl
import os
from pathlib import Path

class RosterTable:
    ### Init our table
    def __init__(self,file_path:Path):
        wb = xl.load_workbook(file_path)
        self.table = etl.fromxlsx(file_path,wb.sheetnames[0])

    def get_row_count(self) -> int:
        return etl.nrows(self.table)

    ### Return a list of column headers
    def get_headers(self) -> tuple:
        return etl.header(self.table)

    ### Return a list of str values from specific row indices in a loaded column
    def find_value_from_row_indices(self,indices:list[int],column) -> list[str]:
        return_list = []
        for id in indices:
            return_list.append(column[id])
        return return_list

    ### Find all indices of a name within a table
    def find_name(self,provided_name:str) -> list[int]:
        names_column = etl.values(self.table,'Name')
        row_indices = []
        for row, name in enumerate(names_column):
            if name == provided_name:
                row_indices.append(row)
        return row_indices

    ### Get a list of communities from a given name
    def find_comms(self,name:str) -> list[str]:
        row_indices = self.find_name(name)
        comm_column = etl.values(self.table,"Community Name")
        return self.find_value_from_row_indices(row_indices, comm_column)
    
    ### Get each column value associated with a certain community
    def find_roster_info(self,comm_name:str,column_name:str) -> list[str]:
        comm_column = etl.values(self.table,"Community Name")
        roster_indices = []
        for row, comm in enumerate(comm_column):
            if comm == comm_name:
                roster_indices.append(row)
        return self.find_value_from_row_indices(roster_indices,etl.values(self.table,column_name))
    
    ### Find all names within a roster of each community that a certain individual is in
    def find_all_roster_names_from_name(self,name:str):
        all_rosters = []
        comm_list = self.find_comms(name)
        for comm_name in comm_list:
            all_rosters.append(self.find_roster_info(comm_name,"Name"))
        return all_rosters
    
    ### The same as above, but for emails.
    def find_all_roster_emails_from_name(self,name:str):
        all_rosters = []
        comm_list = self.find_comms(name)
        for comm_name in comm_list:
            all_rosters.append(self.find_roster_info(comm_name,"Email Address"))
        return all_rosters
