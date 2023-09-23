import django_filters

from rest_framework import viewsets, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from django.db import transaction
from rest_framework.permissions import IsAuthenticated

from advertise.models import Advertise
from advertise.serializers import (
    AdvertiseListSerializer,
    AdvertiseSerializer,
    AdvertiseImageSerializer)
from advertise.filters import AdvertiseFilter
from advertise.permissions import IsImageOwner, IsOwnerOrReadOnly, IsProfileComplete
from advertise.models import AdvertiseImage, Advertise
from account.permissions import IsPhoneVerified


class AdvertiseViewSet(viewsets.ModelViewSet):
    queryset = Advertise.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, ]
    filterset_class = AdvertiseFilter
    ordering_fields = ['created', 'price']
    pagination_class = PageNumberPagination
    pagination_class.page_size = 30
    permission_classes = [IsPhoneVerified,
                          IsOwnerOrReadOnly, IsProfileComplete, ]

    def perform_create(self, serializer):
        with transaction.atomic():
            advertise = serializer.save(user=self.request.user)
            files = self.request.FILES.getlist('images')

            if not files:
                raise ValidationError(
                    {'images': 'this field is required'})

            if len(files) > 3:
                raise ValidationError(
                    {'error': 'you can not upload more than 3 images'})

            for file in files:
                image_serializer = AdvertiseImageSerializer(
                    data={'image': file})
                if image_serializer.is_valid():
                    image_serializer.save(advertise=advertise)
                else:
                    raise ValidationError(
                        {'error': 'image sent is not valid'})

    def get_serializer(self, *args, **kwargs):
        if self.action == 'list':
            return AdvertiseListSerializer(*args, **kwargs)

        serailizer = AdvertiseSerializer(*args, **kwargs)
        if self.action in ['update', 'partial_update', 'create']:
            serailizer.fields['images'].read_only = True

        return serailizer

    def get_queryset(self):
        queryset = super().get_queryset()
        ordering = self.request.query_params.get('ordering')

        if ordering in self.ordering_fields:
            queryset = queryset.order_by(ordering)

        return queryset


class DeleteImageView(generics.DestroyAPIView):
    serializer_class = AdvertiseImageSerializer
    permission_classes = [IsPhoneVerified,
                          IsAuthenticated, IsImageOwner, IsProfileComplete, ]

    def get_queryset(self):
        return AdvertiseImage.objects.filter(advertise__user=self.request.user)

    def perform_destroy(self, instance):
        if instance.advertise.images.count() <= 1:
            raise ValidationError(
                {'error': 'you can\'t delete all images related to an ad'})
        return super().perform_destroy(instance)


class CreateImageView(generics.CreateAPIView):
    serializer_class = AdvertiseImageSerializer
    permission_classes = [IsPhoneVerified,
                          IsAuthenticated, IsProfileComplete, ]

    def perform_create(self, serializer):
        advertise = Advertise.objects.get(id=self.kwargs.get('pk'))
        if advertise.images.count() == 3:
            raise ValidationError(
                {'detail': 'you can not upload more than 3 images for one add'})
        if advertise.user == self.request.user:
            serializer.save(advertise=advertise)
            return
        raise ValidationError({'detail': 'ad doesn\'t belong to you'})
