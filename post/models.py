from django.db import models

from category.models import Category

# Create your models here.
class Post(models.Model):
    """
    post id is a surrogate key (generated by django automatically)
    so it will not be included here.
    """
    text = models.TextField(blank=False, null=False, default='')
    likes = models.PositiveIntegerField(default=0)
    time_created = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)

    category = models.ManyToManyField(Category, blank=True)
