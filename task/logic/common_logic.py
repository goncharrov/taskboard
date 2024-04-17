import datetime
import locale

# locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))

def get_start_date(type_of_period, end_date):
    if type_of_period == 'week':
        start_date = end_date - datetime.timedelta(days=7)
    elif type_of_period == 'month':
        start_date = end_date - datetime.timedelta(days=30)
    elif type_of_period == 'quarter':
        start_date = end_date - datetime.timedelta(days=90)
    elif type_of_period == 'year':
        start_date = end_date - datetime.timedelta(days=365)

    return start_date
