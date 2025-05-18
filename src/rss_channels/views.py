from rest_framework.decorators import action
from django.core.serializers import serialize
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from auth_app.permissions import IsOwner, IsAdmin
from rest_framework.viewsets import ModelViewSet

from .serializers import RssChannelSerializer
from .models import RssChannel
from .feed import create_feed, delete_feed


class RssChannelViewSet(viewsets.ModelViewSet):
    serializer_class = RssChannelSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        """Get all user`s channels"""
        return RssChannel.objects.filter(user_id=self.request.user.get('id'))

    def create(self, request, *args, **kwargs):
        """Create new channel"""

        data = request.data.copy()
        user_id = request.user.get('id')

        #Check max limit
        # max_feed_limit = max_feeds(request)
        # if not max_feed_limit:
        #     return Response({'detail': 'Unable to fetch max feeds.'}, status=status.HTTP_400_BAD_REQUEST)
        #
        # current_feeds_count = RssChannel.objects.filter(user_id=user_id).count()
        # if current_feeds_count >= max_feed_limit:
        #     return Response({'detail': 'Max feeds reached.'}, status=status.HTTP_403_FORBIDDEN)

        if not data.get('articles'):
            return Response({f'detail': f'No articles provided.' }, status=status.HTTP_400_BAD_REQUEST)

        data['user_id'] = user_id
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            new_channel = serializer.save()
            feed_id = create_feed(new_channel.id, data).get('feed_id')
            responses_data = serializer.data.copy()
            responses_data.update({'feed_id': feed_id})
            return Response(responses_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Update an RSS channel"""

        kwargs['partial'] = True

        allowed_fields = {'title, subtitle, image_url', 'status', 'is_new'}
        data = {key: value for key, value in request.data.items() if key in allowed_fields}
        request._full_data = data

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({"detail": "Update successful"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Delete an RSS channel"""

        instance = self.get_object()
        channel_id = instance.id

        response = delete_feed(channel_id)

        if response.status_code == 204:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def source(self, request, pk=None):
        """Get source information"""
        channel = self.get_object()

        response_data = {
            'id': channel.id,
            'url': channel.url,
            'tittle': channel.title,
            'subtitle': channel.subtitle,
            'image_url': channel.image_url,
            'is_new': channel.is_new,
            'status': channel.status,
            'update': channel.updated,
            'created_at': channel.created_at,
        }
        return Response(response_data)

class AdminChannelViewSet(ModelViewSet):
    queryset = RssChannel.objects.all()
    serializer_class = RssChannelSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        channel_id = instance.id

        response = delete_feed(channel_id)

        if response.status_code == 204:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'Failed to delete channel from parser.'},
                            status=status.HTTP_502_BAD_GATEWAY)

# Delete code
# class RssChannelAPIView(APIView):
#
#     def get(self, request, *args, **kwargs):
#         user = request.user
#         if not user:
#             return Response({'detail': 'User unauthorized.'}, status=status.HTTP_401_UNAUTHORIZED)
#         user_id = user.get('id')
#         channels = RssChannel.objects.filter(user_id=user_id)
#         count = len(channels)
#         response_data = []
#         for channel in channels:
#             response_item ={
#                 'id': channel.id,
#                 'url': channel.url,
#                 'tittle': channel.title,
#                 'subtitle': channel.subtitle,
#                 'image_url': channel.image_url,
#                 'is_new': channel.is_new,
#                 'status': channel.status,
#                 'updated': channel.updated,
#                 'created_at': channel.created_at,
#             }
#             response_data.append(response_item)
#
#         return Response({'count':count, 'channels':response_data})
#
#     def post(self, request, *args, **kwargs):
#         data = request.data.copy()
#         user = request.user
#
#         if not user:
#             return Response({'detail': 'User unauthorized.'}, status=status.HTTP_401_UNAUTHORIZED)
#         user_id = user.get('id')
#         # max_feed_limit = max_feeds(request)
#         # if not max_feed_limit:
#         #     return Response({'detail': 'Unable to fetch max feeds.'}, status=status.HTTP_400_BAD_REQUEST)
#         #
#         # current_feeds_count = RssChannel.objects.filter(user_id=user_id).count()
#         # if current_feeds_count >= max_feed_limit:
#         #     return Response({'detail': 'Max feeds reached.'}, status=status.HTTP_403_FORBIDDEN)
#
#         if not data.get('articles'):
#             return Response({'detail': 'No articles provided.'}, status=status.HTTP_400_BAD_REQUEST)
#
#         data['user_id'] = user_id
#         serializer = RssChannelSerializer(data=data)
#         if serializer.is_valid():
#                 new_channel = serializer.save()
#                 feed_id = create_feed(new_channel.id, data).get('feed_id')
#                 response_data = serializer.data.copy()
#                 response_data.update({'feed_id': feed_id})
#                 return Response(response_data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def get_object(self, channel_id):
#         if not self.request.user:
#             return Response({'detail': 'User unauthorized.'}, status=status.HTTP_401_UNAUTHORIZED)
#
#         try:
#             obj = RssChannel.objects.get(id=channel_id)
#         except RssChannel.DoesNotExist:
#             raise PermissionDenied("Collection not found.")
#
#         if str(obj.user_id) != str(self.request.user.get('id')):
#             raise PermissionDenied(f"You do not have permission to edit this collection.")
#
#         return obj
#
#     def patch(self, request, *args, **kwargs):
#         channel_id = kwargs.get('pk')
#         channel = self.get_object(channel_id)
#
#         allowed_fields = {'title', 'subtitle', 'image_url', 'status', 'is_new'}
#         data = {key: value for key, value in request.data.items() if key in allowed_fields}
#
#         serializer = RssChannelSerializer(channel, data=data, partial=True)
#
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"detail": "Update successful"}, status=status.HTTP_200_OK)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, *args, **kwargs):
#         channel_id = kwargs.get('pk')
#         channel = self.get_object(channel_id)
#
#         response = delete_feed(channel_id)
#         if response.status_code==204:
#             channel.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         else:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#
# class RssChannelSourseAPIView(APIView):
#     def get(self, request, *args, **kwargs):
#         if not self.request.user:
#             return Response({'detail': 'User unauthorized.'}, status=status.HTTP_401_UNAUTHORIZED)
#         channel_id = kwargs.get('pk')
#         channel = get_object_or_404(RssChannel, id=channel_id)
#
#         response_data = {
#             'id': channel.id,
#             'url': channel.url,
#             'tittle': channel.title,
#             'subtitle': channel.subtitle,
#             'image_url': channel.image_url,
#             'is_new': channel.is_new,
#             'status': channel.status,
#             'update': channel.updated,
#             'created_at': channel.created_at,
#         }
#
#         return Response(response_data)