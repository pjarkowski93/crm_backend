from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from rest_framework import permissions, viewsets
from user.forms import UserRegisterForm
from user.models import User
from user.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            team = form.cleaned_data.get("team")
            messages.success(
                request,
                f"Your account {username} has been created! You are now able to log in",
            )
            user = User.objects.get(username=username)
            group = Group.objects.get(name="traders")
            user.groups.add(group)
            return redirect("login")
    else:
        form = UserRegisterForm()
    return render(request, "user/register.html", {"form": form})


@login_required
def profile(request):
    return render(request, "user/profile.html")
