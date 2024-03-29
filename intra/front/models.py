from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.forms.models import model_to_dict

class BaseManager(models.Manager):
   def get_or_none(self, **kwargs):
       """
       検索にヒットすればそのモデルを、しなければNoneを返す。
       """
       try:
           return self.get_queryset().get(**kwargs)
       except self.model.DoesNotExist:
           return None


class Schedule(models.Model):
    userid = models.CharField(max_length=20, null=True)
    date = models.DateTimeField(auto_now_add=True)
    allday = models.BooleanField()
    notification_datetime = models.DateTimeField()
    title = models.CharField(max_length=100)
    content = models.CharField(max_length=1000)
    status = models.CharField(max_length=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "schedule"


class Attendance(models.Model):
    user = models.ForeignKey(User, db_column='user', related_name='attendance', on_delete=models.CASCADE, null=True)
    date = models.DateField(null=True)
    work_detail = models.CharField(max_length=100, null=True)
    work_status = models.IntegerField(null=True)
    work_start = models.DateTimeField()
    work_end = models.DateTimeField()
    work_off = models.TimeField(default="00:00:00")
    work_time = models.TimeField(default="00:00:00")
    work_overtime = models.TimeField(default="00:00:00")
    carfare = models.IntegerField(default=0)
    memo = models.TextField()
    sysmemo = models.TextField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "date"], name="unique_user")
        ]
        db_table = "attendance"


class WorkStatus(models.Model):
    objects = BaseManager()
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(max_length=20, null=True)
    name_selection = models.CharField(max_length=3)
    use = models.BooleanField(default=True)
    holiday = models.BooleanField(default=True)
    memo = models.TextField(null=True)
    systemStatus = models.BooleanField(default=False)

    class Meta:
        db_table = "work_status"


class Holiday(models.Model):
    date = models.DateField(primary_key=True)
    name = models.CharField(max_length=50, null=True)
    memo = models.TextField(null=True)

    class Meta:
        db_table = "holiday"


class UserSetting(models.Model):

    user = models.OneToOneField(User, related_name='user_setting', on_delete=models.CASCADE, null=True)
    day_worktime = models.TimeField(default="08:00:00")
    mon_is_holiday = models.BooleanField(default=False)
    tue_is_holiday = models.BooleanField(default=False)
    wed_is_holiday = models.BooleanField(default=False)
    thu_is_holiday = models.BooleanField(default=False)
    fri_is_holiday = models.BooleanField(default=False)
    sat_is_holiday = models.BooleanField(default=True)
    sun_is_holiday = models.BooleanField(default=True)
    rank = models.IntegerField(default=3)
    memo = models.TextField(null=True)

    class Meta:
        db_table = "user_setting"


class Approval(models.Model):
    user = models.ForeignKey(User, db_column='user', related_name='approval', on_delete=models.CASCADE, null=True)
    date = models.DateField(auto_now_add=True)
    date_complete = models.DateField(default=datetime.now)
    title = models.CharField(max_length=100, null=True)
    detail = models.TextField()
    status = models.IntegerField(default=0)
    status_complete = models.IntegerField(default=0)

    class Meta:
        db_table = "approval"


class Approval_route(models.Model):
    # tips on_delete=models.CASCADEは、Django上でemurateするだけ、DBには登録されない（直接クエリ叩くと、CASCADEになっていないので参照先は削除できない）
    id = models.AutoField(primary_key=True)
    approval = models.ForeignKey(Approval, db_column='approval', on_delete=models.CASCADE, related_name='related_route', null=True)
    user = models.ForeignKey(User, db_column='user', on_delete=models.CASCADE, null=True)
    approved_date = models.DateField(null=True)
    status = models.IntegerField(default=0)
    comment = models.TextField(null=True)

    class Meta:
        db_table = "approval_route"


class Approval_format(models.Model):
    title = models.CharField(max_length=100, null=True)
    detail = models.TextField(null=True)

    class Meta:
        db_table = "approval_format"


class Approval_format_route(models.Model):
    format_id = models.IntegerField()
    userid = models.CharField(max_length=20, null=True)
    roll = models.IntegerField(default=1)

    class Meta:
        db_table = "approval_format_route"


class Board(models.Model):
    user = models.ForeignKey(User, db_column='user', on_delete=models.DO_NOTHING, null=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    title = models.TextField()
    detail = models.TextField()
    category_id = models.IntegerField(default=0)
    good_count = models.IntegerField(default=0)

    class Meta:
        db_table = "board"


class Board_comment(models.Model):
    user = models.ForeignKey(User, db_column='user', on_delete=models.DO_NOTHING, null=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    detail = models.TextField()
    board = models.ForeignKey(Board, db_column='board', on_delete=models.CASCADE, related_name='board_comments', null=True)

    class Meta:
        db_table = "board_comment"

    def to_dict(self):
        ret = model_to_dict(self)
        ret['created_datetime'] = self.created_datetime.strftime("%y/%m/%d %H:%M")
        return ret

class Board_category(models.Model):
    name = models.CharField(max_length=20, null=True)

    class Meta:
        db_table = "board_category"


class Chat(models.Model):
    author_id = models.CharField(max_length=20, null=True)
    created_datetime = models.DateTimeField(null=False, auto_now=True)
    room_id = models.CharField(max_length=10, null=False)
    text = models.TextField()

    class Meta:
        db_table = "chat"
