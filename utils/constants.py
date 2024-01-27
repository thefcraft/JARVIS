import pyaudio

device = 'cuda'

### open ai server
api_base = "http://localhost:1234/v1"  # point to the local server
api_key = '' # no need for an API key

### OpenVoice parameters
ckpt_base = 'checkpoints/base_speakers/EN'
ckpt_converter = 'checkpoints/converter'
source_se = 'en_default_se' # en_style_se
reference_speaker = 'resources/example_reference.mp3'

### wisper parameters
model_size = "small"#"large-v3" tiny.en, tiny, base.en, base, small.en, small, medium.en, medium, large-v1, large-v2, large-v3, large
compute_type = 'float16'
beam_size = 7


TRIGGER_RMS = 10 # start recording above 10
RATE = 16000 # sample rate
TIMEOUT_SECS = 1 # silence time after which recording stops
FRAME_SECS = 0.25 # length of frame(chunks) to be processed at once in secs
CUSHION_SECS = .25 # amount of recording before and after sound

SHORT_NORMALIZE = (1.0/32768.0)
FORMAT = pyaudio.paInt16
CHANNELS = 1
SHORT_WIDTH = 2
CHUNK = int(RATE * FRAME_SECS)
CUSHION_FRAMES = int(CUSHION_SECS / FRAME_SECS)
TIMEOUT_FRAMES = int(TIMEOUT_SECS / FRAME_SECS)
