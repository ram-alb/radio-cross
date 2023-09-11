from anpusr_mail import send_email
from radio_cross.enm import get_radio_data
from radio_cross.parser import parse_radio_data
from radio_cross.report import fill_report


def make_radio_cross_report():
    """Make report about cross connections in shared radios."""
    enm_radio_data = get_radio_data()
    radio_data = parse_radio_data(enm_radio_data)
    report_path = fill_report(radio_data)

    to = ['Ramil.Albakov@kcell.kz']
    subject = 'Radio Crosses'
    message = 'Good day!\n Please find the Radio Cross report in attachment.'
    send_email(to, subject, message, report_path)
