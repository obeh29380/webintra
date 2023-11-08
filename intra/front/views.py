import calendar
import datetime
import json
from logging import getLogger
from typing import Any

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import (
    Max,
)
from django.forms.models import model_to_dict
from django.utils.timezone import make_aware
from django.contrib.auth.models import User
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.contrib.auth import login
from django.contrib.auth.views import (
    LoginView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    View,
    TemplateView
)
from django.views.generic.edit import (
    CreateView,
    FormView
)
from django.shortcuts import render
from django.urls import reverse_lazy

from . import forms
from .common import (
    get_workStatus,
    nvl,
    get_d_h_m_s,
    second2time
)
from .consts import (
    WEEKDAYS,
    MAP_APPROVAL_STATUS,
    APPROVAL_STATUS_CODE
)
from .models import (
    Attendance,
    WorkStatus,
    UserSetting,
    Approval,
    Approval_route,
    Approval_format,
    Approval_format_route,
    Board,
    Board_comment,
)

logger = getLogger(__name__)


def is_admin():
    return True


def register_attendance_month(user_id, year, month):

    dayCnt = calendar.monthrange(year, month)[1]

    for i in range(dayCnt):

        date = make_aware(datetime.datetime(year, month, i+1))
        work_status = get_workStatus(date, user_id)
        if work_status['name']:
            sysmemo = '★' + work_status['name']
        else:
            sysmemo = ''

        user = User.objects.get(id=user_id)

        b = Attendance(
            user=user,
            date=date,
            work_status=work_status['status'],
            work_start=date,
            work_end=date,
            sysmemo=sysmemo
        )
        b.save()

class BaseView(View):

    def _get_url_info(self, request):

        host = request.get_host()
        protocol = request.headers['Referer'].split(':')[0]
        return f'{protocol}://{host}'

    def _is_valid_user(self, user_id):
        """ユーザがログイン認証されているかどうかを判定する
        """
        user = User.objects.filter(id=user_id)
        if user.count() == 0:
            return False
        return user[0].is_authenticated

    def _is_permitted_function(self, user_id, permissions: list):
        """ユーザが指定された機能の権限を持っているかを判定する
        """
        user = User.objects.get(id=user_id)
        return user.get_user_permissions(permissions)

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

class HomeView(LoginRequiredMixin, TemplateView):

    template_name = 'front/home.html'

    def get(self, request):

        params = {"message": "",
                  }

        return render(request, self.template_name, params)


class ApprovalView(BaseView):

    template_name = 'front/approval.html'

    def get(self, request):

        if not self._is_valid_user(request.user.id):
            return render(request, 'front/no_session.html', status=403)

        user = User.objects.get(id=request.user.id)
        field = Approval._meta._get_fields()
        complete_status_min = 5

        # 未完了の決裁
        data = Approval.objects.filter(
            user=user, status__lt=complete_status_min
            ).select_related('user')
        approval = {}
        for obj in data:

            # q = Approval_route.objects.filter(approval_id=obj.id)
            status = MAP_APPROVAL_STATUS[obj.status]

            approval[obj.id] = {'approval': obj,
                                'status': status,
                                'route': obj.related_route.all(),
                                }

        # 完了済の決裁
        data_complete = Approval.objects.filter(
            user=user, status__gte=complete_status_min)
        approval_complete = {}
        for obj in data_complete:

            # q = Approval_route.objects.filter(approval_id=obj.id)
            status = MAP_APPROVAL_STATUS[obj.status]

            # なぜかdateだけmodel_to_dictのとき抜け落ちるので、自分で入れる（多分migrateで関連付けが失敗してる）
            obj_dict = model_to_dict(obj)
            obj_dict['date'] = obj.date

            approval_complete[obj.id] = {'approval': obj_dict,
                                         'status': status,
                                         'route': obj.related_route.all(),
                                         }

        # 決裁ルートに自身がいて、かつ自身の決裁待ちであるデータを抽出
        q = Approval_route.objects.filter(user=user, status=2)
        need_check = {}
        for obj in q:
            # need_check[obj.approval_id] = Approval.objects.get(
            #     id=obj.approval_id)
            need_check[obj.approval.id] = obj.approval


        params = {'message': '一覧',
                  'data': data,
                  'field': field,
                  'user': request.user,
                  'approval': approval,
                  'approval_complete': approval_complete,
                  'page_approval': 1,
                  'need_check': need_check,
                  'base_url': self._get_url_info(request)
                  }

        return render(request, self.template_name, params)


