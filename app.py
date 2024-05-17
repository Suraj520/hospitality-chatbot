# Import necessary libraries
import streamlit as st  # Importing Streamlit for creating web applications
import whisper  # Importing whisper for ASR (Automatic Speech Recognition)
import openai  # Importing OpenAI library for chatGPT
from audiorecorder import audiorecorder  # Importing audiorecorder for recording audio
import magic  # Importing magic for identifying file types
import os  # Importing os for interacting with the operating system
import re  # Importing re for regular expressions
from dotenv import load_dotenv  # Importing load_dotenv to load environment variables

# Define a function to generate TTS (Text-to-Speech) voices using the Web Speech API
def generate_voice(text, voice):
    """
    Generate a TTS voice using the Web Speech API
    :param text: The text to be spoken
    :param voice: The voice to use
    """
    # Define the JavaScript code to generate the voice
    js_code = f"""
        const synth = window.speechSynthesis;
        const utterance = new SpeechSynthesisUtterance("{text}");
        utterance.voice = speechSynthesis.getVoices().filter((v) => v.name === "{voice}")[0];
        synth.speak(utterance);
    """
    # Use the components module to embed the JavaScript code in the web page
    st.components.v1.html(f"<script>{js_code}</script>", height=0)

# Define a function to get the audio record format based on file magic
def get_audio_record_format(orgfile):
    """
    Get the audio record format based on file magic
    :param orgfile: The original file
    :return: The audio record format (e.g..webm,.mp4,.wav)
    """
    info = magic.from_file(orgfile).lower()
    print(f'\n\n Recording file info is:\n {info} \n\n')
    if 'webm' in info:
        return '.webm'
    elif 'iso media' in info:
        return '.mp4'
    elif 'wave' in info:
        return '.wav'
    else:
        return '.mp4'

# Define a Conversation class to handle chatGPT responses
class Conversation:
    def __init__(self, engine):
        """
        Initialize the Conversation class
        :param engine: The chatGPT engine to use
        """
        self.engine = engine

    def generate_response(self, message):
        """
        Generate a response from chatGPT
        :param message: The input message
        :return: The response from chatGPT
        """
        response = openai.Completion.create(
            engine=self.engine,
            prompt=message,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.2,
            presence_penalty=0.6,
            frequency_penalty=0.6
        )
        return response.choices[0].text

# Define a function to initialize load setups
def init_load_setups():
    """
    Initialize load setups for ASR (Automatic Speech Recognition), chatGPT, and TTS (Text-to-Speech)
    :return: ASR model, chatGPT instance, and TTS voices
    """
    # Setup ASR engine
    asrmodel = whisper.load_model('base', download_root='asrmodel')
    # Setup chatGPT instance
    load_dotenv('.env')  # Load the environment variables from the .env file
    openai.api_key = os.getenv("OPENAI_API_KEY").strip('"')  # Get the OpenAI API key from the environment variables
    conversation = Conversation(engine="text-davinci-003")
    # Load TTS voices and language code mapping
    ttsVoices = {}
    for line in open('language-tts-voice-mapping.txt', 'rt').readlines():
        if len(line.strip().split(',')) == 3:
            language, langCode, voiceName = line.strip().split(',')
            ttsVoices[langCode.strip()] = voiceName.strip()
    return asrmodel, conversation, ttsVoices

# Define the main voice chat app
def app():
    """
    The main voice chat app
    """
    # Put expensive initialize computation here
    st.title("Hospitality Chatbot - Voice Assistant")  # Title of the web application
    st.subheader("It understands 97 Spoken Languages!")  # Subheader describing the capability

    # Get initial setup
    asr, chatgpt, ttsVoices = init_load_setups()

    # Recorder
    audio = audiorecorder("Push to Talk", "Recording... (push again to stop)")

    if len(audio) > 0:
        # To play audio in frontend:
        st.audio(audio.tobytes())
        # To save audio to a file:
        audioname = 'recording.tmp'
        with open(audioname, "wb") as f:
            f.write(audio.tobytes())
        ## Get record file format based on file magic
        recordFormat = get_audio_record_format(audioname)
        os.rename(audioname, audioname + recordFormat)

        st.markdown("<b>Chat History</b> ", unsafe_allow_html=True)

        with st.spinner("Recognizing your voice command..."):
            asr_result = asr.transcribe(audioname + recordFormat)
            text = asr_result["text"]
            languageCode = asr_result["language"]
            st.markdown("<b>You:</b> " + text, unsafe_allow_html=True)
            print('ASR result is:' + text)

        st.write('')

        with st.spinner("Getting ChatGPT answer for your command..."):
            response = chatgpt.generate_response(text)
            st.markdown("<b>chatGPT:</b> " + response, unsafe_allow_html=True)
            print('chatGPT response is: ' + response)
            spokenResponse = re.sub(r'\s+', ', response)
            spokenResponse = spokenResponse.lstrip().rstrip()
            # Speak the input text
            generate_voice(spokenResponse, ttsVoices[languageCode])

if __name__ == "__main__":
    app()
