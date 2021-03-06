import re, json
isoDict = {'AED': 784, 'AFN': 971, 'ALL': 8, 'AMD': 51, 'ANG': 532, 'AOA': 973, 'ARS': 32, 'AUD': 36, 'AWG': 533, 'AZN': 944, 'BAM': 977, 'BBD': 52, 'BDT': 50, 'BGN': 975, 'BHD': 48, 'BIF': 108, 'BMD': 60, 'BND': 96, 'BOB': 68, 'BOV': 984, 'BRL': 986, 'BSD': 44, 'BTN': 64, 'BWP': 72, 'BYN':933, 'BYR': 974, 'BZD': 84, 'CAD': 124, 'CDF': 976, 'CHE': 947, 'CHF': 756, 'CHW': 948, 'CLF': 990, 'CLP': 152, 'CNY': 156, 'COP': 170, 'COU': 970, 'CRC': 188, 'CUC': 931, 'CUP': 192, 'CVE': 132, 'CZK': 203, 'DJF': 262, 'DKK': 208, 'DOP': 214, 'DZD': 12, 'EEK': 233, 'EGP': 818, 'ERN': 232, 'ETB': 230, 'EUR': 978, 'FJD': 242, 'FKP': 238, 'GBP': 826, 'GEL': 981, 'GHS': 936, 'GIP': 292, 'GMD': 270, 'GNF': 324, 'GTQ': 320, 'GYD': 328, 'HKD': 344, 'HNL': 340, 'HRK': 191, 'HTG': 332, 'HUF': 348, 'IDR': 360, 'ILS': 376, 'INR': 356, 'IQD': 368, 'IRR': 364, 'ISK': 352, 'JMD': 388, 'JOD': 400, 'JPY': 392, 'KES': 404, 'KGS': 417, 'KHR': 116, 'KMF': 174, 'KPW': 408, 'KRW': 410, 'KWD': 414, 'KYD': 136, 'KZT': 398, 'LAK': 418, 'LBP': 422, 'LKR': 144, 'LRD': 430, 'LSL': 426, 'LTL': 440, 'LVL': 428, 'LYD': 434, 'MAD': 504, 'MDL': 498, 'MGA': 969, 'MKD': 807, 'MMK': 104, 'MNT': 496, 'MOP': 446, 'MRU': 478, 'MUR': 480, 'MVR': 462, 'MWK': 454, 'MXN': 484, 'MXV': 979, 'MYR': 458, 'MZN': 943, 'NAD': 516, 'NGN': 566, 'NIO': 558, 'NOK': 578, 'NPR': 524, 'NZD': 554, 'OMR': 512, 'PAB': 590, 'PEN': 604, 'PGK': 598, 'PHP': 608, 'PKR': 586, 'PLN': 985, 'PYG': 600, 'QAR': 634, 'RON': 946, 'RSD': 941, 'RUB': 643, 'RWF': 646, 'SAR': 682, 'SBD': 90, 'SCR': 690, 'SDG': 938, 'SEK': 752, 'SGD': 702, 'SHP': 654, 'SLL': 694, 'SOS': 706, 'SRD': 968, 'STD': 678, 'SYP': 760, 'SZL': 748, 'THB': 764, 'TJS': 972, 'TMT': 795, 'TND': 788, 'TOP': 776, 'TRY': 949, 'TTD': 780, 'TWD': 901, 'TZS': 834, 'UAH': 980, 'UGX': 800, 'USD': 840, 'USN': 997, 'USS': 998, 'UYU': 858, 'UZS': 860, 'VEF': 937, 'VND': 704, 'VUV': 548, 'WST': 882, 'XAF': 950, 'XAG': 961, 'XAU': 959, 'XBA': 955, 'XBB': 956, 'XBC': 957, 'XBD': 958, 'XCD': 951, 'XDR': 960, 'XOF': 952, 'XPD': 964, 'XPF': 953, 'XPT': 962, 'XTS': 963, 'XXX': 999, 'YER': 886, 'ZAR': 710, 'ZMK': 894, 'ZWL': 932}

def isoNumToName(num: int):
    for x in isoDict.items():
        if num == x[1]: return x[0]
    raise ValueError(f"Could not find currency in ISO 4217 (by num) num={num}")

def isoNameToNum(name: str):
    for x in isoDict.items():
        if name == x[0]: return x[1]
    raise ValueError(f"Could not find currency in ISO 4217 (by name) name={name}")

def is_dict(var):
    return isinstance(var, dict)

def is_str(var):
    return isinstance(var, str)

def is_list(var):
    return isinstance(var, list)

def is_URL_Valid(val):

    #from https://stackoverflow.com/a/7160778
    regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, val) is not None

def to_JSON(data):

    return json.dumps(data)

def find_in(obj, find:str, searchDesc:bool = False):

    if hasattr(obj, "Statements"):
        ret = []
        if not searchDesc:
            for x in obj.Statements.items():
                if x[0].find(find) >= 0:
                    ret.append(x[1])
        else:
            for x in obj.Statements.items():
                if x[0].find(find) >=0 or x[1].Description.find(find) >= 0:
                    ret.append(x[1])
    elif hasattr(obj, "Accounts"):
        ret = []
        for x in obj.Accounts.items():
            if x[0].find(find) >= 0:
                ret.append(x[1])
    else:
        raise TypeError("obj is not MonoPersonalData or MonoStatements")
    return ret
        