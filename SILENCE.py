"""
System for Identifying Loud Environments and Neutralizing Conversation Effectively by Mavial
a Scimia by Novecento fork

This script is meant to be run directly.
"""

import os
import sys
import time
import sys
from queue import Queue

import keyboard
import numpy as np
import sounddevice as sd  # mypy: ignore
import soundfile as sf  # mypy: ignore
from termcolor import colored

from timeit import default_timer as timer

scimia_enabled = True
BAR_LENGTH = 60

os.system("color")
os.system("mode con: cols=65 lines=32")

# If this file is compiled, we will use the _MEIPASS path (the temporary path/folder used by PyInstaller),
# otherwise use the CWD (current working directory).
data, fs = sf.read(os.path.join(getattr(sys, "_MEIPASS", os.getcwd()), "sound.wav"))


print(
    r"""    ____    ______   __       ____    __  __  ____     ____
   /\  _`\ /\__  _\ /\ \     /\  _`\ /\ \/\ \/\  _`\  /\  _`\
   \ \,\L\_\/_/\ \/ \ \ \    \ \ \L\_\ \ `\\ \ \ \/\_\\ \ \L\_\
    \/_\__ \  \ \ \  \ \ \  __\ \  _\L\ \ , ` \ \ \/_/_\ \  _\L
      /\ \L\ \ \_\ \__\ \ \L\ \\ \ \L\ \ \ \`\ \ \ \L\ \\ \ \L\ \
      \ `\____\/\_____\\ \____/ \ \____/\ \_\ \_\ \____/ \ \____/
       \/_____/\/_____/ \/___/   \/___/  \/_/\/_/\/___/   \/___/
"""
)

if len(sys.argv) > 1:
    print("Volume threshold set to " + sys.argv[1])
    val = sys.argv[1]
    if len(sys.argv) > 2:
        threshold_time = int(sys.argv[2])
    else:
        threshold_time = 4
else:
    val = input(" Set microphone treshold: ")
    threshold_time = input(" Set threshold time (optional): ")
    if threshold_time == "":
        threshold_time = 4
    else:
        threshold_time = int(threshold_time)

print(" Please be quiet. SILENCE is listening...")
print(
    r"""
                    ⠀⢠⣤⣤⣤⣤⣤⣤⣤⣤⣤⢀⣤⣤⣤⣤⣤⣤⡀⣤⣤⣤⣤⣤⣤⣤⣤⣤⡄⠀
                    ⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣼⣿⣿⣿⣿⣿⣿⣧⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀
                    ⠀⢸⣿⣿⣿⣿⣿⣿⣿⣏⠀⢀⠙⠿⣿⣿⠿⠋⡀⠀⣹⣿⣿⣿⣿⣿⣿⣿⡇⠀
                    ⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣤⣤⣴⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀
                    ⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⢉⠀⣤⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀
                    ⠀⠀⢿⣿⣿⣿⣿⠉⠋⠉⠉⠉⠉⠀⣾⠀⣿⠀⠉⠉⠉⠙⠉⣿⣿⣿⣿⡿⠀⠀
                    ⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣶⣶⠀⣿⣦⣈⠀⣶⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀
                    ⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⣿⣿⣿⠀⢻⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀
                    ⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣍⣠⠀⣿⣿⣿⡇⢨⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠈⠛⠿⣿⣿⣿⣿⠀⢹⣿⣿⣇⠘⣿⣿⠿⠛⠁⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠙⠃⢸⣿⣿⣿⡄⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⢠⣶⣷⣶⣤⣤⣀⣈⡉⠛⠛⠛⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⢀⡴⠀⣿⣿⠋⣉⣙⡛⠛⠛⠛⠿⠿⠷⢶⣶⣦⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠛⠃⠐⠛⠃⠘⠛⠛⠛⠛⠛⠛⠛⠓⠒⠒⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

"""
)

max_audio_value = int(val)
print(" p to pause" + "\033[F" + "\033[F" + "\033[F")

# Create the queue that will hold the audio chunks
audio_queue: Queue = Queue()


# noinspection PyUnusedLocal
def callback(
    indata: np.ndarray,
    outdata: np.ndarray,
    frames: int,
    time_,
    status: sd.CallbackFlags,
) -> None:
    """
    This is called (from a separate thread) for each audio block.

    Taken from the sounddevice docs:
    https://python-sounddevice.readthedocs.io/en/0.3.14/examples.html#recording-with-arbitrary-duration

    According to the docs, our function must have this signature:
    def callback(indata: ndarray, outdata: ndarray, frames: int,
                             time: CData, status: CallbackFlags) -> None
    """
    # Add the data to the queue
    audio_queue.put(indata.copy())


with sd.Stream(callback=callback):
    start = timer()
    try:
        while True:
            # Pull a chunk of audio from the queue
            # This call is blocking, so if the queue is empty, we will wait until chunk has been added
            loudness = np.linalg.norm(audio_queue.get()) * 10
            bar = int(loudness * (BAR_LENGTH / max_audio_value))

            # Check if we need to pause
            if keyboard.is_pressed("p"):
                # Flip the boolean
                scimia_enabled = not scimia_enabled
                print(
                    f"\n\n p to {'pause' if scimia_enabled else 'resume'} "
                    + "\033[F" * 3
                )
                time.sleep(0.3)

            # If we are quiet, then print the audio bar
            if loudness < max_audio_value:
                print(" [" + "|" * bar + " " * (BAR_LENGTH - bar) + "]", end="\r")
            else:
                # Add the color red if we have passed the audio threshold
                print(colored(" [" + "!" * BAR_LENGTH + "]", "red"), end="\r")
                # Play a sound to the user to let them know that they are loud
                if scimia_enabled and (timer() - start) > threshold_time:
                    start = timer()
                    sd.play(data, fs)
                    sd.wait()
    except KeyboardInterrupt:
        print("\n\n\nStopping...")
