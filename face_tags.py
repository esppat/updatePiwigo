import gi
import logging
from do_changes import *
gi.require_version('GExiv2', '0.10')
from gi.repository import GExiv2


search_person_tags = [('Xmp.mwg-rs.Regions/mwg-rs:RegionList[', ']/mwg-rs:Name'),
                      ('Xmp.MP.RegionInfo/MPRI:Regions[', ']/MPReg:PersonDisplayName')]


def _transfer_tags(current_file, metadata):
    if metadata.has_tag('Iptc.Application2.Keywords'):
        person_names = set(metadata.get_tag_multiple('Iptc.Application2.Keywords'))
    else:
        person_names = set()
    original_person_names = set(person_names)
    for person_num in range(1, 1000):
        for tag_begin, tag_end in search_person_tags:
            current_tag = tag_begin + str(person_num) + tag_end
            if metadata.has_tag(current_tag):
                current_person_name = metadata[current_tag]
                if current_person_name not in original_person_names:
                    logging.info('%s = %s', str(person_num), current_person_name)
                    person_names.add(current_person_name)
    if len(person_names) > len(original_person_names):
        if DO_CHANGES:
            metadata.set_tag_multiple('Iptc.Application2.Keywords', list(person_names))
            metadata.save_file()
        logging.info("%s ... face tags copied from XMP to IPTC", current_file)


def transfert_picasa_to_piwigo_face_tags(current_file):
    metadata = GExiv2.Metadata(str(current_file))
    has_face_tags = False
    for tag_begin, tag_end in search_person_tags:
        if metadata.has_tag(tag_begin + '1' + tag_end):
            has_face_tags = True
            break
    if has_face_tags:
        _transfer_tags(current_file, metadata)
