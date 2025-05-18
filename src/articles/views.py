from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from auth_app.permissions import IsOwner, IsAdmin
from rest_framework.viewsets import ModelViewSet

from .models import Article, ArticleCollection
from .serializers import ArticleSerializer, ArticleCollectionSerializer
from datetime import datetime

class ArticleCollectionViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleCollectionSerializer
    permission_classes = [IsAuthenticated, IsOwner]


    def get_queryset(self):
        """Get all collections"""
        return ArticleCollection.objects.filter(user_id=self.request.user.get('id'))

    def perform_create(self, serializer):
        """Create collection"""
        serializer.save(user_id=self.request.user.get('id'))

    @action(detail=False, methods=['get'])
    def with_articles(self, request):
        """Get all collections with all articles"""
        collections = self.get_queryset()

        collections_data = []
        for collection in collections:
            articles = Article.objects.filter(collection_id=collection.id)
            article_data = ArticleSerializer(articles, many=True).data
            collection_data = ArticleCollectionSerializer(collection).data
            collections_data.append({
                'collection': collection_data,
                'articles': article_data,
            })
        return Response(collections_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def articles_list(self, request):
        """Get saved articles with basic info"""
        collections=self.get_queryset()

        article_data = []
        for collection in collections:
            for article in Article.objects.filter(collection_id=collection.id):
                article_data.append({
                    'collection_id': collection.id,
                    'site_id': article.site_id,
                    'link': article.link,
                })
        if not article_data:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(article_data, status=status.HTTP_200_OK)

class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get all articles in collection"""
        return Article.objects.filter(collection_id__user_id=self.request.user.get('id'))

    def perform_create(self, serializer):
        """Add article to collection"""
        collection_id = self.request.data.get('collection_id')
        try:
            collection = ArticleCollection.objects.get(id=collection_id)
            if str(collection.user_id) != str(self.request.user.get('id')):
                raise PermissionDenied("No permissions to add articles to this collection")

            data = self.request.data.copy()
            if 'published' in data and isinstance(data['published'], list):
                try:
                    published_date = datetime(*data['published'][:6])
                    data['published'] = published_date.isoformat()
                    serializer.validated_data['published'] = published_date.isoformat()
                except (ValueError, TypeError):
                    raise serializer.ValidationError({'published': ['Invalid date format.']})

            serializer.save()
        except ArticleCollection.DoesNotExist:
            raise PermissionDenied('Collection not found')

class AdminArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

class AdminArticleCollectionViewSet(viewsets.ModelViewSet):
    queryset = ArticleCollection.objects.all()
    serializer_class = ArticleCollectionSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    @action(detail=True, methods=['get'])
    def articles(self, request, pk=None):
        """All collections for admin"""
        try:
            collection = self.get_object()
            articles = Article.objects.filter(collection_id=collection.id)
            data = ArticleSerializer(articles, many=True).data
            return Response(data, status=status.HTTP_200_OK)
        except ArticleCollection.DoesNotExist:
            return Response({'error': 'Collection not found'}, status=status.HTTP_404_NOT_FOUND)

#DELETE CODE
# class ArticleDeleteAPIView(APIView):
#     def get_object(self, article_id):
#         if not self.request.user:
#             return Response({'detail': 'User unauthorized.'}, status=status.HTTP_401_UNAUTHORIZED)
#         try:
#             obj = Article.objects.get(id=article_id)
#         except Article.DoesNotExist:
#             raise PermissionDenied("Collection not found.")
#
#
#         collection = ArticleCollection.objects.get(id=obj.collection_id_id)
#         if str(collection.user_id) != str(self.request.user.get('id')):
#             raise PermissionDenied("You do not have permission to edit this collection.")
#         return obj
#
#     def delete(self, request, *args, **kwargs):
#         article_id = kwargs.get('pk')
#         article = self.get_object(article_id)
#
#         article.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
# class CollectionWithArticles(APIView):
#     def get(self, request, *args, **kwargs):
#         if not request.user:
#             return Response({'detail': 'User unauthorized.'}, status=status.HTTP_401_UNAUTHORIZED)
#
#         collections = ArticleCollection.objects.filter(user_id=self.request.user.get('id'))
#
#         collections_data = []
#         for collection in collections:
#             articles = Article.objects.filter(collection_id=collection.id)
#             article_data = ArticleSerializer(articles, many=True).data
#             collection_data = ArticleCollectionSerializer(collection).data
#             collections_data.append({
#                 'collection': collection_data,
#                 'articles': article_data,
#             })
#
#         return Response(collections_data, status=status.HTTP_200_OK)
# class AddArticleToCollection(APIView):
#     def post(self, request):
#         if not request.user:
#             return Response({'detail': 'User unauthorized.'}, status=status.HTTP_401_UNAUTHORIZED)
#
#         data = request.data.copy()
#         serializer = ArticleSerializer(data=data)
#
#         if 'published' in data and isinstance(data['published'], list):
#             try:
#                 published_date = datetime(*data['published'][:6])
#                 data['published'] = published_date.isoformat()
#             except (ValueError, TypeError) as e:
#                 return Response({'published': ['Invalid date format.']}, status=status.HTTP_400_BAD_REQUEST)
#
#         if serializer.is_valid():
#             serializer.save()
#             return Response(status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
# class ArticlesInCollections(APIView):
#     def get(self, request, *args, **kwargs):
#         if not request.user:
#             return Response({'detail': 'User unauthorized.'}, status=status.HTTP_401_UNAUTHORIZED)
#
#         collections = ArticleCollection.objects.filter(user_id=request.user.get('id'))
#
#         data = []
#         for collection in collections:
#             for article in Article.objects.filter(collection_id=collection.id):
#                 data.append({
#                     'collection_id': collection.id,
#                     'site_id': article.site_id,
#                     'link': article.link,
#                 })
#
#         if not data:
#             return Response(status=status.HTTP_204_NO_CONTENT)
#
#         return Response(data, status=status.HTTP_200_OK)