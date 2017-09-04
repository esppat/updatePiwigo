import requests

import html5lib

import logging
from init_logger import init_logger


def _get_tag(root, tag, name):
    for child_tag in root:
        if str(child_tag.tag).endswith('}' + tag):
            if 'name' in child_tag.attrib:
                if child_tag.attrib['name'] == name:
                    return child_tag
        found_tag = _get_tag(child_tag, tag, name)
        if found_tag:
            return found_tag
    return None


def internal_piwigo_synchronize():
    url1 = "https://esppat.net/piwigo/ws.php?format=json"
    payload = {'method':'pwg.session.login', 'username':'PatriceE', 'password':'poupinou2'}

    url2 = "https://esppat.net/piwigo/admin.php?page=site_update&site=1"

    s = requests.Session()

    r = s.post(url1, data=payload)

    r = s.get(url2)

    doc = html5lib.parse(r.text)
    tag_select = _get_tag(doc, 'select', 'cat')

    cat_values = []
    for option in tag_select:
        cat_values.append((option.attrib['value'], option.text))

    url3 = "https://esppat.net/piwigo/admin.php?page=site_update&site=1"

    for cat_value, cat_name in cat_values:
        payload = {'sync':'files',
                   'display_info':0,
                   'add_to_caddie':0,
                   'privacy_level':0,  #everyone
                   'simulate':0,
                   'cat':cat_value,
                   'subcats-included':0,
                   'submit':1,
                   'sync_meta':1,
                   'meta_all':1,
                   'meta_empty_overrides':1}
        r = s.post(url3, data=payload)
        logging.info('Cat = %s (%s)', cat_value, cat_name)


if __name__ == "__main__":
    init_logger(logfile_name='/home/esppat/Temp/internal_piwigo_synchronize.log')

    logging.info('Internal Piwigo Synchronize')
    internal_piwigo_synchronize()

