from django.urls import re_path
from .views import *

app_name = 'chat'

urlpatterns = [
    re_path(r'^$', main_view, name="main_view")
]