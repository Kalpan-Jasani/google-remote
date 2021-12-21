"""main runner for the project"""
import sys

import pychromecast
from pychromecast.discovery import stop_discovery
from .getch import getch

# amount in seconds by which forward or backward buttons should move the song
TIME_JUMP = 15

# map of inputs provided by user to commands to run
COMMANDS_MAP = {
    '\r': 'play',
    '5': 'subtitles',
    '+': 'increase_volume',
    '-': 'decrease_volume',
    '7': 'back',
    '9': 'front',
}


def run():
    """run the remote"""
    chromecasts, browser = pychromecast.get_listed_chromecasts(
        friendly_names=["Living Room TV"]
    )

    if not chromecasts:
        print('Chromecast not discovered')
        sys.exit(1)

    cast = chromecasts[0]
    print('Found chromecast')
    # Start socket client's worker thread and wait for initial status update
    cast.wait()

    mc = cast.media_controller
    rc = cast.socket_client.receiver_controller

    # random initial assumption of whether subtitles are enabled. Used for
    # toggling between two states
    subtitles_enabled = True

    # main read loop taking user input
    while(True):
        try:
            # get user input
            # map user input to a command
            # execute command

            ch = getch()
            # TODO: remove next line, just for debugging
            if ch == '0':
                break

            # TODO: maybe print enter key as not a literal new line but a \r
            print('pressed: ', ch, flush=True)
            mc.update_status()
            rc.update_status()
            command = COMMANDS_MAP.get(ch)
            if command == 'play':
                mc.pause() if mc.status.player_is_playing else mc.play()

            elif command == 'subtitles':
                mc.disable_subtitle() if subtitles_enabled else len(
                    mc.status.subtitle_tracks) > 0 and mc.status.subtitle_tracks[0]['trackId'] or None
                subtitles_enabled = not subtitles_enabled
            elif command == 'increase_volume':
                rc.set_volume(rc.status.volume_level+0.1)
            elif command == 'decrease_volume':
                rc.set_volume(rc.status.volume_level-0.1)
            elif command == 'back':
                new_time = mc.status.current_time - TIME_JUMP
                mc.seek(max(0, new_time))
            elif command == 'front':
                new_time = mc.status.curret_time + TIME_JUMP
                mc.seek(min(new_time, mc.status.duration))

        except KeyboardInterrupt:
            break

    browser.stop_discovery()
    print('exiting')
