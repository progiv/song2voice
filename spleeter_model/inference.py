import os
import logging
import tempfile
import warnings
#disabling FutureWarnings at the initialization
warnings.filterwarnings('ignore', category=FutureWarning)

from pydub import AudioSegment
from spleeter.separator import Separator
#disabling tensorflow logs at the inference
logging.getLogger("tensorflow").setLevel(logging.ERROR)

logger = logging.getLogger('default')

class Spleeter:
    """
    Music separator model based on spleeter:2stems from https://github.com/deezer/spleeter.
    """
    
    def __init__(self, max_duration=30, overlap=1, music_format="wav",
                 music_types=["vocals", "accompaniment"], sup_dir="sup"):
        """
        Args:
            max_duration (int): maximum duration of one music chunk in seconds
            overlap (int): overlap for music chunks in seconds
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
        logger.info('Initialization is finished successfully')
        

    def predict(self, path_to_input, path_to_output):
        """
        Extracting 'vocals' and/or 'accompaniment' from audio and saving results on disk
        Args:
            path_to_input (str): path to input file; file must be in ('mp3', 'wav', 'raw', 'ogg')
            path_to_output (str): path to folder where to save file
        Returns:
            None
        """
        
        music_dir = os.path.splitext(os.path.basename(path_to_input))[0]
        
        path_to_music_dir = os.path.join(path_to_output, music_dir)
        
        if music_dir not in os.listdir(path_to_output):
            os.mkdir(path_to_music_dir)
        
        with tempfile.TemporaryDirectory() as path_to_sup_dir:

            sound = AudioSegment.from_file(path_to_input)                
            logger.info('Audio file was loaded successfully')

            n_chunks = self._separate_audio(sound, path_to_sup_dir)            
            logger.info('Audio file was divided into chunks successfully')

            self._predict_audio_chunks(n_chunks, path_to_sup_dir)
            logger.info('Vocal was extracted from each chunk successfully')
            
            self._join_audio(n_chunks, path_to_sup_dir, path_to_music_dir)
            logger.info('All chunks were joined into one audio file successfully')
            
        logger.info('Vocal extraction was finished successfully')
 

    def _separate_audio(self, sound, path_to_sup_dir):
        
        left_border, right_border, num = 0, 0, 0
        
        while right_border < len(sound):
            
            left_border, right_border = num * self.max_duration, (num + 1) * self.max_duration + self.overlap
            
            path_to_chunk = f"{path_to_sup_dir}/chunk{num}.{self.music_format}"
            sound[left_border:right_border].export(open(path_to_chunk, "wb"), format=self.music_format)
            
            num += 1
            
        return num

    
    def _predict_audio_chunks(self, n_chunks, path_to_sup_dir):
        
        for num in range(n_chunks):
            
            path_to_chunk = f"{path_to_sup_dir}/chunk{num}.{self.music_format}"
            self.separator.separate_to_file(path_to_chunk, path_to_sup_dir, codec=self.music_format)

            
    def _join_audio(self, n_chunks, path_to_sup_dir, path_to_music_dir):

        for music_type in self.music_types:
            
            path_to_chunk = f"{path_to_sup_dir}/chunk0/{music_type}.{self.music_format}"
            sound = AudioSegment.from_file(path_to_chunk)
            
            for num in range(1, n_chunks):   
                
                path_to_chunk = f"{path_to_sup_dir}/chunk{num}/{music_type}.{self.music_format}"
                sound = sound[:-self.overlap] + AudioSegment.from_file(path_to_chunk)
                
            path_to_output = f"{path_to_music_dir}/{music_type}.{self.music_format}"
            sound.export(open(path_to_output, "wb"), format=self.music_format)
