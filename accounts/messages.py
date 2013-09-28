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

def make_msg(criterion, action, state = "{state}", fuel = "{fuel}"):
    a = 'WattTime alert: {} {}'.format(criterion, action)
    return a.format(state = state, fuel = fuel)

def rand(options):
    index = random.randint(0, len(options) - 1)
    return options[index]

criterion_dirtiest = [
    "Right now in {state}, dirty electricity is contaminating our power grid.",
    "This is as dirty as our electricity will get today."]

# (1) we don't know what time these messages are going out
# (2) the majority of electricity lost to "vampire electronics" is
# due to a very small minority of badly designed devices which are difficult
# for the consumer to identify; and phone chargers are barely even noticeable
# (3) ac messaging belongs in the next category
action_dirtiest_home_generic = [
    # "Postpone any major appliance and equipment use until after 4 p.m.",
    # "Unplug vampire electronics like phone chargers and monitors.",
    "Adjust your air conditioning thermostat to 78F or higher.",
    "Look around. Can you find one thing on that doesn't need to be?",
    "Think you could turn off one thing? What do you need least?",
    "What practices could you put off to a cleaner time?"]

action_dirtiest_home_ac = [
    "Turn off all unnecessary lights, electronics, and appliances.",
    "If your A/C is on right now, switch it off and get some fresh air.",
    "Adjust your air conditioning thermostat to 78F or higher."]

action_dirtiest_work_generic = [
    "Making copies? Save it for later when our electricity is cleaner.",
    # "Set A/C to 78F. Adjust clothing and activity for comfort.",
    "What practices can you shift to later in the day?",
    "Adjust your clothing and modulate your activity for warmer temps."]

action_dirtiest_work_ac = [
    "Can some of your electricity consumption be rescheduled?",
    "Take a break from using electricity.",
    "What energy-intensive tasks could you schedule to run overnight?",
    "Dialing your A/C to 78F or higher makes an immediate impact."]

def ca_message_dirty(up):
    # TODO choose between home vs. work appropriately.
    c = rand(criterion_dirtiest)
    a = rand(action_dirtiest_home_generic)
    return Message.use_less(make_msg(c, a, state = 'CA'))

criterion_cleanest = [
    "Eureka! This is today's clean power peak!"]

action_cleanest_dishwasher = [
    "Some of the biggest reductions in energy consumption come from more efficient techology.",
    "This is generally a great time to run the dishwasher.",
    "Running a dishwasher late at night is the best time for cleaner electricity."]

action_cleanest_home_ac = [
    "This is the best time of day for electricity-intensive tasks.",
    "Major appliances and equipment run on a cleaner power grid right now.",
    "Vacuuming keeps your home clean. Around now, it helps keep the grid clean too."]

action_cleanest_home_generic = [
    "Solar and wind power are decontaminating the grid. Could you run the laundry right now?",
    "If your washing requires electricity, this is the best time for it.",
    "What electricity-based chores could you do regularly at this time?"]

def ca_message_clean(up):
    # TODO choose actions appropriately
    c = rand(criterion_cleanest)
    a = rand(action_cleanest_home_generic)
    return Message.use_more(make_msg(c, a, state = 'CA'))

criterion_unusually_dirty = [
    "In {state}, dirty electricity is contaminating the power grid.",
    "This is as dirty as our electricity will get today."]

criterion_unusually_clean = [
    "{state} electricity is achieving a rare clean power peak.",
    "This is an especially clean time to utilize electricity.",
    "Solar and wind power are decontaminating the grid."]

criterion_dirty_emergency = [
    "The {state} electricity grid is as dirty as it ever gets right now.",
    "The {state} power grid is highly contaminated with dirty energy."]

action_unusually_dirty_work_ac = [
    "Can you rearrange your electricity consumption to a later time?",
    "Take a break from electricity. Go chat with someone.",
    "Dial back your A/C to 78F or higher and lower the shades."]

action_unusually_dirty_work_generic = [
    "Which energy-intensive jobs could you schedule to run overnight?",
    "Which practices could you shift to later in the day?"
    # "Postpone major appliance and equipment use until after 4 p.m."
    ]

action_unusually_dirty_home_ac = [
    # "Postpone any major appliance and equipment use until after 4 p.m.",
    "Turn off all unnecessary lights, electronics, and appliances.",
    "Dialing back your A/C to 78F or higher will save you money."]

action_unusually_dirty_home_generic = [
    "Turn off all unnecessary lights, electronics, and appliances.",
    # "Postpone any major appliance and equipment use until after 4 p.m.",
    "Take a break from electricity. Go chat with someone."]

