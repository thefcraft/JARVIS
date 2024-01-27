import utils
from colorama import Fore, Style

recorder = utils.stt.Recorder(filename='.temp/recorder.wav', transcribeFunction=utils.stt.transcribeFunction)
speaker = utils.tts.Speaker(filename='.temp/speaker.wav', speaker='default', language='English', speed=1) # speaker=whispering


### llm parameters
# system_prompt = "Below is an instruction that describes a task. Write a response that appropriately completes the request."
# system_prompt = '''I want you to act as an interviewer. I will be the candidate and you will ask me the interview questions for the [INSERT] position. I want you to only reply as the interviewer. Do not write all the conservation at once. I want you to only do the interview with me. Ask me the questions and wait for my answers. Do not write explanations. Ask me the questions one by one like an interviewer does and wait for my answers.'''
# system_prompt = '''I want you to act as an interviewer. I will be the candidate and you will ask me the interview questions for the any position (chose any random). I want you to only reply as the interviewer. Do not write all the conservation at once. I want you to only do the interview with me. Ask me the questions and wait for my answers. Do not write explanations. Ask me the questions one by one like an interviewer does and wait for my answers.'''
system_prompt = '''You are Anna, act as you are talking to someone, respond only speakible responses'''
num_history_prompts = 10
first_prompt = None #'My first sentence is "Hi".'

ai = utils.llmUtils.llm(system_prompt=system_prompt, num_history_prompts=num_history_prompts)

if first_prompt:
    print(Fore.GREEN, first_prompt, Style.RESET_ALL)
    response = ''
    print(Fore.RED)
    for chunk in ai(first_prompt):
        print(chunk, end='')
        response+=chunk
    print(Style.RESET_ALL)
    speaker.speak(response)

for text in recorder.record():
    print(Fore.GREEN, text, Style.RESET_ALL)
    response = ''
    print(Fore.RED)
    for chunk in ai(text):
        print(chunk, end='')
        response+=chunk
    print(Style.RESET_ALL)
    speaker.speak(response)