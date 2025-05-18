from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import RssChannelViewSet, AdminChannelViewSet

router = DefaultRouter()
router.register(r'channels', RssChannelViewSet, basename='channel')
router.register(r'admin/channels', AdminChannelViewSet, basename='admin-channel')

urlpatterns =[
    path('', include(router.urls)),
]