'''
This module will be used to connect and access google drive and spreadsheets update the sheets using google api
Inputs: google provided credentials in json file, sheet name , sheet reading range, sheet writing range
'''

import gspread
import json
from oauth2client.client import SignedJwtAssertionCredentials
import gspread_dataframe as gd
import pandas as pd

class access_google_api:

    def __init__(self, cred_path, worksheet, spread_sheet_name):

        self.cred_path = cred_path
        self.spread_sheet_name = spread_sheet_name
        self.worksheet = worksheet

    # accessing google spread sheet and google drive
    def access(self):
        path = str(self.cred_path)
        # API credentials provided by google drive during setting up project
        json_key = json.load(open(path))
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

        # fetching credentials from json_key
        credentials = SignedJwtAssertionCredentials(json_key['client_email'],
                                                    json_key['private_key'].encode(), scope)

        # authenticate the spread sheet with Google API credentials
        file = gspread.authorize(credentials)
        sheet_access = file.open(self.spread_sheet_name).worksheet(str(self.worksheet))
        return sheet_access

    # google spread sheet reader
    def spread_sheet_reader(self, read_range_start, read_range_finsh):
        sheet_access = self.access()
        all_cells = sheet_access.range(str(read_range_start+':'+str(read_range_finsh)))
        search_key = []
        for cell in all_cells:
            search_key.append(cell.value)

        return search_key # written's list of items

    # google spread sheet writer : helpful package 'gspread_dataframe' https://github.com/robin900/gspread-dataframe
    def spread_sheet_writer(self, dataframe):
        sheet_access = self.access()
        check_col = self.spread_sheet_reader(read_range_finsh='A1', read_range_start='A1')

        try:
            if len(check_col[0]) != 0:
                existing_records = pd.DataFrame(sheet_access.get_all_records()) #import gspread
                new_records = existing_records.append(dataframe)
                gd.set_with_dataframe(sheet_access, new_records)
            else:
                gd.set_with_dataframe(sheet_access, dataframe) #import gspread_dataframe as gd

        except:
            pass



