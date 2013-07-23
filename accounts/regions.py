from django.db import models
from django import forms
from django_localflavor_us.us_states import STATE_CHOICES

# This module MUST be imported from accounts/models.py so that the models
# created here will be visibly to syncdb and other Django operations that
# need to inspect all available models.

EQUIPMENT_CHOICES = [
        (1, 'I have A/C at home (biggest single use of power in the summer)'),
        (2, 'I have A/C at work (and can control the thermostat)'),
        (3, 'I have a dishwasher (one of the easiest major appliances to time better)'),
        (4, 'I have a pool pump (these use a LOT of energy and are easy to time better)'),
        (5, 'My water heater is electric (gas heaters don\'t help with electricity timing)')
    ]

EQUIPMENT_LONG = dict(EQUIPMENT_CHOICES)
EQUIPMENT_SHORT = {
        1 : 'A/C at home',
        2 : 'A/C at work',
        3 : 'dishwasher',
        4 : 'pool pump',
        5 : 'electric water heater'
    }


class UserProfileForm(forms.Form):
    name            = forms.CharField(help_text='Name', required = False)
    password        = forms.CharField(help_text='Password', required = False)
    state           = forms.ChoiceField(choices = STATE_CHOICES, help_text='State')
    phone           = forms.CharField(help_text='Phone', required = False)
    equipment       = forms.MultipleChoiceField(help_text='Equipment', choices = EQUIPMENT_CHOICES, widget = forms.CheckboxSelectMultiple(), required = False)
    beta_test       = forms.BooleanField(help_text='Beta test', widget = forms.CheckboxInput(), required = False)
    ask_feedback    = forms.BooleanField(help_text='Ask feedbac', widget = forms.CheckboxInput(), required = False)


# Instances of ConfigType cannot (I think) be reused across multiple
# regions or configuration parameters.
class ConfigType:
    def __init__(self, name):
        self.name = name
        self.model_field = None
        self.form_field = None

    def form_to_model(self, value):
        return value

    def model_to_form(self, value):
        return value

    def model_to_display(self, value):
        return value

class ConfigBoolean(ConfigType):
    def __init__(self, name):
        ConfigType.__init__(self, name)
        self.model_field = models.BooleanField(default = False)
        self.form_field = forms.BooleanField(
                widget = forms.CheckboxInput(), required = False)

    def model_to_display(self, value):
        if value:
            return 'Yes'
        else:
            return 'No'

class ConfigInteger(ConfigType):
    def __init__(self, name):
        ConfigType.__init__(self, name)
        self.model_field = models.IntegerField(default = 0)
        self.form_field = forms.IntegerField(required = False)

    def model_to_display(self, value):
        return str(value)

class ConfigChoice(ConfigType):
    # choices: list of pairs of strings
    #   first item is for display on /profile (shorter version)
    #   second item is for setting on /profile/edit (longer version)
    # at most 36 choices should be present due to character length restrictions
    def __init__(self, name, choices):
        assert (len(choices) < 36)
        ConfigType.__init__(self, name)
        self.choices = choices[:]
        int_xs = [(i, choices[i][1]) for i in range(len(choices))]
        str_xs = [(str(i), choices[i][1]) for i in range(len(choices))]
        self.model_field = models.IntegerField(choices = int_xs, default = 0)
        self.form_field = forms.ChoiceField(
                choices = str_xs, widget = forms.RadioSelect(), required = False)

    def form_to_model(self, value):
        return int(value)

    def model_to_form(self, value):
        return str(value)

    def model_to_display(self, value):
        return self.choices[int(value)][0]


class ConfigMultichoice(ConfigType):
    # like in ConfigChoice
    def __init__(self, name, choices):
        assert (len(choices) < 36)
        ConfigType.__init__(self, name, choices)
        self.choices = choices[:]
        int_xs = [(i, choices[i][1]) for i in range(len(choices))]
        str_xs = [(str(i), choices[i][1]) for i in range(len(choices))]
        self.model_field = models.CommaSeparatedIntegerField(
                choices = int_xs, default = '', max_length = 100)
        self.form_field = forms.MultipleChoiceField(
                choices = str_xs, widget = forms.CheckboxSelectMultiple(),
                required = False)

    def form_to_model(self, value):
        return ','.join(x for x in value)

    def model_to_form(self, value):
        if value:
            return list(value.split(','))
        else:
            # split() doesn't work properly on the empty string
            return []

    def model_to_display(self, value):
        if value:
            return '; '.join(self.choices[int(x)][0] for x in value.split(','))
        else:
            return '(none)'


class Region:
    # settings_name -- identifier for the field of UserProfile which refers
    #   to the settings for this region
    # states -- list of US states which lie at least partially in this region
    def __init__(self, name, settings_name, states, params):
        self.name = name
        self.settings_name = settings_name
        self.states = states[:]
        self.params = params[:]

        self._setup_fields()

    def _setup_fields(self):
        model_fields = {}
        form_fields = {}

        model_fields['__module__'] = 'accounts.models'

        for param in self.params:
            name = param.name
            model_fields[name] = param.model_field
            form_fields[name] = param.form_field

        model_name  = '{}UserProfile'.format(self.name)
        form_name   = 'UserForm_{}'.format(self.name)
        self.user_prefs_model = type(model_name, (models.Model,), model_fields)
        self.user_prefs_form = type(form_name, (UserProfileForm,), form_fields)

    def has_state(self, state):
        return state in self.states

    def save_from_form(self, up, vals):
        s = up.get_region_settings()
        for param in self.params:
            setattr(s, param.name, param.form_to_model(vals[param.name]))
        s.save()

    def form_initial_values(self, up, vals):
        s = up.get_region_settings()
        for param in self.params:
            vals[param.name] = param.model_to_form(getattr(s, param.name))

    def display_values(self, up, vals):
        s = up.get_region_settings()
        for param in self.params:
            vals[param.name] = param.model_to_display(getattr(s, param.name))


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
        params = [ConfigChoice('message_frequency', ne_freq_choices)])

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
        params = [ConfigChoice('message_frequency', ca_freq_choices),
            ConfigBoolean('forecast_email')])

null_region = Region(
        name = 'Nowhere',
        settings_name = 'null_settings',
        states = [],
        params = [])

regions = [newengland, california, null_region]

def state_to_region(state):
    for region in regions:
        if region.has_state(state):
            return region
    return null_region
