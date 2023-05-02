from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST, 
                                   HTTP_403_FORBIDDEN)
from rest_framework import permissions
from rest_framework.views import APIView

from .models import Feeds, Likes
from .serializer import FeedSerializer, CommentSerializer, LikesSerializer

from django.core.exceptions import ObjectDoesNotExist


# Create your views here.
class FeedsListCreateView(ListCreateAPIView):
    '''
    Class based view for handling listing/creating feeds extending ListCreateAPIView
    '''
    permission_classes = [permissions.IsAuthenticated]
    queryset = Feeds.objects.all()
    serializer_class = FeedSerializer

class FeedRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    '''
    Class based view for handling detail/editing/deleting feeds extending RetrieveUpdateDestroyAPIView
    '''
    permission_classes = [permissions.IsAuthenticated]
    queryset = Feeds.objects.all()
    serializer_class = FeedSerializer

class FeedCommentsView(APIView):
    '''
    Class based view for handling comments made for a feed extending APIView
    '''
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer

    try:
        def post(self, request):
            data = request.data
            if data is None:
                return Response({
                    'status': HTTP_400_BAD_REQUEST,
                    'message': 'Blank comment is not allowed'
                })
       
            try:
                # Check is feed exists or not
                feed = Feeds.objects.get(feed_id=request.data.get('feed'))
            except ObjectDoesNotExist as e:
                return Response({
                    'status': HTTP_400_BAD_REQUEST,
                    'message': 'This comment is not available'
                })

            user = request.user
            serializer = CommentSerializer(data=data, context={'user':user, 'feed':feed})
       
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'status': HTTP_200_OK,
                    'message': 'Comment posted successfully',
                    'Your Comment': serializer.data.get('comment'),
                    'For feed': feed.title
                })
            return Response({
                'status': HTTP_403_FORBIDDEN,
                'message': 'Something went wrong'
            })
    except Exception as e:
        print('Exception is: ', e)
        
class FeedLikeView(APIView):
    '''
    Class based view for handling likes to a feed extending APIView
    '''
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LikesSerializer
    
    try:
        def post(self, request):
            data = request.data
            if data.get('feed') is None:
                return Response({
                    'status': HTTP_400_BAD_REQUEST,
                    'message': "Feed can't be none"
                })
            
            try:
                # Check is feed exists or not
                feed = Feeds.objects.get(feed_id=request.data.get('feed'))
            except ObjectDoesNotExist as e:
                return Response({
                    'status': HTTP_400_BAD_REQUEST,
                    'message': 'This comment is not available'
                })
            
            user = request.user
            serializer = LikesSerializer(data = data, context={'user':user, 'feed':feed})
            if serializer.is_valid():
                serializer.save()

                # Set the number of likes for a feed in the Feeds model
                feed.likes = len(Likes.objects.filter(feed=feed))
                feed.save()
                return Response({
                    'status': HTTP_200_OK,
                    'message': 'Like posted successfully',
                    'For feed': feed.title
                })
            return Response({
                'status': HTTP_403_FORBIDDEN,
                'message': 'Something went wrong'
            })                
    except Exception as e:
        print('Exception is: ', e)
