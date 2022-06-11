from django.urls import include, path
from rest_framework import routers
from user import views

router = routers.DefaultRouter()
router.register("users", views.UserViewSet, basename="users")

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
]
