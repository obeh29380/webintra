import json

import jpholiday

from .consts import WEEKDAY
from .models import (
    UserSetting,
    Holiday,
    WorkStatus
)

FILE_WORK_STATUS = '/code/data/work_status.json'
with open(FILE_WORK_STATUS, 'r') as f:
    work_status_default = json.load(f)


def get_work_status_id(status):
    data = WorkStatus.objects.get_or_none(name=status)

    if data:
        return data.id

    for i, work_status in enumerate(work_status_default):
        if work_status["name"] == status:
            return i


def get_workStatus(date, user):

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
        if date.weekday() == WEEKDAY.MON and regHoli.mon_is_holiday:
            work_status = {'status': get_work_status_id('HOLIDAY'),
                           'name': None,
                           }
        elif date.weekday() == WEEKDAY.TUE and regHoli.tue_is_holiday:
            work_status = {'status': get_work_status_id('HOLIDAY'),
                           'name': None,
                           }
        elif date.weekday() == WEEKDAY.WED and regHoli.wed_is_holiday:
            work_status = {'status': get_work_status_id('HOLIDAY'),
                           'name': None,
                           }
        elif date.weekday() == WEEKDAY.THU and regHoli.thu_is_holiday:
            work_status = {'status': get_work_status_id('HOLIDAY'),
                           'name': None,
                           }
        elif date.weekday() == WEEKDAY.FRI and regHoli.fri_is_holiday:
            work_status = {'status': get_work_status_id('HOLIDAY'),
                           'name': None,
                           }
        elif date.weekday() == WEEKDAY.SAT and regHoli.sat_is_holiday:
            work_status = {'status': get_work_status_id('HOLIDAY'),
                           'name': None,
                           }
        elif date.weekday() == WEEKDAY.SUN and regHoli.sun_is_holiday:
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
