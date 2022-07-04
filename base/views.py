from django.shortcuts import render, redirect
from django.http import HttpResponse, request
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Task

# Create your views here.
class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False)
        return context

class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'complete']
    success_url = reverse_lazy('tasklist')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)

def delete_task(request, task_id):
    task = Task.objects.get(pk=task_id)
    task.delete()
    return redirect('tasklist')

def complete_task(request, task_id):
    task = Task.objects.get(pk=task_id)
    task.complete = True
    task.save()
    return redirect('tasklist')

def uncomplete_task(request, task_id):
    task = Task.objects.get(pk=task_id)
    task.complete = False
    task.save()
    return redirect('tasklist')


def home_view(request):
    context = {}
    return render(request, 'home.html', context)

def register_user(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("You signed up succesfully!"))
            return redirect('tasklist')
    else:
        form = UserCreationForm()
    
    context = {'form': form}
    return render(request, 'signup.html', context)

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('tasklist')
        else:
            messages.success(request, ("Something went wrong. Please try again."))
            return redirect('login')

    context = {}
    return render(request, 'registration/login.html', context)

def logout_user(request):
    logout(request)
    messages.success(request, ("You logged out succesfully!"))
    return redirect('home')

