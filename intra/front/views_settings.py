import json
import logging

from urllib.parse import urlencode
from django.views.generic import ListView
from django.http.response import JsonResponse
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import redirect
from .models import WorkStatus, Holiday, UserSetting, Approval_format, Approval_format_route
from django.forms.models import model_to_dict


class SettingView(View):

    """設定画面一覧

    Args:
        View (_type_): _description_
    """

    def get(self, request):

        params = {"message": "",
                  }

        return render(request, "front/setting.html", params)

    def post(self, request):

        params = {"message": "",
                  }

        return render(request, "front/setting.html", params)


class SettingBase(ListView):

    """各設定画面用ベースクラス
        modelを指定して、該当するテーブルの内容すべてを渡す。
        object_list という名前でデータが渡される
        template_name を指定しない場合、デフォルト値（[テーブル名]_list.html)となる

    Returns:
        _type_: _description_
    """

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

        self.callback_url = None
        self.model = None
        self.template_name = None

    # 追加で渡したいパラメータがあれば、実装
    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)

        error_message = self.request.GET.get('error_massage', None)
        # page_title を追加する
        ctx['error_massage'] = error_message

        return ctx
    
    def _get_url_info(self, request):

        host = request.get_host()
        protocol = request.headers['Referer'].split(':')[0]
        return {
            'host': host,
            'protocol': protocol,
        }

    def post(self, request):

        # 継承クラスで実装
        pass

    def get(self, request):

        # 継承クラスで実装
        pass

    def _check_validator(self):
       # 継承クラスで実装
        pass

    def _update(self, request):
       # 継承クラスで実装
        pass

    def _insert(self, request):
       # 継承クラスで実装
        pass

    def _make_callback(self, param):

        if not self.false_callback_url:
            return

        if not param:
            return f'{self.false_callback_url}'

        # URLにパラメータを付与する
        return f'{self.false_callback_url}?{urlencode(param)}'

    def _get_columns(self, model):

        meta_fields = model._meta.get_fields()

        ret = []
        for meta_field in meta_fields:
            ret.append(meta_field.name)
        return ret


class SettingWorkStatusView(SettingBase):

    def get(self, request):

        url = self._get_url_info(request)

        data = WorkStatus.objects.all()

        columns = self._get_columns(WorkStatus)
        columns.append('is_new')

        params = dict(
            tab='勤怠区分設定',
            title='勤怠区分設定',
            data=data,
            columns=columns,
            host=url['host'],
            protocol=url['protocol'],
        )
        return render(request, "front/setting_workstatus.html", params)

    def post(self, request):

        # 初期設定
        self.callback_url = reverse_lazy('front:setting_work_status')

        datas = json.loads(request.body)

        name_selection = datas.get('name')
        valid = datas.get('valid')
        holiday = datas.get('holiday')
        memo = datas.get('memo')

        b = WorkStatus(
            name="",
            name_selection=name_selection,
            use=valid,
            holiday=holiday,
            memo=memo,
        )
        b.save()

        data = {'result': True}
        return JsonResponse(data)


class SettingWorkStatusViewById(SettingBase):

    def delete(self, request, id):
        obj = WorkStatus.objects.get(id=id)
        obj.delete()

        data = {'result': True}
        return JsonResponse(data)

    def post(self, request, id):

        # データ存在チェック＆取得
        obj = WorkStatus.objects.get(id=id)
        # 初期設定
        import json
        datas = json.loads(request.body)
        logging.debug(datas)
        
        name_selection = datas.get('name')
        valid = datas.get('valid')
        holiday = datas.get('holiday')
        memo = datas.get('memo')

        obj.name_selection = name_selection
        obj.use = valid
        obj.holiday = holiday
        obj.memo = memo
        obj.save()

        data = {'result': True}
        return JsonResponse(data)


class SettingHolidayView(SettingBase):

    success_url = reverse_lazy('front:setting_holiday')

    def get(self, request):

        data = Holiday.objects.all()

        columns = self._get_columns(Holiday)
        url = self._get_url_info(request)

        params = {
            'tab': '公休日設定',
            'title': '会社の休日設定',
            'data': data,
            'columns': columns,
            'host': url['host'],
            'protocol': url['protocol'],
        }
        return render(request, "front/setting_base.html", params)


class SettingHolidayInfo(SettingBase):

    def get(self, request):

        data = Holiday.objects.all()
        rtn = list()
        for d in data:
            rtn.append(model_to_dict(d))
        return JsonResponse(rtn, safe=False)

class SettingHolidayByDate(SettingBase):

    def delete(self, request, date):
        date_valid = f'2000-{date[0]}{date[1]}-{date[2]}{date[3]}'
        obj = Holiday.objects.get(date=date_valid)
        obj.delete()

        data = {'result': True}
        return JsonResponse(data)

    def post(self, request, date):

        date_valid = f'2000-{date[0]}{date[1]}-{date[2]}{date[3]}'

        obj = Holiday.objects.filter(date=date_valid)
        params = json.loads(request.body)

        name = params.get('name')
        memo = params.get('memo')

        # データ存在チェック＆取得
        if obj.count() == 0:
            # create
            b = Holiday(
                date=date_valid,
                name=name,
                memo=memo,
            )
            b.save()

        else:
            # update
            obj = Holiday.objects.get(date=date_valid)

            obj.date = date_valid
            obj.name = name
            obj.memo = memo
            obj.save()

        data = {'result': True} # 空だとjs側でエラーになるため
        return JsonResponse(data)

