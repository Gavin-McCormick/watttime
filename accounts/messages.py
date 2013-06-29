# content of text messages
# the %s symbol is replaced by the variable that appears after the % symbol at the end
import random

def use_central_ac_message(marginal_fuel):
    randint = random.randint(0,2)
    if randint == 0:
# characters counts:
#              0         1         2         3         4         5         6         7         8         9         0         1         2         3
        return "WattTime Alert! Your power is now clean %s. Hot out? You can precool your house on clean power! Turn down temp a bit for 30 mins." % marginal_fuel
    elif randint == 1:
        return "WattTime Alert! You're now running on clean %s power. Won't last long! Can you use that clean power now instead of later?" % marginal_fuel
    else:
        return "WattTime Alert! Your power is really clean %s right now. Anything you can recharge now to use all that clean energy? Laptop?" % marginal_fuel

def use_message(marginal_fuel):
    randint = random.randint(0,2)
    if randint == 0:
        return "WattTime Alert! Your power is unusually clean now - %s. Can you avoid wasting that clean power? Great time to do laundry or dishes!" % marginal_fuel
    elif randint == 1:
        return "WattTime Alert! You're now running on clean %s power. Won't last long! Can you use that clean power now instead of later?" % marginal_fuel
    else:
        return "WattTime Alert! Your power is really clean %s right now. Anything you can recharge now to use all that clean energy? Laptop?" % marginal_fuel

def dont_use_central_ac_message(marginal_fuel):
    randint = random.randint(0,3)
    if randint == 0:
        return "WattTime Alert! You're now getting dirty %s power. Help us shut them down, save some power now! Can you turn off your AC for 20 mins?" % marginal_fuel
    elif randint == 1:
        return "WattTime Alert! You're now running on %s. Help us shut them down! Think you could dial back the temperature 2 degrees for an hour?" % marginal_fuel
    elif randint == 2:
        return "WattTime Alert! Your power is from %s right now. Help us use less of that dirty energy source! Can you turn out an extra light?" % marginal_fuel
    else:
        return "WattTime Alert! You're now running on %s. Are you doing anything that uses power right now? Maybe you could take a 15 min break!" % marginal_fuel

def dont_use_message(marginal_fuel):
    randint = random.randint(0,3)
    if randint == 0:
        return "The marginal fuel is %s, so avoid using electricity if you can!" % marginal_fuel
    elif randint == 1:
        return "WattTime Alert! You're now running on %s. Are you doing anything that uses power right now? Maybe you could take a 15 min break!" % marginal_fuel
    elif randint == 2:
        return "WattTime Alert! Your power is from %s right now. Help us use less of that dirty energy source! Can you turn out an extra light?" % marginal_fuel
    else:
        return "WattTime Alert! You're now on dirty %s power. Great time to save energy! Anything charging that you charge later on cleaner power?" % marginal_fuel

def verify_phone_message(code):
    return "Hello from WattTime! Enter [%s] on the sign up page to verify your device. This is a 1-time message." % code

def intro_message(frequency='daily'):
    return "Thanks for signing up for %s SMS notifications from WattTime!" % (frequency)

def edit_profile_message(frequency, goals):
    msg = "Thanks for editing your WattTime preferences! You are now signed up for %s SMS notifications" % frequency
    if goals:
        msg += " %s." % goals
    else:
        msg += '.'
    return msg

def email_signup_message(userid, name):
    lines = ["Hi %s," % name,
             "Thank you for your interest in WattTime! As of Monday July 1 we will support California and will begin beta testing.",
             "We'll send you a note on Monday with an access code for the beta.", 
             "We hope you'll enjoy the service, and hope you won't mind if we ask you a few questions about it after a week or two.",
             "Cheers,",
             "the team at WattTime"
             ]
    return "\n".join(lines)

def account_activated_message(userid, name, phone):
    lines = ["Hi %s," % name,
             "Thanks for signing up for WattTime! You are now subscribed to SMS notifications from WattTime about the status of your electricity source at this phone number:",
             "%s" % phone,
             "To personalize this service and increase your impact, just answer a few quick questions at http://wattTime.herokuapp.com/profile/%s. You can return to this link to update your preferences at any time." % userid,
             "To unsubscribe from SMS notifications, click on http://wattTime.herokuapp.com/unsubscribe/%s." % phone.replace('-',''),
             "Cheers,",
             "the team at WattTime"
             ]
    return "\n".join(lines)

def account_inactivated_message(userid, name, phone):
    lines = ["Hi %s," % name,
             "You are now unsubscribed from SMS notifications from WattTime to this phone number:",
             "%s" % phone,
             "We're sorry to see you go! You can turn SMS notifications back on at any time by updating your preferences at http://wattTime.herokuapp.com/profile/%s." % userid,
             "Cheers,",
             "the team at WattTime"
             ]
    return "\n".join(lines)

