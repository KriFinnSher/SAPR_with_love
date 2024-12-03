import re


def natural_positive_number(val):
    pattern = r'^([1-9]\d*|)$'
    return re.match(pattern, val) is not None


def rational_positive_number(val):
    pattern = r'^(0(\.\d*)?|[1-9]\d*(\.\d*)?)?$'
    return re.match(pattern, val) is not None


def rational_number(val):
    pattern = r'^-?(0(\.\d*)?|[1-9]\d*(\.\d*)?)?$'
    return re.match(pattern, val) is not None

