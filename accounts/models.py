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

class User(models.Model):
    # name
    name = models.CharField(max_length=100, help_text='Name')

    # email
    email = models.EmailField(help_text='Email')

    # US phone
    phone = PhoneNumberField(blank = True, help_text='XXX-XXX-XXXX')

    verification_code = models.IntegerField()
    is_verified = models.BooleanField()

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
        return self.namepoll.id

class UserProfile(models.Model):

    userid = models.ForeignKey(User)

    # air conditioning
    AC_CHOICES = (
        (0, "None"),
        (1, "Central A/C"),
        (2, "Window unit"),
        (3, "Other or don't know"),
        )
    ac = models.IntegerField('Air conditioner type',
                             blank=False, default=0,
                             choices=AC_CHOICES,
                             )

    # furnace and water heater
    HEATER_CHOICES = (
        (0, 'None'),
        (1, 'Electric'),
        (2, 'Gas'),
        (3, "Other or don't know"),
        )
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
    SENDTEXT_FREQ_CHOICES = (
        (1, 'About once an hour! Woo!'),
        (2, 'About once a day'),
        (3, 'About once a week'),
        )
    text_freq = models.IntegerField('How often you want to receive texts',
                                    blank=False, default=1,
                                    choices=SENDTEXT_FREQ_CHOICES,
                                    )

    # goals for using service
    GOALS_CHOICES = (
        (0, "I'm up for anything"),
        (1, 'Boycott coal'),
        (2, 'Maximize renewables'),
        (3, 'Minimize carbon'),
        )
    goal = MultiSelectField(verbose_name='Which goals would you like to receive notifications about?',
                            blank=False,
                            max_length=100,
                            choices=GOALS_CHOICES,)

    # On how user learned about WattTime
    CHANNEL_CHOICES = (
        (0, "Sierra Club"),
        (1, "Internet"),
        (2, "Word of mouth"),
        (3, "Other"),
        )
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

    def is_good_time_to_message(timestamp):
        """ Returns True if hour/day are ok for user,
            and if they haven't received a message too recently.
            Returns False if not ok.
        """
        # TO DO
        current_hour = 0

        # bools
        hour_test = current_hour > 8 and current_hour < 22
        recent_test = False # has text been sent recently, based on database

        if hour_test and recent_test:
            return True
        else:
            return False

    def get_personalized_message(percent_green, percent_coal,
                                 marginal_fuel):
        """ Select an appropriate message for a user
            based on their preferences and the state of the grid,
            or None.
        """
        # if there's no marginal, there's no message
        if marginal_fuel == 'None':
            return None

        # marginal is renewable
        if marginal_fuel in ['Wind', 'Hydro', 'Wood', 'Refuse'] and goal in [0, 2, 3]:
            if ac == 1: # central
                return messages.use_central_ac_message(marginal_fuel)
            else:
                return messages.use_message(marginal_fuel)

        # marginal is coal
        if marginal_fuel in ['Coal'] and goal in [0, 1, 3]:
            if ac == 1: # central
                return messages.dont_use_central_ac_message(marginal_fuel)
            else:
                return messages.dont_use_message(marginal_fuel)

        # marginal is oil
        if marginal_fuel in ['Oil'] and goal in [0, 3]:
            if ac == 1: # central
                return messages.dont_use_central_ac_message(marginal_fuel)
            else:
                return messages.messages.dont_use_message(marginal_fuel)

class NewUserForm(ModelForm):
    class Meta:
        model = User
        exclude = ['verification_code', 'is_verified']

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.fields['phone'].widget = HiddenInput()
        self.fields['name'].initial = 'Name'
        self.fields['email'].initial = 'Email'
        #self.fields['phone'].initial = '000-000-0000' # set the initial value of phone number

class UserPhoneForm(ModelForm):
    class Meta:
        model = User
        fields = ('phone',)


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
