from django.urls import path
from . import views

urlpatterns = [
    path("requests", views.hello_request, name="hello_request"),
]
