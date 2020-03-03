import os
import shutil
from pydub import AudioSegment
from spleeter.separator import Separator

__author__ = "Kirill Talalaev"

class Spleeter:
    """
    Music separator model based on spleeter:2stems from https://github.com/deezer/spleeter.
    """
    
    def __init__(self, max_duration=30, overlap=1, music_format="wav",
                 music_types=["vocals", "accompaniment"], sup_dir="sup"):
        """
        Args:
            max_duration (int): maximum duration of one music part in seconds
            overlap (int): overlap for music parts in seconds
            music_format (str): music saving format ('mp3', 'wav', 'raw', 'ogg')
            music_types (list[str]): music saving types ('vocals' for voice, 'accompaniment' for music)
            sup_dir (str): support directory which will be created at the beginning and removed at the end
        """
        
        self.sup_dir = sup_dir
        self.overlap = overlap * 1000
        self.max_duration = max_duration * 1000
        self.music_types = music_types
        self.music_format = music_format
        
        self.separator = Separator('spleeter:2stems')
 

    def predict(self, path_to_input, path_to_output):
        """
        Extracting 'vocals' and/or 'accompaniment' from audio and saving results on disk
        Args:
            path_to_input (str): path to input file; file must be in ('mp3', 'wav', 'raw', 'ogg')
            path_to_output (str): path to folder where to save file
        Returns:
            None
        """     
        
        path_to_sup_dir = os.path.join(path_to_output, self.sup_dir)
        
        if self.sup_dir not in os.listdir(path_to_output):
            os.mkdir(path_to_sup_dir)
        
        try:
            music_dir = os.path.splitext(os.path.basename(path_to_input))[0].replace("\\", "")

            sound = AudioSegment.from_file(path_to_input)
            
            n_parts = self._separate_audio(sound, path_to_sup_dir)
            
            self._predict_audio_parts(n_parts, path_to_sup_dir, music_dir)

            path_to_music_dir = os.path.join(path_to_output, music_dir)
            
            if music_dir not in os.listdir(path_to_output):
                os.mkdir(path_to_music_dir)

            self._join_audio(n_parts, path_to_sup_dir, music_dir, path_to_music_dir)
            
        except Exception as ex:            
            print("Something went wrong:(")
            raise ex
        
        finally:
            shutil.rmtree(path_to_sup_dir)
 

    def _separate_audio(self, sound, path_to_sup_dir):
        
        left_border, right_border, num = 0, 0, 0
        
        while right_border < len(sound):
            
            left_border, right_border = num * self.max_duration, (num + 1) * self.max_duration + self.overlap
            
            path_to_part = f"{path_to_sup_dir}/part{num}.{self.music_format}"
            sound[left_border:right_border].export(open(path_to_part, "wb"), format=self.music_format)
            
            num += 1
            
        return num

    
    def _predict_audio_parts(self, n_parts, path_to_sup_dir, music_dir):
        
        path_to_output = os.path.join(path_to_sup_dir, music_dir)
        
        for num in range(n_parts):
            
            path_to_input = f"{path_to_sup_dir}/part{num}.{self.music_format}"
            self.separator.separate_to_file(path_to_input, path_to_output)

            
    def _join_audio(self, n_parts, path_to_sup_dir, music_dir, path_to_music_dir):
        
        path_to_input = os.path.join(path_to_sup_dir, music_dir)
        
        for music_type in self.music_types:
            
            path_to_part = f"{path_to_input}/part0/{music_type}.wav"
            sound = AudioSegment.from_file(path_to_part)
            
            for num in range(1, n_parts):   
                
                path_to_part = f"{path_to_input}/part{num}/{music_type}.wav"
                sound = sound[:-self.overlap] + AudioSegment.from_file(path_to_part)
                
            path_to_output = f"{path_to_music_dir}/{music_type}.{self.music_format}"
            sound.export(open(path_to_output, "wb"), format=self.music_format)
