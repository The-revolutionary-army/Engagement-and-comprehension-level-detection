from django.apps import AppConfig
from tensorflow import keras

class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'

    states_model = keras.models.load_model('parallel_model.h5')