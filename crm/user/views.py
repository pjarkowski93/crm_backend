from django.contrib.auth import authenticate, login
from django.shortcuts import render
from rest_framework import generics, permissions, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from user.forms import LoginForm
from user.models import User
from user.serializers import UserSerializer


def home(request):
    return render(request, "login.html", context={"form": LoginForm})


class AuthView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        import pdb

        pdb.set_trace()
        login_form = LoginForm(
            username=request.data["username"], password=request.data["password"]
        )
        if not login_form.is_valid():
            return Response(status=400, template_name="dashboard/index.html")
        user = authenticate(
            username=login_form.cleaned_data["username"],
            password=login_form.cleaned_data["password"],
        )
        if user is not None:
            login(request, user)
            message = f"Hello {user.username}! You have been logged in"
        else:
            message = "Login failed!"
        return Response(
            {"user_uuid": user.uuid, "email": user.email, "message": message},
            template_name="dashboard/index.html",
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
