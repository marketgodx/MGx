from apscheduler.schedulers.background import BackgroundScheduler
import multiprocessing as mp
import atexit
from notification.smtp import send_email
from notification.discord import discord_notify
from selenium import webdriver
import time
import hmac, base64, struct, hashlib
import datetime
import os
import logging
import sys
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.firefox.options import Options as FireFox_Options
from selenium.webdriver.chrome.options import Options as Chrome_Options
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as BS
import re, itertools


LOGGER.setLevel(logging.WARNING)
import configparser
from multiprocessing import Queue

q = Queue()


### MG MGMT ###
MG_USER_MGMT = 'https://www.tradingview.com/script/fY4QMhMJ-test-script-zerpgames/'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SAMPLE_SPREADSHEET_ID = '1CLM_FsqIwiDnndAlmgifuy-y8Z4Hy3GhplE_ixr3h4Y'
SAMPLE_RANGE_NAME = 'TempNames!A2:C'
### END MG MGMT ###


### MG MGMT SUPPLEMENTAL ###
class TV:
    def __init__(self, logintype='auto', headless=True,monitor=True, browser='firefox',
                 email_sms=True, discord_enabled=True):
        #send_email('x', 'x')

        if logintype == 'auto':
            if os.path.exists('tvcreds.json'):
                import json
                creds = json.loads(open('tvcreds.json').read())
                self.username = creds['EMAIL_ADDRESS']
                self.password = creds['PASSWORD']
                if (self.username or self.password) == "":
                    logging.error('MUST ENTER CREDENTIALS INTO tvcreds.json FILE')
                # If there are no (valid) credentials available, let the user log in.
            if not os.path.exists('tvcreds.json'):
                logging.error('MUST ENTER CREDENTIALS INTO tvcreds.json FILE')


        else:
            username = input('EMAIL ADDRESS : ')
            password = input('PASSWORD : ')


        ### Drivers for
        self.gecko_source_win64 = 'https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-win64.zip'
        self.gecko_source_linux64 = 'https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz'
        self.gecko_source_linux32 = 'https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux32.tar.gz'

        self.chrome_driver74_win_url = 'https://chromedriver.storage.googleapis.com/74.0.3729.6/chromedriver_win32.zip'
        self.chrome_driver74_mac_url = 'https://chromedriver.storage.googleapis.com/74.0.3729.6/chromedriver_mac64.zip'
        self.chrome_driver74_linux_url = 'https://chromedriver.storage.googleapis.com/74.0.3729.6/chromedriver_linux64.zip'

        self.chrome_driver75_win_url = 'https://chromedriver.storage.googleapis.com/75.0.3770.8/chromedriver_win32.zip'
        self.chrome_driver75_mac_url = 'https://chromedriver.storage.googleapis.com/75.0.3770.8/chromedriver_mac64.zip'
        self.chrome_driver75_linux_url = 'https://chromedriver.storage.googleapis.com/75.0.3770.8/chromedriver_linux64.zip'

        self.chrome_driver76_win_url = 'https://chromedriver.storage.googleapis.com/76.0.3809.12/chromedriver_win32.zip'
        self.chrome_driver76_mac_url = 'https://chromedriver.storage.googleapis.com/76.0.3809.12/chromedriver_mac64.zip'
        self.chrome_driver76_linux_url = 'https://chromedriver.storage.googleapis.com/76.0.3809.12/chromedriver_linux64.zip'

        ### Tradingview Login Page ###
        self.tvurl = 'https://www.tradingview.com/chart/13uGYavE/#signin'

        self.mg_indicator = 'https://www.tradingview.com/script/fY4QMhMJ-test-script-zerpgames/'
        self.browser = browser
        if monitor:
            #atexit.register(self._close_browser)  # AUTO CLOSE BROWSER WHEN
            self.google_api = mp.Process(target=self.get_google_user_list, args=(q, SCOPES,SAMPLE_SPREADSHEET_ID ,SAMPLE_RANGE_NAME))
            self.google_api.daemon = True
            self.google_api.start()
            self.schedule()
            self.update_tv(headless=headless, username=self.username, password=self.password, browser=self.browser)

            # ### COIL ###
            # self.p1_coil = mp.Process(target=self.open_coil, args=(q, browser, monitor))
            # self.p1_coil.daemon = True
            # self.p1_coil.start()
            # self.p2_tv = mp.Process(target=self.update_tv,args=(username,password,browser,headless))
            # self.p2_tv.daemon = True
            # self.p2_tv.start()
            
        else:
            logging.error('Attempting to run two process failed for some unknown reason. - DEBUG - ')
            ### END INIIT ###



    def update_tv(self,headless=False,username='',password='',browser=''):

        if browser == 'firefox':
            self.get_firefox_profile_dir(headless=headless)
            self.driver = webdriver.Firefox(options=self.options, firefox_profile=str(self.data_path),
                                            executable_path=str(self.gecko))
            self.driver.get(self.tvurl)  # OPEN TRADINGVIEW URL
            try:
                self.login(username=username, password=password)
            except Exception as e:
                logging.warning(e)
                try:
                    self.driver.get(self.mg_indicator)
                    time.sleep(4)
                    loggedin = self.driver.find_element_by_css_selector('.tv-header__dropdown-text--username')
                    if loggedin:
                        pass
                except Exception as e:
                    print(e , "Cannot grab URL")

            while True:
                if q.empty():
                    pass
                else:
                    google_sheet_user_list = q.get()
                    self.manage_users(google_sheet_user_list)

            #self.alert_monitoring(email_sms=email_sms, discord_alert=discord_enabled)

    def _close_browser(self):
        q.put('goodbye')
        self.coil_driver.close()

    def file_unzip(self, file, path):
        import zipfile
        zip_ref = zipfile.ZipFile(file, 'r')
        zip_ref.extractall(path=path)
        zip_ref.close()

    def file_unzip_tar(self, file, path):
        import tarfile
        file = tarfile.open(file)
        file.extractall(path=path)
        file.close()

    def get_google_user_list(self,q ,SCOPES,SAMPLE_SPREADSHEET_ID ,SAMPLE_RANGE_NAME):
        logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)

        import pickle
        import os.path
        from googleapiclient.discovery import build
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from pprint import pprint
        SCOPES = SCOPES

        SAMPLE_SPREADSHEET_ID = SAMPLE_SPREADSHEET_ID
        SAMPLE_RANGE_NAME = SAMPLE_RANGE_NAME

        usernames = []
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds,cache_discovery=False)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
        else:
            #print('FirstName, LastName, UserName')
            for row in values:
                # Print columns A and E, which correspond to indices 0 and 4.
                #print('%s, %s, %s' % (row[0], row[1], row[2]))
                usernames.append(row[2])
        q.put(usernames)

    def get_coil_url(self):
        return self.driver.get(self.coilurl)

    def get_tv_url(self):
        return self.tvdriver.get(self.tvurl)

    def get_mg_indicator(self):
        return self.driver.get(self.mg_indicator)

    def get_firefox_profile_dir(self, headless=False):
        from pathlib import Path
        self.gecko_path = os.path.dirname(__file__)
        self.options = FireFox_Options()
        self.options.headless = headless
        self.options.set_preference("dom.webnotifications.serviceworker.enabled", True)
        self.options.set_preference("dom.webnotifications.enabled", True)
        self.options.set_preference('permissions.default.desktop-notification', 1)
        self.options.log.level = "debug"

        if sys.platform in ['linux', 'linux2']:
            import subprocess
            self.ff_gecko = Path(self.gecko_path + '/geckodriver')
            bits = 'uname -m'
            ver_32_64 = subprocess.getstatusoutput(bits)
            cmd = "ls -d /home/$USER/.mozilla/firefox/*.default/"
            fp = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
            FF_PRF_DIR = fp.communicate()[0][0:-2]
            self.FF_PRF_DIR_DEFAULT = str(FF_PRF_DIR, 'utf-8')

            if 'x86_64' in ver_32_64:
                if not self.ff_gecko.is_file():
                    import wget
                    self.gecko_targz = self.gecko_path + '/' + self.gecko_source_linux64.split('/')[-1]
                    wget.download(self.gecko_source_linux64, self.gecko_path)
                    self.file_unzip_tar(self.gecko_path + '/' + self.gecko_targz)
                    os.remove(self.gecko_path + '/' + self.gecko_targz)
                if self.ff_gecko.is_file():
                    self.data_path = self.FF_PRF_DIR_DEFAULT
                    self.gecko = self.ff_gecko

            if 'i368' in ver_32_64:
                if not self.ff_gecko.is_file():
                    import wget
                    self.gecko_targz = self.gecko_path + '/' + self.gecko_source_linux32.split('/')[-1]
                    wget.download(self.gecko_source_linux32, self.gecko_path)
                    self.file_unzip_tar(self.gecko_path + '/' + self.gecko_targz)
                    os.remove(self.gecko_path + '/' + self.gecko_targz)
                if self.ff_gecko.is_file():
                    self.data_path = str(self.FF_PRF_DIR_DEFAULT)
                    self.gecko = str(self.ff_gecko)

        elif sys.platform == 'win32' or 'nt':
            from pathlib import Path
            self.gecko = self.gecko_path + "\geckodriver.exe"
            self.ff_gecko = Path(self.gecko)
            mozilla_profile = os.path.join(os.getenv('APPDATA'), r'Mozilla\Firefox')
            mozilla_profile_ini = os.path.join(mozilla_profile, r'profiles.ini')
            profile = configparser.ConfigParser()
            profile.read(mozilla_profile_ini)
            self.FF_PRF_DIR_DEFAULT = os.path.normpath(os.path.join(mozilla_profile, profile.get('Profile0', 'Path')))
            ff_gecko = Path(self.gecko)
            if not ff_gecko.is_file():
                import wget
                self.gecko_win64zip = self.gecko_path + '\\' + self.gecko_source_win64.split('/')[-1]
                wget.download(self.gecko_source_win64, self.gecko_path)
                self.file_unzip(self.gecko_win64zip, self.gecko_path)
                os.remove(self.gecko_win64zip)  # self.gecko_path + '\\' +

            if ff_gecko.is_file():
                self.data_path = self.FF_PRF_DIR_DEFAULT
                self.gecko = self.ff_gecko

    def click(self, button):
        page_element = self.driver.find_element_by_css_selector(button).click()
        return page_element

    def input_field(self, field, text):
        page_element = self.driver.find_element_by_css_selector(field)
        page_element.click()
        page_element.send_keys(text)
        return page_element

    def get_hotp_token(self, secret, intervals_no):
        key = base64.b32decode(secret, True)
        msg = struct.pack(">Q", intervals_no)
        h = hmac.new(key, msg, hashlib.sha1).digest()
        o = h[19] & 15
        h = (struct.unpack(">I", h[o:o + 4])[0] & 0x7fffffff) % 1000000
        return h

    def get_totp_token(self, secret):
        return self.get_hotp_token(secret, intervals_no=int(time.time()) // 30)

    def login(self, username='', password=''):
        # self.driver.maximize_window()
        # print(self.driver.get_window_size()) #{'width': 1936, 'height': 1176}
        #self.driver.set_window_size(1936, 700)
        #### LOAD WEBPAGE ###
        time.sleep(5)
        uname = self.driver.find_element_by_name('username')
        uname.send_keys(username)
        pw = self.driver.find_element_by_name('password')
        pw.send_keys(password)
        login = self.driver.find_element_by_xpath('//span[contains(text(),\'Log In\')]/parent::button').click()
        time.sleep(3)
        print('TradingView Login Successful')
        self.get_mg_indicator() #https://www.tradingview.com/script/fY4QMhMJ-test-script-zerpgames/
        time.sleep(3)

    def compare_lists(self,master, slave):
        missing = []
        d = [x.lower() for x in master]
        for m in slave:
            if m.lower() not in d:
                missing.append(m)
        print(missing)
        # self.compare_lists(google_sheet_user_list, tv_users)
        return missing
    def failedtoaddtotv(self, usernamelist):

        import os  # must import this library
        if os.path.exists('failedtoaddtotradingview.txt'):
            os.remove('failedtoaddtotradingview.txt')  # this deletes the file
        else:
            print("The file does not exist")  # add this to prevent errors


        with open("failedtoaddtotradingview.txt", 'w') as filetowrite:
            filetowrite.seek(0)
            for user in usernamelist:
                filetowrite.writelines(user + '\n')
            filetowrite.close()

    def manage_users(self, google_sheet_user_list):
        from lxml.html.soupparser import fromstring
        tv_users = []
        print("Google Sheets Current List : " , google_sheet_user_list)
        #Grab users from TV Manage Access
        wait(self.driver, 6).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Manage Access']"))).click()
        time.sleep(3)
        usercount = self.driver.find_element_by_xpath("//*[@class='tv-text tv-manage-access-dialog__user-list-header js-user-list-header']").text
        usercount = usercount.split(' ')
        usercount = int(usercount[0])
        try:
            # INCOMPLETE LIST PROVIDED - SAVING TO PAGE_SOURCE
            #tv_userlist = self.driver.find_elements_by_class_name('tv-manage-access-dialog__user-list-row')

            htmlsource = self.driver.page_source
            #USE BEAUTIFUL SOUP TO PARSE DIV/CLASS TEXT VALUES.
            names = BS(htmlsource, features="html.parser")
            result = names.find_all("div", {"class":"tv-manage-access-dialog__user-list-row"})
            count = 0
            for res in result:
                tv_users.append(res.text)
                #print(res.text)
                count +=1
            #print("TradingView Current List : ", count, tv_users)
        except:
            print("TV UserList appears to be empty.  Creating empty list.")
            tv_users = []

        #SORT FOR COMPARISON
        google_sheet_user_list.sort()
        tv_users.sort()
        #LOWER CASE TO PREVENT TYPOS
        google_sheet_user_list_lower = [item.lower() for item in google_sheet_user_list]
        tv_users_lower = [item.lower() for item in tv_users]

        if (google_sheet_user_list_lower == tv_users_lower):
            identical = True
            close = self.driver.find_element_by_xpath("//*[@class='tv-dialog__close js-dialog__close']").click()
            return identical
        else:
            addnewusers = self.compare_lists(tv_users, google_sheet_user_list)
            if len(addnewusers) > 0:
                print("ADD USERS TO TRADINGVIEW :", addnewusers)
                self.addusers(addnewusers)
            else:
                print("No users to add to TradingView.")
                print("TradingView NEW USER LIST: ", addnewusers)

            ####  CLOSE MANAGE ACCESS  ####
            close = self.driver.find_element_by_xpath("//*[@class='tv-dialog__close js-dialog__close']").click()
            self.get_mg_indicator()  # https://www.tradingview.com/script/fY4QMhMJ-test-script-zerpgames/
            time.sleep(5)

            #####  TIME TO REMOVE FROM TV IF GOOGLE SHEETS DOESNT HAVE THE USER  #####
            removeoldusers = self.compare_lists(google_sheet_user_list, tv_users)

            if len(removeoldusers) > 0:
                print("REMOVE USERS FROM TRADINGVIEW: ", removeoldusers)
                self.removeusers(removeoldusers, htmlsource)
            else:
                #print("No users to delete from TradingView.")
                print("NO USER TO REMOVE FROM TradingView : .", removeoldusers)
            #####  END TIME TO REMOVE FROM TV IF GOOGLE SHEETS DOESNT HAVE THE USER  #####


    def addusers(self, newusers):
        failedusers = []
        adduser = self.driver.find_element_by_xpath("//input[@name='q'][@type='text']")
        for user in newusers:
            try:
                adduser.send_keys(user)
                time.sleep(3)
                activehighlight = self.driver.find_element_by_xpath("//*[@class='js-user tv-username-hint-list__user i-active']").text
                activehighlight_hintfield = self.driver.find_element_by_xpath("//*[@class='js-user tv-username-hint-list__user i-active']")
                #print(activehighlight)
                time.sleep(3)
                if activehighlight.lower() == user.lower():
                    #print("adding: " + user)
                    activehighlight_hintfield.click()
                    time.sleep(3)
                    tv_userlist = self.driver.find_elements_by_class_name('tv-manage-access-dialog__user-list-row')
                    print("ADDED: " + user)
                else:
                    #IF USER FAILS TO BE ADDED TO LIST DUE TO NO MATCH FOUND.
                    logging.warning('failed to add user : ' + user + ' it appears this user cannot be found.')
                    failedusers.append(user)
                    adduser.clear()
                    pass


            except Exception as e:
                print('Failed to parse user in list for some reason: ', user)
                print("ERROR: ",e)
                failedusers.append(user)
                adduser.clear()

        self.failedtoaddtotv(failedusers)

    def removeusers(self, unsubscribed, htmlsource):
        #print("Missing users in Unsubscribed list:",unsubscribed)
        wait(self.driver, 6).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Manage Access']"))).click()
        time.sleep(3)
        for name in unsubscribed:
            #print( "//div[@data-username='{}']//div[contains(@class,'tv-manage-access-dialog__user-remove-btn')]".format(name))
            try:
                self.driver.find_element_by_xpath(
                    "//div[@data-username='{}']//div[contains(@class,'tv-manage-access-dialog__user-remove-btn')]".format(
                        name)).click()
                print("REMOVED : ",name)

            except Exception as e:
                print(e)


    def schedule(self):
        scheduler = BackgroundScheduler()  # SCHEDULE PAGE REFRESH EVERY 5 MINS
        scheduler.add_job(self.get_google_user_list, 'interval', seconds=60, args=(q, SCOPES,SAMPLE_SPREADSHEET_ID ,SAMPLE_RANGE_NAME))
        #scheduler.add_job(self.get_google_user_list, 'interval', seconds=15)
        scheduler.start()

    def open_coil(self, q, coil_headless=True, browser='firefox', monitor=False):

        if browser == 'firefox':
            try:  # firefox + coil
                # self.options = FireFox_Options()
                # self.options.headless = coil_headless
                self.get_firefox_profile_dir(headless=coil_headless, monitor=monitor)
                self.coil_driver = webdriver.Firefox(options=self.options, firefox_profile=str(self.data_path),
                                                     executable_path=str(self.gecko))
                self.coil_driver.get(self.coilurl)  # OPEN URL
                self.schedule()

            except:
                logging.info('No \' Firefox Browser\' Supported for Coil')

        while True:
            if q.empty():
                pass
            else:
                print(q)
                self.driver.close()


if __name__ == '__main__':
    start = TV(headless=False, browser='firefox',logintype='auto')


