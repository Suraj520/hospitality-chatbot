from EdgeGPT.EdgeUtils import Query
import streamlit as st
import time
import openai

# Wake word variable
HOSPITALITY_BOT_WAKE_WORD = "ok hospitality bot"

# Initialize the OpenAI API
openai.api_key = "sk-proj-MCIgSStRmBYNGqwu6O5yT3BlbkFJOCuWnPeTWQ0A2GCbPP4l"

def speak(text):
    st.write(text)

def listen_for_wake_word(audio):
    # Transcribe audio to text and check for wake word
    text_input = audio
    if HOSPITALITY_BOT_WAKE_WORD in text_input.lower().strip():
        speak('Speak your prompt to the Hospitality Bot.')

def prompt_hospitality_bot(audio):
    try:
        # Process the audio prompt
        result = audio # You need to process the audio here
        prompt_text = result
        if len(prompt_text.strip()) == 0:
            speak("Empty prompt. Please speak again.")
        else:
            output = Query(prompt_text) # Assuming Query function handles the response for the hospitality bot
            speak('Hospitality Bot: ' + output)
    except Exception as e:
        speak("Prompt error: " + str(e))

def main():
    st.title('Hospitality Chatbot')

    # Use Streamlit's WebRTC component for microphone access
    audio_input = st.webrtc(
        key="microphone",
        audio_receiver=True,
        video_receiver=False,
        client_settings={"default_language": "en-US"},
    )

    if audio_input:
        audio_data = audio_input["data"]
        listen_for_wake_word(audio_data)
        prompt_hospitality_bot(audio_data)

if __name__ == '__main__':
    main()
