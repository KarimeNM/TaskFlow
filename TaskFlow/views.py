from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Task
from .forms import RegisterUserForm

def home(request):
    return render(request, 'home.html')

def about_us(request):
    return render(request, 'about_us.html')

def freqask(request):
    return render(request, 'frequently_asked.html')

def contact(request):
    return render(request, 'contact.html')

class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['email', 'username', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

def signup(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                form.add_error('email', 'An account with this email already exists.')
            else:
                user = form.save(commit=False)
                user.email = email
                user.save()
                return redirect('log')
    else:
        form = RegisterUserForm()

    return render(request, 'signup.html', {"form": form})


def log(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect('home') 

            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect('home')
    return render(request, 'logout_confirm.html') 

class TaskList(LoginRequiredMixin, ListView):
    template_name = 'task_list.html'

    def get(self, request):
        incomplete_tasks = Task.objects.filter(user=request.user, complete=False)
        completed_tasks = Task.objects.filter(user=request.user, complete=True)
        return render(request, self.template_name, {
            'incomplete_tasks': incomplete_tasks,
            'completed_tasks': completed_tasks,
        })

    def post(self, request):
        task_id = request.POST.get('task_id')
        if task_id:
            task = Task.objects.get(id=task_id, user=request.user)
            task.complete = not task.complete
            task.save()
        return redirect('tasks')

class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'task.html'

class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')
    template_name = 'task_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')
    template_name = 'task_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
    template_name = 'task_confirm_delete.html'
