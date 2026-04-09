from django.db import models


class FormSubmission(models.Model):
    """Stores each user form submission with AI suggestions."""

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    occupation = models.CharField(max_length=150)
    bio = models.TextField(blank=True)

    # AI feedback stored as text
    ai_suggestions = models.TextField(blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.full_name} — {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"
