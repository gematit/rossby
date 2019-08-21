"""Routine to send e-mail with information including last 10 lines of log file."""

import smtplib
from email.message import EmailMessage
from os import access, R_OK
from os.path import isfile
from subprocess import Popen, PIPE


def send_report(e_mail=None, subject='Report', log_name=None):
    """Send e-mail with information including last 10 lines of log file.
    The sender's address is nannyrobot009@gmail.com

    Args:
        e_mail (str, optional): E-mail to send the report
        subject (str, optional): Subject of the mail (default: Report)
        log_name (str, optional): Path to the log file

    Examples:
        send_report(e_mail=name@yourmail.com, subject='Report about wrf run', log_name='/path/to/wrf.log')
    """

    username = 'nannyrobot009'
    password = 'wihzof-Pupxez-kawjy3'
    smtp_server = 'smtp.gmail.com'
    port = 465
    from_name = username + '@gmail.com'
    signature = '\n\n---------------------------------\nI hope your program finished succesfully\n' \
                + chr(0x1F916) + chr(0x1F609)

    if e_mail is None:
        print('No e-mail to send')
        return

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_name
    msg['To'] = e_mail

    if log_name is not None:
        if not(isfile(log_name) and access(log_name, R_OK)):
            msg.set_content('Log file {} doesn\'t exist or isn\'t readable '.format(log_name) +
                            chr(0x1F914) +
                            signature)
        else:
            msg.set_content('THE LAST 10 LINES OF FILE {}:\n'.format(log_name) +
                            Popen('tail {}'.format(log_name), shell=True, stdout=PIPE).stdout.read().decode("utf-8") +
                            signature)
    else:
        msg.set_content(signature)

    with smtplib.SMTP_SSL(smtp_server, port) as server:
        server.login(username, password)
        server.send_message(msg)
