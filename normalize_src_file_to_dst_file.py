from PIL import Image
from _operator import attrgetter
import gi
from gi.repository import GExiv2
import logging
import math
from pathlib import Path
import shutil
import subprocess

from walk_folders import *
from do_changes import *
from video_information import *


gi.require_version('GExiv2', '0.10')


def _normalize_picture(src_file, dst_file):
    try:
        src_image = Image.open(src_file)
        src_size = src_image.size
        ratio = src_size[0] / 1920
        dst_image = src_image.resize((1920, int(src_size[1] / ratio)))
        if DO_CHANGES:
            if dst_file.is_file():
                dst_file.unlink()
            dst_file.touch()
            dst_image.save(dst_file, 'jpeg', quality=50)
        metadata = GExiv2.Metadata(str(src_file))
        metadata.set_tag_long('Exif.Photo.PixelXDimension', 1920)
        metadata.set_tag_long('Exif.Photo.PixelYDimension', int(src_size[1] / ratio))
        metadata.erase_exif_thumbnail()
        if DO_CHANGES:
            metadata.save_file(str(dst_file))
    except:
        logging.warning('Cannot normalize src pic %s', src_file)


def _check_normalize_src_to_dst_picture(src_file, dst_folder, dst_files):
    dst_file = Path(dst_folder, src_file.stem + '.jpg')
    must_recreate = False
    if src_file.name in dst_files:
        if src_file.stat().st_mtime > dst_file.stat().st_mtime:
            reason = 'dst file too old'
            must_recreate = True
        else:
            try:
                dest_image = Image.open(dst_file)
                if dest_image.size[0] != 1920:
                    reason = 'dst pic width not OK (' + str(dest_image.size[0]) + ')'
                    must_recreate = True
            except:
                reason = 'dst pic invalid'
                must_recreate = True
    else:
        reason = 'dst file does not exist'
        must_recreate = True
    if must_recreate:
        logging.info('Normalize pic (%s octets): %s %s to %s', readable_byte_size(src_file.stat().st_size), reason, src_file, dst_file)
        _normalize_picture(src_file, dst_file)


