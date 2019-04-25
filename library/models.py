from django.db import models
from common.models import TimeStampedModel
from organisations.models import OrganisationGeneralPractice
from instructions.models import Instruction


class Library(TimeStampedModel):
    gp_practice = models.ForeignKey(OrganisationGeneralPractice, on_delete=models.CASCADE)
    key = models.CharField(max_length=255, verbose_name='Text', unique=True)
    value = models.CharField(max_length=255, blank=True, verbose_name='Replaced by')

    def __str__(self):
        return self.key + ': ' + self.value

    class Meta:
        verbose_name = 'Library'
        verbose_name_plural = 'Libraries'
        ordering = ('-created', )


class LibraryHistory(TimeStampedModel):
    instruction = models.ForeignKey(Instruction, on_delete=models.CASCADE)
    action = models.CharField(max_length=255, verbose_name='Action')
    old = models.CharField(max_length=255, blank=True, verbose_name='Old value')
    new = models.CharField(max_length=255, blank=True, verbose_name='New value')
