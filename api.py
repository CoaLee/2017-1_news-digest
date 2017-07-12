from flask import Flask, jsonify, abort, json, make_response
from config import LATEST_API
import logging
from logging.handlers import RotatingFileHandler

#import logging.logging
#from logging.handlers import SMTPHandler
#from email_account import EMAIL_ID, EMAIL_PW
#import logging.handlers
 
# from dummy_db import sections, headlines, articles

app = Flask(__name__)
'''
ADMINS = ['coaleeyong@gmail.com', 'dukeow@naver.com']
mail_handler = SMTPHandler(('smtp.gmail.com', 587),
    'coaleeyong@gmail.com',
    ADMINS, 
    'Failed',
    (EMAIL_ID, EMAIL_PW),
    ()
)
mail_handler.setLevel(logging.ERROR)
app.logger.addHandler(mail_handler)
'''
'''
class TlsSMTPHandler(logging.handlers.SMTPHandler):
    def emit(self, record):
        """
        Emit a record.
 
        Format the record and send it to the specified addressees.
        """
        try:
            import smtplib
            import string # for tls add this line
            try:
                from email.utils import formatdate
            except ImportError:
                formatdate = self.date_time
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port)
            msg = self.format(record)
            msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                            self.fromaddr,
                            string.join(self.toaddrs, ","),
                            self.getSubject(record),
                            formatdate(), msg)
            if self.username:
                smtp.ehlo() # for tls add this line
                smtp.starttls() # for tls add this line
                smtp.ehlo() # for tls add this line
                smtp.login(self.username, self.password)
            smtp.sendmail(self.fromaddr, self.toaddrs, msg)
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
 
logger = logging.getLogger()
 
gm = TlsSMTPHandler(("smtp.gmail.com", 587), 'coaleeyong@gmail.com', ADMINS, 'Error found!', (EMAIL_ID, EMAIL_PW))
gm.setLevel(logging.ERROR)
 
logger.addHandler(gm)
'''
API_ADDRESS = '/news_digest/api/'
API_VERSION = LATEST_API
CURRENT_API = API_ADDRESS + API_VERSION + '/' 

# to ensure unicode transmitted unbroken
app.config['JSON_AS_ASCII'] = False
def kor_jsonify(somedict):
    res = jsonify(somedict)
    res.headers['Content-Type'] += '; charset=utf-8'
    return res 

@app.route(API_ADDRESS)
def version_notice():
    return "Latest API version is {}. Try 'GET [api_address]{}'\n".format(API_VERSION, CURRENT_API)

if __name__ == '__main__':
    handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    #app.run(host='0.0.0.0', debug=True)
    app.run(host='0.0.0.0', port=80, debug=True)
    '''
    gm = TlsSMTPHandler(("smtp.gmail.com", 587), 'coaleeyong@gmail.com', ADMINS, 'Error found!', (EMAIL_ID, EMAIL_PW))
    gm.setLevel(logging.ERROR)
    app.logger.addHandler(gm)
    '''
