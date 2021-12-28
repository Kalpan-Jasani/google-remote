"""main runner for the project"""
import sys
import string
import time

import pychromecast
from .getch import getch

TV_NAME = 'Living Room TV'
SPEAKER_NAME = 'Living Room speaker'

# amount in seconds by which forward or backward buttons should move the song
TIME_JUMP = 15

# map of inputs provided by user to commands to run
COMMANDS_MAP = {
    '.': 'play',
    '0': 'subtitles',
    '/': 'increase_volume',
    '-': 'decrease_volume',
    '1': 'back',
    '3': 'front',
    '\t': 'switch_device'
}


def connect(device_name):
    """connect to a device"""
    chromecasts, browser = pychromecast.get_listed_chromecasts(
        friendly_names=[device_name]
    )

    if not chromecasts:
        print(f'{device_name} not discovered')
        sys.exit(1)

    cast = chromecasts[0]
    print(f'Found {device_name}')

    # Start socket client's worker thread and wait for initial status update
    cast.wait()
    browser.stop_discovery()

    # nudge the volume up and down to show as connected
    rc = cast.socket_client.receiver_controller
    rc.update_status()
    original_volume = rc.status.volume_level
    rc.set_volume(original_volume-0.1)
    time.sleep(1)
    rc.set_volume(original_volume)

    return cast


def run():
    """run the remote"""
    cast = connect(TV_NAME)
    mc, rc = cast.media_controller, cast.socket_client.receiver_controller

    # random initial assumption of whether subtitles are enabled. Used for
    # toggling between two states
    subtitles_enabled = True
    tab_count = 0
    active_device = TV_NAME
    # main read loop taking user input
    while(True):
        try:
            # get user input
            # map user input to a command
            # execute command

            ch = getch()
            if ch == '\r':
                print('pressed: \\r')
            elif ch == '\t':
                print('pressed: \\t')
            elif ch not in string.printable or ch in string.whitespace:
                print('pressed: ?')
            else:
                print('pressed:', ch)

            if ch == 'q':
                break
            mc.update_status()
            rc.update_status()
            command = COMMANDS_MAP.get(ch)

            # a special case of a command to switch to the speaker to control
            # it!
            if command == 'switch_device':
                tab_count += 1
                if tab_count >= 2:
                    print('switching devices')
                    active_device = (
                        SPEAKER_NAME if active_device == TV_NAME else TV_NAME)
                    cast = connect(active_device)
                    mc, rc = cast.media_controller, cast.socket_client.receiver_controller
                    tab_count = 0

            # resetting tab count as a double tap of tab is required to switch
            else:
                tab_count = 0

            if command == 'play':
                mc.pause() if mc.status.player_is_playing else mc.play()

            elif command == 'subtitles':
                mc.disable_subtitle() if subtitles_enabled else len(
                    mc.status.subtitle_tracks) > 0 and mc.enable_subtitle(mc.status.subtitle_tracks[0]['trackId'])
                subtitles_enabled = not subtitles_enabled
            elif command == 'increase_volume':
                rc.set_volume(rc.status.volume_level+0.1)
            elif command == 'decrease_volume':
                rc.set_volume(rc.status.volume_level-0.1)
            elif command == 'back':
                new_time = mc.status.current_time - TIME_JUMP
                mc.seek(max(0, new_time))
            elif command == 'front':
                new_time = mc.status.current_time + TIME_JUMP
                mc.seek(min(new_time, mc.status.duration))

        except pychromecast.error.PyChromecastError:
            # eat up such errors, effectively ignoring them
            continue
        except KeyboardInterrupt:
            break

    print('exiting')