class SettingUserView(SettingBase):

    success_url = reverse_lazy('front:setting_user')
    def get(self, request):

        data = UserSetting.objects.all()
        rtn = list()
        for d in data:
            user = model_to_dict(d.userid)
            rtn_d = model_to_dict(d)
            rtn_d['user'] = user
            rtn.append(rtn_d)

        url = self._get_url_info(request)

        params = {
            'data': rtn,
            'host': url['host'],
            'protocol': url['protocol'],
        }
        return render(request, "front/setting_user.html", params)

    def post(self, request):

        # 更新処理
        q = UserSetting.objects.all()
        print('usersetting POST')

        cnt = 0
        for obj in q:

            cnt += 1
            userid = request.POST['userid_' + str(cnt)]
            day_worktime = request.POST['day_worktime_' + str(cnt)]
            rank = request.POST['rank_' + str(cnt)]
            if 'regular_holiday_0_' + str(cnt) in request.POST:
                mon = 1
            else:
                mon = 0
            if 'regular_holiday_1_' + str(cnt) in request.POST:
                tue = 1
            else:
                tue = 0
            if 'regular_holiday_2_' + str(cnt) in request.POST:
                wed = 1
            else:
                wed = 0
            if 'regular_holiday_3_' + str(cnt) in request.POST:
                thu = 1
            else:
                thu = 0
            if 'regular_holiday_4_' + str(cnt) in request.POST:
                fry = 1
            else:
                fry = 0
            if 'regular_holiday_5_' + str(cnt) in request.POST:
                sat = 1
            else:
                sat = 0
            if 'regular_holiday_6_' + str(cnt) in request.POST:
                sun = 1
            else:
                sun = 0

            obj.userid = userid
            obj.day_worktime = day_worktime
            obj.rank = rank
            obj.regular_holiday = {mon, tue, wed, thu, fry, sat, sun}
            obj.save()

        return HttpResponseRedirect(reverse_lazy('front:setting_user'))  # リダイレクト


class SettingUserById(SettingBase):

    def post(self, request, id):

        obj = UserSetting.objects.get(id=id)
        params = json.loads(request.body)

        worktime = params.get('worktime')
        mon_is_holiday = params.get('mon')
        tue_is_holiday = params.get('tue')
        wed_is_holiday = params.get('wed')
        thu_is_holiday = params.get('thu')
        fri_is_holiday = params.get('fri')
        sat_is_holiday = params.get('sat')
        sun_is_holiday = params.get('sun')
        rank = params.get('rank')
        memo = params.get('memo')

        # update
        obj.day_worktime = worktime
        obj.mon_is_holiday = mon_is_holiday
        obj.tue_is_holiday = tue_is_holiday
        obj.wed_is_holiday = wed_is_holiday
        obj.thu_is_holiday = thu_is_holiday
        obj.fri_is_holiday = fri_is_holiday
        obj.sat_is_holiday = sat_is_holiday
        obj.sun_is_holiday = sun_is_holiday
        obj.rank = rank
        obj.memo = memo
        obj.save()

        data = {'result': True} # 空だとjs側でエラーになるため
        return JsonResponse(data)


class SettingApprovalFormatView(SettingBase):

    success_url = reverse_lazy('front:setting_approval_format', args=(0,))

    def get(self, request, id, *args, **kwargs):

        if id != 0:
            data = Approval_format.objects.get(id=id)
            format_name = data.title
            route = Approval_format_route.objects.filter(format_id=id)

            title = '決裁フォーマット更新'
            upd = True
        else:
            data = ''
            format_name = ''
            route = ''
            title = '決裁フォーマット新規登録'
            upd = False

        format_all = Approval_format.objects.all()
        user_all = User.objects.all()

        params = {'title': title,
                  'data': data,
                  'counter': (1, 2, 3, 4, 5),
                  'user': request.user,
                  'page_setting': 1,
                  'format_all': format_all,
                  'format_name': format_name,
                  'route': route,
                  'upd': upd,
                  'user_all': user_all,
                  }

        return render(request, "front/approval_detail.html", params)

    def post(self, request, id, *args, **kwargs):

        if id == 0 or 'btn_insert' in request.POST:
            # idが空（新規）または既存のフォーマットをコピーして新規作成する場合
            if Approval_format.objects.all().count() != 0:
                id = Approval_format.objects.all().order_by("-id")[0].id + 1
            else:
                id = 1

            b = Approval_format(
                title=request.POST['title'],
                detail=request.POST['detail'],
            )
            b.save()
        else:
            b = Approval_format.objects.get(id=id)
            b.title = request.POST['title']
            b.detail = request.POST['detail']
            b.save()

        # route
        record = Approval_format_route.objects.filter(format_id=id)
        if record.count() > 0:
            record.delete()

        s = request.POST['route']
        l = s.split(',')

        for username in l:
            b = Approval_format_route(
                format_id=id,
                userid=username
            )
            b.save()

        return HttpResponseRedirect(self.success_url)  # リダイレクト
