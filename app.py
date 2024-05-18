import streamlit as st
import streamlit_webrtc as webrtc
import whisper
import openai
from EdgeGPT.EdgeUtils import Query

# Wake word variable
HOSPITALITY_BOT_WAKE_WORD = "ok hospitality bot"

# Initialize the OpenAI API
openai.api_key = "sk-proj-MCIgSStRmBYNGqwu6O5yT3BlbkFJOCuWnPeTWQ0A2GCbPP4l"

tiny_model = whisper.load_model('base', download_root='asrmodel' )
base_model = whisper.load_model('base', download_root='asrmodel' )
listening_for_wake_word = True
hospitality_bot_engine = True

def speak(text):
    # Use streamlit's built-in text-to-speech functionality
    st.speak(text)

def listen_for_wake_word(audio):
    global listening_for_wake_word
    global hospitality_bot_engine
    result = tiny_model.transcribe(audio)
    text_input = result['text']
    if HOSPITALITY_BOT_WAKE_WORD in text_input.lower().strip():
        print("Speak your prompt to the Hospitality Bot.")
        speak('Listening')
        listening_for_wake_word = False

def prompt_hospitality_bot(audio):
    global listening_for_wake_word
    global hospitality_bot_engine
    try:
        result = base_model.transcribe(audio)
        prompt_text = result['text']
        if len(prompt_text.strip()) == 0:
            print("Empty prompt. Please speak again.")
            speak("Empty prompt. Please speak again.")
            listening_for_wake_word = True
        else:
            print('User: ' prompt_text)
            output = Query(prompt_text) # Assuming Query function handles the response for the hospitality bot
            print('Hospitality Bot: ' str(output))
            speak(str(output))
            print('\nSay Ok Hospitality Bot to wake me up. \n')
            hospitality_bot_engine = True
            listening_for_wake_word = True
    
    except Exception as e:
        print("Prompt error: ", e)

def app():
    st.title("Hospitality Bot")
    st.subheader("Say 'Ok Hospitality Bot' to wake me up.")

    webrtc_ctx = webrtc.WebRtcContext()
    audio_receiver = webrtc_ctx.audio_receiver

    while True:
        audio_frames = audio_receiver.get_frames()
        if audio_frames:
            audio = audio_frames[0]
            if listening_for_wake_word:
                listen_for_wake_word(audio)
            elif hospitality_bot_engine:
                prompt_hospitality_bot(audio)

if __name__ == '__main__':
    app()
