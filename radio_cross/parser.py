import re


def parse_fdn(fdn, mo_type):
    """
    Parse the MO value from a Full Distinguished Name (FDN).

    Args:
        fdn (str): the FDN string to parse
        mo_type (str): the type of MO to parse from the FDN (e.g. 'SubNetwork')

    Returns:
        str: the value of the specified MO in the FDN string
    """
    re_patterns = {
        'MeContext': 'MeContext=[^,]*',
        'FieldReplaceableUnit': 'FieldReplaceableUnit=.*',
        'SubNetwork': ',SubNetwork=[^,]*',
    }

    mo_value_index = -1
    if mo_type == 'MeContext':
        try:
            mo = re.search(re_patterns['MeContext'], fdn).group()
        except AttributeError:
            mo = re.search(re_patterns['ManagedElement'], fdn).group()
    else:
        mo = re.search(re_patterns[mo_type], fdn).group()

    return mo.split('=')[mo_value_index]


def parse_product_data(enm_product_data):
    """
    Parse radio's product data.

    Args:
        enm_product_data (str): parameter wich contains serial and product name

    Returns:
        tuple: a tuple of serial number and product name for the radio
    """
    try:
        serial_number_data = re.search(
            'serialNumber=[^,]*',
            enm_product_data,
        ).group()
        serial_number = serial_number_data.split('=')[-1]
    except AttributeError:
        serial_number = None

    try:
        product_name_data = re.search(
            'productName=[^,]*',
            enm_product_data,
        ).group()
        product_name = product_name_data.split('=')[-1]
    except AttributeError:
        product_name = None

    return serial_number, product_name


def parse_sector(field_unit):
    """
    Parse sector where radio installed.

    Args:
        field_unit (str): a ENM MO which identifies radio

    Returns:
        str: a sector identifier for the radio
    """
    try:
        sector_number = re.search(r'S\d', field_unit).group()
    except AttributeError:
        return None
    last_label = field_unit[-1]
    if last_label in {'L', 'R'}:
        return f'{sector_number}-{last_label}'
    return sector_number


def add_radio_data(radio_data, subnetwork, node_name, sector, serial_number, product_name):
    """
    Add radio data parsed from ENM CLI output to result dict.

    Args:
        radio_data (dict): result of parsing
        subnetwork (str): a subnetwork name
        node_name (str): a site name
        sector (str): a sector where radio installed
        serial_number (str): a serial number of the radio
        product_name (str): a radio's product name
    """
    if None not in {sector, serial_number, product_name}:
        key = f'{serial_number}:{product_name}'
        radio_data.setdefault(key, {})['subnetwork'] = subnetwork
        if sector not in radio_data[key].values():
            radio_data[key][node_name] = sector


def parse_radio_data(enm_radio_data):
    """
    Parse radio data from enm data.

    Args:
        enm_radio_data (ENM ElementGroup): a tuple of elements
            representing the output from the command

    Returns:
        dict: keys defines the radio, vlaues - dicts with nodename and sector
    """
    radio_data = {}

    for element in enm_radio_data:
        element_val = element.value()
        if 'FDN' in element_val:
            subnetwork = parse_fdn(element_val, 'SubNetwork')
            node_name = parse_fdn(element_val, 'MeContext')
            field_unit = parse_fdn(element_val, 'FieldReplaceableUnit')
            sector = parse_sector(field_unit)
        elif 'productData' in element_val and 'S' in field_unit:
            serial_number, product_name = parse_product_data(element_val)
            add_radio_data(
                radio_data,
                subnetwork,
                node_name,
                sector,
                serial_number,
                product_name,
            )

    return radio_data
