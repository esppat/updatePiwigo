import logging
import os
import shutil
from do_changes import *
from common_extensions import *


def readable_byte_size(size):
    result = '' + str(size % 1024) + ' B'
    if size > 1024:  # KB
        result = str((size // 1024) % 1024) + ' KB ' + result
        if size > 1024*1024:  # MB
            result = str((size // (1024 * 1024)) % 1024) + ' MB ' + result
            if size > 1024 * 1024 * 1024:  # GB
                result = str((size // (1024 * 1024 * 1024)) % 1024) + ' GB ' + result
                if size > 1024 * 1024 * 1024 * 1024:  # TB
                    result = str((size // (1024 * 1024 * 1024 * 1024)) % 1024) + ' TB ' + result
    return result


def _walk_file(walk_function, a_dir, files, files_stat):
    for index, file in enumerate(files):
        file_stat = files_stat[index]
        walk_function(str(a_dir + '/' + file), file_stat)


def _walk(walk_function, root, current_dir):
    a_dir = root + current_dir

    if not os.path.isdir(a_dir):
        logging.info("Skip walking %s (does not exist)", a_dir)
        return

    total_dirs_count = 1
    total_files_count = 0
    total_files_size = 0

    dirs = []
    files = []
    files_stat = []
    for entry in os.scandir(a_dir):
        if entry.is_dir():
            dirs.append(entry.name)
        else:
            known_extension = False
            for extension in PHOTOS_VIDEOS_EXTENSIONS:
                if entry.name.lower().endswith(extension):
                    known_extension = True
                    break
            if known_extension:
                files.append(entry.name)
                stat_res = entry.stat()
                total_files_size += stat_res.st_size
                files_stat.append(stat_res)

    total_files_count += len(files)

    yield current_dir, total_dirs_count, total_files_count, total_files_size

    _walk_file(walk_function, a_dir, files, files_stat)

    for nextDir in dirs:
        for current_dir, dirs_count, files_count, files_size in _walk(walk_function, a_dir, '/' + nextDir):
            yield current_dir, dirs_count, files_count, files_size


def walk_folders(walk_function, root):
    if not isinstance(root, str):
        root = str(root)

    logging.info("Walking %s", root)
    total_dirs_count = 0
    total_files_count = 0
    total_files_size = 0

    for current_dir, dirs_count, files_count, files_size in _walk(walk_function, root, ''):
        total_dirs_count += dirs_count
        total_files_count += files_count
        total_files_size += files_size
        logging.info("dirs=%d, files=%d, files size=%s : %s", total_dirs_count,
                     total_files_count, readable_byte_size(total_files_size), current_dir)

    logging.info("Walking %s : done", root)
