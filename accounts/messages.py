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
    def use_more(cls, msg):
        return cls(Message.USE_MORE, msg)

    @classmethod
    def use_less(cls, msg):
        return cls(Message.USE_LESS, msg)

    @classmethod
    def confirmation(cls, msg):
        return cls(Message.CONFIRMATION, msg)

    @classmethod
    def information(cls, msg):
        return cls(Message.INFORMATION, msg)

def msg(criterion, action, state):
    a = 'WattTime alert: {} {}'.format(criterion, action)
    return a.format(state = state)

def rand(options):
    index = random.randint(0, len(options) - 1)
    return options[index]

criterion_dirtiest = [
    "This is probably going to be the dirtiest power {state} sees today.",
    "This hour is the least clean your electricity will get today."]

action_dirtiest_home_generic = [
    "Look around. Can you find one thing on that doesn't need to be?",
    "Think you could turn off one thing? What do you need least?",
    "Look around - see a light on that's not needed?"]

action_dirtiest_home_ac = [
    "Biggest power draw is A/C - think you could dial back the thermostat?",
    "If your A/C is on, think you could switch it off for just a bit?",
    "Look around - see a light on that's not needed?"]

action_dirtiest_work_generic = [
    "Try a treasure hunt break! Can you find 1 thing on that isn't needed?",
    "Think you could turn off one thing? What do you need least?",
    "Look around - see a light or monitor on that's not needed?"]

action_dirtiest_work_ac = [
    "Biggest power draw is A/C - think you could dial back the thermostat?",
    "If the A/C is on, any chance you could dial it back for a bit?",
    "Look around. Can you find one thing on that doesn't need to be?"]

def ca_message_dirty(up):
    # TODO choose between home vs. work appropriately.
    c = rand(criterion_dirtiest)
    a = rand(action_dirtiest_home_generic)
    return Message.use_less(msg(c, a, 'CA'))

criterion_cleanest = [
    "This is the cleanest time today to use power.",
    "Lots of renewable power on the grid right now!"]

action_cleanest_dishwasher = [
    "Can you think of anything you could turn on now rather than later?",
    "Dishwasher loaded? Now would be a great time to run it.",
    "Anything you could run now instead of later? Laundry? Dishwasher?"]

action_cleanest_home_ac = [
    "Anything you could run now instead of later? Laundry? Oven?",
    "Good time to, say, recharge electronics or turn up the A/C if you're hot.",
    "Can you think of anything you could turn on now rather than later?"]

action_cleanest_home_generic = [
    "Can you think of anything you could turn on now rather than later?",
    "Great time to recharge any electronics.",
    "Anything you could run now instead of later? Laundry? Oven?"]

def ca_message_clean(up):
    # TODO choose actions appropriately
    c = rand(criterion_cleanest)
    a = rand(action_cleanest_home_generic)
    return Message.use_more(msg(c, a))

criterion_unusually_dirty = [
    "Power is unusually dirty right now in {state}!",
    "Not much renewable power right now."]

criterion_unusually_clean = [
    "{state} electricity is unusually clean right now.",
    "Your power is unusually full of renewables atm."]

criterion_dirty_emergency = [
    "Electricity's about as dirty as it ever gets in {state} right now.",
    "This is about as dirty as power ever gets in {state}!"]

action_unusually_dirty_work_ac = [
    "Biggest user for power is A/C - think you could dial back the thermostat?",
    "Is the A/C on? Think anyone would mind you dialing it back for a bit?",
    "Look around. Can you find one thing that doesn't need to be on?"]

action_unusually_dirty_work_generic = [
    "Any appliances you aren't using that you could turn off?",
    "Think you could turn off one thing? What do you need least?",
    "Look around - what's one thing that doesn't need to be on? A light?"]

action_unusually_dirty_home_ac = [
    "Biggest draw for power is A/C - think you could dial back the thermostat?",
    "If your A/C is on, think you could switch it off for just a bit?",
    "Any appliances you aren't using that you could turn off?"]

