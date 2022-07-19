import os
import time
import smtplib
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

def send_email(from_addr, to_addr, subject, password,content):
    msg = MIMEText(content,'html','utf-8')
    msg['From'] = u'<{}>'.format(from_addr)
    msg['To'] = u'<{}>'.format(to_addr)
    msg['Subject'] = subject

    smtp = smtplib.SMTP_SSL('smtp.163.com', 465)
    smtp.set_debuglevel(1)
    smtp.ehlo("smtp.163.com")
    smtp.login(from_addr, password)
    smtp.sendmail(from_addr, [to_addr], msg.as_string())

if __name__ == "__main__":
    var=os.popen('tail -1 finish')
    var=var.read().rstrip()
    while True:
        try:
            last=os.popen('tail -1 finish').read().rstrip()
            if last!=var:
                send_email(u'15950591052@163.com',u"15950591052@163.com",u"Done!",u"zh131452",last)
                var=last
        except Exception as e:
            with open('log','a+')as f:
                f.write(e)
        time.sleep(5)
