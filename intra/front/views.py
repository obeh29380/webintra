import requests
from logging import getLogger
from django.db.models import Max
from django.utils.timezone import make_aware
from django.db.models import Min
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from . import forms
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.shortcuts import render
import calendar
import datetime
from .consts import MAP_WEEKDAY, MAP_APPROVAL_STATUS, MAP_APPROVAL_STATUS_CODE
from .common import workStatus, nvl, get_d_h_m_s, second2time
from .models import Attendance, WorkStatus, UserSetting, Approval, \
    Approval_route, Approval_format, Approval_format_route, Board, \
    Chat


logger = getLogger(__name__)


def register_attendance_month(userid, year, month):

    dayCnt = calendar.monthrange(year, month)[1]

    for i in range(dayCnt):

        date = make_aware(datetime.datetime(year, month, i+1))
        work_status = workStatus(date, userid)
        if work_status['name']:
            sysmemo = '★' + work_status['name']
        else:
            sysmemo = ''

        b = Attendance(
            userid=userid,
            date=date,
            work_status=work_status['status'],
            work_start=date,
            work_end=date,
            sysmemo=sysmemo
        )
        b.save()


class TopView(TemplateView):
    template_name = "front/top.html"


def exec_ajax(request):
    if request.method == 'GET':  # GETの処理
        param1 = request.GET.get("param1")  # GETパラメータ1
        param2 = request.GET.get("param2")  # GETパラメータ2
        param3 = request.GET.get("param3")  # GETパラメータ3
        return HttpResponse(param1 + param2 + param3)
    elif request.method == 'POST':  # POSTの処理
        data1 = request.POST.get("input_data")  # POSTで渡された値
        return HttpResponse(data1)


