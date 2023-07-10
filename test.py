import streamlit as st
import webrtc_audio

import speech_recognition as sr


def convert_audio_to_text(audio_data):
    r = sr.Recognizer()

    with sr.AudioFile(audio_data) as source:
        audio = r.record(source)

    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Unable to recognize speech."
    except sr.RequestError as e:
        return f"Error: {e}"


def main():
    st.title("Speech to Text Conversion")

    # Create a recorder object
    rec = webrtc_audio.Recorder(stream=True, filename="temp.wav", record=True)

    st.write("Click the button below to start recording:")

    if st.button("Record"):
        st.write("Recording...")

        # Start recording audio
        rec.record()

        st.write("Recording started. Speak into your microphone.")

    if st.button("Stop"):
        # Stop recording audio
        rec.stop()

        st.write("Recording stopped.")

        # Convert audio to text
        text = convert_audio_to_text("temp.wav")

        # Display the converted text
        st.write("Transcription:")
        st.write(text)


if __name__ == "__main__":
    main()
