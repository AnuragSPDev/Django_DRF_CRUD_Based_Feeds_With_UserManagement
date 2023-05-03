from rest_framework import serializers
from .models import Feeds, Comments, Likes

class FeedSerializer(serializers.ModelSerializer):
    '''
    Serializer for handling Feeds
    '''
    comments = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Feeds
        fields = ('title', 'content', 'comments', 'likes')

    def get_comments(self, obj):
        '''
        Method to get comments data from Comments model using CommentSerializer
        '''
        all_comments = Comments.objects.filter(feed=obj.feed_id)

        # Since we have a queryset returned from Comments model and DRF is unable to serializer the same.
        # We need to use the serializers.SerializerMethodField along with a separate serializer class to
        # serialize the Comments objects
        return CommentSerializer(all_comments, many=True).data
    
    def get_likes(self, obj):
        '''
        Method to get comments data from Likes model
        '''
        all_likes = Likes.objects.filter(feed=obj.feed_id)
        return len(all_likes)

class CommentSerializer(serializers.ModelSerializer):
    '''
    Serializer to handle Comments for a feed feature
    '''
    class Meta:
        model = Comments
        fields = ('comment', )

    def validate(self, validated_data):
        if len(validated_data.get('comment')) < 2:
            raise serializers.ValidationError('Atleast 5 characters are required')
        return validated_data

    def create(self, validated_data):
        user = self.context.get('user')
        feed = self.context.get('feed')
        comments = Comments(
            comment = validated_data.get('comment'),
            user = user,
            feed = feed
        )

        comments.save()
        return comments
    
class LikesSerializer(serializers.ModelSerializer):
    '''
    Serializer to handle Likes for a feed feature
    '''
    class Meta:
        model = Likes
        fields = '__all__'

    def create(self, validated_data):
        user = self.context.get('user')
        feed = self.context.get('feed')
        likes = Likes(
            user = user,
            feed = feed
        )

        likes.save()
        return likes