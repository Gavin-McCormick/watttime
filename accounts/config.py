from django.db import models
from django import forms
from django_localflavor_us.models import PhoneNumberField, USStateField
from django_localflavor_us.us_states import STATE_CHOICES

# DO NOT import accounts.models, including indirectly through other modules
# as this module is imported by accounts.regions. See that file for explanation.

# I don't think there's any harm to reusing instances of ConfigType
# across multiple configuration parameters, but better not to chance it.
class ConfigType:
    def __init__(self, name):
        self.name = name
        self.model_field = None
        self.form_field = None

    def form_to_model(self, value):
        return value

    def python_to_model(self, value):
        return value

    def model_to_form(self, value):
        return value

    def model_to_display(self, value):
        return value

    def model_to_python(self, value):
        return value

    # Doesn't save the model afterwards!
    # Override this method if you need custom saving behavior. Doing so
    # makes the function 'form_to_model' irrelevant.
    def save_form_to_model(self, model, form):
        if self.name in form:
            setattr(model, self.name, self.form_to_model(form[self.name]))
    def save_python_to_model(self, model, vals):
        if self.name in form:
            setattr(model, self.name, self.python_to_model(vals[self.name]))

    # Override this method if you need custom loading behavior. Doing so
    # makes the function 'model_to_form' irrelevant.
    def load_model_to_form(self, model, form):
        form[self.name] = self.model_to_form(getattr(model, self.name))

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
        ConfigType.__init__(self, name)
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

    def python_to_model(self, value):
        return ','.join(str(x) for x in value)

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

    def model_to_python(self, value):
        if value:
            return [int(x) for x in value.split(',')]
        else:
            return []

class ConfigString(ConfigType):
    def __init__(self, name, max_length = 100):
        ConfigType.__init__(self, name)
        self.model_field = models.CharField(max_length = max_length, default = '')
        self.form_field = forms.CharField(required = False)

class ConfigUSState(ConfigType):
    def __init__(self, name):
        ConfigType.__init__(self, name)
        self.model_field = USStateField(default='CA')
        self.form_field = forms.ChoiceField(choices = STATE_CHOICES, help_text='State')

# TODO migration to decrease indices by one

# These names must agree with the attribute names on the UserProfile object.
# Couldn't figure out a clean way to auto-generate the UserProfile object
# from this configuration unfortunately.
config_equipment = ConfigMultichoice('equipment', [
        ('A/C at home', 'I have A/C at home (biggest use of power in the summer)'),
        ('A/C at work', 'I have A/C at work (and can control the thermostat)'),
        ('dishwasher', 'I have a dishwasher (one of the easiest major appliances to time better)'),
        ('pool pump', 'I have a pool pump (these use a LOT of energy and are easy to time better)'),
        ('electric water heater', 'My water heater is electric (gas heaters don\'t help with electricity timing)')])

config_ask_feedback = ConfigBoolean('ask_feedback')
config_beta_test = ConfigBoolean('beta_test')
config_name = ConfigString('name')
config_state = ConfigUSState('state')

# Doing user phone is a bit tricky because it actually uses two different fields
# of UserProfile....
user_profile_configs = [
        config_equipment,
        config_ask_feedback,
        config_beta_test,
        config_name,
        config_state
    ]

def form_to_model(configs, model, form):
    for config in configs:
        config.save_form_to_model(model, form)
    model.save()

def model_to_form(configs, model, form = None):
    if form is None:
        form = {}

    for config in configs:
        config.load_model_to_form(model, form)
    return form

def model_to_display(configs, model, display = None):
    if display is None:
        display = {}

    for config in configs:
        display[config.name] = config.model_to_display(getattr(model, config.name))
    return display
