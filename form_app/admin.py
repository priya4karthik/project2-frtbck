from django.contrib import admin
from .models import FormSubmission


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'city', 'occupation', 'submitted_at')
    search_fields = ('full_name', 'email', 'city')
    list_filter = ('city', 'submitted_at')
    readonly_fields = ('submitted_at', 'ai_suggestions')
