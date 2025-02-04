from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, FormView, UpdateView, DetailView

from interactions.models import Interaction
from users.forms import UserRegisterForm, UserLoginForm, UserUpdateForm
from users.models import User


class RegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'users/register.html'

    def get_success_url(self):
        return reverse_lazy('users:profile', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Successful registration')
        return response


class LoginView(FormView):
    form_class = UserLoginForm
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse_lazy('books:home', kwargs={'pk': self.request.user.pk})

    def form_valid(self, form):
        from django.contrib.auth import login
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, f'Welcome {user.email}!')
        return super().form_valid(form)


class LogoutView(DjangoLogoutView):
    next_page = reverse_lazy('users:login')

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'You have successfully logged out.')
        return super().dispatch(request, *args, **kwargs)


class ProfileView(DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ratings'] = Interaction.objects.filter(
            user=self.object
        ).select_related('book')
        return context


def my_profile_redirect(request):
    return redirect(reverse('users:profile', kwargs={'pk': request.user.pk}))


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'users/edit_profile.html'

    def get_success_url(self):
        return reverse_lazy('users:profile', kwargs={'pk': self.request.user.pk})

    def test_func(self):
        return self.get_object() == self.request.user

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)
