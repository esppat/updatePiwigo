import logging
import os
import shutil
from do_changes import *
from common_extensions import *
from walk_folders import readable_byte_size


def _synchronize_trees(src_dir, src_dirs, src_files, src_files_stat, dst_dir, dst_dirs, dst_files,
                       dst_files_stat, add_only):
    for a_dir in src_dirs:
        if a_dir not in dst_dirs:
            logging.info("Must create dst dir '%s'", dst_dir + '/' + a_dir)
            if DO_CHANGES:
                os.mkdir(dst_dir + '/' + a_dir)
    for index, file in enumerate(src_files):
        must_sync = False
        src_stat = src_files_stat[index]
        if file not in dst_files:
            logging.info("Must create '%s'", dst_dir + '/' + file)
            must_sync = True
        else:
            dst_stat = dst_files_stat[dst_files.index(file)]
            if src_stat.st_size != dst_stat.st_size:
                logging.info("Size mismatch: '%s'", dst_dir + '/' + file)
                must_sync = True
            elif src_stat.st_mtime > dst_stat.st_mtime + 300:
                logging.info("Date mismatch: '%s'", dst_dir + '/' + file)
                must_sync = True
        if must_sync:
            src_file = str(src_dir + '/' + file)
            dst_file = str(dst_dir + '/' + file)
            logging.info("Copy (%s) %s", readable_byte_size(src_stat.st_size), src_file)
            if DO_CHANGES:
                try:
                    shutil.copy2(src_file, dst_file)
                except:
                    logging.error('Cannot copy file %s', src_file)

    if not add_only:
        for a_dir in dst_dirs:
           if a_dir not in src_dirs:
                logging.info("Must delete dst dir '%s'", dst_dir + '/' + a_dir)
                if DO_CHANGES:
                    shutil.rmtree(dst_dir + '/' + a_dir)
        for file in dst_files:
            if file not in src_files:
                logging.info("Must delete dst file '%s'", dst_dir + '/' + file)
                if DO_CHANGES:
                    os.remove(dst_dir + '/' + file)


def _sync(root_src, root_dst, current_dir, add_only, synchronize_function):
    src_dir = root_src + current_dir
    dst_dir = root_dst + current_dir

    if not os.path.isdir(dst_dir):
        os.mkdir(dst_dir)

    total_src_dirs_count = 1
    total_src_files_count = 0
    total_src_files_size = 0

    src_dirs = []
    src_files = []
    src_files_stat = []
    for entry in os.scandir(src_dir):
        if entry.is_dir():
            src_dirs.append(entry.name)
        else:
            known_extension = False
            for extension in PHOTOS_VIDEOS_EXTENSIONS:
                if entry.name.lower().endswith(extension):
                    known_extension = True
                    break
            if known_extension:
                src_files.append(entry.name)
                stat_res = entry.stat()
                total_src_files_size += stat_res.st_size
                src_files_stat.append(stat_res)

    total_src_files_count += len(src_files)

    dst_dirs = []
    dst_files = []
    dst_files_stat = []
    for entry in os.scandir(dst_dir):
        if entry.is_dir():
            dst_dirs.append(entry.name)
        else:
            known_extension = False
            for extension in PHOTOS_VIDEOS_EXTENSIONS:
                if entry.name.lower().endswith(extension):
                    known_extension = True
                    break
            if known_extension:
                dst_files.append(entry.name)
                stat_res = entry.stat()
                dst_files_stat.append(stat_res)

    yield current_dir, total_src_dirs_count, total_src_files_count, total_src_files_size

    synchronize_function(src_dir, src_dirs, src_files, src_files_stat, dst_dir, dst_dirs, dst_files,
                         dst_files_stat, add_only)

    for a_dir in sorted(src_dirs):
        for current_dir, src_dirs_count, src_files_count, src_files_size in _sync(src_dir, dst_dir, '/' + a_dir,
                                                                                  add_only, synchronize_function):
            yield current_dir, src_dirs_count, src_files_count, src_files_size


def sync_folders(root_src, root_dst, add_only, synchronize_function=_synchronize_trees):

    if not isinstance(root_src, str):
        root_src = str(root_src)
    if not isinstance(root_dst, str):
        root_dst = str(root_dst)

    if not os.path.isdir(root_src):
        logging.info("Skip sync folders : source does not exist : %s", root_src)
        return

    if not os.path.isdir(root_dst):
        logging.info("Skip sync folders : destination does not exist : %s", root_dst)
        return

    logging.info("Syncing %s to %s", root_src, root_dst)
    total_src_dirs_count = 0
    total_src_files_count = 0
    total_src_files_size = 0

    for current_dir, src_dirs_count, src_files_count, src_files_size in _sync(root_src, root_dst, '', add_only,
                                                                              synchronize_function):
        total_src_dirs_count += src_dirs_count
        total_src_files_count += src_files_count
        total_src_files_size += src_files_size
        logging.info("src dirs=%d, src files=%d, src files size=%s : %s", total_src_dirs_count,
                     total_src_files_count, readable_byte_size(total_src_files_size), current_dir)

    logging.info("Syncing %s to %s : done", root_src, root_dst)
