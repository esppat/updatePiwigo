import json
import subprocess


def video_info(file):
    result = subprocess.Popen(["ffprobe", '-print_format', 'json',
                        '-show_streams', '-loglevel', 'quiet', str(file)],
                        stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    return json.loads(result.stdout.read().decode('ascii'))

def video_stream(video_info):
    try:
        for stream in video_info['streams']:
            if stream['codec_type'] == 'video':
                return stream
        return None
    except:
        return None

def audio_stream(video_info):
    try:
        for stream in video_info['streams']:
            if stream['codec_type'] == 'audio':
                return stream
        return None
    except:
        return None

def video_duration(video_info):
    try:
        return float(video_stream(video_info)['duration'])
    except:
        return 0.0

def video_size(video_info):
    try:
        return float(video_stream(video_info)['width']), float(video_stream(video_info)['height'])
    except:
        #logging.error('Error reading width or height')
        #print(json.dumps(get_video_stream(video_info), sort_keys=True,
        #    indent=4, separators=(',', ': ')))
        return 0.0, 0.0
