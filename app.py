from EdgeGPT.EdgeUtils import Query
import speech_recognition as sr
import sys, whisper, warnings, time, openai

# Wake word variable
HOSPITALITY_BOT_WAKE_WORD = "ok hospitality bot"

# Initialize the OpenAI API
openai.api_key = "sk-proj-MCIgSStRmBYNGqwu6O5yT3BlbkFJOCuWnPeTWQ0A2GCbPP4l"

r = sr.Recognizer()
tiny_model = whisper.load_model('base', download_root='asrmodel' )
base_model = whisper.load_model('base', download_root='asrmodel' )
listening_for_wake_word = True
hospitality_bot_engine = True
source = sr.Microphone() 
warnings.filterwarnings("ignore", category=UserWarning, module='whisper.transcribe', lineno=114)

if sys.platform != 'darwin':
    import pyttsx3
    engine = pyttsx3.init()

def speak(text):
    if sys.platform == 'darwin':
        ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?!-_$:+-/ ")
        clean_text = ''.join(c for c in text if c in ALLOWED_CHARS)
        system(f"say '{clean_text}'")
    else:
        engine.say(text)
        engine.runAndWait()

def listen_for_wake_word(audio):
    global listening_for_wake_word
    global hospitality_bot_engine
    with open("wake_detect.wav", "wb") as f:
        f.write(audio.get_wav_data())
    result = tiny_model.transcribe('wake_detect.wav')
    text_input = result['text']
    if HOSPITALITY_BOT_WAKE_WORD in text_input.lower().strip():
        print("Speak your prompt to the Hospitality Bot.")
        speak('Listening')
        listening_for_wake_word = False

def prompt_hospitality_bot(audio):
    global listening_for_wake_word
    global hospitality_bot_engine
    try:
        with open("prompt.wav", "wb") as f:
            f.write(audio.get_wav_data())
        result = base_model.transcribe('prompt.wav')
        prompt_text = result['text']
        if len(prompt_text.strip()) == 0:
            print("Empty prompt. Please speak again.")
            speak("Empty prompt. Please speak again.")
            listening_for_wake_word = True
        else:
            print('User: ' + prompt_text)
            output = Query(prompt_text) # Assuming Query function handles the response for the hospitality bot
            print('Hospitality Bot: ' + str(output))
            speak(str(output))
            print('\nSay Ok Hospitality Bot to wake me up. \n')
            hospitality_bot_engine = True
            listening_for_wake_word = True
    
    except Exception as e:
        print("Prompt error: ", e)

def callback(recognizer, audio):
    global listening_for_wake_word
    global hospitality_bot_engine
    if listening_for_wake_word:
        listen_for_wake_word(audio)
    elif hospitality_bot_engine:
        prompt_hospitality_bot(audio)

def start_listening():
    with source as s:
        r.adjust_for_ambient_noise(s, duration=2)
    print('\nSay Ok Hospitality Bot to wake me up. \n')
    r.listen_in_background(source, callback)
    while True:
        time.sleep(1) 

if __name__ == '__main__':
    start_listening()
