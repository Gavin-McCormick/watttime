# content of text messages
# the %s symbol is replaced by the variable that appears after the % symbol at the end
import random
#TODO seasonal messaging: winter/summer/autumn/spring by region

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

action_dirtiest_home_generic = [
    "What practices could you put off to a cleaner time?",
    "If it's summer, you could adjust your air conditioning thermostat to 78° or higher. Use a fan when possible.",
    "It's a good time to unplug vampire electronics like phone chargers. Only plug them in at night if possible.", 
    "Create a bigger impact and postpone any major appliance and equipment use until after 4 p.m."]

action_dirtiest_home_ac = [
    "If it's summer, you could adjust your air conditioning thermostat to 78° or higher. Use a fan when possible.",
    "If your A/C is on right now, switch it off and get some fresh air.",
    "It's a great time to turn off all unnecessary lights, electronics, and appliances."]

action_dirtiest_work_generic = [
    "What practices could you shift to later in the day when solar and wind power are at their peak?",
    "If it's summer and you're at work, set your air conditioning thermostat to 78° or higher. You might need to adjust your clothing and activity to maintain comfort.",
    "Making copies? Why not save all that for later this afternoon when our electricity is cleaner?"]

action_dirtiest_work_ac = [
    "Dial back your A/C to 78° or higher. Lowering shades, wearing appropriate clothing, and modulating your activity will save you money.",
    "What energy-intensive tasks could you schedule to run overnight?",
    "Take a break from using electricity if possible. You could go chat with someone instead or go for a short walk.", 
    "Decontaminate the power grid. Can some of your electricity consumption be rescheduled?"]

def ca_message_dirty(up):
    # TODO choose between home vs. work appropriately.
    c = rand(criterion_dirtiest)
    a = rand(action_dirtiest_home_generic)
    return Message.use_less(make_msg(c, a, state = 'CA'))

criterion_cleanest = [
    "Eureka! This is today's clean power peak!",
    "This is a fantastic time to perform those electricity-intensive tasks you've been putting off."]

action_cleanest_dishwasher = [
    "Some of the biggest reductions in electricity comsumption come from more efficient techology.",
    "If your dishwasher is already loaded, now would be a great time to run it.",
    "Running a dishwasher late at night is the best time for clean dishes and cleaner electricity."]

action_cleanest_home_ac = [
    "This is the best time of day for electricity-intensive tasks.",
    "Major appliances and equipment run on a cleaner power grid right now.",
    "Vacuming keeps your home clean. If you do around {best}, it helps keep {state} clean too."]

action_cleanest_home_generic = [
    "Right now the grid is a clean as it gets. What electricity-based chores could you plan to do at this time of day?",
    "If your washing requires electricity, this is the best time for maximum cleanliness.",
    "Solar and wind power are decontaminating the grid. What appliances or equipment could you run now instead of later?"]

def ca_message_clean(up):
    # TODO choose actions appropriately
    c = rand(criterion_cleanest)
    a = rand(action_cleanest_home_generic)
    return Message.use_more(make_msg(c, a, state = 'CA'))

criterion_unusually_dirty = [
    "Right now in {state}, dirty electricity is contaminating the power grid.",
    "This is as dirty as our electricity will get today."]

criterion_unusually_clean = [
    "{state} electricity is hitting a rare clean power peak right now.",
    "This is an especially clean time to utilize electricity."]

criterion_dirty_emergency = [
    "Right now the {state} electricity grid is about as dirty as it ever gets.",
    "This is as contaminated as electricity ever gets in {state}."]

action_unusually_dirty_work_ac = [
    "Dial back your A/C to 78° or higher. Lowering shades, wearing appropriate clothing, and modulating your activity will save you money.",
    "Take a break from using electricity if possible. You could go chat with someone instead or go for a short walk.",
    "Decontaminate the power grid. Can some of your electricity consumption be rescheduled?"]

action_unusually_dirty_work_generic = [
    "What energy-intensive jobs could you schedule to run overnight?",
    "What practices could you shift to later in the day when solar and wind power are at their peak?",
    "Create a bigger impact and postpone any major appliance and equipment use until after 4 p.m."]

action_unusually_dirty_home_ac = [
    "Dial back your A/C to 78° or higher. Lowering shades, wearing appropriate clothing, and modulating your activity will save you money.",
    "It's a great time to turn off all unnecessary lights, electronics, and appliances.",
    "Create a bigger impact and postpone any major appliance and equipment use until after 4 p.m."]

action_unusually_dirty_home_generic = [
    "It's a great time to turn off all unnecessary lights, electronics, and appliances.",
    "Create a bigger impact and postpone any major appliance and equipment use until after 4 p.m.",
    "What practices could you shift to later in the day when solar and wind power are at their peak?"]

