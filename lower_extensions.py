from walk_folders import *
from local_remote_directories import *
from do_changes import *


#####################################
# Lower extension

def _walk_function_lower_extension(file, file_stat):
    del file_stat
    ext_index = file.rfind('.')
    if ext_index != -1:
        extension = file[ext_index:]
        low_extension = extension.lower()
        if extension != low_extension:
            logging.info("Lower extension %s", file)
            if DO_CHANGES:
                os.rename(file, file[0:ext_index] + low_extension)


def lower_extensions():
#    walk_folders(_walk_function_lower_extension, LOCAL_PHOTOS_PIWIGO)
    walk_folders(_walk_function_lower_extension, LOCAL_PHOTOS_ORIGINALS)
#    walk_folders(_walk_function_lower_extension, LOCAL_BACKUP_PHOTOS_PIWIGO)
#    walk_folders(_walk_function_lower_extension, LOCAL_BACKUP_PHOTOS_ORIGINALS)
