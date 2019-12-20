import configparser

CONFIG_FILE = 'settings.ini'

def convert_to_list(s):
    list = []
    splitted = s.split(';')
    for item in splitted:
        if item.isdigit():
            item = int(item)
        else:
            try:
                item = float(item)
            except:
                pass
        list.append(item)
    return list

def create_config(config_file=None):
    parser = configparser.ConfigParser(converters={'list':convert_to_list}, interpolation=configparser.ExtendedInterpolation())
    parser.read(config_file or CONFIG_FILE)
    return parser

CONFIG = create_config()

def get_config():
    return CONFIG