action_dirty_emergency_work_ac = [
    "Decontaminate the power grid. Reschedule your appliance and equipment use until later in the day.",
    "Dial back your A/C to 78° or higher. Dirty electricity is peaking right now.",
    "If your A/C is on right now, switch it off and get some fresh air."]

action_dirty_emergency_work_generic = [
    "What practices could you shift to later in the day when solar and wind power are at their peak?",
    "It's a good time to unplug vampire electronics like phone chargers. Only plug them in at night if possible.",
    "Create a bigger impact and postpone any major appliance and equipment use until after 4 p.m."]

action_dirty_emergency_pool = [
    "Pool water pumps use a LOT of energy. Only run it occasionally, or put it on a timer so it runs later in the day.",
    "What practices could you shift to later in the day when solar and wind power are at their peak?",
    "Create a bigger impact and postpone any major appliance and equipment use until after 4 p.m."]

action_dirty_emergency_home_ac = [
    "If it's summer, adjust your air conditioning thermostat to 78° or higher. Use a fan when possible.",
    "If your A/C is on right now, switch it off and get some fresh air.",
    "It's a great time to turn off all unnecessary lights, electronics, and appliances."]

action_dirty_emergency_waterheater = [
    "Some of the biggest reductions in electricity comsumption come from more efficient techology.",
    "Hot water requires lots of power. Showering before bed or very early in the morning improves its clean impact."]

action_dirty_emergency_home_generic = [
    "It's a great time to turn off all unnecessary lights, electronics, and appliances.",
    "If your A/C is on right now, switch it off. It's adding to a really dirty power grid.",
    "What practices could you shift to later in the day when solar and wind power are at their peak?"]

action_unusually_clean_work_generic = [
    "Is there anything you could turn on now rather than later?",
    "Great time to, say, recharge any electronics."]

action_unusually_clean_home_ac = [
    "Good time to, say, recharge electronics or turn up the A/C if hot.",
    "Anything you could run now instead of later? Laundry? Oven?",
    "Hot? Maybe you could turn up A/C, precool while you're on clean power?"]

action_unusually_clean_precool = [
    "If it's hot out, this would be a better time to run the A/C or a fan.",
    "Solar and wind are cleaning out the electricity grid. A/C won't have as much a negative impact right now."]

action_unusually_clean_dishwasher = [
    "The electricity grid is unusually clean. This is a great time to run the dishwasher.",
    "Solar and wind are at their peak. Major appliances and equipment run on a cleaner power grid right now.",
    "Are there any energy-intensive tasks you could accomplish now rather than later?"]

action_unusually_clean_home_generic = [
    "Solar and wind power are decontaminating the grid. What appliances or equipment could you run now instead of later?",
    "If your washing requires electricity, this is the best time for maximum power grid cleanliness.",
    "This is one of the best possible times to do laundry or electricity-intensive chores."]

ne_criterion_dirty = [
    "Dirty {fuel} power is at it's peak. This should only last an hour."]
ne_criterion_clean = [
    "Cleaner {fuel} power is at its peak. This should only last an hour."]

ne_action_dirty_daytime = [
    "It's a great time to turn off all unnecessary lights, electronics, and appliances."]
ne_action_dirty_evening = [
    "What energy-intensive practices could you postpone?"]
ne_action_clean = [
    "This is the best time of day for electricity-intensive tasks."]

def ne_message_dirty_daytime(up, fuel):
    c = rand(ne_criterion_dirty)
    a = rand(ne_action_dirty_daytime)
    return Message.use_less(make_msg(c, a, state = up.state, fuel = fuel))

def ne_message_dirty_evening(up, fuel):
    c = rand(ne_criterion_dirty)
    a = rand(ne_action_dirty_evening)
    return Message.use_less(make_msg(c, a, state = up.state, fuel = fuel))

def ne_message_clean(up, fuel):
    c = rand(ne_criterion_clean)
    a = rand(ne_action_clean)
    return Message.use_more(make_msg(c, a, state = up.state, fuel = fuel))

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

# I believe this message refers to the alpha test and is no longer needed. - Gavin
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
        "The WattTime Team"]
    return ("\n".join(lines)).format(name = name)

def morning_forecast_email(name, best_hour, worst_hour):
    lines = ["Good Morning {name}!",
        "",
        "Today's clean power peak for California arrives at {best}, while the dirtiest electricity is at {worst}.",
        "",
        "It takes a while for cleaner energy to get going during the day, and we use a lot of energy in the morning just to get our day started. What practices could you shift to late afternoon that critical in the morning?",
        "",
        "California's clean energy forecast is always available at http://watttime.com/status",
        "",
        "Your Friends at WattTime"]
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
        "–The WattTime Team"]
    return ("\n".join(lines)).format(name = name, best = best_hour, worst = worst_hour)
