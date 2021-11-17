from django.urls import path
from humanoids import views

urlpatterns = [
    path('/humanoids', views.all_humanoids),
    path('/humanoids/<int:id>', views.humanoid_detail),
    path('/countries', views.all_countries)
]