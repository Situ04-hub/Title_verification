from django.db import models

class NewspaperTitle(models.Model):
    title_text = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title_text