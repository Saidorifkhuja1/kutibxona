from django.db import models
from accounts.models import User
from django.utils import timezone
class News(models.Model):
    title = models.CharField(max_length=250)
    body = models.TextField()
    image = models.ImageField(upload_to='news/')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at =models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
