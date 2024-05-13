from django.urls import path
from . import views

urlpatterns = [
    path("requests/hello_request", views.hello_request, name="hello_request"),
    path("get_json", views.get_json_file, name="get_json"),
]
