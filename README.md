# MG_User_Management
Compares the googlesheet source that the onboarding form saves data to with the the TradingView "Manage Access" user list.  If a user is missing it attempts to add that user if a series of checks are passed.

There are two processes running.  A primary process that adds usernames to TV and a background process per se' (multiprocessing) that pulls the google information then uses multiprocessing.Queue to pass the list to the primary process.  Every cycle the process uses the newly sent list to check against.

## Platform Requirements  
* Linux or Windows with GUI
* Python 3.7.3+
* Firefox
* Google Sheet Permissions (ReadOnly)
* Google API Pickle File
* Google API credentials.json file


## Setup  
Enable Google API 
[Google Sheets API QuickStart](https://developers.google.com/sheets/api/quickstart/python)
Click on "Enable the Google Sheets API" (blue button)
Click on "Download Client Credentials" - This comes as a json file.
Place credentials in same directory as tvmonitor.py
Edit tvcreds.json with your own credentials.


# Python Setup 
We are going to create a virtual environment for managing this script.  This prevents package dependancy on specific version being an issue with future scripts.

## Linux Version
```
python3 -m pip install --user virtualenv
python3 -m venv mg_user_mgmt
source mg_user_mgmt/bin/activate
Confirmation you are in virtual environment
which python  
pip install -r requirements.txt

Exit environemnt -> deactivate
```
* You should see .../mg_user_mgmt/bin/python after activating environment.

## Windows Version
```
py -m pip install --user virtualenv
py -m venv mg_user_mgmt
.\mg_user_mgmt\Scripts\activate
where python   
pip install -r requirements.txt

Exit environemnt -> deactivate
```
* You should see `.../mg_user_mgmt/bin/python.exe` after activating environment.


# Clone and Prep the code
`wget https://github.com/snub-fighter/MG_User_Management/archive/master.zip`
`unzip master.zip`
`cd master`
## Edit tv_monitor.py Information
Change this information to match your own info.  
* MG_USER_MGMT = 'https://www.tradingview.com/script/fY4QMhMJ-test-script-zerpgames/'  
** This is the direct URL of your indicator.  The "Manage Access" button should show below on the page.
* SAMPLE_SPREADSHEET_ID = '1CLM_FsqIwiDnndAlmgifuy-y8Z4Hy3GhplE_ixr3h4Y'  
** This is the sheet ID you can find this by open up the sheet in a browser and looking at URL.  
Example: https://docs.google.com/spreadsheets/d/1CLM_FsqIwiDnndAlmgifuy-y8Z4Hy3GhplE_ixr3h4Y/edit#gid=0  
* SAMPLE_RANGE_NAME = 'TempNames!A2:C'  
** This is the google sheet range Starts at 2nd row and looks for columns A,B,C.  Under the function `get_google_user_list` I am looking for usernames under column C. Change usernames.append(row[2]) to the appropriate row [0,1,2,3 etc]

            for row in values:
                # Print columns A and E, which correspond to indices 0 and 4.
                #print('%s, %s, %s' % (row[0], row[1], row[2]))
                usernames.append(row[2])
# Run the code
`python tv_monitor.py`


# Failed UserAdd
In the event that the script cannot find the user in the "hinted active list" it will drop it into the file failedtoaddtotradingview.txt


### Notes:  
A Firefox browser should open up and begin the login process.  It will constantly recheck the google list vs the TradingView list.  You can optionally set this to headless using the `healdess=True` argument as shown below

```
if __name__ == '__main__':
    start = TV(headless=False, browser='firefox',logintype='auto')
    ```
