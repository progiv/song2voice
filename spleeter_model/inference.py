from spleeter.separator import Separator

class Spleeter:
    def __init__(self):
        """
        separator model initialization 
        """
        self.separator = Separator('spleeter:2stems')
    
    def predict(self, path_to_input, path_to_output):
        """
        path_to_input: path to input file; file must be in mp3 or wav format
        path_to_output: path to folder where to save file; files will be saved in wav format
        """
        self.separator.separate_to_file(path_to_input, path_to_output)
