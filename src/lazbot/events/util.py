import re


def unicode_clean(txt):
    return str(re.sub(r'[^\x00-\x7f]', r'?', txt))
