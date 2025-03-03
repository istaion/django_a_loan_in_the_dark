from django.db import models
from accounts.models import CustomUser
from uuid import uuid4
from static.enum_choices import STATE_CHOICES, STATUS_CHOICES, BANK_CHOICES, NAICS_CHOICES


class Loan(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid4)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="STATUS_TO_TREAT", null=True)

    state = models.CharField(max_length=2, choices=STATE_CHOICES, default=None, null=True)
    bank = models.CharField(max_length=100, choices=BANK_CHOICES, default=None, null=True)
    naics = models.CharField(max_length=2, choices=NAICS_CHOICES, default=None, null=True)
    rev_line_cr = models.IntegerField(null=True)
    low_doc = models.IntegerField(null=True)
    new_exist = models.IntegerField(null=True)
    create_job = models.IntegerField(null=True)
    has_franchise = models.IntegerField(null=True)
    recession = models.IntegerField(null=True)
    urban_rural = models.IntegerField(null=True)
    retained_job = models.IntegerField(null=True)
    no_emp = models.IntegerField(null=True)

    term = models.IntegerField(null=False)
    gr_appv = models.FloatField(null=False)

    # Prediction Fields
    prediction = models.IntegerField(null=False)
    proba_yes = models.FloatField(null=False)
    proba_no = models.FloatField(null=False)
    shap_values = models.JSONField(default=list)