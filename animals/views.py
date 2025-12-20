from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import Http404
from .models import Animal, MedicalRecord, AnimalPhoto
from .forms import AnimalForm, MedicalRecordForm, AnimalPhotoForm
from shelter.models import ShelterUser

class ShelterPermissionMixin(LoginRequiredMixin):
    """Mixin to check shelter permissions"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        try:
            self.shelter_user = ShelterUser.objects.get(user=request.user)
        except ShelterUser.DoesNotExist:
            raise Http404("User not associated with any shelter")
        
        return super().dispatch(request, *args, **kwargs)

class AdminOnlyMixin(ShelterPermissionMixin):
    """Mixin for admin-only views"""
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if self.shelter_user.role != 'admin':
            raise Http404("Admin access required")
        return response

class AnimalListView(ShelterPermissionMixin, ListView):
    model = Animal
    template_name = 'animals/animal_list.html'
    context_object_name = 'animals'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Animal.objects.all().prefetch_related('photos', 'medical_records')
        
        # Apply filters
        species = self.request.GET.get('species')
        if species:
            queryset = queryset.filter(species=species)
            
        adoption_status = self.request.GET.get('adoption_status')
        if adoption_status:
            queryset = queryset.filter(adoption_status=adoption_status)
            
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(chip_id__icontains=search)
            )
        
        return queryset.order_by('-created_at')

class AnimalDetailView(ShelterPermissionMixin, DetailView):
    model = Animal
    template_name = 'animals/animal_detail.html'
    context_object_name = 'animal'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['medical_records'] = self.object.medical_records.all()
        context['photos'] = self.object.photos.all()
        return context

class AnimalCreateView(ShelterPermissionMixin, CreateView):
    model = Animal
    form_class = AnimalForm
    template_name = 'animals/animal_form.html'
    success_url = reverse_lazy('animals:animal_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, f'Animal {form.instance.name} created successfully!')
        return super().form_valid(form)

class AnimalUpdateView(ShelterPermissionMixin, UpdateView):
    model = Animal
    form_class = AnimalForm
    template_name = 'animals/animal_form.html'
    
    def get_success_url(self):
        return reverse_lazy('animals:animal_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, f'Animal {form.instance.name} updated successfully!')
        return super().form_valid(form)

class AnimalDeleteView(AdminOnlyMixin, DeleteView):
    model = Animal
    template_name = 'animals/animal_confirm_delete.html'
    success_url = reverse_lazy('animals:animal_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, f'Animal {self.get_object().name} deleted successfully!')
        return super().delete(request, *args, **kwargs)

class MedicalRecordCreateView(ShelterPermissionMixin, CreateView):
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'animals/medical_record_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.animal = get_object_or_404(Animal, pk=kwargs['animal_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.animal = self.animal
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Medical record added successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('animals:animal_detail', kwargs={'pk': self.animal.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['animal'] = self.animal
        return context

class AnimalPhotoListView(ShelterPermissionMixin, ListView):
    model = AnimalPhoto
    template_name = 'animals/animal_photos.html'
    context_object_name = 'photos'
    
    def dispatch(self, request, *args, **kwargs):
        self.animal = get_object_or_404(Animal, pk=kwargs['animal_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return AnimalPhoto.objects.filter(animal=self.animal)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['animal'] = self.animal
        context['photo_form'] = AnimalPhotoForm()
        return context

# Public views (no authentication required)
class PublicAdoptionView(ListView):
    model = Animal
    template_name = 'public/adoption_list.html'
    context_object_name = 'animals'
    paginate_by = 12
    
    def get_queryset(self):
        return Animal.objects.filter(
            public_visibility=True,
            adoption_status__in=['available', 'pending']
        ).prefetch_related('photos').order_by('-created_at')

class PublicAnimalDetailView(DetailView):
    model = Animal
    template_name = 'public/animal_detail.html'
    context_object_name = 'animal'
    
    def get_queryset(self):
        return Animal.objects.filter(public_visibility=True)

# Landing page (no authentication required)
class LandingPageView(TemplateView):
    template_name = 'public/index.html'
