import os
import io

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment
from pydub.playback import play

p_num = 50

class WaveProcessor():
    """
    A class for processing audio files.

    Attributes:
        file_format (str): The file format of the audio file.
        file_name (str): The name of the audio file.
        sample_rate (float): The sample rate of the audio file.
        duration (float): The duration of the audio file.
        frequency (float): The frequency of the audio file.
        audio_array (ndarray): A NumPy array containing the audio data.
    """

    def __init__(self, file):
        """
        Initializes WaveProcessor object with the given file.

        Args:
            file: File object to read the audio data from.

        Returns:
            None
        """

        file_path = file.filename
        print(file_path)

        # Extract the file format from the string
        self.file_format = os.path.splitext(file_path)[1][1:]
        print(self.file_format)

        # Extract the filename from the path
        self.file_name = os.path.basename(os.path.splitext(file_path)[0])
        print(self.file_name)
        
        # Load the audio file into an AudioSegment object
        audio_data = file.read()
        audio = AudioSegment.from_file(
            io.BytesIO(audio_data), format=self.file_format
        )

        # Extract the sample rate, duration, and frequency
        self.sample_rate = audio.frame_rate / audio.channels
        self.duration = audio.frame_count() / audio.frame_rate
        self.frequency = audio.frame_rate / 2

        # Extract the audio data as a NumPy array
        self.audio_array = np.array(audio.get_array_of_samples())

        self.audio = audio
    
    def get_audio_array(self):
        """
        Returns the NumPy array representation of the audio file.

        Args:
            None

        Returns:
            numpy.ndarray: Audio data as a NumPy array.
        """

        return self.audio_array

    def plot_audio_array(self, audio_array=None):
        """
        Plots the given audio data as a graph.

        Args:
            audio_array (numpy.ndarray): Audio data to plot as a graph. If None, plots the audio data stored in the object.

        Returns:
            None
        """

        if audio_array is None:
            audio_array = self.audio_array

        plt.plot(audio_array)
        plt.show()
    
    def play_audio(self):
        """
        Plays the audio file using PyAudio if it's a WAV file. Otherwise, uses pydub library to play it.

        Args:
            None

        Returns:
            None
        """

        if self.file_format == "wav":
            chunk = 1024  
            # Create an interface to PortAudio
            p = pyaudio.PyAudio()

            # Open a .Stream object to write the MP3 file to
            stream = p.open(format = p.get_format_from_width(self.audio.getsampwidth()),
            channels = self.audio.getnchannels(),
            rate = self.audio.getframerate(),
            output = True)

            # Read data in chunks
            data = self.audio.readframes(chunk)

            # Play the sound by writing the audio data to the stream
            while data != '':
                stream.write(data)
                data = self.audio.readframes(chunk)

            # Close and terminate the stream
            stream.close()
            p.terminate()
        else:
            play(self.audio)

    def save_to_mp3(self, audio_path=""):
        """
        Saves the audio file as a MP3 file.

        Args:
            audio_path (str): Path to save the MP3 file. If empty, saves to the current directory with the original file name.

        Returns:
            str: Path to the saved MP3 file.
        """

        if not audio_path:
            audio = self.audio
            file_name = self.file_name
        else:
            # Load the audio file into an AudioSegment object
            file_format = os.path.splitext(audio_path)[1][1:]
            audio = AudioSegment.from_file(audio_path, format=file_format)

            # Get the file's name
            file_name = os.path.basename(os.path.splitext(audio_path)[0])

        # Extract the file to MP3 format
        export_path = os.getcwd()+"/audio_processed/"+file_name+".mp3"
        audio.export(export_path)

        return export_path

    def impute_outliers(self, data, m = 7.):
        """
        Replaces any significant outliers with the mean audio value.

        Args:
            data (numpy.ndarray): Audio data as a NumPy array.
            m (float): Outlier threshold. Data points more than m times the median absolute deviation from the median will be considered as outliers.

        Returns:
            numpy.ndarray: Audio data with replaced outliers.
        """

        d = np.abs(data - np.median(data))
        mdev = np.median(d)

        s = d/mdev if mdev else np.zero(len(d))
        data[s>=m] = np.mean(data)

        return data

    def process(self, plot = False, save=False):
        """
        Processes the audio data by reducing its size, replacing outliers and normalizing the data.

        Args:
            plot (bool): If True, plots the processed audio data.
            save (bool): If True, saves the processed audio data as a CSV file.

        Returns:
            numpy.ndarray: Processed audio data as a NumPy array.
        """

        audio_array = self.get_audio_array()

        # Calculate the number of elements to take the average from to fill each element in the new array
        average_size = len(audio_array) // p_num

        # Create an empty array with the desired size
        p_audio_array = np.empty(p_num)

        # Calculate the mean of every few elements and store the result in the new array
        for i in range(p_num):
            p_audio_array[i] = np.mean(audio_array[i*average_size:(i+1)*average_size])

        # Replace any significant outliers with mean audio value
        p_audio_array = self.impute_outliers(p_audio_array)

        # Normalise the array
        p_audio_array = np.interp(p_audio_array, (p_audio_array.min(), p_audio_array.max()), (-0.04, 0.04))

        if plot: self.plot_audio_array(p_audio_array)
        if save: np.savetxt('audio_array.csv', p_audio_array, delimiter=',')

        return p_audio_array