import os

import enmscripting
from dotenv import load_dotenv

load_dotenv()


def cmedit_get(enm, command):
    """
    Execute ENM CLI cmedit get commad with given enm and command.

    Args:
        enm (str): the ENM server to connect to
        command (str): cmedit get command

    Returns:
        list: the response from the ENM after executing the CLI command
    """
    if enm == 'ENM4':
        enm_server = os.getenv('ENM_SERVER_4')
    elif enm == 'ENM2':
        enm_server = os.getenv('ENM_SERVER_2')

    session = enmscripting.open(enm_server).with_credentials(
        enmscripting.UsernameAndPassword(
            os.getenv('ENM_LOGIN'),
            os.getenv('ENM_PASSWORD'),
        ),
    )
    enm_cmd = session.command()
    response = enm_cmd.execute(command)
    enmscripting.close(session)
    return response.get_output()


def _filter_enm_data(enm_data):
    """
    Filter enm data where FieldReplaceableUnit is shared.

    Args:
        enm_data: a list of ENM ElementGroups with radio data

    Returns:
        a list of strings
    """
    filtered_data = []

    fdn = ''
    is_shared = ''
    product_data = ''

    for row in enm_data:
        row_value = row.value()
        if 'FDN' in row_value:
            fdn = row_value
        if 'isSharedWithExternalMe' in row_value:
            is_shared = row_value
        if 'productData' in row_value:
            product_data = row_value
            if 'true' in is_shared:
                filtered_data.append(fdn)
                filtered_data.append(product_data)
    return filtered_data


def get_radio_data():
    """
    Get radio data from enms.

    Returns:
        list: a list of ENM ElementGroups with radio data
    """
    enms = ('ENM4', 'ENM2')
    command_scope_mo = 'cmedit get * FieldReplaceableUnit.'
    mo_params = '(isSharedWithExternalMe,productData)'
    command = command_scope_mo + mo_params
    enm_data = [
        enm_item for enm in enms for enm_item in cmedit_get(enm, command)
    ]
    return _filter_enm_data(enm_data)
