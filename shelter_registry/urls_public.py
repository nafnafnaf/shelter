from django.urls import path
from django.views.generic import TemplateView

# Public schema URLs (for main site, shelter registration, etc.)
urlpatterns = [
    path('', TemplateView.as_view(template_name='public/index.html'), name='public_home'),
]
