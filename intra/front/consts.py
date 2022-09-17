

MAP_WEEKDAY = {0: '月',
               1: '火',
               2: '水',
               3: '木',
               4: '金',
               5: '土',
               6: '日',
               }

MAP_WEEKDAY_K = {"MON": 0,
                 "TUE": 1,
                 "WED": 2,
                 "THU": 3,
                 "FRI": 4,
                 "SAT": 5,
                 "SUN": 6,
                 }

MAP_DAY_STATUS = {"WORK": "01",
                  "HOLIDAY": "11",
                  "HOLIDAY_COUNTRY": "12",
                  "HOLIDAY_COMPANY": "13",
                  "HOLIDAY_SALARY": "14",
                  }

MAP_HOLIDAY = (MAP_DAY_STATUS["HOLIDAY"],
               MAP_DAY_STATUS["HOLIDAY_COUNTRY"],
               MAP_DAY_STATUS["HOLIDAY_COMPANY"],
               )

MAP_APPROVAL_STATUS = {0: "未承認",
                       2: "要承認",
                       7: "パス",
                       8: "却下",
                       9: "承認",
                       }

MAP_APPROVAL_STATUS_CODE = {'WAITMYTURN': 0,
                            'MYTURN': 2,
                            'PASSED': 7,
                            'REJECTED': 8,
                            'APPROVED': 9,
                            }
