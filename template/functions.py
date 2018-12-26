from snomedct.models import CommonSnomedConcepts
from template.models import TemplateAdditionalQuestion, TemplateAdditionalCondition


def get_common_with_snomed(snomedconcepts):
    common_ids = []
    for snomed in snomedconcepts:
        for common in CommonSnomedConcepts.objects.filter(snomed_concept_code__in=snomed):
            common_snomed = [concept.pk for concept in common.snomed_concept_code.all()]
            if common_snomed != snomed: continue
            return common.pk


def create_question(template, questions):
    for question in questions:
        TemplateAdditionalQuestion.objects.create(
            template_instruction=template,
            question=question
        )


def create_condition(template, conditions):
    for condition in conditions:
        TemplateAdditionalCondition.objects.create(
            template_instruction=template,
            snomedct_id=int(condition)
        )
