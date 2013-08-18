iso = 'isone'

# temps = [(good_temp, .1), (neutral_temp, .9), (bad_temp, 0)]

# temps = [(72, .45), (74, .45), (80, .1)]

temps = [(70 + 0.1 * x, .1) for x in range(100)]

make_config_public = True
