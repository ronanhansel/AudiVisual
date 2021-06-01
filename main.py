import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.fftpack import fft
import time
from tkinter import TclError

# constants
import access_tok
import spotify
from spotify import colourise, refresh_token

CHUNK = 1024 * 2  # samples per frame
FORMAT = pyaudio.paInt16  # audio format (bytes per sample?)
CHANNELS = 2  # single channel for microphone
RATE = 44100  # samples per second

# create matplotlib figure and axes
fig, ax2 = plt.subplots(figsize=(15, 7))

# pyaudio class instance
p = pyaudio.PyAudio()

# stream object to get data from microphone
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

# variable for plotting
xf = np.linspace(0, RATE, CHUNK)  # frequencies (spectrum)

# create semilogx line for spectrum
line_fft, = ax2.semilogx(xf, np.random.rand(CHUNK), '-ro', lw=2)
# show the plot
plt.show(block=False)

# format spectrum axes
ax2.set_xlabel('Frequency')
ax2.set_ylabel('Rate')
ax2.set_xlim(20, RATE / 2)

# for measuring frame rate
frame_count = 0
start_time = time.time()
i = 0
try:
    colour = colourise(token=access_tok.acc_token)
except Exception as e:
    newtok = refresh_token(access_tok.acc_token)
    print('Retrying')
    colour = colourise(token=newtok)
print(colour)

print('stream started')


def loopfreq():
    while True:

        # binary data
        data = stream.read(CHUNK, exception_on_overflow=False)

        # convert data to integers, make np array, then offset it by 127
        data_int = np.frombuffer(data, dtype='B')
        # create np array and offset by 128

        # compute FFT and update line
        yf = fft(data_int)
        y_value = np.abs(yf[0:CHUNK]) / (128 * CHUNK)
        line_fft.set_ydata(y_value)
        strongy = np.where(y_value[1:] >= 0.6)
        lighty = y_value[1:][y_value[1:] < 0.6]
        # print(lighty)
        medy = np.where(lighty > 0.25)
        medy = np.array(medy)
        strongy = np.array(strongy)
        filter_strongy = strongy[strongy < 10000]
        filter_lighty = np.array(lighty[lighty < 10000])
        filter_medy = np.array(medy[medy < 10000])
        strongyfreq = filter_strongy * 22
        lightyfreq = filter_lighty * 22
        medyfreq = filter_medy * 22
        speed = len(medyfreq)
        if speed > 4:
            print('FAST!')
        print(strongyfreq)
        # for f in strongyfreq:
        #     if f < 250:
        #         # beat.append(f)
        #         print('BEAT!')
        #     elif 250 <= f < 500:
        #         # musical.append(f)
        #         print('MUSICAL!')
        #     elif 500 <= f < 4000:
        #         # vocal.append(f)
        #         print('VOCAL!')
        #     elif 4000 <= f:
        #         # vocal.append(f)
        #         print('BRIDGE!')
        #     else:
        #         print('idk bro')
        # time.sleep(1)
        try:
            fig.canvas.draw()
            fig.canvas.flush_events()
        except TclError:
            # calculate average frame rate
            print('stream stopped')
            break


loopfreq()
