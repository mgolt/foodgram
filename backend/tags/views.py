from rest_framework import viewsets

from tags.models import Tags
from tags.serializers import TagSerializer


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
