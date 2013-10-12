from django.db import models
from django_localflavor_us.models import PhoneNumberField, USStateField
from django_localflavor_us.us_states import STATE_CHOICES
import pytz
from django.utils.timezone import now, localtime
from django.contrib.auth.models import User

from accounts import config

# Several models are defined dynamically in regions.py, so this import is
# critical
import accounts.regions
from accounts.regions import regions

# This creates the models corresponding to region-specific user settings.
regions.create_models()

up_configs = config.user_profile_configs

ca_model = accounts.regions.california.user_prefs_model
ne_model = accounts.regions.newengland.user_prefs_model
null_model = accounts.regions.null_region.user_prefs_model

class UserProfile(models.Model):
    user                = models.OneToOneField(User)

    password_is_set     = models.BooleanField()

    magic_login_code    = models.IntegerField(db_index = True)
    name                = config.config_name.model_field
    email               = models.EmailField(help_text='Email')
    phone               = PhoneNumberField()
    verification_code   = models.IntegerField()
    is_verified         = models.BooleanField()
    state               = config.config_state.model_field

    ask_feedback        = config.config_ask_feedback.model_field
    beta_test           = config.config_beta_test.model_field

    ca_settings         = models.ForeignKey(ca_model, blank = True, null = True)
    ne_settings         = models.ForeignKey(ne_model, blank = True, null = True)
    null_settings       = models.ForeignKey(null_model, blank = True, null = True)

    equipment           = config.config_equipment.model_field

    def supported_location(self):
        return self.region() in [accounts.regions.newengland, accounts.regions.california]

    def supported_location_forecast(self):
        return self.region() in [accounts.regions.california]

    def region(self):
        return regions.by_state(self.state)

    def get_region_settings(self):
        region = self.region()
        label = region.settings_name
        s = getattr(self, label)
        if s is None:
            s = region.user_prefs_model()
            s.save()
            setattr(self, label, s)
            self.save()
            return s
        else:
            return s

    def save_from_form(self, vals):
        # Remember that the value of `self.region()` depends on the value of
        # self.state! Therefore 'state' must be the last thing that is set
        # (or at least after any region-specific settings).
        config.form_to_model(self.region().configs, self.get_region_settings(), vals)
        if 'phone' in vals:
            self.set_phone(vals['phone'])

        if 'name' in vals:
            self.name = vals['name']
        if 'email' in vals:
            self.email = vals['email']

        if 'password' in vals:
            password = vals['password']
            if not password in ['(not used)', '######']:
                self.set_password(password)

        config.form_to_model(up_configs, self, vals)
        self.save()

    def form_initial_values(self, vals = None):
        if vals is None:
            vals = {}
        config.model_to_form(self.region().configs, self.get_region_settings(), vals)
        config.model_to_form(up_configs, self, vals)
        vals['phone'] = self.phone

        if self.password_is_set:
            vals['password'] = '######'
        else:
            vals['password'] = '(not used)'
        return vals

    def display_values(self, vals = None):
        if vals is None:
            vals = {}
        config.model_to_display(self.region().configs, self.get_region_settings(), vals)
        config.model_to_display(up_configs, self, vals)

        if self.phone:
            if self.is_verified:
                vals['phone'] = self.phone + ' (verified)'
            else:
                vals['phone'] = self.phone + ' (not verified)'
        else:
            vals['phone'] = '(none)'

        vals['email'] = self.email
        vals['long_state'] = self.long_state_name()
        vals['region'] = self.region().name
        vals['supported_region'] = self.supported_location()
        vals['phone_verified'] = self.is_verified
        vals['phone_blank'] = (len(self.phone) == 0)
        return vals

    def set_equipment(self, xs):
        self.equipment = config.config_equipment.python_to_model(xs)

    def get_equipment(self):
        return config.config_equipment.model_to_python(self.equipment)

    def local_now(self):
         # TO DO make it work for other states
         if self.state in ['MA', 'VT', 'NH', 'ME', 'CT', 'RI']:
             return localtime(now(), pytz.timezone('America/New_York'))
         elif self.state in ['CA', 'WA', 'ID', 'OR']:
             return localtime(now(), pytz.timezone('America/Los_Angeles'))
         else:
             return now()

    def set_password(self, password):
        if password:
            self.user.set_password(password)
            self.user.save()
            self.password_is_set = True
            print 'saved password'
        else:
            self.user.set_unusable_password()
            self.user.save()
            self.password_is_set = False
            print 'did not save password'

    def set_phone(self, phone):
        if phone != self.phone:
            self.phone = phone
            self.is_verified = False

    def long_state_name(self):
        try:
            return dict(STATE_CHOICES)[self.state]
        except KeyError:
            return self.state

    def __unicode__(self):
        res = u'{self.name} ({self.state}, {self.email}, {self.phone}{pv}){e1}{e2}'
        pv = e1 = e2 = u''

        if not self.is_verified:
            pv = u' (not verified)'
        if not self.user.is_active:
            e1 = u', inactive'
        if not self.password_is_set:
            e2 = u', no password'

        res = res.format(self = self, pv = pv, e1 = e1, e2 = e2)

        return res
