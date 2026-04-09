from django.urls import path
from . import views

urlpatterns = [
    path('',               views.form_view,         name='form'),
    path('ai-suggest/',    views.ai_suggest_view,   name='ai_suggest'),
    path('submissions/',   views.submissions_view,  name='submissions'),
]
