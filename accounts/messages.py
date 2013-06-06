# content of text messages
# the %s symbol is replaced by the variable that appears after the % symbol at the end
import random

def use_central_ac_message(marginal_fuel):
	randint = random.randint(0,2)
	if randint == 0:
		return "WattTime Alert! Your power now clean %s. Hot out? You could pre-cool your house on clean power! Turn down temp a bit, put it back in 30 mins. Don't forget." % marginal_fuel
	elif randint == 1:
		return "WattTime Alert! You're now running on clean %s power. Won't last long! Can you think of something you could do to use power now instead of later?." % marginal_fuel
	else:
		return "WattTime Alert! Your power is really clean %s right now. Anything you can recharge now to use all that clean energy? Laptop? Phone?" % marginal_fuel
		
def use_message(marginal_fuel):
	randint = random.randint(0,2)
	if randint == 0:
		return "WattTime Alert! Your power is unusually clean right now - %s. Can you avoid wasting that clean power? Great time to do laundry, or dishes! " % marginal_fuel
	elif randint == 1:
		return "WattTime Alert! You're now running on clean %s power. Won't last long! Can you think of something you could do to use power now instead of later?." % marginal_fuel
	else:	
		return "WattTime Alert! Your power is really clean %s right now. Anything you can recharge now to use all that clean energy? Laptop? Phone?" % marginal_fuel
		
def dont_use_central_ac_message(marginal_fuel):
	randint = random.randint(0,3)
	if randint == 0:
		return "WattTime Alert! You're now getting dirty %s power. Help us shut them down, save some power now! Can you turn off your thermostat for 20 mins?" % marginal_fuel
	elif randint == 1:
		return "WattTime Alert! You're now running on %s. Help us shut them down by saving some power now! Think you could dial back the temperature 2 degrees for an hour?" % marginal_fuel
	elif randint == 2:
		return "WattTime Alert! Your power is from %s right now. Help us use less of that dirty energy source! Can you turn out an extra light?" % marginal_fuel
	else:
		return "WattTime Alert! You're now running on %s. Great time to procrastinate! Are you doing anything that uses power right now? Maybe you could take a 15 min break!" % marginal_fuel

def dont_use_message(marginal_fuel):
	randint = random.randint(0,3)
	if randint == 0:
		return "The marginal fuel is %s, so avoid using electricity if you can!" % marginal_fuel
	elif randint == 1:
		return "WattTime Alert! You're now running on %s. Great time to procrastinate! Are you doing anything that uses power right now? Maybe you could take a 15 min break!" % marginal_fuel
	elif randint == 2:
		return "WattTime Alert! Your power is from %s right now. Help us use less of that dirty energy source! Can you turn out an extra light?" % marginal_fuel
	else:
		return "WattTime Alert! You're now on dirty %s power. Great time to save energy! Anything charging that you could unplug now and put back later when power is cleaner?" % marginal_fuel
	
def verify_phone_message(code):
    return "Hello from WattTime! Enter [%s] on the sign up page to verify your device. This is a 1-time message." % code

def email_signup_message(userid, name):
    lines = ["Hi %s," % name,
             "Thanks for your interest in WattTime! You are now subscribed to occasional email updates about WattTime products and services.",
             "Currently we are piloting WattTime's SMS notification service in Massachusetts. To participate in the pilot, just enter your phone number at http://wattTime.herokuapp.com/phone_setup/%s." % userid,
             "To unsubscribe from our email list, please reply to this email with the message 'unsubscribe'.",
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