action_dirty_emergency_work_ac = [
    "If your A/C is on right now, switch it off.",
    "Dial back your A/C to 78F or higher. ",
    "Reschedule your electricity use until later in the day."]

action_dirty_emergency_work_generic = [
    "Which practices could you shift to later in the day?",
    # "Unplug vampire electronics like phone chargers and monitors",
    # "Postpone major appliance and equipment use until after 4 p.m."
    ]

action_dirty_emergency_pool = [
    # "Enlarge your impact. Postpone electric appliances until 4 p.m.",
    "What practices can you shift to later this evening?",
    "Running the pool pump at night would be ideal."]

action_dirty_emergency_home_ac = [
    "It's a good time to turn off unneeded lights and appliances.",
    "If your A/C is on, switch it off and get some fresh air.",
    "If it's summer, adjust your A/C to 78F or higher."]

action_dirty_emergency_waterheater = [
    "Try showering before bed or very early in the morning.",
    "Electricity consumption can be reduced by efficient techology."]

action_dirty_emergency_home_generic = [
    "What practices could you shift to later in the day?",
    "This is a great time to audit your home energy use.",
    "Turn off unnecessary lights, electronics, and appliances."]

action_unusually_clean_work_generic = [
    "This is an especially clean time to utilize electricity.",
    "What appliances or equipment could you run now instead of later?",
    "This is a fantastic time for electricity-intensive tasks."]

action_unusually_clean_home_ac = [
    "Major appliances and equipment run on a cleaner power grid right now.",
    "This is the best time of day for electricity-intensive tasks like A/C.",
    "If it's hot out, this would be a better time to run the A/C or a fan."]

action_unusually_clean_precool = [
    "What appliances or equipment should run now instead of later?",
    "If it's hot out, this would be a better time to run the A/C or a fan."]

action_unusually_clean_dishwasher = [
    "This is a great time to run the dishwasher.",
    "Major appliances and equipment run on a cleaner power grid right now.",
    "What energy-intensive tasks could you accomplish now rather than later?"]

action_unusually_clean_home_generic = [
    "This is one of the best possible times for electricity-intensive chores.",
    "This is one of the best possible times to do laundry.",
    "What appliances or equipment should you run now instead of later?"]

ne_criterion_dirty = [
    "Dirty {fuel} power is at its peak. This should only last an hour."]
ne_criterion_clean = [
    "Cleaner {fuel} power is at its peak. This should only last an hour."]

ne_action_dirty_daytime = [
    "Turn off unnecessary lights, electronics, and appliances."]
ne_action_dirty_evening = [
    "What energy-intensive practices could you postpone?"]
ne_action_clean = [
    "This is the best time of day for electricity-intensive tasks."]

def ne_message_dirty_daytime(up, fuel):
    c = rand(ne_criterion_dirty)
    a = rand(ne_action_dirty_daytime)
    return Message.use_less(make_msg(c, a, state = up.state, fuel = fuel.lower()))

def ne_message_dirty_evening(up, fuel):
    c = rand(ne_criterion_dirty)
    a = rand(ne_action_dirty_evening)
    return Message.use_less(make_msg(c, a, state = up.state, fuel = fuel.lower()))

def ne_message_clean(up, fuel):
    c = rand(ne_criterion_clean)
    a = rand(ne_action_clean)
    return Message.use_more(make_msg(c, a, state = up.state, fuel = fuel.lower()))

old_msgs = [
    ["WattTime Alert! Your power is now clean %s. Hot out? You can precool your house on clean power! Turn down temp a bit for 30 mins.",
    "WattTime Alert! You're now running on clean %s power. Won't last long! Can you use that clean power now instead of later?",
    "WattTime Alert! Your power is really clean %s right now. Anything you can recharge now to use all that clean energy? Laptop?"],

    ["WattTime Alert! Your power is unusually clean now - %s. Can you avoid wasting that clean power? Great time to do laundry or dishes!",
    "WattTime Alert! You're now running on clean %s power. Won't last long! Can you use that clean power now instead of later?",
    "WattTime Alert! Your power is really clean %s right now. Anything you can recharge now to use all that clean energy? Laptop?"],

    ["WattTime Alert! You're now getting dirty %s power. Help us shut them down, save some power now! Can you turn off your AC for 20 mins?",
    "WattTime Alert! You're now running on %s. Help us shut them down! Think you could dial back the temperature 2 degrees for an hour?",
    "WattTime Alert! Your power is from %s right now. Help us use less of that dirty energy source! Can you turn out an extra light?",
    "WattTime Alert! You're now running on %s. Are you doing anything that uses power right now? Maybe you could take a 15 min break!"],


    ["The marginal fuel is %s, so avoid using electricity if you can!",
    "WattTime Alert! You're now running on %s. Are you doing anything that uses power right now? Maybe you could take a 15 min break!",
    "WattTime Alert! Your power is from %s right now. Help us use less of that dirty energy source! Can you turn out an extra light?",
    "WattTime Alert! Your electricity is dirty dirty %s. That means it's an excellent time to save energy! What could you do differently to avoid using excess electricity in the next two hours?"]]

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

