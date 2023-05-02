from django.db import models
from UserManagement.models import MyUser

# Create your models here.
class Feeds(models.Model):
    '''
    Model representing Feeds
    '''
    feed_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    publish_date = models.DateField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    # dislikes = models.IntegerField()  # To Do - add dislikes feature

    # To remove extra 's' from model name in admin panel
    class Meta:
        verbose_name_plural = "Feed"

    def __str__(self):
        return self.title
    
class Comments(models.Model):
    '''
    Models representing comments made on a feed
    '''
    comment = models.TextField()
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    feed = models.ForeignKey(Feeds, on_delete=models.CASCADE)
    # is there any parent of this comment; here, this is the reply to a comment
    # this will be the foriegn key to itself
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)  # To Do - add reply to a comment feature
    time_stamp = models.DateTimeField(auto_now=True)

    # To remove extra 's' from model name in admin panel
    class Meta:
        verbose_name_plural = "Comment"

    def __str__(self):
        return self.comment[0:25] + '...'
    
class Likes(models.Model):
    '''
    Models representing likes to a feed
    '''
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    feed = models.ForeignKey(Feeds, related_name='likes_feed', on_delete=models.CASCADE, null=True)

    # To remove extra 's' from model name in admin panel
    class Meta:
        verbose_name_plural = "Like"