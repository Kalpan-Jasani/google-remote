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

    # random initial assumption of whether something is playing vs paused
    # used for toggling between the two states
    playing = True

    # similar logic as above for subtitles
    subtitles_enabled = True

    # similar logic for setting an arbitrary initial volume which gets nudged
    # relatively
    volume = 0

    # main read loop taking user input
    while(True):
        try:
            # get user input
            # map user input to a command
            # execute command

            ch = getch()
            print('pressed: ', ch)
            command = COMMANDS_MAP.get(ch)
            if command == 'play':
                mc.pause() if playing else mc.play()
            elif command == 'subtitles':
                mc.disable_subtitle() if subtitles_enabled else len(
                    mc.status.subtitle_tracks) > 0 and mc.status.subtitle_tracks[0]['trackId'] or None
            elif command == 'increase_volume':
                if not volume == 0.5:
                    volume += 0.1
                    rc.set_volume(volume)
            elif command == 'decrease_volume':
                if not volume == -0.5:
                    volume -= 0.1
                    rc.set_volume(volume)
            elif command == 'back':
                mc.update_status()
                if mc.status.current_position - TIME_JUMP > 0:
                    mc.seek(mc.status.current_position - TIME_JUMP)
            elif command == 'front':
                mc.update_status()
                if mc.status.current_position + TIME_JUMP < mc.status.duration:
                    mc.seek(mc.status.current_position + TIME_JUMP)

        except KeyboardInterrupt:
            break

    browser.stop_discovery()
    print('exiting')
