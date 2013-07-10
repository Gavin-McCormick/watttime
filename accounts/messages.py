# content of text messages
# the %s symbol is replaced by the variable that appears after the % symbol at the end
import random

class Message:
    USE_LESS = 'use_less'
    USE_MORE = 'use_more'
    CONFIRMATION = 'confirmation'
    INFORMATION = 'information'

    def __init__(self, msg_type, msg):
        self.msg_type = msg_type
        self.msg = msg

    @classmethod
    def use_more_message(cls, msg):
        return cls(Message.USE_MORE, msg)

    @classmethod
    def use_less_message(cls, msg):
        return cls(Message.USE_LESS, msg)

    @classmethod
    def confirmation_message(cls, msg):
        return cls(Message.CONFIRMATION, msg)

    @classmethod
    def information_message(cls, msg):
        return cls(Message.INFORMATION, msg)

def dirtiesthour_criteria(percent_green, marginal_fuel, state):
    randsituation = random.randint(0,1)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:
        situation_msg = "This is probably going to be the dirtiest power %s sees today."
    else:
        situation_msg = "This hour is the least clean your electricity will get today."
    return Message.dirtiesthour_criteria(situation_msg)

def unusuallydirtyhour_criteria(percent_green, marginal_fuel, state):
    randsituation = random.randint(0,1)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:
        situation_msg = "Power is unusually dirty right now in %s!" % state
    else:
        situation_msg = "Not much renewable power right now."
    return Message.use_less_message(situation_msg)

def cleanesthour_criteria(percent_green, marginal_fuel, state):
    randsituation = random.randint(0,1)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:
        situation_msg = "This is the cleanest time today to use power."
    else:
        situation_msg = "Lots of renewable power on the grid right now!"
    return Message.use_more_message(situation_msg)

def unusuallycleanhour_criteria(percent_green, marginal_fuel, state):
    randsituation = random.randint(0,1)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:
        situation_msg = "%s electricity is unusually clean right now." % state
    else:
        situation_msg = "Your power is unusually full of renewables atm."
    return Message.use_more_message(situation_msg)

def dirtyemergency_criteria(percent_green, marginal_fuel, state):
    randsituation = random.randint(0,1)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:
        situation_msg = "Electricity's about as dirty as it ever gets in %s right now." % state
    else:
        situation_msg = "This is about as dirty as power ever gets in %s!" % state
    return Message.use_less_message(situation_msg)

def dirtiesthour_homegeneric_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Look around. Can you find one thing on that doesn't need to be?"
    elif randsituation == 1:
        action_msg = "Think you could turn off one thing? What do you need least?"
    else:
        action_msg = "Look around - see a light on that's not needed?"
    return Message.use_less_message(action_msg)

def dirtiesthour_homeac_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Biggest power draw is A/C - think you could dial back the thermostat?"
    elif randsituation == 1:
        action_msg = "If your A/C is on, think you could switch it off for just a bit?"
    else:
        action_msg = "Look around - see a light on that's not needed?"
    return Message.use_less_message(action_msg)

def dirtiesthour_workgeneric_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Try a treasure hunt break! Can you find 1 thing on that isn't needed?"
    elif randsituation == 1:
        action_msg = "Think you could turn off one thing? What do you need least?"
    else:
        action_msg = "Look around - see a light or monitor on that's not needed?"
    return Message.use_less_message(action_msg)

def dirtiesthour_workac_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Biggest power draw is A/C - think you could dial back the thermostat?"
    elif randsituation == 1:
        action_msg = "If the A/C is on, any chance you could dial it back for a bit?"
    else:
        action_msg = "Look around. Can you find one thing on that doesn't need to be?"
    return Message.use_less_message(action_msg)

def unusuallydirtyhour_workac_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Biggest user for power is A/C - think you could dial back the thermostat?"
    elif randsituation == 1:
        action_msg = "Is the A/C on? Think anyone would mind you dialing it back for a bit?"
    else:
        action_msg = "Look around. Can you find one thing that doesn't need to be on?"
    return Message.use_less_message(action_msg)

