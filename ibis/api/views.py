from rest_framework.viewsets import ModelViewSet

from api.models import Source, Period, TagType, Tag, Alias, Fact
from api.serializers import SourceSerializer, PeriodSerializer, TagTypeSerializer, TagSerializer, AliasSerializer, \
    FactSerializer


class UserModelViewSet(ModelViewSet):
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user.id)


class SourceViewSet(UserModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer


class PeriodViewSet(UserModelViewSet):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer


class TagTypeViewSet(UserModelViewSet):
    queryset = TagType.objects.all()
    serializer_class = TagTypeSerializer


class TagViewSet(UserModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class AliasViewSet(UserModelViewSet):
    queryset = Alias.objects.all()
    serializer_class = AliasSerializer


class FactViewSet(UserModelViewSet):
    queryset = Fact.objects.all()
    serializer_class = FactSerializer
