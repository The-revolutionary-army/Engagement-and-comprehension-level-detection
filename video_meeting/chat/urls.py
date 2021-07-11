from django.urls import re_path
from .views import *

app_name = 'chat'

urlpatterns = [
    re_path(r'^$', main_view, name="main_view"),
    re_path(r'^create/$', create_csv, name="create_csv"),
    re_path(r'^model/$', model_view, name="model_view"),
    re_path(r'^states/$', states_view, name="states_view")
]