# I believe this message refers to the alpha test and is no longer needed. - Gavin
def account_activated_message(userid, name, phone):
    lines = ["Welcome to Wattime %s," % name,
             "We're excited that you've launched WattTime clean energy notifications! You are now subscribed to SMS notifications that let you know when you can make a immediate impact. We'll send notifications to:",
             "%s" % phone,
             "If you answer a few quick questions at http://watttime.com/profile/%s, we'll send you more relevant messages. You can update your preferences at any time." % userid,
             "To unsubscribe from SMS notifications, click on http://watttime.com/unsubscribe/%s." % phone.replace('-',''),
             "Thanks!",
             "The WattTime Team"
             ]
    return Message.information("\n".join(lines))

def account_inactivated_message(userid, name, phone):
    lines = ["Greetings %s," % name,
             "You are now unsubscribed from WattTime SMS notifications to this phone number:",
             "%s" % phone,
             "We are super sorry to see you go! You can turn SMS notifications on at any time by updating your preferences at http://watttime.com/profile/%s." % userid,
             "Whatever your destination, we hope you keep an eye out for ways to help build today's clean energy economy.",
             "",
             "Good Luck!",
             "The WattTime Team"
             ]
    return Message.information("\n".join(lines))

def invite_message(email, url, name = None):
    lines = ["Hey there {name}!",
            "",
            "Welcome to WattTime!",
            "",
            "We're excited that you're joining us in building a cleaner energy economy.",
            "",
            "Using WattTime is free and easy, and you can make an impact immediately. To begin, visit {url} to set up your notifications."
            "",
            "Thanks!",
            "The WattTime Team"
        ]
    if name is None:
        name = email
    return ("\n".join(lines)).format(name = name, url = url)

def invite_message_unsupported(email, url, name = None):
    lines = ["Hi {name}! Welcome to WattTime!",
            "",
            "We're excited that you're joining us to build a cleaner energy economy.",
            "",
            "Right now, our service is only available in California and New England. But we're growing fast! As soon as we're available in your area, we'll send you a note so you can set up an account if you like.",
            "",
            "Can't wait that long? You could set up your account now if you like! Just visit {url} to get started.",
            "",
            "Have a great day,",
            "The WattTime Team"
        ]
    if name is None:
        name = email
    return ("\n".join(lines)).format(name = name, url = url)

def resend_login_message(name, url):
    lines = ["Hi {name}!",
            "",
            "You can log in to your account at {url}.",
            "",
            "Thanks!",
            "The WattTime Team"]
    return ("\n".join(lines)).format(name = name, url = url)

def morning_forecast_email(name, best_hour, worst_hour):
    lines = ["Good Morning {name}!",
        "",
        "Today's clean power peak for California arrives at {best}, while the dirtiest electricity is at {worst}.",
        "",
        "It takes a while for cleaner energy to get going during the day, and we use a lot of energy in the morning just to get our day started. In general, the late afternoon, evening, and overnight periods are the best times for clean electricity. What practices could you shift?",
        "",
        "California's clean energy forecast is always available at http://watttime.com/status",
        "",
        "Your friends at WattTime"]
    return ("\n".join(lines)).format(name = name, best = best_hour, worst=worst_hour)

def morning_forecast_email_first(name, best_hour, worst_hour):
    lines = ["Good morning {name}!",
        "",
        "Welcome to the WattTime morning forecast! Today's clean power peak for California arrives at {best}, while the dirtiest electricity is at {worst}. Do you normally perform any energy-intensive practices at {worst}? What could you easily shift to later in the day?",
        "",
        "You can always see the daily clean energy outlook for California or other regions at http://watttime.com/status (updated hourly)",
        "",
        "Questions? Feedback? Write us at this email address or at the website.",
        "",
        "-The WattTime Team"]
    return ("\n".join(lines)).format(name = name, best = best_hour, worst = worst_hour)
