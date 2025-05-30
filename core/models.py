from django.db import models
from ansible_base.lib.abstract_models import CommonModel

# Create your models here.

class Pattern(CommonModel):
    class Meta:
        app_label = 'core'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=["collection_name", "collection_version", "pattern_name"],
         name = "pattern_collection_version")]        
    collection_name = models.CharField(max_length=200)
    collection_version = models.CharField(max_length=50)
    collection_version_uri = models.CharField(max_length=200, blank=True)
    pattern_name = models.CharField(max_length=200)
    pattern_definition = models.JSONField(blank=True)

class ControllerLabel(CommonModel):
    class Meta:
        app_label = 'core'
        ordering = ['id']
    label_id = models.BigIntegerField(unique=True)     

class PatternInstance(CommonModel):
    class Meta:
        app_label = 'core'
        ordering = ['id']
    organization_id = models.BigIntegerField()
    controller_project_id = models.BigIntegerField(blank=True)
    controller_ee_id = models.BigIntegerField(null=True, blank=True)
    credentials = models.JSONField()
    executors = models.JSONField(null=True)
    
    pattern = models.ForeignKey(Pattern, on_delete=models.CASCADE, related_name="pattern_instances")
    controller_labels = models.ManyToManyField (ControllerLabel, related_name="pattern_instances")

class Automation(CommonModel):
    class Meta:
        app_label = 'core'
        ordering = ['id']
    automation_type_choices = (("job_template", "Job template"),)
    automation_type = models.CharField(choices=automation_type_choices)
    automation_id = models.BigIntegerField()
    primary = models.BooleanField(default=False)

    pattern_instance = models.ForeignKey(PatternInstance, on_delete=models.CASCADE, related_name="automations")
