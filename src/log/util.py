import json

def format_dict(dict_string : dict):
    """
        formats a dictionary. Used improve the quality of din
    """
    return json.dumps(dict_string, indent=4)