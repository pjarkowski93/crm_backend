from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from user import views

router = routers.DefaultRouter()
router.register("users", views.UserViewSet, basename="users")

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("auth/", obtain_auth_token, name="token"),
]
