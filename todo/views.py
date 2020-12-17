from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate


def home(request):
    return render(request, 'todo/home.html')


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(request, 'todo/loginuser.html',
                          {'form': AuthenticationForm(), 'error': 'Username and password mismatch.'})
        else:
            login(request, user=user)
            return redirect('currenttodos')


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        new_username = request.POST['username']
        new_password1 = request.POST['password1']
        new_password2 = request.POST['password2']

        if new_password1 == new_password2:
            try:
                new_user = User.objects.create_user(new_username, password=new_password2)
                new_user.save()
                login(request, user=new_user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html',
                              {'form': UserCreationForm(), 'error': 'Username already exists.'})
        else:
            # tell user the password mismatch
            return render(request, 'todo/signupuser.html',
                          {'form': UserCreationForm(), 'error': 'Password did not match'})


def currenttodos(request):
    return render(request, 'todo/currenttodos.html')


def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
