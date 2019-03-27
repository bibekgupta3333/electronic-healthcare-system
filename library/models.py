from django.db import models
from common.models import TimeStampedModel
from organisations.models import OrganisationGeneralPractice


class Library(TimeStampedModel):
    gp_practice = models.ForeignKey(OrganisationGeneralPractice, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.key + ': ' + self.value

    class Meta:
        verbose_name = 'Library'
        verbose_name_plural = 'Libraries'
