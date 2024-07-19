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


def is_sector_different(radio_params):
    """
    Check if the sectors in the provided radio parameters are different.

    Args:
        radio_params (dict): subnetwork, nodes and their sectors

    Returns:
        bool
    """
    nodes = [radio_key for radio_key in radio_params.keys() if radio_key != 'subnetwork']
    sector1 = radio_params[nodes[0]]
    sector2 = radio_params[nodes[1]]

    if len(sector1) == len(sector2):
        return sector1 != sector2

    sector1_number = sector1[:2]
    sector2_number = sector2[:2]
    return sector1_number != sector2_number


def filter_radio_data(radio_data):
    """
    Filter radio data with crosses.

    Args:
        radio_data (dict): result of parsing

    Returns:
        dict
    """
    filtered_radio_data = {}
    for radio, radio_params in radio_data.items():
        if len(radio_params.keys()) == 3 and is_sector_different(radio_params):
            filtered_radio_data[radio] = radio_params
    return filtered_radio_data


def count_crosses(radio_data):
    """
    Count crosses by subnetworks.

    Args:
        radio_data (dict): result of parsing

    Returns:
        dict
    """
    stat = {}
    radio_params = radio_data.values()
    for radio_param in radio_params:
        subnetwork = radio_param['subnetwork']
        if stat.get(subnetwork):
            stat[subnetwork] += 1
        else:
            stat[subnetwork] = 1
    sorted_stat = {subnet: stat[subnet] for subnet in sorted(stat)}
    sorted_stat['Total'] = len(radio_params)
    return sorted_stat


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
    filtered_radio_data = filter_radio_data(radio_data)
    stat = count_crosses(filtered_radio_data)

    return filtered_radio_data, stat
