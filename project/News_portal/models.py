from itertools import product

from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
from datetime import datetime, timezone
from django.utils import timezone


from django.template.defaultfilters import length

sport = 'SP'
politics = 'PO'
education = 'ED'
showbusiness = 'SH'
breaking = 'BR'
economy = 'EC'


categories = [
    (sport, 'SP'),
    (politics, 'PO'),
    (education, 'ED'),
    (showbusiness, 'SH'),
    (breaking, 'BR'),
    (economy, 'EC')
]




class Category(models.Model):
    category_name = models.CharField(max_length=2, choices=categories, unique=True)

    def __str__(self):
        return self.get_category_name_display()

class Author(models.Model):
    id = models.AutoField(primary_key=True)
    author_name = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.author_name

    def update_rating(self):
        post_rating = sum(post.rating * 3 for post in self.post_set.all())
        comment_rating = sum(comment.rating for comment in self.user.comment_set.all())
        post_comment_rating = 0
        for post in self.post_set.all():
            for comment in post.comment_set.all():
                post_comment_rating += comment.rating
        self.rating = post_rating + comment_rating + post_comment_rating
        self.save()


class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NE'
    POST_TYPES = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость'),
    ]
    post_type = models.CharField(
        max_length=2,
        choices=POST_TYPES
    )
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    categories = models.ManyToManyField('Category',through='PostCategory')
    date = models.DateTimeField(default=timezone.now, editable=False)
    content = models.TextField()
    rating = models.FloatField(default=0)

    def __str__(self):
        return f"{self.title} ({self.get_post_type_display()})"

    def preview(self):
        return self.content[:124]+'...'

    def like(self):
        self.rating +=1
        self.save()

    def dislike(self):
        if self.rating < 1:
            self.rating = 0
        else:
            self.rating -=1
            self.save()


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    comment = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now, editable=False)
    rating = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user.username}: {self.comment[:50]}..."

    def like(self):
        self.rating +=1
        self.save()

    def dislike(self):
        if self.rating < 1:
            self.rating = 0
        else:
            self.rating -=1
            self.save()




