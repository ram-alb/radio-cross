from openpyxl import Workbook
from openpyxl.utils.cell import get_column_letter


def fill_headers(sheet):
    """
    Fill headers for radio cross report in excel.

    Args:
        sheet (openpyxl sheet obj): an active sheet
    """
    headers = [
        'Serial',
        'Radio',
        'Site1',
        'Site1 sector',
        'Site2',
        'Site2 sector',
        'is Same',
    ]

    for column, header in enumerate(headers, start=1):
        sheet.cell(row=1, column=column, value=header)


def fill_radio_params(sheet, row, radio_params):
    """
    Fill sitename and sector for radio into excel report.

    Args:
        sheet (openpyxl sheet obj): an active sheet
        row (int): a row number
        radio_params (dict): keys - sitename, values - sector used a radio
    """
    col = 3
    for sitename, sector in radio_params.items():
        sheet.cell(row=row, column=col, value=sitename)
        col += 1
        sheet.cell(row=row, column=col, value=sector)
        col += 1


def fill_report(radio_data):
    """
    Fill radio cross information to excel report.

    Args:
        radio_data (dict): keys - radio serials, values - dict with radio data

    Returns:
        str: a report path
    """
    work_book = Workbook()
    sheet = work_book.active

    fill_headers(sheet)

    row = 2
    for radio, radio_params in radio_data.items():
        if len(radio_params.keys()) != 2:
            continue
        serial, radio_type = radio.split(':')
        sheet.cell(row=row, column=1, value=serial)
        sheet.cell(row=row, column=2, value=radio_type)

        fill_radio_params(sheet, row, radio_params)

        cell1_column = get_column_letter(4)
        cell2_column = get_column_letter(6)
        sheet.cell(
            row=row,
            column=7,
            value=f'={cell1_column}{row}={cell2_column}{row}',
        )
        row += 1

    report_path = 'reports/radio_cross.xlsx'
    work_book.save(report_path)
    return report_path
