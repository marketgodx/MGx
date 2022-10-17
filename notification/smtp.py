from pprint import pprint
# YouTube Video: https://www.youtube.com/watch?v=mP_Ln-Z9-XY
import smtplib
import json
from logging_settings import *



def send_email(subject, msg):
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(source_email, email_password)
        message = 'Subject: {}\n\n{}'.format(subject, msg)
        server.sendmail(dest_email, dest_email, message)
        server.quit()
        print("Success: Email sent!")
        log_smtp.info(msg)
    except:
        print("Email failed to send.")
        log_smtp.warning('EMAIL FAILED')

##################  END FINAL EMAIL SETTINGS ########################


if __name__ == '__main__':
    ###############  OPEN SMTP CONFIG ################
    with open('config.json', 'r') as smtp_config:
        smtp_data = json.load(smtp_config)

        ##################  FINAL EMAIL SETTINGS ############################
        source_email = smtp_data['EMAIL_ADDRESS']
        dest_email = smtp_data['DEST_EMAIL']
        email_password = smtp_data['PASSWORD']  # password_verification()
        ##############  END FINAL EMAIL SETTINGS ############################

        send_email('test','test')
else:

    ###############  OPEN SMTP CONFIG ################
    with open('notification/config.json', 'r') as smtp_config:
        smtp_data = json.load(smtp_config)
    # pprint(smtp_data)

    ##################  FINAL EMAIL SETTINGS ############################
    source_email = smtp_data['EMAIL_ADDRESS']
    dest_email = smtp_data['DEST_EMAIL']
    email_password = smtp_data['PASSWORD']  # password_verification()
    ##############  END FINAL EMAIL SETTINGS ############################


#subject = "TEST NOTICE"
#msg = "New source settings."
#send_email(subject, msg)