class NewApprovalView(BaseView):

    def post(self, request, id, *args, **kwargs):

        datas = json.loads(request.body)
        user = User.objects.get(id=request.user.id)

        with transaction.atomic():
            b = Approval(
                user=user,
                title=datas.get('title'),
                detail=datas.get('detail'),
                date=datetime.date.today(),
            )
            b.save()

            new_approval = Approval.objects.all().order_by("-id")[0]

            # route
            route = datas.get('route')

            for cnt, user_id in enumerate(route):

                if cnt == 0:
                    status = APPROVAL_STATUS_CODE.MYTURN.value
                else:
                    status = APPROVAL_STATUS_CODE.WAITMYTURN.value
                
                user = User.objects.get(id=user_id)

                b = Approval_route(
                    approval=new_approval,
                    user=user,
                    status=status,
                )
                b.save()

        return JsonResponse({'reload': True})


class Approval_checkView(BaseView):

    def get(self, request, id, *args, **kwargs):

        if not self._is_valid_user(request.user.id):
            return render(request, 'front/no_session.html', status=403)

        data = Approval.objects.get(id=id)
        approval_route = data.related_route
        route = list()
        for r in approval_route.all():
            route.append(
                dict(name=f'{r.user.last_name}{r.user.first_name}'))
        return JsonResponse({
            'data': model_to_dict(data),
            'route': route,
            })

    def post(self, request, id, *args, **kwargs):

        with transaction.atomic():
            datas = json.loads(request.body)
            user = User.objects.get(id=request.user.id)
            status = datas.get('status')

            target_approval = Approval.objects.get(id=id)
            target_approval_route = target_approval.related_route.get(
                status=APPROVAL_STATUS_CODE.MYTURN.value, user=user)

            if status != 0:
                target_approval_route.status = status
                target_approval_route.approved_date = datetime.date.today()
                target_approval_route.save()

                next_route = target_approval.related_route.filter(status=APPROVAL_STATUS_CODE.WAITMYTURN.value).order_by("id")

                if next_route.count() == 0 or \
                        status in [APPROVAL_STATUS_CODE.REJECT.value, APPROVAL_STATUS_CODE.CANCEL.value]:
                    # 却下か取り下げされた場合もしくは最終承認者であった場合、この決裁自体が完了となる
                    target_approval.status = status
                    target_approval.date_complete = datetime.date.today()
                    target_approval.save()
                else:
                    # 次の人の承認ステータスも承認待ちに更新
                    # これは更新されない（なぜ？）
                    # next_route[0].status = APPROVAL_STATUS_CODE['MYTURN']
                    # next_route[0].save()

                    target_next_route = Approval_route.objects.get(id=next_route[0].id)
                    target_next_route.status = APPROVAL_STATUS_CODE.MYTURN.value
                    target_next_route.save()

        return JsonResponse({'reload': True})


class BoardView(BaseView):
    def get(self, request, *args, **kwargs):

        if not self._is_valid_user(request.user.id):
            return render(request, 'front/no_session.html', status=403)

        board_items = Board.objects.all()

        datas = list()
        for d in board_items:
            board = model_to_dict(d)
            user = {
                'id': d.user.id,
                'first_name': d.user.first_name,
                'last_name': d.user.last_name,
            }
            board_comments = d.board_comments.all()
            board['user'] = user
            board['comment_count'] = len(board_comments)
            datas.append(board)

        params = {'title': '掲示板一覧',
                  'datas': datas,
                  'user': request.user,
                  'page_board': 1,
                  }

        return render(request, "front/board.html", params)

class BoardCreateView(BaseView):

    def get(self, request, *args, **kwargs):

        if not self._is_valid_user(request.user.id):
            return render(request, 'front/no_session.html', status=403)

        # data = Board.objects.all()

        params = {'title': '掲示板作成',
                  }

        return render(request, "front/board_detail.html", params)

    def post(self, request, *args, **kwargs):

        datas = json.loads(request.body)
        user = User.objects.get(id=request.user.id)
        b = Board(
            title=datas.get('title'),
            detail=datas.get('detail'),
            user=user,
        )
        b.save()

        return JsonResponse({'result': True})

