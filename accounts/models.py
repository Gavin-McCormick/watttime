from django.db import models
from django_localflavor_us.models import PhoneNumberField, USStateField
from django_localflavor_us.us_states import STATE_CHOICES
import pytz
from django.utils.timezone import now, localtime
from django.contrib.auth.models import User

# Several models are defined dynamically in regions.py, so this import is
# critical
import accounts.regions

CA_SENDTEXT_FREQ_CHOICES = (
        (1, 'Text me the dirtiest hour of the day so I can try to use less energy then'),
        (2, 'Text me the cleanest hour of the evening so I can try to time some appliances that way'),
        (3, 'Text me whenever something unusual happens, less than once per day'),
        (4, 'Only text me during dirty energy emergencies, at most once a week')
    )
CA_SENDTEXT_FREQ_LONG = dict(CA_SENDTEXT_FREQ_CHOICES)
CA_SENDTEXT_FREQ_SHORT = {
        1 : 'Dirtiest hour each day',
        2 : 'Cleanest hour each evening',
        3 : 'Less than once a day',
        4 : 'Only in extremes (once a week)'
    }

NE_SENDTEXT_FREQ_CHOICES = (
        (1, 'Text me about once per day'),
        (2, 'Text me about once per week')
    )
NE_SENDTEXT_FREQ_LONG = dict(NE_SENDTEXT_FREQ_CHOICES)
NE_SENDTEXT_FREQ_SHORT = {
        1 : 'About daily',
        2 : 'About weekly'
    }

ca_model = accounts.regions.california.user_prefs_model
ne_model = accounts.regions.newengland.user_prefs_model
null_model = accounts.regions.null_region.user_prefs_model

class UserProfile(models.Model):
    user                = models.OneToOneField(User)

    password_is_set     = models.BooleanField()

    magic_login_code    = models.IntegerField(db_index = True)
    name                = models.CharField(max_length=100, help_text='Name', blank=True)
    email               = models.EmailField(help_text='Email')
    phone               = PhoneNumberField()
    verification_code   = models.IntegerField()
    is_verified         = models.BooleanField()
    state               = USStateField(default='CA')

    ca_settings         = models.ForeignKey(ca_model, blank = True, null = True)
    ne_settings         = models.ForeignKey(ne_model, blank = True, null = True)
    null_settings       = models.ForeignKey(null_model, blank = True, null = True)

    forecast_email = models.BooleanField(default = False)
    equipment = models.CommaSeparatedIntegerField(default = '', max_length=100, blank=True)
    ask_feedback = models.BooleanField(default = False)
    beta_test = models.BooleanField(default = False)

    def supported_location(self):
        return self.region() in [accounts.regions.newengland, accounts.regions.california]

    def region(self):
        return accounts.regions.state_to_region(self.state)

    def get_region_settings(self):
        region = self.region()
        label = region.settings_name
        s = getattr(self, label)
        if s is None:
            s = region.user_prefs_model()
            s.save()
            setattr(self, label, s)
            return s
        else:
            return s

    def save_from_form(self, vals):
        self.region().save_from_form(self, vals)

    def form_initial_values(self, vals):
        self.region().form_initial_values(self, vals)

    def display_values(self, vals):
        self.region().display_values(self, vals)

    # Takes a list of integers
    def set_equipment(self, indices):
        self.equipment = ','.join(str(index) for index in indices)

    # Returns a list of integers
    def get_equipment(self):
        if len(self.equipment) > 0:
            return list(int(index) for index in self.equipment.split(','))
        else:
            return []

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
        else:
            self.user.set_unusable_password()
            self.user.save()
            self.password_is_set = False

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

# class OldUser(models.Model):
#     # name
#     name = models.CharField(max_length=100, help_text='Name')
# 
#     # email
#     email = models.EmailField(help_text='Email',error_messages = {'blank': 'No name? OK, what should we call you?',})
# 
#     # US phone
#     phone = PhoneNumberField(help_text='XXX-XXX-XXXX')
# 
#     # verification info
#     verification_code = models.IntegerField()
#     is_verified = models.BooleanField()
# 
#     # long nonconsequetive userid
#     userid = models.IntegerField(primary_key=True)
# 
#     # is active user
#     is_active = models.BooleanField()
# 
#     # US state
#     state = USStateField(default='MA')
# 
#     # state logic
#     VALID_STATE_CHOICES = ('MA', 'VT', 'CT', 'RI', 'NH', 'ME')
# 
#     def is_valid_state(self):
#         if self.state in self.VALID_STATE_CHOICES:
#             return True
#         else:
#             return False
# 
#     def long_state_name(self):
#         try:
#             return dict(STATE_CHOICES)[self.state]
#         except KeyError:
#             return self.state
# 
#     def __unicode__(self):
#         return self.name
# 
#     def local_now(self):
#         # TO DO make it work for other states
#         return localtime(now(), timezone('US/Eastern'))
#         #if self.state == 'MA':
#             #return localtime(now(), timezone('US/Eastern'))
#         #else:
#             #return now()
# 
# 

