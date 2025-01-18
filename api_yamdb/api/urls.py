from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    ReviewViewSet,
    CommentViewSet
)

router_v1 = DefaultRouter()
router_v1.register('categories', CategoryViewSet, basename='сategories')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('reviwes', ReviewViewSet, basename='revivwes')
router_v1.register('comments', CommentViewSet, basename='comments')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
