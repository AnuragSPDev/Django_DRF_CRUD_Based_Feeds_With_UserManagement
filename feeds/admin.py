from django.contrib import admin
from .models import Feeds, Comments, Likes

# Register your models here.
@admin.register(Feeds)
class FeedsAdmin(admin.ModelAdmin):
    list_display = ['feed_id', 'title', 'content', 'likes', 'publish_date']

admin.site.register(Comments)
admin.site.register(Likes)
