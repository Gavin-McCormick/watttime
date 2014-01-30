from windfriendly.balancing_authorities import BA_PARSERS
from .celery import app

@app.task
def update(ba_name='bpa'):
    try:
        result = BA_PARSERS[ba_name.upper()]().update()
    except Exception as e:
        result = "Update failed with error: %s" % e
    return result
    