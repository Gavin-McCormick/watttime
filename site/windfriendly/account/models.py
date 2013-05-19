from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)

    # heat info


    #url = models.URLField("Website", blank=True)
    #company = models.CharField(max_length=50, blank=True)


class UserProfileForm(forms.Form):
    pass