# SENDTEXT_FREQ_CHOICES = (
    # (1, 'Several times per day'),
    # (2, 'About once a day'),
    # (3, 'About once a week'),
    # )
# SENDTEXT_TIMEDELTAS = {
    # 1: timedelta(hours=3),
    # 2: timedelta(days=1),
    # 3: timedelta(days=7),
    # }
# SENDTEXT_FREQWORDS = {
    # 1: 'several-times-daily',
    # 2: 'daily',
    # 3: 'weekly',
    # }
# AC_CHOICES = (
    # (0, "None"),
    # (1, "Central A/C"),
    # (2, "Window unit"),
    # (3, "Other or don't know"),
    # )
# HEATER_CHOICES = (
    # (0, 'None'),
    # (1, 'Electric'),
    # (2, 'Gas'),
    # (3, "Other or don't know"),
    # )
# GOALS_CHOICES = (
    # (0, "I'm up for anything"),
    # (1, 'Help me use less coal'),
    # (2, 'Help me use more renewables'),
    # (3, 'More renewables & nuclear, less coal & oil'),
    # )
# GOAL_WORDS = {
    # 0: 'everything',
    # 1: 'using less coal',
    # 2: 'using more renewables',
    # 3: 'lowering my carbon footprint',
# }
# CHANNEL_CHOICES = (
    # (0, "Sierra Club"),
    # (1, "Internet"),
    # (2, "Word of mouth"),
    # (3, "Other"),
    # )
