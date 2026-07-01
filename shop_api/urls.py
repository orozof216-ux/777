from django.contrib import admin
from django.urls import path, include
from shop_api.swagger import schema_view

urlpatterns = [
    path("admin/", admin.site.urls),

    path("users/", include("users.urls")),
    path("product/", include("product.urls")),  

    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),

    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]