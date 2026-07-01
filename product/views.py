from collections import OrderedDict

from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from common.permissions import IsOwner, IsModerator
from common.validators import validate_user_age

from .models import Category, Product, Review
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductWithReviewsSerializer,
    ReviewSerializer,
    ReviewValidateSerializer,
)

PAGE_SIZE = 5


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("total", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )

    def get_page_size(self, request):
        return PAGE_SIZE


class CategoryListCreateAPIView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPagination


class CategoryDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "id"


class ProductListCreateAPIView(ListCreateAPIView):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        validate_user_age(self.request)
        serializer.save(owner=self.request.user)


class ProductDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    lookup_field = "id"
    permission_classes = [IsOwner | IsModerator]


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = CustomPagination
    lookup_field = "id"
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = ReviewValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review = Review.objects.create(
            text=serializer.validated_data.get("text"),
            stars=serializer.validated_data.get("stars"),
            product=serializer.validated_data.get("product"),
        )

        return Response(
            ReviewSerializer(review).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        serializer = ReviewValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review.text = serializer.validated_data.get("text")
        review.stars = serializer.validated_data.get("stars")
        review.product = serializer.validated_data.get("product")
        review.save()

        return Response(ReviewSerializer(review).data)


class ProductWithReviewsAPIView(APIView):
    def get(self, request):
        paginator = CustomPagination()

        products = (
            Product.objects.select_related("category")
            .prefetch_related("reviews")
            .all()
        )

        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductWithReviewsSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)