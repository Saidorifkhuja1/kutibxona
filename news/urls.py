from django.urls import path
from .views import *

urlpatterns = [
    path('news_create/', CreateNewsAPIView.as_view()),
    path('news_list/', NewsListAPIView.as_view()),
    path('news_update/<int:pk>/', NewsUpdateAPIView.as_view()),
    path('news_details/<int:pk>/', NewsDetailAPIView.as_view()),
    path('news_delete/<int:pk>/', NewsDeleteAPIView.as_view()),

]