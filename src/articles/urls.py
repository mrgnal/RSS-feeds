from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, ArticleCollectionViewSet, AdminArticleCollectionViewSet, AdminArticleViewSet

route = DefaultRouter()
route.register(r'collections', ArticleCollectionViewSet, basename='collection')
route.register(r'articles', ArticleViewSet, basename='article')

admin_router = DefaultRouter()
admin_router.register(r'admin/collections', AdminArticleCollectionViewSet, basename='admin-collections')
admin_router.register(r'admin/articles', AdminArticleViewSet, basename='admin-articles')


urlpatterns=[
    path('',include(route.urls)),
    path('', include(admin_router.urls)),
]

# urlpatterns = [
#     path('article_collections/', ArticleCollectionListAPIView.as_view()),
#     path('article_collections/create/', ArticleCollectionCreateAPIView.as_view()),
#     path('article_collections/<uuid:pk>/update/', ArticleCollectionAPIView.as_view()),
#     path('article_collections/<uuid:pk>/delete/', ArticleCollectionAPIView.as_view()),
#     path('article/<uuid:pk>/delete/', ArticleDeleteAPIView.as_view()),
#     path('article/add/', AddArticleToCollection.as_view()),
#     path('article_collection/articles/', CollectionWithArticles.as_view()),
#     path('articles/saved/', ArticlesInCollections.as_view()),
# ]