def _create_thumbnail(src_file, thumbnail_file, size):
    if size is None:
        info = video_info(src_file)
        size = video_size(info)
        ratio = size[0] / 1280
        height = str(int(size[1] / ratio))
        size = (1280, height)
    if DO_CHANGES:
        if not thumbnail_file.parent.is_dir():
                thumbnail_file.parent.mkdir()
        result = subprocess.Popen(["nice", '-n', '15', 'avconv', '-y', '-i',
                                   str(src_file), '-vframes', '1', '-s',
                                   str(size[0]) + 'x' + str(size[1]), str(thumbnail_file)],
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result.stdout.read()


def _normalize_video(src_file, dst_file):
    info = video_info(src_file)
    size = video_size(info)
    if size[0] > 0:
        ratio = size[0] / 1280
        height = int(int(size[1] / ratio))
        if height % 2 == 1:
            height += 1
        size = (1280, height)
        if DO_CHANGES:
            result = subprocess.Popen(["nice", '-n', '15', 'avconv', '-y', '-i',
                                       str(src_file), '-strict', '-2', '-ac', '2', '-movflags',
                                       '+faststart', '-b:v', '900k', '-b:a', '128k', '-r', '24', '-ar',
                                       '24000', '-s', '1280x' + str(height), str(dst_file)],
                                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            result.stdout.read()
        thumbnail_file = Path(dst_file.parent, 'pwg_representative', src_file.stem + '.jpg')
        _create_thumbnail(src_file, thumbnail_file, size)
    else:
        logging.error('Cannot normalize: size = ' + str(size))


def _check_normalize_src_to_dst_video(src_file, dst_folder, dst_files):
    del dst_files
    dst_file = Path(dst_folder, src_file.stem + '.mp4')
    must_recreate = False
    src_video_info = None
    reason = ''
    if dst_file.is_file():
        if src_file.stat().st_mtime > dst_file.stat().st_mtime:
            reason = 'dest file too old'
            must_recreate = True
        else:
            src_video_info = video_info(src_file)
            dest_video_info = video_info(dst_file)
            src_duration = video_duration(src_video_info)
            if src_duration == 0:
                logging.error('Skipping %s because source duration unknown', src_file)
                return
            else:
                dest_duration = video_duration(dest_video_info)
                if math.fabs(dest_duration - src_duration) > 0.5:
                    reason = 'dest duration too different: ' + str(src_duration) + ' vs ' + str(dest_duration)
                    must_recreate = True
                else:
                    dest_video_width, _ = video_size(dest_video_info)
                    if dest_video_width != 1280:
                        reason = 'dest video image width not OK: ' + str(dest_video_width) + ' Info: '\
                                 + str(dest_video_info)
                        must_recreate = True
    else:
        reason = 'dest file does not exist'
        must_recreate = True
    if must_recreate:
        logging.info('Normalize video (%s octets): %s %s to %s', readable_byte_size(src_file.stat().st_size), reason, src_file, dst_file)
        _normalize_video(src_file, dst_file)
        if DO_CHANGES:
            # check
            src_video_info = video_info(src_file)
            dest_video_info = video_info(dst_file)
            src_duration = video_duration(src_video_info)
            dest_duration = video_duration(dest_video_info)
            if math.fabs(dest_duration - src_duration) > 0.5:
                logging.error('... error: destination duration NOK: %s', dest_duration)
            else:
                # done
                logging.info('... done')
        else:
            logging.info('... done')
    else:
        thumbnail_file = Path(dst_folder, 'pwg_representative', src_file.stem + '.jpg')
        if not thumbnail_file.is_file():
            if src_video_info is not None:
                size = video_size(src_video_info)
                ratio = size[0] / 1280
                height = str(int(size[1] / ratio))
                size = (1280, height)
            else:
                size = None
            _create_thumbnail(src_file, thumbnail_file, size)


def _check_normalize_src_to_dst_file(src_file, dst_folder, dst_files):
    if src_file.suffix in ['.jpg', '.jpeg', '.png']:
        _check_normalize_src_to_dst_picture(src_file, dst_folder, dst_files)
    elif src_file.suffix in ['.mp4', '.mov', '.avi', '.mpg', '.mkv', '.m2ts']:
        _check_normalize_src_to_dst_video(src_file, dst_folder, dst_files)


def _check_normalize_dst_to_src_picture(dst_file, src_folder, src_files):
    src_exists = False
    for ext in ['.jpg', '.jpeg', '.png']:
        src_file = Path(src_folder, dst_file.stem + ext)
        if src_file.name in src_files:
            src_exists = True
            break
    if not src_exists:
        logging.info('Deleting destination file %s because source file does not exist: %s',
                     dst_file,
                     Path(src_folder, dst_file.stem + '.[jpg jpeg tif png]'))
        if DO_CHANGES:
            dst_file.unlink()


def _check_normalize_dst_to_src_video(dst_file, src_folder, src_files):
    src_exists = False
    for ext in ['.m2ts', '.mp4', '.mov', '.avi', '.mpg', '.mkv']:
        src_file = Path(src_folder, dst_file.stem + ext)
        if src_file.name in src_files:
            src_exists = True
            break
    if not src_exists:
        logging.info('Deleting destination file %s because source file does not exist: %s',
                     dst_file,
                     Path(src_folder, dst_file.stem + '.[mp4 mov avi mpg mkv m2ts]'))
        if DO_CHANGES:
            dst_file.unlink()


def _check_normalize_dst_to_src_file(dst_file, src_folder, src_files):
    if dst_file.suffix in ['.jpg', '.jpeg', '.png']:
        _check_normalize_dst_to_src_picture(dst_file, src_folder, src_files)
    elif dst_file.suffix in ['.mp4', '.mov', '.avi', '.mpg', '.mkv', '.m2ts']:
        _check_normalize_dst_to_src_video(dst_file, src_folder, src_files)


def _check_normalize_src_to_dst_folder(src_folder, dst_folder, src_files, dst_files):
    if not dst_folder.is_dir():
        logging.info('Create missing destination directory: %s', dst_folder)
        if DO_FOLDER_CHANGES:
            dst_folder.mkdir()
    for src_file in sorted(src_files, key=str):
        _check_normalize_src_to_dst_file(Path(str(src_folder) + '/' + src_file),
                                         dst_folder,
                                         dst_files)


def _check_normalize_dst_to_src_folder(src_folder, dst_folder, src_files, dst_files):
    if dst_folder.name != 'pwg_representative':
        if not src_folder.is_dir():
            logging.info('Deleting destination directory %s because source does not exist:', dst_folder.path)
            if DO_CHANGES:
                shutil.rmtree(dst_folder.path)
        else:
            for dst_file in sorted(dst_files, key=str):
                _check_normalize_dst_to_src_file(Path(str(dst_folder) + '/' + dst_file),
                                                 src_folder,
                                                 src_files)


def synchronize_picture_and_video_normalization(src_dir, src_dirs, src_files, src_files_stat, dst_dir, dst_dirs,
                                                dst_files, dst_files_stat, add_only):
    del src_dirs
    del src_files_stat
    del dst_dirs
    del dst_files_stat
    _check_normalize_src_to_dst_folder(Path(src_dir), Path(dst_dir), src_files, dst_files)
    if not add_only:
        _check_normalize_dst_to_src_folder(Path(src_dir), Path(dst_dir), src_files, dst_files)
