from .constants import *
import pyaudio
import math
import struct
import wave
import time
from faster_whisper import WhisperModel

model = WhisperModel(model_size, device=device, compute_type=compute_type)

def transcribeFunction(filename):
    segments, info = model.transcribe(filename, beam_size=beam_size)
    # print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
    # for segment in segments:
        # print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    return ' '.join([segment.text for segment in segments])

class Recorder:
    @staticmethod
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

    def __init__(self, transcribeFunction=transcribeFunction, filename = 'output.wav'):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        output=True,
                        frames_per_buffer=CHUNK)
        
        if transcribeFunction == None: transcribeFunction = lambda x : x
        
        self.time = time.time()
        self.quiet = []
        self.quiet_idx = -1
        self.timeout = 0
        self.filename = filename
        self.transcribeFunction = transcribeFunction

    def record(self)->iter:
        print('')
        sound = []
        start = time.time()
        # begin_time = None
        while True:
            data = self.stream.read(CHUNK)
            rms_val = self.rms(data)
            if self.inSound(data):
                sound.append(data)
                # if begin_time == None:
                    # begin_time = datetime.datetime.now()
            else:
                if len(sound) > 0:
                    self.write(sound, self.filename)
                    sound.clear()
                    # begin_time = None
                    yield self.transcribeFunction(self.filename)
                else:
                    self.queueQuiet(data)

            curr = time.time()
            secs = int(curr - start)
            tout = 0 if self.timeout == 0 else int(self.timeout - curr)
            label = 'Listening' if self.timeout == 0 else 'Recording'
            print('[+] %s: Level=[%4.2f] Secs=[%d] Timeout=[%d]' % (label, rms_val, secs, tout), end='\r')
                
    # quiet is a circular buffer of size cushion
    def queueQuiet(self, data):
        self.quiet_idx += 1
        # start over again on overflow
        if self.quiet_idx == CUSHION_FRAMES:
            self.quiet_idx = 0
        
        # fill up the queue
        if len(self.quiet) < CUSHION_FRAMES:
            self.quiet.append(data)
        # replace the element on the index in a cicular loop like this 0 -> 1 -> 2 -> 3 -> 0 and so on...
        else:            
            self.quiet[self.quiet_idx] = data
            
    def dequeueQuiet(self, sound):
        if len(self.quiet) == 0:
            return sound
        
        ret = []
        
        if len(self.quiet) < CUSHION_FRAMES:
            ret.append(self.quiet)
            ret.extend(sound)
        else:
            ret.extend(self.quiet[self.quiet_idx + 1:])
            ret.extend(self.quiet[:self.quiet_idx + 1])
            ret.extend(sound)

        return ret
    
    def inSound(self, data):
        rms = self.rms(data)
        curr = time.time()

        if rms > TRIGGER_RMS:
            self.timeout = curr + TIMEOUT_SECS
            return True
        
        if curr < self.timeout:
            return True

        self.timeout = 0
        return False
    
    def write(self, sound, filename)->None:
        # insert the pre-sound quiet frames into sound
        sound = self.dequeueQuiet(sound)

        # sound ends with TIMEOUT_FRAMES of quiet
        # remove all but CUSHION_FRAMES
        keep_frames = len(sound) - TIMEOUT_FRAMES + CUSHION_FRAMES
        recording = b''.join(sound[0:keep_frames])


        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(recording)
        wf.close()
        print('[+] Saved: {}'.format(filename))