action_unusually_dirty_home_generic = [
    "Any appliances you aren't using that you could turn off?",
    "Think you could turn off one thing? What do you need least?",
    "Look around - see a light on that's not needed?"]

action_dirty_emergency_work_ac = [
    "If the A/C is on, think anyone would mind you dialing it back for a bit?",
    "Up to 40% of power in CA goes to A/C. Can you dial yours back 2 degrees?",
    "Think you could turn off one thing? What do you need least?"]

action_dirty_emergency_work_generic = [
    "Think you could turn off one thing? What do you need least?",
    "Look around. Can you find one thing on that doesn't need to be?",
    "Can you turn off one thing? See a light or monitor on that's not needed?"]

action_dirty_emergency_pool = [
    "Pool pump use a LOT of power. Could you turn yours off for the day?",
    "Think you could turn off one thing? What do you need least?",
    "Look around. Anything you could stand to turn off? Lights? Pool pump?"]

action_dirty_emergency_home_ac = [
    "Up to 40% of power in CA goes to A/C. Is yours on? Can you turn off for now?",
    "If the A/C is on, any chance you could turn it off at least for a bit?",
    "Look around. Anything you could stand to turn off for now?"]

action_dirty_emergency_waterheater = [
    "Your water heater is a huge power draw. Can you shut it off for an hour?",
    "Hot water requires lots of power. Can you avoid using any for a few hours?",
    "Look around. Anything you could stand to turn off for now?"]

action_dirty_emergency_home_generic = [
    "What's one thing that doesn't need to be on? A light? TV?",
    "Think you could turn off one thing? What do you need least?",
    "Look around. Anything you could stand to turn off for now?"]

action_unusually_clean_work_generic = [
    "Is there anything you could turn on now rather than later?",
    "Great time to, say, recharge any electronics."]

action_unusually_clean_home_ac = [
    "Good time to, say, recharge electronics or turn up the A/C if hot.",
    "Anything you could run now instead of later? Laundry? Oven?",
    "Hot? Maybe you could turn up A/C, precool while you're on clean power?"]

action_unusually_clean_precool = [
    "Think it'll be hot today? Why not turn up A/C now while it's clean?",
    "Expecting a hot day? Why not pre-cool your house before work?"]

action_unusually_clean_dishwasher = [
    "No chance your dishwasher's full? Could you run it now while power's clean?",
    "Anything you could run now instead of later? Laundry? Oven? Dishwasher?",
    "Can you think of anything you could turn on now rather than later?"]

action_unusually_clean_home_generic = [
    "Can you think of anything you could turn on now rather than later?",
    "Great time to recharge any electronics.",
    "Anything you could run now instead of later? Laundry? Oven?"]

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
    return Message.confirmation("Hello from WattTime! Enter [%s] on the sign up page to verify your device. This is a 1-time message." % code)

def intro_message(frequency='daily'):
    return Message.information("Thanks for signing up for %s SMS notifications from WattTime!" % (frequency))

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

def morning_forecast_email(name, best_hour, worst_hour):
    lines = ["Good morning {name},",
        "",
        "Today in California the cleanest time to use power will be {best} and the dirtiest time will be {worst}. ",
        "",
        "(More info always available at https://watttime.herokuapp.com/status .)",
        "",
        "Cheers,",
        "",
        "The WattTime team"]
    return ("\n".join(lines)).format(name = name, best = best_hour, worst=worst_hour)

def morning_forecast_email_first(name, best_hour, worst_hour):
    lines = ["Hi {name},",
        "",
        "Welcome to your first WattTime morning forecast! Today in California electricity will be cleanest at {best} and dirtiest at {worst}. Can you find a way to shift any energy consumption towards the cleanest time or away from the dirtiest?",
        "",
        # "In addition, you can now always see the full day's clean energy outlook for California or other regions at https://watttime.herokuapp.com/status. (It's updated hourly throughout the day.)",
        # "",
        "We hope you find this forecast helpful! Questions? Feedback? You can write us at this address at any time.",
        "",
        "Cheers,",
        "",
        "The WattTime team"]
    return ("\n".join(lines)).format(name = name, best = best_hour, worst = worst_hour)