def unusuallydirtyhour_workgeneric_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Any appliances you aren't using that you could turn off?"
    elif randsituation == 1:
        action_msg = "Think you could turn off one thing? What do you need least?"
    else:
        action_msg = "Look around - what's one thing that doesn't need to be on? A light?"
    return Message.use_less_message(action_msg)

def unusuallydirtyhour_homeac_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Biggest draw for power is A/C - think you could dial back the thermostat?"
    elif randsituation == 1:
        action_msg = "If your A/C is on, think you could switch it off for just a bit?"
    else:
        action_msg = "Any appliances you aren't using that you could turn off?"
    return Message.use_less_message(action_msg)

def unusuallydirtyhour_homegeneric_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Any appliances you aren't using that you could turn off?"
    elif randsituation == 1:
        action_msg = "Think you could turn off one thing? What do you need least?"
    else:
        action_msg = "Look around - see a light on that's not needed?"
    return Message.use_less_message(action_msg)

def dirtyemergency_workac_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "If the A/C is on, think anyone would mind you dialing it back for a bit?"
    elif randsituation == 1:
        action_msg = "Up to 40% of power in CA goes to A/C. Can you dial yours back 2 degrees?"
    else:
        action_msg = "Think you could turn off one thing? What do you need least?"
    return Message.use_less_message(action_msg)

def dirtyemergency_workgeneric_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Think you could turn off one thing? What do you need least?"
    elif randsituation == 1:
        action_msg = "Look around. Can you find one thing on that doesn't need to be?"
    else:
        action_msg = "Can you turn off one thing? See a light or monitor on that's not needed?"
    return Message.use_less_message(action_msg)

def dirtyemergency_pool_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Pool pump use a LOT of power. Could you turn yours off for the day?"
    elif randsituation == 1:
        action_msg = "Think you could turn off one thing? What do you need least?"
    else:
        action_msg = "Look around. Anything you could stand to turn off? Lights? Pool pump?"
    return Message.use_less_message(action_msg)

def dirtyemergency_homeac_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Up to 40% of power in CA goes to A/C. Is yours on? Can you turn off for now?"
    elif randsituation == 1:
        action_msg = "If the A/C is on, any chance you could turn it off at least for a bit?"
    else:
        action_msg = "Look around. Anything you could stand to turn off for now?"
    return Message.use_less_message(action_msg)

def dirtyemergency_waterheater_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Your water heater is a huge power draw. Can you shut it off for an hour?"
    elif randsituation == 1:
        action_msg = "Hot water requires lots of power. Can you avoid using any for a few hours?"
    else:
        action_msg = "Look around. Anything you could stand to turn off for now?"
    return Message.use_less_message(action_msg)

def dirtyemergency_homegeneric_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "What's one thing that doesn't need to be on? A light? TV?"
    elif randsituation == 1:
        action_msg = "Think you could turn off one thing? What do you need least?"
    else:
        action_msg = "Look around. Anything you could stand to turn off for now?"
    return Message.use_less_message(action_msg)

def unusuallycleanhour_workgeneric_actions(marginal_fuel):
    randaction = random.randint(0,1)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Is there anything you could turn on now rather than later?"
    else:
        action_msg = "Great time to, say, recharge any electronics."
    return Message.use_more_message(action_msg)

def unusuallycleanhour_homeac_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Good time to, say, recharge electronics or turn up the A/C if hot."
    elif randsituation == 1:
        action_msg = "Anything you could run now instead of later? Laundry? Oven?"
    else:
        action_msg = "Hot? Maybe you could turn up A/C, precool while you're on clean power? "
    return Message.use_more_message(action_msg)

def unusuallycleanhour_precool_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Think it'll be hot today? Why not turn up A/C now while it's clean?"
    else:
        action_msg = "Expecting a hot day? Why not pre-cool your house before work?"
    return Message.use_more_message(action_msg)

def unusuallycleanhour_dishwasher_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "No chance your dishwasher's full? Could you run it now while power's clean?"
    elif randsituation == 1:
        action_msg = "Anything you could run now instead of later? Laundry? Oven? Dishwasher?"
    else:
        action_msg = "Can you think of anything you could turn on now rather than later?"
    return Message.use_more_message(action_msg)

