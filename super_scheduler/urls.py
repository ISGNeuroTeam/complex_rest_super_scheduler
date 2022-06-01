from django.urls import re_path
from .views.hello import HelloView
from .views.task import TaskView


urlpatterns = [
    re_path('hello/', HelloView.as_view()),
    re_path(r'^task/?$', TaskView.as_view()),
]