class Board_detailView(BaseView):

    def get(self, request, id, *args, **kwargs):

        if not self._is_valid_user(request.user.id):
            return render(request, 'front/no_session.html', status=403)

        data = Board.objects.get(id=id)
        board_comments = data.board_comments.all()
        comments = [c.to_dict() for c in board_comments]

        comments = list()
        for comment in board_comments:
            user = {
                'id': comment.user.id,
                'first_name': comment.user.first_name,
                'last_name': comment.user.last_name,
            }
            c = comment.to_dict()
            c['user'] = user
            comments.append(c)

        params = {
            'title': '掲示板詳細',
            'data': model_to_dict(data),
            'comments': comments
        }

        return render(request, "front/board_detail.html", params)

    def post(self, request, id, *args, **kwargs):

        req_body = json.loads(request.body)
        target = Board.objects.get(id=id)
        target.title = req_body['title']
        target.detail = req_body['detail']
        target.save()

        return JsonResponse({'result': True})

    def delete(self, request, id):
        """指定された掲示板を削除する。
        """

        target = Board.objects.get(id=id)
        
        if not request.user.id == target.user.id and \
            not is_admin(request.user.id):

            # 403を返したい
            raise PermissionDenied()

        target.delete()
        return JsonResponse({'result': True})


class BoardComment(BaseView):

    def post(self, request, id, *args, **kwargs):
        """ここで渡されるidは、Boardのid
        """

        req_body = json.loads(request.body)
        target = Board.objects.get(id=id)
        user = User.objects.get(id=request.user.id)
        comment = req_body['detail']
        b = Board_comment(
            user = user,
            detail = comment,
            board = target
        )
        b.save()

        return JsonResponse({'result': True})

    def delete(self, request, id):
        """指定された掲示板を削除する。
        ここで渡されるidは、Board_commentのid
        """

        target = Board_comment.objects.get(id=id)

        if not request.user.id == target.user.id and \
            not is_admin(request.user.id):

            # 403を返したい
            raise PermissionDenied()

        target.delete()
        return JsonResponse({'result': True})


class BoardGood(BaseView):

    def post(self, request, id, *args, **kwargs):
        """ここで渡されるidは、Boardのid
        """

        # TODO ユーザ毎のいいね回数は１回まで、DELETEで取り消し
        target = Board.objects.get(id=id)
        target.good_count += 1
        target.save()

        return JsonResponse({'result': True})

    # def delete(self, request, id):
    #     """指定された掲示板を削除する。
    #     ここで渡されるidは、Board_commentのid
    #     """

    #     target = Board_comment.objects.get(id=id)

    #     if not request.user.id == target.user.id and \
    #         not is_admin(request.user.id):

    #         # 403を返したい
    #         raise PermissionDenied()

    #     target.delete()
    #     return JsonResponse({'result': True})


class ToolsView(BaseView):
    def get(self, request):

        if not self._is_valid_user(request.user.id):
            return render(request, 'front/no_session.html', status=403)

        params = {"page_tools": 1,
                  }
        return render(request, "front/tools.html", params)

    def post(self, request):
        params = {"message": "SettingView:Post処理",
                  "page_tools": 1,
                  }
        return render(request, "front/tools.html", params)


