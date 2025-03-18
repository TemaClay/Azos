from django.db import models

class Equipment(models.Model):
    name = models.CharField(max_length=100)
    article = models.DecimalField(max_digits=10, decimal_places=1, default='0')
    serial_number = models.DecimalField(max_digits=10, decimal_places=1, default='0', unique = True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('under_repair', 'Under Repair')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.name