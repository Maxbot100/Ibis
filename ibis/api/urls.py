from django.conf.urls import url
from django.urls import include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from api.views import SourceViewSet, PeriodViewSet, TagTypeViewSet, TagViewSet, AliasViewSet, FactViewSet

router = DefaultRouter()
router.register(r'sources', SourceViewSet)
router.register(r'periods', PeriodViewSet)
router.register(r'tag_types', TagTypeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'aliases', AliasViewSet)
router.register(r'facts', FactViewSet)


urlpatterns = [
    url(r'^token/', obtain_auth_token),
    url(r'^', include(router.urls))
]
