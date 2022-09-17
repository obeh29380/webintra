
import jpholiday
from .consts import MAP_WEEKDAY_K
from .models import UserSetting, Holiday, WorkStatus


def get_work_status_id(status):
    data = WorkStatus.objects.get(name=status)
    return data.id


def workStatus(date, user):

    # ユーザ毎の指定休日（初期値では土日）
    regHoli = UserSetting.objects.get(userid=user)

    q = Holiday.objects.filter(date=date)
    if q.count() > 0:
        for data in q:
            name = data.detail

        work_status = {'status': get_work_status_id('HOLIDAY_COMPANY'),
                       'name': name,
                       }

    elif jpholiday.is_holiday(date):
        work_status = {'status': get_work_status_id('HOLIDAY_COUNTRY'),
                       'name': jpholiday.is_holiday_name(date),
                       }
    else:
        if date.weekday() == MAP_WEEKDAY_K['MON'] and regHoli.mon_is_holiday:
            work_status = {'status': get_work_status_id('HOLIDAY'),
                           'name': None,
                           }
        elif date.weekday() == MAP_WEEKDAY_K['TUE'] and regHoli.tue_is_holiday:
            work_status = {'status': get_work_status_id('HOLIDAY'),
                           'name': None,
                           }
        elif date.weekday() == MAP_WEEKDAY_K['WED'] and regHoli.wed_is_holiday:
            work_status = {'status': get_work_status_id('HOLIDAY'),
                           'name': None,
                           }
        elif date.weekday() == MAP_WEEKDAY_K['THU'] and regHoli.thu_is_holiday:
            work_status = {'status': get_work_status_id('HOLIDAY'),
                           'name': None,
                           }
        elif date.weekday() == MAP_WEEKDAY_K['FRI'] and regHoli.fri_is_holiday:
            work_status = {'status': get_work_status_id('HOLIDAY'),
                           'name': None,
                           }
        elif date.weekday() == MAP_WEEKDAY_K['SAT'] and regHoli.sat_is_holiday:
            work_status = {'status': get_work_status_id('HOLIDAY'),
                           'name': None,
                           }
        elif date.weekday() == MAP_WEEKDAY_K['SUN'] and regHoli.sun_is_holiday:
            work_status = {'status': get_work_status_id('HOLIDAY'),
                           'name': None,
                           }
        else:
            work_status = {'status': get_work_status_id('WORK'),
                           'name': None,
                           }

    return work_status


def nvl(v, r):
    if v is None:
        return r
    elif v == "":
        return r
    else:
        return v


def get_keys_from_value(d, val):
    return [k for k, v in d.items() if v == val]


def get_d_h_m_s(td):
    d = td.days
    m, s = divmod(td.seconds, 60)
    h, m = divmod(m, 60)
    return d, h, m, s


def get_ymd(date):
    return date.year, date.month, date.date


def second2time(second):

    if second <= 0:
        return 0, 0, 0

    hour = int(second/3600)
    minute = int((second - hour*3600)/60)
    second = second % 60

    return hour, minute, second
