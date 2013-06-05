from django.db import models
#from django.contrib.auth.models import User
from django.forms import ModelForm, CheckboxSelectMultiple, RadioSelect
from django_localflavor_us.models import PhoneNumberField, USStateField
from choice_others import ChoiceWithOtherField
from django_localflavor_us.us_states import STATE_CHOICES
from django.forms.widgets import HiddenInput
from django import forms
from accounts import messages
from multi_choice import *
from pytz import timezone
from datetime import datetime, timedelta
from django.utils.timezone import now, localtime

class User(models.Model):
    # name
    name = models.CharField(max_length=100, help_text='Name')

    # email
    email = models.EmailField(help_text='Email')

    # US phone
    phone = PhoneNumberField(blank = True, help_text='XXX-XXX-XXXX')

    # verification info
    verification_code = models.IntegerField()
    is_verified = models.BooleanField()

    # long nonconsequetive userid
    userid = models.IntegerField(primary_key=True)

    # is active user
    is_active = models.BooleanField()

    # US state
    state = USStateField(default='MA')

    # state logic
    VALID_STATE_CHOICES = ('MA',)

    def is_valid_state(self):
        if self.state in self.VALID_STATE_CHOICES:
            return True
        else:
            return False

    def long_state_name(self):
        try:
            return dict(STATE_CHOICES)[self.state]
        except KeyError:
            return self.state

    def __unicode__(self):
        return self.name

    def local_now(self):
        # TO DO make it work for other states
        if self.state == 'MA':
            return localtime(now(), timezone('US/Eastern'))
        else:
            return now()

    def twilio_format_phone(self):
        return '+1'+self.phone.replace('-', '')


SENDTEXT_FREQ_CHOICES = (
    (1, 'About once an hour! Woo!'),
    (2, 'About once a day'),
    (3, 'About once a week'),
    )
SENDTEXT_TIMEDELTAS = {
    1: timedelta(hours=1),
    2: timedelta(days=1),
    3: timedelta(days=7),
    }
AC_CHOICES = (
    (0, "None"),
    (1, "Central A/C"),
    (2, "Window unit"),
    (3, "Other or don't know"),
    )
HEATER_CHOICES = (
    (0, 'None'),
    (1, 'Electric'),
    (2, 'Gas'),
    (3, "Other or don't know"),
    )
GOALS_CHOICES = (
    (0, "I'm up for anything"),
    (1, 'Boycott coal'),
    (2, 'Maximize renewables'),
    (3, 'Minimize carbon'),
    )
CHANNEL_CHOICES = (
    (0, "Sierra Club"),
    (1, "Internet"),
    (2, "Word of mouth"),
    (3, "Other"),
    )

class UserProfile(models.Model):

    userid = models.ForeignKey(User)

    # air conditioning
    ac = models.IntegerField('Air conditioner type',
                             blank=False, default=0,
                             choices=AC_CHOICES,
                             )

    # furnace and water heater
    furnace = models.IntegerField('Furnace type',
                                  blank=False, default=0,
                                  choices=HEATER_CHOICES,
                                  )
    water_heater = models.IntegerField('Water heater type',
                                       blank=False, default=0,
                                       choices=HEATER_CHOICES,
                                       )

    # when to text
    SENDTEXT_HOURS_CHOICES = (
        (0, 'Bright and early (6am-9am)'),
        (1, 'Morning  (9am-noon)'),
        (2, 'Afternoon (noon-3pm)'),
        (3, 'After school (3pm-6pm)'),
        (4, 'Evening (6pm-9pm)'),
        (5, 'Night (9pm-midnight)'),
        )
 #   weekday_sendtext_hours = models.IntegerField('When you can receive texts on weekdays',
  #                                               blank=True,
  #                                               choices=SENDTEXT_HOURS_CHOICES,
#)
   # weekend_sendtext_hours = models.IntegerField('When you can receive texts on weekends',
   #                                             # blank=False, default=0,
   #                                              choices=SENDTEXT_HOURS_CHOICES,
    #)

    # how often to contact

    text_freq = models.IntegerField('How often you want to receive texts',
                                    blank=False, default=1,
                                    choices=SENDTEXT_FREQ_CHOICES,
                                    )

    # goals for using service
    goal = MultiSelectField(verbose_name='Which goals would you like to receive notifications about?',
                            blank=False,
                            max_length=100,
                            choices=GOALS_CHOICES,)

    # On how user learned about WattTime
    channel = models.IntegerField('How did you hear of WattTime?',
                                  blank=False,
                                  default=0,
                                  choices=CHANNEL_CHOICES)
    #channel = ChoiceWithOtherField(choices = UserProfile.CHANNEL_CHOICES)
    
   # goal = models.IntegerField('Which goals would you like to receive notifications about?',
   #                            blank=False, default=0,
   #                           # blank=True,
   #                            choices=GOALS_CHOICES,
   #                            )

    def get_personalized_message(self, percent_green, percent_coal,
                                 marginal_fuel):
        """ Select an appropriate message for a user
            based on their preferences and the state of the grid,
            or None.
        """
        # if there's no marginal, there's no message
        if marginal_fuel == 'None':
            return None

        # sort out goals
        # TO DO hacky
        goal_set = set(int(g) for g in self.goal[0].split())

        # marginal is renewable
        if marginal_fuel in ['Wind', 'Hydro', 'Wood', 'Refuse'] and len(goal_set & set([0, 2, 3])) > 0:
            if self.ac == 1: # central
                return messages.use_central_ac_message(marginal_fuel)
            else:
                return messages.use_message(marginal_fuel)

        # marginal is coal
        if marginal_fuel in ['Coal'] and len(goal_set & set([0, 1, 3])) > 0:
            if self.ac == 1: # central
                return messages.dont_use_central_ac_message(marginal_fuel)
            else:
                return messages.dont_use_message(marginal_fuel)

        # marginal is oil or gas
        if marginal_fuel in ['Oil', 'Natural Gas'] and len(goal_set & set([0, 3])) > 0:
            if self.ac == 1: # central
                return messages.dont_use_central_ac_message(marginal_fuel)
            else:
                return messages.dont_use_message(marginal_fuel)

        # else
        return 'No message found for marginal fuel %s and goal %d' % (marginal_fuel, self.goal)

class NewUserForm(ModelForm):
    class Meta:
        model = User
        exclude = ['verification_code', 'is_verified', 'userid']

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.fields['phone'].widget = HiddenInput()
        self.fields['name'].widget.attrs['placeholder'] = u'Name'
        self.fields['email'].widget.attrs['placeholder'] = u'Email'
        #self.fields['phone'].initial = '000-000-0000' # set the initial value of phone number

class UserPhoneForm(ModelForm):
    class Meta:
        model = User
        fields = ('phone',)

    def __init__(self, *args, **kwargs):
        super(UserPhoneForm, self).__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs['placeholder'] = u'Phone'


class UserProfileForm(ModelForm):

    class Meta:
        model = UserProfile
        exclude = ['userid']
        widgets = {
            #'goal': RadioSelect(),
            'ac': RadioSelect(),
            'furnace': RadioSelect(),
            'water_heater': RadioSelect(),
            'text_freq': RadioSelect(),
            'channel': RadioSelect(),
          #  'weekend_sendtext_hours': CheckboxSelectMultiple(),
          #  'weekday_sendtext_hours': CheckboxSelectMultiple(),
            }

class UserVerificationForm(forms.Form):
    verification_code = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(UserVerificationForm, self).__init__(*args, **kwargs)
        self.fields['verification_code'].widget.attrs['placeholder'] = u'xxxxxx'