class ChatInfo(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.template_name = 'front/chat_main.html'

    def get(self, request, *args, **kwargs):
        params = {"message": "",
                  }
        return render(request, self.template_name, params)

    def post(self, request, *args, **kwargs):
        data1 = request.POST.get("param1")
        return HttpResponse(data1)


class ChatRoom(View):

    def get(self, request, room_id, *args, **kwargs):

        chat = Chat.objects.filter(
            room_id=room_id).order_by('created_datetime')

        params = {"message": "ApprovalView:Get処理",
                  "page_home": 1,
                  "room_id": room_id,
                  "data": chat
                  }
        return render(request, "front/chat_room.html", params)

    def post(self, request, room_id, *args, **kwargs):
        room_id = request.POST.get("room_id")
        chat = Chat(
            author_id=request.user,
            room_id=room_id,
            text=request.POST.get("text"),
        )
        chat.save()

        call_back = reverse_lazy(
            'front:chat_room', kwargs={"room_id": room_id})
        return HttpResponseRedirect(call_back)  # リダイレクト


class HomeView(LoginRequiredMixin, TemplateView):

    def __init__(self):
        super().__init__()
        self.template_name = 'front/home.html'

    def get(self, request):

        # URLの設定
        url = 'https://api.openweathermap.org/data/2.5/weather'
        # パラメータの設定
        param = {
            "content-type": "application/json",
            "lat": 34.587411,
            "lon": 133.874795,
            "appid": "7c4204c0eb11890647979d8f2005f71a"}

        # Responseオブジェクトの生成
        res = requests.get(url, params=param)
        data = res.json()

        params = {"message": "",
                  'weather': data
                  }

        return render(request, self.template_name, params)


class ApprovalView(View):

    def __init__(self):
        super().__init__()
        self.template_name = 'front/approval.html'

    def get(self, request):

        field = Approval._meta._get_fields()

        # 未完了の決裁
        data = Approval.objects.filter(userid=request.user, status__lt=8)

        approval = {}
        for obj in data:

            q = Approval_route.objects.filter(approval_id=obj.id)
            status = MAP_APPROVAL_STATUS[obj.status]

            approval[obj.id] = {'approval': obj,
                                'status': status,
                                'route': q,
                                }

        # 完了済の決裁
        data_complete = Approval.objects.filter(status__gte=8)
        approval_complete = {}
        for obj in data_complete:

            q = Approval_route.objects.filter(approval_id=obj.id)
            status = MAP_APPROVAL_STATUS[obj.status]

            approval_complete[obj.id] = {'approval': obj,
                                         'status': status,
                                         'route': q,
                                         }

        # 決裁ルートに自身がいて、かつ自身の決裁待ちであるデータを抽出
        q = Approval_route.objects.filter(userid=request.user, status=2)
        need_check = {}
        for obj in q:
            need_check[obj.approval_id] = Approval.objects.get(
                id=obj.approval_id)

        params = {'message': '一覧',
                  'data': data,
                  'counter': (1, 2, 3, 4, 5),
                  'field': field,
                  'user': request.user,
                  'approval': approval,
                  'approval_complete': approval_complete,
                  'page_approval': 1,
                  'need_check': need_check,
                  }

        return render(request, self.template_name, params)


class NewApprovalView(View):

    '''新規決裁画面用'''
    success_url = reverse_lazy('front:approval')

    def get(self, request, id, *args, **kwargs):

        if id != 0:
            data = Approval_format.objects.get(id=id)
            format_name = data.title
            route = Approval_format_route.objects.filter(format_id=id)

            upd = True
        else:
            data = ''
            format_name = ''
            route = ''
            upd = False

        title = '新規決裁'

        format_all = Approval_format.objects.all()
        user_all = User.objects.all()

        params = {'title': title,
                  'data': data,
                  'counter': (1, 2, 3, 4, 5),
                  'user': request.user,
                  'page_approval': 1,
                  'format_all': format_all,
                  'format_name': format_name,
                  'route': route,
                  'upd': upd,
                  'user_all': user_all,
                  }
        return render(request, "front/approval_detail.html", params)

    def post(self, request, id, *args, **kwargs):

        b = Approval(
            userid=request.user,
            title=request.POST['title'],
            detail=request.POST['detail'],
        )
        b.save()

        id = Approval.objects.all().order_by("-id")[0].id

        # route
        s = request.POST['route']
        route = s.split(',')

        for cnt, username in enumerate(route):

            if cnt == 0:
                status = MAP_APPROVAL_STATUS_CODE['MYTURN']
            else:
                status = MAP_APPROVAL_STATUS_CODE['WAITMYTURN']

            b = Approval_route(
                approval_id=id,
                userid=username,
                status=status,
            )
            b.save()

        return HttpResponseRedirect(self.success_url)  # リダイレクト


class Approval_checkView(View):

    '''決裁承認画面'''
    success_url = reverse_lazy('front:approval')

    def get(self, request, id, *args, **kwargs):

        data = Approval.objects.get(id=id)
        format_name = data.title
        route = Approval_route.objects.filter(approval_id=id)

        title = '決裁承認'

        params = {'title': title,
                  'data': data,
                  'user': request.user,
                  'page_approval': 1,
                  'format_name': format_name,
                  'route': route,
                  'check': 1
                  }
        return render(request, "front/approval_detail.html", params)

    def post(self, request, id, *args, **kwargs):

        route_tmp = Approval_route.objects.filter(
            approval_id=id, status=MAP_APPROVAL_STATUS_CODE['MYTURN'], userid=request.user).aggregate(Min('id'))
        route = Approval_route.objects.get(id=route_tmp['id__min'])

        if 'btn_approve' in request.POST:
            status = MAP_APPROVAL_STATUS_CODE['APPROVED']
        elif 'btn_reject' in request.POST:
            status = MAP_APPROVAL_STATUS_CODE['REJECTED']
        else:
            status = MAP_APPROVAL_STATUS_CODE['WAITMYTURN']

        if status != 0:
            route.status = status
            route.approved_date = datetime.date.today()
            route.save()

            # 最終か？
            next_route_tmp = Approval_route.objects.filter(id=route.id + 1)
            if next_route_tmp.count() == 0 or \
                    status == MAP_APPROVAL_STATUS_CODE['REJECTED']:

                # 最終か却下された場合、決裁ステータスを更新する
                approval = Approval.objects.get(id=id)
                approval.status = status
                approval.save()
            else:

                # 次の人の承認ステータスも承認待ちに更新
                next_route = Approval_route.objects.get(id=route.id + 1)
                next_route.status = MAP_APPROVAL_STATUS_CODE['MYTURN']
                next_route.save()

        return HttpResponseRedirect(self.success_url)  # リダイレクト


class BoardView(View):
    def get(self, request, *args, **kwargs):

        data = Board.objects.all()

        params = {'title': '掲示板一覧',
                  'data': data,
                  'user': request.user,
                  'page_board': 1,
                  }

        return render(request, "front/board_menu.html", params)

    def post(self, request):
        params = {"message": "BoardView:Post処理",
                  "page_board": 1,
                  }
        return render(request, "front/board_menu.html", params)


class Board_detailView(View):

    def get(self, request, *args, **kwargs):

        id = kwargs['id']
        data = None
        new = False
        if not id == 0:
            data = Board.objects.get(id=id)
        else:
            new = True

        params = {
            'title': '掲示板詳細',
            'data': data,
            'user': request.user,
            'page_board': 1,
            'new': new
        }

        return render(request, "front/board_detail.html", params)

    def post(self, request, *args, **kwargs):

        id = kwargs['id']
        if id == 0:
            b = Board(
                author_id=request.user,
                created_datetime=make_aware(datetime.datetime.now()),
                title=request.POST.get('title', 'No Title'),
                detail=request.POST.get('detail', None),
            )
            b.save()

            id = Board.objects.all().aggregate(Max('id'))

        else:
            data = Board.objects.get(id=id)

            data.title = request.POST.get('title', 'No Title')
            data.detail = request.POST.get('detail', None)

            try:
                data.save()
            except Exception as e:
                raise e

        # success_url = reverse_lazy('front:board')
        # return HttpResponseRedirect(reverse_lazy('front:board',args=(id)))
        # return HttpResponseRedirect(success_url) # リダイレクト

        success_url = reverse_lazy('front:board_detail', kwargs=({'id': id}))
        # URLにパラメータを付与する
        return HttpResponseRedirect(success_url)


class ToolsView(View):
    def get(self, request):
        params = {"page_tools": 1,
                  }
        return render(request, "front/tools.html", params)

    def post(self, request):
        params = {"message": "SettingView:Post処理",
                  "page_tools": 1,
                  }
        return render(request, "front/tools.html", params)


class AttendView(View):

    def get(self, request, *args, **kwargs):

        now = make_aware(datetime.datetime.now())

        month = int(request.GET.get("month", default=now.month))
        year = int(request.GET.get("year", default=now.year))

        dayCnt = calendar.monthrange(year, month)[1]

        dayf = str(year)+"-"+str(month)+"-"+"01"
        dayl = str(year)+"-"+str(month)+"-"+str(dayCnt)

        q = Attendance.objects.filter(
            userid=request.user, date__year=year, date__month=month)

        if q.count() == 0:
            #  未登録の年月は、ひと月分まとめて登録する。
            register_attendance_month(request.user, year, month)

        d = Attendance.objects.filter(
            userid=request.user, date__gte=dayf, date__lte=dayl)
        userinfo = UserSetting.objects.get(userid=request.user)
        worktime = userinfo.day_worktime.hour

        day = 0
        workday_month = 0
        attend = {}
        work_time_total_t = datetime.timedelta(hours=0, minutes=0)
        work_day_total = 0
        extra_hour_total_t = datetime.timedelta(hours=0, minutes=0)

        for obj in d:
            day += 1
            weekday = MAP_WEEKDAY[obj.date.weekday()]

            work_time_total_t += datetime.timedelta(
                hours=obj.work_time.hour, minutes=obj.work_time.minute)
            extra_hour_total_t += datetime.timedelta(
                hours=obj.work_overtime.hour, minutes=obj.work_overtime.minute)
            if obj.work_time != datetime.time(0, 0, 0):
                work_day_total += 1

            work_status = workStatus(obj.date, request.user)
            q = WorkStatus.objects.filter(
                id=work_status['status'], holiday=True).count()

            if q > 0:
                holiday = 1
            else:
                holiday = 0
                workday_month += 1

            attend[day] = {'attend': obj,
                           'weekday': weekday,
                           'holiday': holiday,
                           }

        tmp = WorkStatus.objects.filter(use=True)
        ws = list(tmp.values())

        d, h, m, s = get_d_h_m_s(work_time_total_t)
        work_time_total = {'hour': h+d*24,
                           'minute': datetime.time(0, m)}

        d, h, m, s = get_d_h_m_s(extra_hour_total_t)
        extra_hour_total = {'hour': h+d*24,
                            'minute': datetime.time(0, m)}

        params = {
            'request': request,
            'year': year,
            'month': month,
            'workstatus': ws,
            'attend': attend,
            'workday_month': workday_month,
            'workhour_month': workday_month*worktime,
            'workhour_day': worktime,
            'work_time_total': work_time_total,
            'work_day_total': work_day_total,
            'extra_hour_total': extra_hour_total,
            'work_time': obj.work_time,
            'url_base': f'{request.scheme}://{request.get_host()}{request.path}'
        }

        url = "front/attend.html"
        return render(request, url, params)

    def post(self, request, *args, **kwargs):
        """出勤簿の登録処理。指定された月の分を一括で登録する。
            TODO まだ日単位のものをコピペしただけ。処理が長くなるので、別途管理者用コマンドにした方が良いかなー
        """
        year = int(kwargs['year'])
        month = int(kwargs['month'])
        success_url = reverse_lazy('front:attend', args=(year, month))

        # logger.debug(f'attend update day={kwargs["day"]}')

        # q = Attendance.objects.filter(
        #     userid=request.user, date__year=year, date__month=month)

        # if q.count() == 0:
        #     # 未登録の年月は、ひと月分まとめて登録する。
        #     register_attendance_month(request.user, year, month)

        # # 更新処理
        # # TODO 時間の計算は日を跨いだ労働は未考慮。
        # # 跨いだ分は翌日分に登録する必要がある。
        # # その場合、一旦帰宅後、朝通常出勤した場合は、１日に二回出勤したことになるが、これも未対応。
        # # 現状は、間の時間も含めて、休憩として登録するしかない。

        # st = datetime.datetime.strptime(
        #     request.POST["work_start"], '%H:%M')

        # ed = datetime.datetime.strptime(
        #     request.POST["work_end"], '%H:%M')

        # workoff_v = datetime.datetime.strptime(
        #     nvl(request.POST["work_off"], "00:00"), '%H:%M')

        # workoff = datetime.timedelta(
        #     hours=workoff_v.hour, minutes=workoff_v.minute)

        # # 規定労働時間
        # reg_work_time = UserSetting.objects.get(userid=request.user)

        # worktime_b = ed-st-workoff
        # worktime_m, worktime_s = divmod(worktime_b.seconds, 60)
        # worktime_h, worktime_m = divmod(worktime_m, 60)
        # worktime = datetime.time(hour=worktime_h, minute=worktime_m, second=0)

        # if worktime < reg_work_time.day_worktime:
        #     overtime = "00:00"
        # else:
        #     overtime = datetime.timedelta(hours=worktime.hour, minutes=worktime.minute) - datetime.timedelta(
        #         hours=reg_work_time.day_worktime.hour, minutes=reg_work_time.day_worktime.minute)
        #     y, m, d = second2time(overtime.seconds)
        #     overtime = datetime.time(
        #         hour=y, minute=m, second=d)

        # attendance = Attendance.objects.get(userid=request.user, date=date)
        # attendance.work_status = request.POST["work_status"]
        # attendance.work_detail = request.POST["work_detail"]

        # work_start_h, work_start_m = request.POST["work_start"].split(':')
        # attendance.work_start = make_aware(
        #     datetime.datetime(year, month, day, hour=int(
        #         work_start_h), minute=int(work_start_m), second=0, microsecond=0)
        # )
        # work_end_h, work_end_m = request.POST["work_end"].split(':')
        # attendance.work_end = make_aware(datetime.datetime(year, month, day, hour=int(
        #     work_end_h), minute=int(work_end_m), second=0, microsecond=0))
        # attendance.work_off = nvl(request.POST["work_off"], "00:00")
        # attendance.work_time = worktime
        # attendance.work_overtime = overtime
        # attendance.carfare = request.POST["carfare"]
        # attendance.memo = request.POST["memo"]

        # attendance.save()

        return HttpResponseRedirect(success_url)  # リダイレクト


class AttendRegisterDay(View):

    """attend/<int:year>/<int:month>/<int:day>" に対応する処理

    """

    def post(self, request, *args, **kwargs):
        """出勤簿の更新処理。URLに指定された日の出勤情報を更新する。

        """

        year = int(kwargs['year'])
        month = int(kwargs['month'])
        day = int(kwargs['day'])
        date = str(year)+"-"+str(month)+"-"+str(day)
        success_url = reverse_lazy('front:attend', args=(year, month))

        logger.debug(f'attend update day={kwargs["day"]}')

        q = Attendance.objects.filter(
            userid=request.user, date__year=year, date__month=month)

        if q.count() == 0:
            # 未登録の年月は、ひと月分まとめて登録する。
            register_attendance_month(request.user, year, month)

        # 更新処理
        # TODO 時間の計算は日を跨いだ労働は未考慮。
        # 跨いだ分は翌日分に登録する必要がある。
        # その場合、一旦帰宅後、朝通常出勤した場合は、１日に二回出勤したことになるが、これも未対応。
        # 現状は、間の時間も含めて、休憩として登録するしかない。

        st = datetime.datetime.strptime(
            request.POST["work_start"], '%H:%M')

        ed = datetime.datetime.strptime(
            request.POST["work_end"], '%H:%M')

        workoff_v = datetime.datetime.strptime(
            nvl(request.POST["work_off"], "00:00"), '%H:%M')

        workoff = datetime.timedelta(
            hours=workoff_v.hour, minutes=workoff_v.minute)

        # 規定労働時間
        reg_work_time = UserSetting.objects.get(userid=request.user)

        worktime_b = ed-st-workoff
        worktime_m, worktime_s = divmod(worktime_b.seconds, 60)
        worktime_h, worktime_m = divmod(worktime_m, 60)
        worktime = datetime.time(hour=worktime_h, minute=worktime_m, second=0)

        if worktime < reg_work_time.day_worktime:
            overtime = "00:00"
        else:
            overtime = datetime.timedelta(hours=worktime.hour, minutes=worktime.minute) - datetime.timedelta(
                hours=reg_work_time.day_worktime.hour, minutes=reg_work_time.day_worktime.minute)
            y, m, d = second2time(overtime.seconds)
            overtime = datetime.time(
                hour=y, minute=m, second=d)

        attendance = Attendance.objects.get(userid=request.user, date=date)
        attendance.work_status = request.POST["work_status"]
        attendance.work_detail = request.POST["work_detail"]

        work_start_h, work_start_m = request.POST["work_start"].split(':')
        attendance.work_start = make_aware(
            datetime.datetime(year, month, day, hour=int(
                work_start_h), minute=int(work_start_m), second=0, microsecond=0)
        )
        work_end_h, work_end_m = request.POST["work_end"].split(':')
        attendance.work_end = make_aware(datetime.datetime(year, month, day, hour=int(
            work_end_h), minute=int(work_end_m), second=0, microsecond=0))
        attendance.work_off = nvl(request.POST["work_off"], "00:00")
        attendance.work_time = worktime
        attendance.work_overtime = overtime
        attendance.carfare = request.POST["carfare"]
        attendance.memo = request.POST["memo"]

        attendance.save()

        return HttpResponseRedirect(success_url)  # リダイレクト


class AttendDelete(View):

    """attend/delete" に対応する処理
        パラメータで日付の指定が無ければ、指定年月分を削除、
        日付の指定があれば、その日の分のみ削除する。
    """

    def post(self, request, *args, **kwargs):
        """出勤簿の更新処理。

        """

        success_url = reverse_lazy('front:attend')
        year = int(request.POST.get('year'))
        month = int(request.POST.get('month'))
        day = int(request.POST.get('day', default=0))

        if day == 0:
            Attendance.objects.filter(
                userid=request.user,
                date__year=year,
                date__month=month
            ).delete()

        else:
            Attendance.objects.filter(
                userid=request.user,
                date__year=year,
                date__month=month,
                date__day=day
            ).delete()

        return HttpResponseRedirect(success_url)  # リダイレクト


class LoginView(LoginView):
    """ログインページ"""
    form_class = forms.LoginForm
    template_name = "front/login.html"


class LogoutView(LogoutView):
    """ログインページ"""
    template_name = "front/home.html"


class signupView(FormView):
    """新規登録ページ"""
    form_class = forms.SignUpForm
    template_name = "front/signup.html"


class signup_Register(CreateView):
    form_class = forms.SignUpForm
    template_name = "front/signup.html"
    success_url = reverse_lazy('front:top')

    def form_valid(self, form):
        user = form.save()  # formの情報を保存
        login(self.request, user)  # 認証
        self.object = user

        b = UserSetting(
            userid=user.username,
        )
        b.save()

        return HttpResponseRedirect(self.get_success_url())  # リダイレクト
