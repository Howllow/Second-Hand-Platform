import logging


def check(key_list, given_dict, task):
    for key in key_list:
        if key not in given_dict:
            logging.debug(F'key:{key}, not in given data, in task {task}!!! Exit...')
            return 0
        return 1


def is_keyword(keyword, name):
    if keyword in name:
        return 1
    else:
        return 0
