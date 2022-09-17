from urllib.parse import urlencode
from django.views.generic import TemplateView, ListView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import redirect
from .models import WorkStatus, Holiday, UserSetting, Approval_format, Approval_format_route


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

    def post(self, request):

       # 継承クラスで実装
       print('setting base post')
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

    model = WorkStatus
    template_name = 'workstatus_list.html'

    def get(self, request):

        data = WorkStatus.objects.all()

        columns = self._get_columns(WorkStatus)
        columns.append('is_new')

        params = {'tab': '勤怠区分設定',
                  'title': '勤怠区分設定',
                  'data': data,
                  'counter': (1, 2, 3, 4, 5),
                  'columns': columns,
                  }
        return render(request, "front/workstatus_list.html", params)

    def _update(self, request):
        """既存データ更新処理。

        Returns:
            エラー情報
        """

        # 更新処理
        q = WorkStatus.objects.all()

        # 既存更新分
        cnt = q.count()

        for i in range(cnt):
            # システム設定の項目=readonlyの行は、POSTされない。(ただ表示しているだけで、input属性をつけていないため)
            # これを処理しようとすると、MultiValueDictKeyErrorが起きる。

            status = request.POST.get(f'status_{str(i+1)}', False)

            if status == False:
                # DB登録済みで、POSTパラメータに存在しないもの＝readonlyのものは処理しない。
                continue

            data = WorkStatus.objects.get(status=status)

            if data.systemStatus:
                continue

            if 'delete_'+str(i+1) in request.POST:
                data.delete()
            else:
                data.name = request.POST['name_'+str(i+1)]
                data.name_selection = request.POST['name_selection_'+str(i+1)]
                data.use = request.POST['use_'+str(i+1)]
                data.holiday = request.POST['holiday_'+str(i+1)]
                data.memo = request.POST['memo_'+str(i+1)]

                # 各値チェック
                # Todo:今は同期処理のため、再描画して入力した値が消えてしまう。非同期を実装し、これを回避したい。
                if len(data.name_selection) > 3:

                    return f'入力桁数オーバー:[name_selection]'

                try:
                    data.save()
                except Exception as e:
                    raise e

    def _insert(self, request):
        # 新規登録分
        # 更新時にコードを変えたら重複する場合がある？
        for i in range(5):
            status = request.POST.get(f'status_add_{str(i+1)}')
            name = request.POST['name_add_'+str(i+1)]
            name_selection = request.POST['name_selection_add_'+str(i+1)]
            use = request.POST['use_add_'+str(i+1)]
            holiday = request.POST['holiday_add_'+str(i+1)]
            memo = request.POST['memo_add_'+str(i+1)]

            # 各値チェック
            # Todo:今は同期処理のため、再描画して入力した値が消えてしまう。非同期を実装し、これを回避する。
            if len(name_selection) > 3:

                return f'入力桁数オーバー:[name_selection]'

            if status:
                b = WorkStatus(
                    name=name,
                    name_selection=name_selection,
                    use=use,
                    holiday=holiday,
                    memo=memo,
                )
                try:
                    b.save()
                except Exception as e:
                    raise e

    def post(self, request):

        # 初期設定
        self.callback_url = reverse_lazy('front:setting_work_status')

        rtn = ''
        try:
            rtn = self._update(request)
            if rtn:
                raise

            rtn = self._insert(request)
            if rtn:
                raise

        except Exception as e:

            # パラメータのdictをurlencodeする。複数のパラメータを含めることも可能
            parameters = urlencode({'error_massage': rtn})

            # URLにパラメータを付与する
            url = f'{self.callback_url}?{parameters}'
            return redirect(url)

        return HttpResponseRedirect(self.callback_url)  # リダイレクト


class SettingHolidayView(SettingBase):

    success_url = reverse_lazy('front:setting_holiday')

    def get(self, request):

        data = Holiday.objects.all()

        columns = self._get_columns(Holiday)

        params = {'tab': '公休日設定',
                  'title': '会社の休日設定',
                  'data': data,
                  'counter': (1, 2, 3, 4, 5),
                  'columns': columns,
                  }
        return render(request, "front/setting_base.html", params)

    def post(self, request):

        # 更新処理
        q = Holiday.objects.all()

        # 既存更新分
        cnt = q.count()

        if cnt > 0:
            for i in range(cnt):
                b = Holiday(
                    date=request.POST['date_'+str(i+1)],
                    detail=request.POST['detail_'+str(i+1)],
                )
                b.save()

        # 新規登録分
        # 更新時にコードを変えたら重複する場合がある？
        for i in range(5):

            date = request.POST['date_add_'+str(i+1)]
            detail = request.POST['detail_add_'+str(i+1)]

            if date:
                b = Holiday(
                    date=date,
                    detail=detail,
                )
                b.save()

        return HttpResponseRedirect(self.success_url)  # リダイレクト


class SettingUserView(SettingBase):

    success_url = reverse_lazy('front:setting_user')

    def get(self, request):

        data_tmp = UserSetting.objects.all()
        print('usersetting GET')

        data = {}
        for d in data_tmp:

            data[d.id] = {'user': d,
                          }

        params = {'message': '一覧',
                  'data': data,
                  'counter': (1, 2, 3, 4, 5),
                  'page_setting': 1,
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
