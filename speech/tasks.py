import speech_recognition as sr


def audio_recognition(audio_file):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.record(source)
        res = r.recognize_sphinx(audio).replace(" ",'')

    return res