from flask import Flask, request, render_template, jsonify, send_file
import os
from datetime import datetime
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig, Part
from google.cloud import texttospeech
import mimetypes
import tempfile
from pydub import AudioSegment
import io

app = Flask(__name__)

# Initialize vertexai
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "Ajay_application_default_credentials.json"
vertexai.init(project="llmsproject", location="us-central1")

# Global variable to store the latest audio response
latest_audio_response = None

def clean_audio_data(audio_data, original_format=None):
    try:
        # Process audio in memory using BytesIO
        audio_buffer = io.BytesIO()
        
        if original_format == 'mp3':
            audio_buffer.write(audio_data)
        else:
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=original_format or 'wav')
            audio = audio.set_channels(1).set_frame_rate(44100)
            audio.export(audio_buffer, format='mp3', parameters=["-q:a", "0"])
        
        audio_buffer.seek(0)
        return audio_buffer
    except Exception as e:
        print(f"Error cleaning audio: {str(e)}")
        return None

def analyze_audio(audio_buffer):
    model = GenerativeModel("gemini-1.5-pro")
    prompt = """
    Please analyze this audio and provide:
    1. Detailed transcription with:
       - Timestamps in [HH:MM:SS] format
       - Speaker identification (Speaker A, B, etc.)
    2. Sentiment analysis for:
       - Overall conversation tone
       - Each speaker's emotional state
       - Key emotional moments

    Format the response as:
    Transcription:
    [timestamp] Speaker: text

    Sentiment Analysis:
    Overall Tone:
    Speaker Analysis:
    Key Emotional Moments:
    """

    try:
        audio_content = audio_buffer.getvalue()
        mime_type = "audio/mpeg"
        audio_part = Part.from_data(data=audio_content, mime_type=mime_type)

        response = model.generate_content(
            contents=[audio_part, prompt],
            generation_config=GenerationConfig(
                temperature=0.2,
                top_k=40,
                top_p=0.95,
                audio_timestamp=True
            )
        )

        return response.text
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        return None

def clean_text_for_speech(text):
    parts = text.split('Sentiment Analysis:')
    transcription = parts[0].replace('Transcription:', '').strip()
    sentiment = parts[1].strip() if len(parts) > 1 else ''

    cleaned_sentiment = sentiment.replace('**', '').replace('##', '')
    cleaned_sentiment = cleaned_sentiment.replace('[', '').replace(']', '')
    cleaned_sentiment = ' '.join(line.strip() for line in cleaned_sentiment.split('\n') if line.strip())

    clean_text = f"Transcription: {transcription}\n\nSentiment Analysis: {cleaned_sentiment}"
    return clean_text.replace('*', '').replace('#', '')

def text_to_speech(text):
    try:
        clean_text = clean_text_for_speech(text)
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=clean_text)

        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Neural2-F",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.9,
            pitch=0.0,
            effects_profile_id=["telephony-class-application"]
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        # Return the audio content directly
        return io.BytesIO(response.audio_content)
    except Exception as e:
        print(f"Error during text-to-speech conversion: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index3.html')

@app.route('/upload', methods=['POST'])
def upload_audio():
    try:
        audio_file = request.files['audio']
        audio_data = audio_file.read()

        audio_buffer = clean_audio_data(audio_data, 'mp3')
        if not audio_buffer:
            return jsonify({'success': False, 'error': 'Failed to process audio'}), 500

        analysis = analyze_audio(audio_buffer)
        if not analysis:
            return jsonify({'success': False, 'error': 'Analysis failed'}), 500

        global latest_audio_response
        latest_audio_response = text_to_speech(analysis)
        if not latest_audio_response:
            return jsonify({'success': False, 'error': 'Text-to-speech failed'}), 500

        parts = analysis.split('Sentiment Analysis:')
        return jsonify({
            'success': True,
            'transcription': parts[0].strip(),
            'sentiment': parts[1].strip() if len(parts) > 1 else '',
            'audio_url': '/get_audio'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_audio_endpoint():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    try:
        file = request.files['file']
        audio_data = file.read()
        file_ext = file.filename.split('.')[-1].lower()

        audio_buffer = clean_audio_data(audio_data, file_ext)
        if not audio_buffer:
            return jsonify({'error': 'Failed to process audio'}), 500

        analysis = analyze_audio(audio_buffer)
        if not analysis:
            return jsonify({'error': 'Analysis failed'}), 500

        global latest_audio_response
        latest_audio_response = text_to_speech(analysis)
        if not latest_audio_response:
            return jsonify({'error': 'Text-to-speech failed'}), 500

        parts = analysis.split('Sentiment Analysis:')
        return jsonify({
            'success': True,
            'transcription': parts[0].strip(),
            'sentiment': parts[1].strip() if len(parts) > 1 else '',
            'audio_url': '/get_audio'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_audio')
def get_audio():
    if latest_audio_response:
        latest_audio_response.seek(0)
        return send_file(
            latest_audio_response,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='response.mp3'
        )
    return jsonify({'error': 'No audio response available'}), 404

@app.route('/_ah/warmup')
def warmup():
    return '', 200

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))