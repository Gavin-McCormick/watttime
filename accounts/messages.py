# content of text messages
# the %s symbol is replaced by the variable that appears after the % symbol at the end

def use_central_ac_message(marginal_fuel):
    return "The marginal fuel is %s, so it's a great time to switch on your AC!" % marginal_fuel

def use_message(marginal_fuel):
    return "The marginal fuel is %s, so it's a great time to use energy!" % marginal_fuel

def dont_use_central_ac_message(marginal_fuel):
    return "The marginal fuel is %s, so avoid using your AC if you can!" % marginal_fuel

def dont_use_message(marginal_fuel):
    return "The marginal fuel is %s, so avoid using electricity if you can!" % marginal_fuel

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
             "To personalize this service and increase your impact, just answer a few quick questions at http://wattTime.herokuapp.com/profile/%s." % userid,
             "To unsubscribe from our email list, please reply to this email with the message 'unsubscribe'.",
             "Cheers,",
             "the team at WattTime"
             ]
    return "\n".join(lines)

def account_unactivated_message():
    return ""
