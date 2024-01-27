import socket
import random
import time
import pyaudio
import math
import struct
import os


RATE = 16000 # sample rate
FRAME_SECS = 0.02 # length of frame(chunks) to be processed at once in secs

SHORT_NORMALIZE = (1.0/32768.0)
FORMAT = pyaudio.paInt16
CHANNELS = 1
SHORT_WIDTH = 2
CHUNK = int(RATE * FRAME_SECS)


def rms(frame):
    count = len(frame) / SHORT_WIDTH
    format = "%dh" % (count)
    shorts = struct.unpack(format, frame)

    sum_squares = 0.0
    for sample in shorts:
        n = sample * SHORT_NORMALIZE
        sum_squares += n * n
    rms = math.pow(sum_squares / count, 0.5)

    return rms * 1000

def minMax(value, min_value=0, max_value=1):
    assert min_value<=max_value
    return min(max(min_value, value), max_value)

def normalize(x, p=.3, max_value=667, threshold_value=.2):
    threshold_func = lambda x: 0 if x < threshold_value else x
    return threshold_func(minMax(math.pow(x, p)/math.pow(max_value, p)))

class vtuber:
    def __init__(self, address =  ('127.0.0.1', 5066), path='gui_unitychan\\unitychan.exe'):
        os.startfile(path)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        i=1
        while True:
            try: 
                self.s.connect(address)
                break
            except Exception as e:
                print('waiting for connection '+'.'*i, end='\r')
                time.sleep(.5)
            if i==3: i=0
            i+=1
                
            
        # self.roll, self.pitch, self.yaw, self.mar, self.mdst = (
        #     0, 0, 0, 0, 0
        # )
    def close(self): self.s.close()
    
    def update(self, roll, pitch, yaw, mar, mdst):
        msg = '%.4f %.4f %.4f %.4f %.4f %.4f %.4f %.4f'% \
            (roll, pitch, yaw, 0, mar, mdst, 0, 0)
            # (self.roll, self.pitch, self.yaw, 0, self.mar, self.mdst, 0, 0)
        self.s.send(bytes(msg, "utf-8"))

os.chdir(os.path.dirname(__file__))


p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    if (dev['name'] == 'Stereo Mix (Realtek(R) Audio)' and dev['hostApi'] == 0):
        dev_index = dev['index']
        print('dev_index', dev_index)
        break
    
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True, # see this
                input_device_index = dev_index,
                frames_per_buffer=CHUNK)
model = vtuber()

roll, pitch, yaw, mar, mdst = (0,0,0,0,0)
vars_max = 8
alpha = .5
while True:
    roll = minMax(roll, -vars_max, vars_max)+random.randint(-1, 1)*alpha
    pitch = minMax(pitch, -vars_max, vars_max)+random.randint(-1, 1)*alpha
    yaw = minMax(yaw, -vars_max, vars_max)+random.randint(-1, 1)*alpha
    
    mar = normalize(rms(stream.read(CHUNK)), p=.3, max_value=667, threshold_value=.05)
    mar = random.choice([mar, mar, mar, 0])
    print('[+] roll=[%4.2f], pitch=[%4.2f], yaw=[%4.2f], mar=[%4.2f], mdst=[%4.2f]' % \
        (roll, pitch, yaw, mar, mdst), end='\r')
    model.update(roll, pitch, yaw, mar, mdst)

    time.sleep(.05)