from .constants import *

import torch
import simpleaudio as sa

from .OpenVoice import se_extractor
from .OpenVoice.api import BaseSpeakerTTS, ToneColorConverter

base_speaker_tts = BaseSpeakerTTS(f'{ckpt_base}/config.json', device=device)
base_speaker_tts.load_ckpt(f'{ckpt_base}/checkpoint.pth')

tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

source_se = torch.load(f'{ckpt_base}/{source_se}.pth').to(device)

target_se, audio_name = se_extractor.get_se(reference_speaker, tone_color_converter, target_dir='processed', vad=True)


class Speaker:
    def __init__(self, filename, speaker='default', language='English', speed=1.0):
        self.filename = filename
        self.speaker = speaker
        self.language = language
        self.speed = speed
    
    def speak(self, text, speaker=None, language=None, speed=None, wait=True):
        base_speaker_tts.tts(text, self.filename, speaker=speaker or self.speaker, language=language or self.language, speed=speed or self.speed)
        # Run the tone color converter
        encode_message = "@MyShell"
        tone_color_converter.convert(
            audio_src_path=self.filename, 
            src_se=source_se, 
            tgt_se=target_se, 
            output_path=self.filename,
            message=encode_message)
        
        wave_obj = sa.WaveObject.from_wave_file(self.filename)
        play_obj = wave_obj.play()
        # Wait for the sound to finish playing
        if wait:
            play_obj.wait_done()