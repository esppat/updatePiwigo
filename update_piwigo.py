from walk_folders import *
from sync_folders import *
from init_logger import init_logger
from local_remote_directories import *
from face_tags import transfert_picasa_to_piwigo_face_tags
from lower_extensions import lower_extensions
from normalize_src_file_to_dst_file import synchronize_picture_and_video_normalization


#####################################
# Picasa to Piwigo face tags

def walk_function_picasa_to_piwigo_face_tags(file, file_stat):
    del file_stat
    try:
        transfert_picasa_to_piwigo_face_tags(file)
    except:
        pass


def picasa_to_piwigo_face_tags():
    walk_folders(walk_function_picasa_to_piwigo_face_tags, LOCAL_PHOTOS_ORIGINALS)


#####################################
# Normalize source files

def normalize_source_files():
    sync_folders(LOCAL_PHOTOS_ORIGINALS, LOCAL_PHOTOS_PIWIGO, add_only=False,
                 synchronize_function=synchronize_picture_and_video_normalization)


#####################################
# Copy files


def synchronize_trees():
    sync_folders(LOCAL_PHOTOS_ORIGINALS,    LOCAL_BACKUP_PHOTOS_ORIGINALS,  add_only=False)
    sync_folders(LOCAL_PHOTOS_PIWIGO,       LOCAL_BACKUP_PHOTOS_PIWIGO,     add_only=False)
    sync_folders(LOCAL_PHOTOS_PIWIGO,       REMOTE_PHOTOS_PIWIGO,           add_only=False)
    sync_folders(LOCAL_PHOTOS_ORIGINALS,    REMOTE_BACKUP_PHOTOS_ORIGINALS, add_only=False)


#####################################
# Main program

if __name__ == "__main__":
    init_logger(logfile_name='/home/esppat/Temp/fullprocess.log')

    logging.info('Lowering extensions')
    lower_extensions()

    logging.info('Start picasaToPiwigoFaceTags')
    picasa_to_piwigo_face_tags()

    logging.info('Normalize source files')
    normalize_source_files()

    logging.info('Synchronize trees')
    synchronize_trees()
