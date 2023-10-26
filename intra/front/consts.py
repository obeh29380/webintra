from enum import (
    Enum,
    auto
)


class WEEKDAY(Enum):
    MON = 0
    TUE = auto()
    WED = auto()
    THU = auto()
    FRI = auto()
    SAT = auto()
    SUN = auto()

class MAP_APPROVAL_STATUS_CODE(Enum):
    WAITMYTURN = 0
    MYTURN = 2
    CANCEL = 3
    PASSED = 7
    REJECTED = 8
    APPROVED = 9

WEEKDAYS = ['月', '火', '水', '木', '金', '土', '日']

MAP_DAY_STATUS = {"WORK": "01",
                  "HOLIDAY": "11",
                  "HOLIDAY_COUNTRY": "12",
                  "HOLIDAY_COMPANY": "13",
                  "HOLIDAY_SALARY": "14",
                  }

MAP_APPROVAL_STATUS = {0: "未承認",
                       2: "要承認",
                       3: "取下",
                       7: "パス",
                       8: "却下",
                       9: "承認",
                       }
