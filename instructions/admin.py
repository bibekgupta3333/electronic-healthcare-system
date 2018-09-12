from django.contrib import admin

from .models import Instruction, InstructionAdditionQuestion

admin.site.register(
    (
        Instruction,
        InstructionAdditionQuestion
     )
)
