import os

from anpusr_mail import send_email
from radio_cross.enm import get_radio_data
from radio_cross.parser import parse_radio_data
from radio_cross.report import fill_report


def make_radio_cross_report():
    """Make report about cross connections in shared radios."""
    enm_radio_data = get_radio_data()
    radio_data, stat = parse_radio_data(enm_radio_data)
    report_path = fill_report(radio_data)

    message = [
        'Good day!\n',
        'Please find the Radio Cross report in attachment.\n\n',
        'Cross statistics:\n',
    ]

    for subnetwork, cross_count in stat.items():
        message.append(f'{subnetwork}: {cross_count}\n')

    msg = ''.join(message)

    to = os.getenv('TO').split(',')
    subject = 'Radio Crosses'
    send_email(to, subject, msg, report_path)
