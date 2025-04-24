from django.db import models

# Create your models here.


class Prediction(models.Model):
    nom_patient = models.CharField(max_length=255)
    value = models.FloatField()
    pred = models.CharField(max_length=10)
    confidence = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom_patient