class AttendView(BaseView):

    def get(self, request, year, month, *args, **kwargs):

        if not self._is_valid_user(request.user.id):
            return render(request, 'front/no_session.html', status=403)

        dayCnt = calendar.monthrange(year, month)[1]

        dayf = str(year)+"-"+str(month)+"-"+"01"
        dayl = str(year)+"-"+str(month)+"-"+str(dayCnt)

        user = User.objects.get(id=request.user.id)

        q = Attendance.objects.filter(
            user=user, date__year=year, date__month=month)

        if q.count() == 0:
            #  未登録の年月は、ひと月分まとめて登録する。
            register_attendance_month(request.user.id, year, month)

        d = Attendance.objects.filter(
            user=user, date__gte=dayf, date__lte=dayl)
        userinfo = UserSetting.objects.get(user=user)
        worktime = datetime.timedelta(hours=userinfo.day_worktime.hour, minutes=userinfo.day_worktime.minute)

        day = 0
        workday_month = 0
        attend = {}
        work_time_total_t = datetime.timedelta(hours=0, minutes=0)
        work_day_total = 0
        extra_hour_total_t = datetime.timedelta(hours=0, minutes=0)

        work_status_db = WorkStatus.objects.all()
        work_status = dict()
        for r in work_status_db:
            work_status[r.id] = r.holiday

        car_fare = 0
        for obj in d:
            day += 1
            weekday = WEEKDAYS[obj.date.weekday()]

            work_time_total_t += datetime.timedelta(
                hours=obj.work_time.hour, minutes=obj.work_time.minute)
            extra_hour_total_t += datetime.timedelta(
                hours=obj.work_overtime.hour, minutes=obj.work_overtime.minute)
            if obj.work_time != datetime.time(0, 0, 0):
                work_day_total += 1

            car_fare += obj.carfare
            is_holiday = work_status[obj.work_status]

            if not is_holiday:
                workday_month += 1

            attend[day] = {'attend': obj,
                           'weekday': weekday,
                           'holiday': is_holiday,
                           }

        tmp = WorkStatus.objects.filter(use=True)
        ws = list(tmp.values())

        d, h, m, s = get_d_h_m_s(work_time_total_t)
        work_time_total = {'hour': h+d*24,
                           'minute': datetime.time(0, m)}

        d, h, m, s = get_d_h_m_s(extra_hour_total_t)
        extra_hour_total = {'hour': h+d*24,
                            'minute': datetime.time(0, m)}

        worktime_month = worktime + datetime.timedelta(
            hours=userinfo.day_worktime.hour, minutes=userinfo.day_worktime.minute) * workday_month
        worktime_month_hour = int((worktime_month.total_seconds() / 60) // 60)
        worktime_month_minute = int(worktime_month.total_seconds() % (worktime_month.total_seconds() / 60))
        worktime_month_t = str(worktime_month_hour) + ':' + str(worktime_month_minute).rjust(2, '0')
        
        params = {
            'year': year,
            'month': month,
            'workstatus': ws,
            'attend': attend,
            'workday_month': workday_month,
            'workhour_month': worktime_month_t,
            'workhour_day': worktime,
            'work_time_total': work_time_total,
            'work_day_total': work_day_total,
            'extra_hour_total': extra_hour_total,
            'base_url': self._get_url_info(request),
            'car_fare_total': car_fare,
        }

        url = "front/attend.html"
        return render(request, url, params)
    
    def delete(self, request, year, month):
        """指定された月の出勤簿を初期化する。
        """

        
        user = User.objects.get(id=request.user.id)
        day = int(request.POST.get('day', default=0))

        if day == 0:
            Attendance.objects.filter(
                user=user,
                date__year=year,
                date__month=month
            ).delete()

        else:
            Attendance.objects.filter(
                user=user,
                date__year=year,
                date__month=month,
                date__day=day
            ).delete()

        return JsonResponse({'result': True})




def attend_info(request, *args, **kwargs) -> JsonResponse:

    def _get_attendance_info(user_id, year, month):
        """Attendanceテーブルの内容から、出勤簿の内容を返す
        Array形式で、1日目、2日目・・・と各要素に１日分の情報をdictで含んでいる。
        [{ 
            'attend': obj,
            'weekday': weekday,
            'holiday': holiday,
        }]
        """

        user = User.objects.get(id=request.user.id)

        dayCnt = calendar.monthrange(year, month)[1]
        date_from = str(year)+"-"+str(month)+"-"+"01"
        date_to = str(year)+"-"+str(month)+"-"+str(dayCnt)

        d = Attendance.objects.filter(
            user=user, date__gte=date_from, date__lte=date_to)

        if d.count() == 0:
            return None

        workday_month = 0
        attend_info = {}
        work_time_total_t = datetime.timedelta(hours=0, minutes=0)
        work_day_total = 0
        extra_hour_total_t = datetime.timedelta(hours=0, minutes=0)

        for obj in d:
            weekday = WEEKDAYS[obj.date.weekday()]
            work_time_total_t += datetime.timedelta(
                hours=obj.work_time.hour, minutes=obj.work_time.minute)
            extra_hour_total_t += datetime.timedelta(
                hours=obj.work_overtime.hour, minutes=obj.work_overtime.minute)
            if obj.work_time != datetime.time(0, 0, 0):
                work_day_total += 1

            work_status = get_workStatus(obj.date, user_id)
            q = WorkStatus.objects.filter(
                id=work_status['status'], holiday=True).count()

            if q > 0:
                holiday = 1
            else:
                holiday = 0
                workday_month += 1

            attend_info.append({'attend': obj,
                            'weekday': weekday,
                            'holiday': holiday,
                            })

        d, h, m, s = get_d_h_m_s(work_time_total_t)
        work_time_total = {'hour': h+d*24,
                            'minute': datetime.time(0, m)}

        d, h, m, s = get_d_h_m_s(extra_hour_total_t)
        extra_hour_total = {'hour': h+d*24,
                            'minute': datetime.time(0, m)}

        return {'attend_info': attend_info,
                'work_time_total': work_time_total,
                'extra_hour_total': extra_hour_total,
                'workday_month': workday_month,
                'work_day_total': work_day_total,
                }

    if request.user.is_anonymous:
        return JsonResponse(data=None)

    user = User.objects.get(id=request.user.id)
    now = make_aware(datetime.datetime.now())
    month = int(request.GET.get("month", default=now.month))
    year = int(request.GET.get("year", default=now.year))
    attend_infos = _get_attendance_info(request.user.id, year, month)

    tmp = WorkStatus.objects.filter(use=True)
    work_status = list(tmp.values())

    userinfo = UserSetting.objects.get(user=user)
    worktime = userinfo.day_worktime.hour

    params = {
        'year': year,
        'month': month,
        'workstatus': work_status,
        'attend': attend_infos['attend_info'],
        'workday_month': attend_infos['workday_month'],
        'workhour_day': worktime,
        'workhour_month': attend_infos['workday_month'] * worktime,
        'work_time_total': attend_infos['work_time_total'],
        'work_day_total': attend_infos['work_day_total'],
        'extra_hour_total': attend_infos['extra_hour_total'],
    }

    return JsonResponse(data=params)


class AttendRegisterDay(BaseView):

    """attend/<int:year>/<int:month>/<int:day>" に対応する処理
    """

    def post(self, request, *args, **kwargs):
        """出勤簿の更新処理。URLに指定された日の出勤情報を更新する。
        """

        user = User.objects.get(id=request.user.id)
        year = int(kwargs['year'])
        month = int(kwargs['month'])
        day = int(kwargs['day'])
        date = str(year)+"-"+str(month)+"-"+str(day)

        datas = json.loads(request.body)

        work_status = datas.get('work_status')
        work_detail = datas.get('work_detail')
        work_start = datas.get('work_start')
        work_end = datas.get('work_end')
        work_off = datas.get('work_off')
        carfare = datas.get('carfare')
        memo = datas.get('memo')

        st = datetime.datetime.strptime(
            nvl(work_start, '00:00'), '%H:%M')

        ed = datetime.datetime.strptime(
            nvl(work_end, '00:00'), '%H:%M')

        workoff_v = datetime.datetime.strptime(
            nvl(work_off, "00:00"), '%H:%M')

        workoff = datetime.timedelta(
            hours=workoff_v.hour, minutes=workoff_v.minute)

        # 規定労働時間
        reg_work_time = UserSetting.objects.get(user=user)

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

        attendance = Attendance.objects.get(user=user, date=date)
        attendance.work_status = work_status
        attendance.work_detail = work_detail

        work_start_h, work_start_m = nvl(work_start, '00:00').split(':')
        attendance.work_start = make_aware(
            datetime.datetime(year, month, day, hour=int(
                work_start_h), minute=int(work_start_m), second=0, microsecond=0)
        )
        work_end_h, work_end_m = nvl(work_end, '00:00').split(':')
        attendance.work_end = make_aware(datetime.datetime(year, month, day, hour=int(
            work_end_h), minute=int(work_end_m), second=0, microsecond=0))
        attendance.work_off = nvl(work_off, "00:00")
        attendance.work_time = worktime
        attendance.work_overtime = overtime
        attendance.carfare = carfare
        attendance.memo = memo

        attendance.save()

        data = {'result': True}
        return JsonResponse(data)


class UserInfo(BaseView):

    def get(self, request, *args, **kwargs):

        if not self._is_valid_user(request.user.id):
            return render(request, 'front/no_session.html', status=403)

        users = User.objects.filter(
            is_active=True)
        
        rtn = list()
        for user in users:
            rtn.append(model_to_dict(user))

        return JsonResponse({'users': rtn})


class LoginView(LoginView):
    """ログインページ"""
    form_class = forms.LoginForm
    template_name = "front/index.html"


class LogoutView(BaseView):
    """ログアウト"""
    def get(self, request):
        return HttpResponseRedirect(reverse_lazy('front:top'))


class signupView(FormView):
    """新規登録ページ"""
    form_class = forms.SignUpForm
    template_name = "front/signup.html"


class signup_Register(CreateView):
    form_class = forms.SignUpForm
    template_name = "front/signup.html"
    success_url = reverse_lazy('front:top')

    def form_valid(self, form):

        with transaction.atomic():
            user = form.save()  # formの情報を保存
            login(self.request, user)  # 認証

            b = UserSetting(
                user=user,
            )
            b.save()

        return HttpResponseRedirect(self.success_url)  # リダイレクト
