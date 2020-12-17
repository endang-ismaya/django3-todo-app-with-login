from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone

from .forms import TodoForm
from .models import Todo
from django.contrib.auth.decorators import login_required


def home(req):
    return render(req, 'todo/home.html')


def loginuser(req):
    if req.method == 'GET':
        return render(req, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        username = req.POST['username']
        password = req.POST['password']

        user = authenticate(req, username=username, password=password)
        if user is None:
            return render(req, 'todo/loginuser.html',
                          {'form': AuthenticationForm(), 'error': 'Username and password mismatch.'})
        else:
            login(req, user=user)
            return redirect('currenttodos')


def signupuser(req):
    if req.method == 'GET':
        return render(req, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        new_username = req.POST['username']
        new_password1 = req.POST['password1']
        new_password2 = req.POST['password2']

        if new_password1 == new_password2:
            try:
                new_user = User.objects.create_user(new_username, password=new_password2)
                new_user.save()
                login(req, user=new_user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(req, 'todo/signupuser.html',
                              {'form': UserCreationForm(), 'error': 'Username already exists.'})
            except ValueError:
                return render(req, 'todo/signupuser.html',
                              {'form': UserCreationForm(), 'error': 'Please fill all forms.'})
        else:
            # tell user the password mismatch
            return render(req, 'todo/signupuser.html',
                          {'form': UserCreationForm(), 'error': 'Password did not match'})


@login_required
def currenttodos(req):
    todos = Todo.objects.filter(user=req.user, datecompleted__isnull=True)
    return render(req, 'todo/currenttodos.html', {'todos': todos})


@login_required
def completedtodos(req):
    todos = Todo.objects.filter(user=req.user, datecompleted__isnull=False)
    todos.order_by('-datecompleted')
    return render(req, 'todo/completedtodos.html', {'todos': todos})


@login_required
def logoutuser(req):
    if req.method == 'POST':
        logout(req)
        return redirect('home')


# Todos
@login_required
def createtodo(req):
    if req.method == 'GET':
        return render(req, 'todo/crud/createtodo.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(req.POST)
            new_todo = form.save(commit=False)
            new_todo.user = req.user
            new_todo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(req, 'todo/crud/createtodo.html',
                          {'form': TodoForm(), 'error': 'invalid data was submitted.'})


@login_required
def viewtodo(req, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, user=req.user)
    if req.method == 'GET':
        form = TodoForm(instance=todo)
        return render(req, 'todo/crud/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(req.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            form = TodoForm(instance=todo)
            return render(req, 'todo/crud/viewtodo.html',
                          {'todo': todo, 'form': form, 'error': 'invalid data was submitted.'})


@login_required
def completetodo(req, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, user=req.user)
    if req.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')


@login_required
def deletetodo(req, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, user=req.user)
    if req.method == 'POST':
        todo.delete()
        return redirect('currenttodos')


def pagenotfound(req):
    return render(req, 'todo/404.html')