# 
# class OldUserProfile(models.Model):
# 
#     userid = models.ForeignKey(User)
#     
#     # goals for using service
#     goal = MultiSelectField(verbose_name='Which goals would you like to receive notifications about?',
#                             blank=False,
#                             max_length=100,
#                             choices=GOALS_CHOICES,)
# 
#     # when to text
#     SENDTEXT_HOURS_CHOICES = (
#         (0, 'Bright and early (6am-9am)'),
#         (1, 'Morning  (9am-noon)'),
#         (2, 'Afternoon (noon-3pm)'),
#         (3, 'After school (3pm-6pm)'),
#         (4, 'Evening (6pm-9pm)'),
#         (5, 'Night (9pm-midnight)'),
#         )
#  #   weekday_sendtext_hours = models.IntegerField('When you can receive texts on weekdays',
#   #                                               blank=True,
#   #                                               choices=SENDTEXT_HOURS_CHOICES,
# #)
#    # weekend_sendtext_hours = models.IntegerField('When you can receive texts on weekends',
#    #                                             # blank=False, default=0,
#    #                                              choices=SENDTEXT_HOURS_CHOICES,
#     #)
# 
#     # how often to contact
#     text_freq = models.IntegerField('How often you want to receive texts',
#                                     blank=False, default=3,
#                                     choices=SENDTEXT_FREQ_CHOICES,
#                                     )
# 
#     # On how user learned about WattTime
#     channel = models.IntegerField('How did you hear of WattTime?',
#                                   blank=False,
#                                   default=0,
#                                   choices=CHANNEL_CHOICES)
#     #channel = ChoiceWithOtherField(choices = UserProfile.CHANNEL_CHOICES)
# 
# 
#     # air conditioning
#     ac = models.IntegerField('Air conditioner type',
#                              blank=False, default=3,
#                              choices=AC_CHOICES,
#                              )
# 
#     # furnace and water heater
#     furnace = models.IntegerField('Furnace type',
#                                   blank=False, default=3,
#                                   choices=HEATER_CHOICES,
#                                   )
#     water_heater = models.IntegerField('Water heater type',
#                                        blank=False, default=3,
#                                        choices=HEATER_CHOICES,
#                                        )
# 
# 
# 
# 
#    # goal = models.IntegerField('Which goals would you like to receive notifications about?',
#    #                            blank=False, default=0,
#    #                           # blank=True,
#    #                            choices=GOALS_CHOICES,
#    #                            )
# 
#     def goal_set(self):
#         # TO DO hacky
#         return set(int(g) for g in self.goal[0].split())
# 
#     def get_intro_message(self):
#         return messages.intro_message(SENDTEXT_FREQWORDS[self.text_freq])
# 
#     def get_edit_profile_message(self):
#         goal_set = self.goal_set()
#         if len(goal_set) == 0:
#             goal_words = None
#         elif len(goal_set) == 1:
#             goal_words = GOAL_WORDS[goal_set.pop()]
#         elif len(goal_set) == 2:
#             goal_words = ' and '.join([GOAL_WORDS[g] for g in goal_set])
#         else:
#             goal_words = ''
#             while len(goal_set) > 1:
#                 goal_words += GOAL_WORDS[goal_set.pop()]+', '
#             goal_words += 'and '+GOAL_WORDS[goal_set.pop()]
# 
#         msg = messages.edit_profile_message(SENDTEXT_FREQWORDS[self.text_freq],
#                                              goal_words)
#         print msg
#         return msg
# 
#     def get_personalized_message(self, percent_green, percent_coal,
#                                  marginal_fuel):
#         """ Select an appropriate message for a user
#             based on their preferences and the state of the grid,
#             or None.
#         """
#         # if there's no marginal, there's no message
#         if marginal_fuel == 'None':
#             debug('      No message (no marginal fuel)')
#             return None
# 
#         # sort out goals
#         goal_set = self.goal_set()
# 
#         # marginal is renewable
#         if marginal_fuel in ['Wind', 'Hydro', 'Wood', 'Refuse'] and len(goal_set & set([0, 2, 3])) > 0:
#             if self.ac == 1: # central
#                 return messages.use_central_ac_message(marginal_fuel)
#             else:
#                 return messages.use_message(marginal_fuel)
# 
#         # marginal is coal
#         if marginal_fuel in ['Coal'] and len(goal_set & set([0, 1, 3])) > 0:
#             if self.ac == 1: # central
#                 return messages.dont_use_central_ac_message(marginal_fuel)
#             else:
#                 return messages.dont_use_message(marginal_fuel)
# 
#         # marginal is oil
#         if marginal_fuel in ['Oil'] and len(goal_set & set([0, 3])) > 0:
#             if self.ac == 1: # central
#                 return messages.dont_use_central_ac_message(marginal_fuel)
#             else:
#                 return messages.dont_use_message(marginal_fuel)
# 
#         # else
#         print 'No message found for marginal fuel %s and goal %s' % (marginal_fuel, self.goal)
#         debug('      No message (marginal fuel {}, goal {})'.format(marginal_fuel, self.goal))
#         return None
# 
# class NewUserForm(ModelForm):
#     name = forms.CharField(error_messages={'required': 'No name? OK, what should we call you?'})
#     email = forms.CharField(error_messages={'required': "That's not an email address!"})
#     class Meta:
#         model = User
#         exclude = ['verification_code', 'is_verified', 'userid', 'phone']
# 
#     def __init__(self, *args, **kwargs):
#         super(NewUserForm, self).__init__(*args, **kwargs)
#         #self.fields['phone'].widget = HiddenInput()
#         self.fields['name'].widget.attrs['placeholder'] = u'Name'
#         self.fields['email'].widget.attrs['placeholder'] = u'Email'
#         #self.fields['phone'].initial = '000-000-0000' # set the initial value of phone number
# 
# class UserPhoneForm(ModelForm):
#     class Meta:
#         model = User
#         fields = ('phone',)
# 
#     def __init__(self, *args, **kwargs):
#         super(UserPhoneForm, self).__init__(*args, **kwargs)
#         self.fields['phone'].widget.attrs['placeholder'] = u'Phone'
# 
#     def clean_phone(self):
#         # this should probably be done using User unique_together
#         email = self.instance.email
#         phone = self.cleaned_data['phone']
#         preexisting_users =  User.objects.filter(phone=phone, email=email)
#         if preexisting_users.count() > 0:
#             userid = preexisting_users[0].userid
#             msg = "User %d already exists with email %s and phone %s.\n" % (userid,
#                                                                           email,
#                                                                           phone)
#             if preexisting_users[0].is_verified:
#                 if preexisting_users[0].is_active:
#                     msg += "Edit profile: http://wattTime.herokuapp.com/profile/%s" % userid
#                 else:
#                     msg += "Reactivate SMS notifications and edit profile: http://wattTime.herokuapp.com/profile/%s" % userid
#             else:
#                 msg += "Verify phone: http://wattTime.herokuapp.com/phone_verify/%s" % userid
#             raise ValidationError(msg)
#         else:
#             return phone
# 
# class UserProfileForm(ModelForm):
# 
#     class Meta:
#         model = UserProfile
#         exclude = ['userid']
#         widgets = {
#             #'goal': RadioSelect(),
#             'ac': RadioSelect(),
#             'furnace': RadioSelect(),
#             'water_heater': RadioSelect(),
#             'text_freq': RadioSelect(),
#             'channel': RadioSelect(),
#           #  'weekend_sendtext_hours': CheckboxSelectMultiple(),
#           #  'weekday_sendtext_hours': CheckboxSelectMultiple(),
#             }
# 
# class UserVerificationForm(forms.Form):
#     verification_code = forms.IntegerField(min_value=100000, max_value=999999, error_messages = {'min_value': 'Please make sure to enter a 6 digits code', 'max_value' : 'Please make sure to enter a 6 digits code'})
# 
#     def __init__(self, *args, **kwargs):
#         super(UserVerificationForm, self).__init__(*args, **kwargs)
#         self.fields['verification_code'].widget.attrs['placeholder'] = u'xxxxxx'
