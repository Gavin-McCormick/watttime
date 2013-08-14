from django.db import models
from django import forms
from django_localflavor_us.us_states import STATE_CHOICES

from accounts.config import ConfigChoice, ConfigBoolean

from accounts.forms import UserProfileForm

# DO NOT import accounts.models here, including indirectly through other
# modules. See note at the end of the file.

class Regions:
    def __init__(self):
        self.region_list = []
        self.regions_by_name = {}
        self.default_region = None

    def register_region(self, region):
        if region.name in self.regions_by_name:
            msg = "There is already one region named {}, cannot create another!"
            raise ValueError(msg.format(region.name))

        self.region_list.append(region)
        self.regions_by_name[region.name] = region

    def regions(self):
        return self.region_list[:]

    def __len__(self):
        return len(self.region_list)

    def __getitem__(self, name):
        return self.regions_by_name[name]

    def get(self, name, default):
        return self.regions_by_name.get(name, default)

    def by_state(self, state):
        for region in self.region_list:
            if region.has_state(state):
                return region
        return self.default_region

    def set_default(self, region):
        region_ = self.get(region.name, None)
        if region_ is not region:
            raise ValueError("Region {} is not already registered".
                    format(region.name))

        self.default_region = region

    def create_models(self):
        for region in self.region_list:
            region.create_model()

regions = Regions()

class Region:
    # settings_name -- identifier for the field of UserProfile which refers
    #   to the settings for this region
    # states -- list of US states which lie at least partially in this region
    def __init__(self, name, settings_name, states, configs):
        self.name = name
        self.settings_name = settings_name
        self.states = states[:]
        self.configs = configs[:]

        self.user_prefs_form = None
        self.user_prefs_model = None
        self.created_model = False
        self.created_form = False

        self.create_form()
        # self.create_model()   -- this is now done in accounts/models.py

        regions.register_region(self)

    def create_form(self):
        if self.created_form:
            return
        self.created_form = True

        fields = {}

        for config in self.configs:
            fields[config.name] = config.form_field

        form_name = 'UserForm_{}'.format(self.name)
        self.user_prefs_form = type(form_name, (UserProfileForm,), fields)

    def create_model(self):
        if self.created_model:
            return
        self.created_model = True

        fields = {}
        fields['__module__'] = 'accounts.models'

        for config in self.configs:
            fields[config.name] = config.model_field

        model_name = '{}UserProfile'.format(self.name)
        self.user_prefs_model = type(model_name, (models.Model,), fields)

    def has_state(self, state):
        return state in self.states

null_region = Region(
        name = 'Nowhere',
        settings_name = 'null_settings',
        states = [],
        configs = [])

regions.set_default(null_region)

ne_freq_choices = [
    ('About daily, working hours, when dirty',
        'Up to once a day 9-5, Monday-Friday, when fuel is particularly dirty'),
    ('About daily, after hours, when dirty',
        'Up to once a day evenings or weekends, when fuel is particularly dirty'),
    ('About daily, after hours, when clean',
        'Up to once a day evenings or weekends, when fuel is particularly clean'),
    ('Never',
        'Never')]
newengland = Region(
        name = 'NewEngland',
        settings_name = 'ne_settings',
        states = ['MA', 'VT', 'NH', 'ME', 'CT', 'RI'],
        configs = [ConfigChoice('message_frequency', ne_freq_choices)])

ca_freq_choices = [
    ('Dirtiest hour each day',
        'Text me at the dirtiest hour of each day, so I can try to use less energy then'),
    ('Cleanest hour each evening',
        'Text me at the cleanest hour of each evening, to help me time my power use better'),
    ('Less than once a day',
        'Text me whenever power is unusually clean or dirty, at most once a day'),
    ('Only in extremes (once a week)',
        'Only text me during dirty energy emergencies, at most once a week'),
    ('Never',
        'Never')]
california = Region(
        name = 'California',
        settings_name = 'ca_settings',
        states = ['CA'],
        configs = [ConfigChoice('message_frequency', ca_freq_choices),
            ConfigBoolean('forecast_email')])

# The region setup is performed at module-runtime, in two steps.
# First, in accounts.regions, each of the regions are created, with their
# individual configurations. Second, in accounts.models, custom models are
# created corresponding to these regions (as all models must be created in
# accounts.models for Django to find them). As neither step works without
# the other (if you only perform the first step, code that hits the database
# will fail), there is a circular import, so some care must be taken to
# do the circular import correctly.
#
# (All this is only necessary because Django requires models to be in the
# models module.)
#
# Within accounts.regions, AFTER all regions have been created, we import
# accounts.models so that users who import accounts.regions will still have
# the custom models created.
# Within accounts.models, BEFORE the custom models are created (with the
# command "regions.create_models()"), we import accounts.regions so that
# the regions will have been configured first. (Admittedly this import is
# necessary to execute the command anyhow.)
#
# Short version: every time we import accounts.regions, we must then
# import accounts.models, and the easy way to guarantee that is to place
# this import here, at the END of the file. Placing it before the regions
# have been configured will cause problems.
import accounts.models
