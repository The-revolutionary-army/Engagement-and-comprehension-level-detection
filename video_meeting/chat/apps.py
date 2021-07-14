from django.apps import AppConfig
from tensorflow import keras
import sys
sys.path.append("C:/Users/Moh.Massoud/Documents/GitHub/Comprehension-Level-Detection/OpenFace2")

import openface2


class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'

    states_model = keras.models.load_model('parallel_model.h5')
    au_model=openface2.AUs("C:/Users/Moh.Massoud/Documents/GitHub/Comprehension-Level-Detection/OpenFace2/model")
