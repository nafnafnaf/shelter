from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import Http404
from .models import ShelterUser
from animals.models import Animal

class CustomLoginView(LoginView):
    template_name = 'shelter/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('shelter:dashboard')

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'shelter/dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        try:
            self.shelter_user = ShelterUser.objects.get(user=request.user)
        except ShelterUser.DoesNotExist:
            raise Http404("User not associated with any shelter")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get dashboard statistics
        context.update({
            'total_animals': Animal.objects.count(),
            'available_for_adoption': Animal.objects.filter(
                adoption_status='available', 
                public_visibility=True
            ).count(),
            'pending_adoptions': Animal.objects.filter(adoption_status='pending').count(),
            'recent_animals': Animal.objects.all()[:5],
            'shelter_user': self.shelter_user,
        })
        
        return context

class AdminRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure only admin users can access certain views"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        try:
            shelter_user = ShelterUser.objects.get(user=request.user)
            if shelter_user.role != 'admin':
                raise Http404("Admin access required")
        except ShelterUser.DoesNotExist:
            raise Http404("User not associated with any shelter")
        
        return super().dispatch(request, *args, **kwargs)

class UserListView(AdminRequiredMixin, ListView):
    model = ShelterUser
    template_name = 'shelter/user_list.html'
    context_object_name = 'shelter_users'

class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    template_name = 'shelter/user_form.html'
    fields = ['username', 'email', 'first_name', 'last_name']
    success_url = reverse_lazy('shelter:user_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Set a temporary password
        temp_password = User.objects.make_random_password()
        self.object.set_password(temp_password)
        self.object.save()
        
        # Create ShelterUser with default employee role
        ShelterUser.objects.create(
            user=self.object,
            role='employee'
        )
        
        messages.success(
            self.request, 
            f'User {self.object.username} created with temporary password: {temp_password}'
        )
        return response

class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = ShelterUser
    template_name = 'shelter/shelteruser_form.html'
    fields = ['role']
    success_url = reverse_lazy('shelter:user_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'User role updated successfully!')
        return super().form_valid(form)

class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = ShelterUser
    template_name = 'shelter/user_confirm_delete.html'
    success_url = reverse_lazy('shelter:user_list')
    
    def delete(self, request, *args, **kwargs):
        shelter_user = self.get_object()
        username = shelter_user.user.username
        
        # Delete the actual User object (this will cascade to ShelterUser)
        shelter_user.user.delete()
        
        messages.success(request, f'User {username} deleted successfully!')
        return redirect(self.success_url)