from django.db import models

# Create your models here.
class Stands(models.Model):
    stand=models.CharField(max_length=255)
    stand_url = models.CharField(max_length=255)
    auth_url=models.CharField(max_length=255)
    graphql_url=models.CharField(max_length=255)

    def __str__(self):
        return self.stand
