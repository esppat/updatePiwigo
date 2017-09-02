import os
from init_logger import *

from local_remote_directories import *
from common_extensions import *
from sync_folders import *


def _find_folder(source, subSource):
    for root, _, _ in os.walk(source):
        if str(root).endswith(subSource):
            yield root

            
def _find_identifier_dir(possibleSource, subSource, identifierDirs):
    for root, identifierDir, transferExtension in identifierDirs:
        # search up
        curDir = subSource
        while curDir != possibleSource:
            if str(curDir).endswith(identifierDir):
                return root, str(curDir), transferExtension
            curDir = str(os.path.pardir(curDir))
        # search down
        for curDir, _, _ in os.walk(subSource):
            if str(curDir).endswith(identifierDir):
                return root, str(curDir), transferExtension
    return None, None


def collect_photos_and_videos():
    logging.info('Start collectPhotosAndVideos')

    possibleSources = ['/media/esppat',
                       '/run/user/1000/gvfs',
                       '/mnt/C_DRIVE/Users/pespie/Google Drive/Google Photos']

    possibleSubSources = ['gphoto2:host=%5Busb%3A002%2C027%5D/DCIM',
                          'gphoto2:host=%5Busb%3A002%2C028%5D/DCIM',
                          'disk/DCIM',
                          'disk/PRIVATE/AVCHD/BDMV/STREAM',
                          'Google Photos']

    identifierDirs = [(LOCAL_PHOTOS_TRANSFER,                   'Mémoire de stockage interne',  'Téléphone'),
                      (LOCAL_PHOTOS_TRANSFER,                   'DCIM/100NIKON',                'Appareil photo'),
                      (LOCAL_PHOTOS_TRANSFER,                   'PRIVATE/AVCHD/BDMV/STREAM',    'Caméscope (vidéos)'),
                      (LOCAL_PHOTOS_TRANSFER,                   'disk/DCIM',                    'Caméscope (photos)'),
                      (LOCAL_PHOTOS_TRANSFER,                   'DCIM/100MEDIA',                'Caméra sport'),
                      ('/mnt/E_DRIVE/Piwigo/photos-transfer',   'Google Photos',                'Google Photos')]
    
    threads = []
    
    for possibleSource in possibleSources:
        for possibleSubSource in possibleSubSources:
            for subSource in _find_folder(possibleSource, possibleSubSource):
                root, identifierDir, transferExtension = _find_identifier_dir(possibleSource, subSource, identifierDirs)
                if identifierDir:
                    destDir = root + '/' + transferExtension
                    logging.info('Found source match : %s and %s', subSource, destDir)
                    sync_folders(subSource, destDir, add_only=True)

    logging.info('Done collectPhotosAndVideos')

if __name__ == "__main__":
    init_logger(logfile_name='/home/esppat/Temp/collectphotosandvideos.log')
    
    collect_photos_and_videos()