def unusuallycleanhour_homegeneric_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Can you think of anything you could turn on now rather than later?"
    elif randsituation == 1:
        action_msg = "Great time to recharge any electronics."
    else:
        action_msg = "Anything you could run now instead of later? Laundry? Oven?"
    return Message.use_more_message(action_msg)

def cleanesthour_dishwasher_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Can you think of anything you could turn on now rather than later?"
    elif randsituation == 1:
        action_msg = "Dishwasher loaded? Now would be a great time to run it."
    else:
        action_msg = "Anything you could run now instead of later? Laundry? Dishwasher?"
    return Message.use_more_message(action_msg)

def cleanesthour_homeac_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Anything you could run now instead of later? Laundry? Oven?"
    elif randsituation == 1:
        action_msg = "Good time to, say, recharge electronics or turn up the A/C if you're hot."
    else:
        action_msg = "Can you think of anything you could turn on now rather than later?"
    return Message.use_more_message(action_msg)

def cleanesthour_homegeneric_actions(marginal_fuel):
    randaction = random.randint(0,2)
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
    if randaction == 0:    
        action_msg = "Can you think of anything you could turn on now rather than later?"
    elif randsituation == 1:
        action_msg = "Great time to recharge any electronics."
    else:
        action_msg = "Anything you could run now instead of later? Laundry? Oven?"
    return Message.use_more_message(action_msg)

def use_central_ac_message(marginal_fuel):
    randint = random.randint(0,2)
    if randint == 0:
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
        msg = "WattTime Alert! Your power is now clean %s. Hot out? You can precool your house on clean power! Turn down temp a bit for 30 mins." % marginal_fuel
    elif randint == 1:
        msg = "WattTime Alert! You're now running on clean %s power. Won't last long! Can you use that clean power now instead of later?" % marginal_fuel
    else:
        msg = "WattTime Alert! Your power is really clean %s right now. Anything you can recharge now to use all that clean energy? Laptop?" % marginal_fuel
    return Message.use_more_message(msg)

def use_message(marginal_fuel):
    randint = random.randint(0,2)
    if randint == 0:
        msg = "WattTime Alert! Your power is unusually clean now - %s. Can you avoid wasting that clean power? Great time to do laundry or dishes!" % marginal_fuel
    elif randint == 1:
        msg = "WattTime Alert! You're now running on clean %s power. Won't last long! Can you use that clean power now instead of later?" % marginal_fuel
    else:
        msg = "WattTime Alert! Your power is really clean %s right now. Anything you can recharge now to use all that clean energy? Laptop?" % marginal_fuel
    return Message.use_more_message(msg)

def dont_use_central_ac_message(marginal_fuel):
    randint = random.randint(0,3)
    if randint == 0:
        msg = "WattTime Alert! You're now getting dirty %s power. Help us shut them down, save some power now! Can you turn off your AC for 20 mins?" % marginal_fuel
    elif randint == 1:
        msg = "WattTime Alert! You're now running on %s. Help us shut them down! Think you could dial back the temperature 2 degrees for an hour?" % marginal_fuel
    elif randint == 2:
        msg  ="WattTime Alert! Your power is from %s right now. Help us use less of that dirty energy source! Can you turn out an extra light?" % marginal_fuel
    else:
        msg = "WattTime Alert! You're now running on %s. Are you doing anything that uses power right now? Maybe you could take a 15 min break!" % marginal_fuel
    return Message.use_less_message(msg)


def dont_use_message(marginal_fuel):
    randint = random.randint(0,3)
    if randint == 0:
        msg = "The marginal fuel is %s, so avoid using electricity if you can!" % marginal_fuel
    elif randint == 1:
        msg = "WattTime Alert! You're now running on %s. Are you doing anything that uses power right now? Maybe you could take a 15 min break!" % marginal_fuel
    elif randint == 2:
        msg = "WattTime Alert! Your power is from %s right now. Help us use less of that dirty energy source! Can you turn out an extra light?" % marginal_fuel
    else:
        msg = "WattTime Alert! You're now on dirty %s power. Great time to save energy! Anything charging that you charge later on cleaner power?" % marginal_fuel
    return Message.use_less_message(msg)


