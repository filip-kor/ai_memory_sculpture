from flask import Flask, request, send_file, render_template
import cadquery as cq
import time

from WaveProcessor import WaveProcessor
from EmotionExtractor import EmotionExtractor
from SculptureGenerator import SculptureGenerator

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('website.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Retrieves the audio file from the website, processes it and generates the sculpture.
    """
    file = request.files['file']

    # Process audio and return audio array and the path to WAV file
    p_audio_array, mp3_path = process_audio(file)

    # Extract emotions from the audio recording using IBM Speech-to-text and IBM Natural Language Understanding tools
    response = extract_emotions(mp3_path)

    # Generate the sculpture
    outputfile = generate_sculpture(response, p_audio_array)

    return send_file(outputfile, as_attachment=True)

def process_audio(file):
    """
    Processes an audio file to prepare it for modeling and emotion extraction.
    
    Args:
        file: The audio file to process.
        
    Returns:
        tuple: A tuple containing the processed audio array and the path to the saved WAV file.
    """

    print("Processing audio...")
    w_proc = WaveProcessor(file)

    # Prepare audio for modelling
    p_audio_array = w_proc.process()

    # Prepare audio for emotion extraction
    mp3_path = w_proc.save_to_mp3()

    return p_audio_array, mp3_path

def extract_emotions(path):
    """
    Extracts emotions from an audio file using IBM Speech-to-Text and Natural Language Understanding tools.
    
    Args:
        path: The path to the audio file.
        
    Returns:
        list: A list of dictionaries containing the emotion classes and confidences.
    """
    
    print("Extracting emotions...")
    em_extractor = EmotionExtractor()

    # Get text from recording
    text = em_extractor.get_stt_response(path)

    # Get emotions from text
    response = em_extractor.get_nlu_response(text)

    # Format the response
    for el in response:
        print('Emotion:', el['class_name'])
        print('Confidence:', el['confidence'])
        print()

    return response

def generate_sculpture(response, p_audio_array):
    """
    Generates a sculpture based on the extracted emotions and processed audio.
    
    Args:
        response: A list of dictionaries containing the emotion classes and confidences.
        p_audio_array: The processed audio array.
        
    Returns:
        str: The path to the generated sculpture file as an STL file.
    """

    print("Generating sculpture...")

    sculp_gen = SculptureGenerator()

    # Generate the model
    sculpture = sculp_gen.generate(response, p_audio_array)

    # Render and export the model
    print("Rendering sculpture...")

    outputfile = 'outputs/yoursculpture.stl'
    cq.exporters.export(sculpture, outputfile)

    return outputfile

if __name__ == '__main__':
    app.run()