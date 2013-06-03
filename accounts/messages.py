# content of text messages
# the %s symbol is replaced by the variable that appears after the % symbol at the end

def use_central_ac_message(marginal_fuel):
    return "The marginal fuel is %s, so it's a grea time to switch on your AC!" % marginal_fuel

def use_message(marginal_fuel):
    return "The marginal fuel is %s, so it's a great time to use energy!" % marginal_fuel

def dont_use_central_ac_message(marginal_fuel):
    return "The marginal fuel is %s, so avoid using your AC if you can!" % marginal_fuel

def dont_use_message(marginal_fuel):
    return "The marginal fuel is %s, so avoid using electricity if you can!" % marginal_fuel