def verify_phone_message(code):
    return Message.confirmation_message("Hello from WattTime! Enter [%s] on the sign up page to verify your device. This is a 1-time message." % code)

def intro_message(frequency='daily'):
    return Message.information_message("Thanks for signing up for %s SMS notifications from WattTime!" % (frequency))

def edit_profile_message(frequency, goals):
    msg = "Thanks for editing your WattTime preferences! You are now signed up for %s SMS notifications" % frequency
    if goals:
        msg += " %s." % goals
    else:
        msg += '.'
    return Message.information_message(msg)

def email_signup_message(userid, name):
    lines = ["Hi %s," % name,
             "Thank you for your interest in WattTime! As of Monday July 1 we will support California and will begin beta testing.",
             "We'll send you a note on Monday with an access code for the beta.", 
             "We hope you'll enjoy the service, and hope you won't mind if we ask you a few questions about it after a week or two.",
             "Cheers,",
             "the team at WattTime"
             ]
    return Message.information_message("\n".join(lines))

def account_activated_message(userid, name, phone):
    lines = ["Hi %s," % name,
             "Thanks for signing up for WattTime! You are now subscribed to SMS notifications from WattTime about the status of your electricity source at this phone number:",
             "%s" % phone,
             "To personalize this service and increase your impact, just answer a few quick questions at http://wattTime.herokuapp.com/profile/%s. You can return to this link to update your preferences at any time." % userid,
             "To unsubscribe from SMS notifications, click on http://wattTime.herokuapp.com/unsubscribe/%s." % phone.replace('-',''),
             "Cheers,",
             "the team at WattTime"
             ]
    return Message.information("\n".join(lines))

def account_inactivated_message(userid, name, phone):
    lines = ["Hi %s," % name,
             "You are now unsubscribed from SMS notifications from WattTime to this phone number:",
             "%s" % phone,
             "We're sorry to see you go! You can turn SMS notifications back on at any time by updating your preferences at http://wattTime.herokuapp.com/profile/%s." % userid,
             "Cheers,",
             "the team at WattTime"
             ]
    return Message.information("\n".join(lines))

def invite_message(email, url, name = None):
    lines = ["Hi {name},",
            "",
            "This is an invitation to join the WattTime beta test.",
            "",
            "We hope you will join us in testing out this novel way to take control of how your own electricity is made.",
            "",
            "To begin, please just head to {url} to set up your account."
            "",
            "Cheers,",
            "the team at WattTime"
            ]
    if name is None:
        name = email
    return ("\n".join(lines)).format(name = name, url = url)

def resend_login_message(name, url):
    lines = ["Hi {name},",
            "You can log in to your account at {url}.",
            "Cheers,",
            "the team at WattTime"]
    return ("\n".join(lines)).format(name = name, url = url)

def alpha_completed(name):
    lines = ["Hi {name},",
        "",
        "Thank you for being one of the first WattTime users and helping us test out the earliest version of our service! We're going to wrap up this alpha test now in order to switch to a slightly more advanced beta version.",
        "",
        "We've already learned a lot from the alpha test, and we'd love to hear any thoughts you'd like to share. What has your experience been like with the service so far? Was it interesting to be receiving the texts? Or was it annoying to receive them too often, or in the middle of a workday? Did you actually follow any of the suggestions? What could make our advice more relevant to you? Drop us a line by replying to this email - we'd love to hear your thoughts!",
        "",
        "Now our site is going to go down for the rest of the weekend during the switch. On Monday, we'll send you a link and a code that will allow you to access the beta version if you like. We hope you'll consider joining us for that pilot as well!",
        "",
        "Thanks again for helping us out,",
        "",
        "Gavin",
        "and rest of the WattTime team"]
    return ("\n".join(lines)).format(name = name)
