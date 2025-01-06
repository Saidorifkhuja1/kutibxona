from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.permissions import BasePermission
from accounts.utils import unhash_token
from books.views import APIListPagination
from .models import *
from .serializers import *


class NewsListAPIView(generics.ListAPIView):
    queryset = News.objects.all().order_by('-uploaded_at')
    serializer_class = NewsSerializer
    pagination_class = APIListPagination



class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class CreateNewsAPIView(generics.CreateAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class NewsUpdateAPIView(generics.UpdateAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAdminUser]

    def perform_update(self, serializer):
        serializer.save()


class NewsDetailAPIView(generics.RetrieveAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer

    lookup_field = 'pk'

class NewsDeleteAPIView(generics.DestroyAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAdminUser]





