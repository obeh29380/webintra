from django.urls import register_converter, path
from . import views
from . import views_settings

class NegativeIntConverter:
    regex = '-?\d+'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%d' % value

register_converter(NegativeIntConverter, 'negint')

app_name = "front"
urlpatterns = [
     path("", views.LoginView.as_view(), name="top"),
     path("logout", views.LogoutView.as_view(), name="logout"),
     path("home", views.HomeView.as_view(), name="home"),
     path("board", views.BoardView.as_view(), name="board_menu"),
     path("board/new", views.BoardCreateView.as_view(), name="board_create"),
     path("board/<str:id>",
          views.Board_detailView.as_view(),
          name="board_detail"),
     path("board/<str:id>/comment",
         views.BoardComment.as_view(),
         name="board_comment"),
     path("board/<str:id>/good",
         views.BoardGood.as_view(),
         name="board_good"),
     path("attend/<int:year>/<int:month>",
          views.AttendView.as_view(),
          name="attend"),
     path("attend-info/<int:year>/<int:month>",
          views.attend_info,
          name="attend_info"),
     path("attend/<int:year>/<int:month>/<int:day>",
          views.AttendRegisterDay.as_view(),
          name="attend_register_day"),
     path("approval", views.ApprovalView.as_view(), name="approval"),
     path("approval/check/<str:id>",
          views.Approval_checkView.as_view(), name="approval_check"),
     path("approval/new/<int:id>",
          views.NewApprovalView.as_view(), name="new_approval"),
     path('signup/', views.signupView.as_view(), name='signup'),
     path('signup/register',
          views.signup_Register.as_view(),
          name='signup_register'),
     path("tools", views.ToolsView.as_view(), name="tools"),
     path("setting", views_settings.SettingView.as_view(), name="setting"),
     path("setting/work_status", views_settings.SettingWorkStatusView.as_view(),
          name="setting_work_status"),
     path("setting/work_status/<int:id>", views_settings.SettingWorkStatusViewById.as_view(),
          name="setting_work_status_by_id"),
     path("setting/holiday", views_settings.SettingHolidayView.as_view(),
          name="setting_holiday"),
     path("setting/holiday/info", views_settings.SettingHolidayInfo.as_view(),
          name="setting_holiday_info"),
     path("setting/holiday/<str:date>", views_settings.SettingHolidayByDate.as_view(),
          name="setting_holiday_by_date"),
     path("setting/user",
          views_settings.SettingUserView.as_view(),
          name="setting_user"),
     path("setting/user/<int:id>", views_settings.SettingUserById.as_view(),
          name="setting_user_by_id"),
     path("setting/approval_format/<int:id>",
          views_settings.SettingApprovalFormatView.as_view(),
          name="setting_approval_format"),
     path("test", views.exec_ajax, name='test'),
     path("userinfo",
          views.UserInfo.as_view(),
          name="user_info"),
]
