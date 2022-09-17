from django.db import models


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
    userid = models.CharField(max_length=20, null=True)
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
                fields=["userid", "date"], name="unique_user")
        ]
        db_table = "attendance"


class WorkStatus(models.Model):
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
    detail = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = "holiday"


class UserSetting(models.Model):

    userid = models.CharField(max_length=20, null=True)
    day_worktime = models.TimeField(default="08:00:00")
    mon_is_holiday = models.BooleanField(default=False)
    tue_is_holiday = models.BooleanField(default=False)
    wed_is_holiday = models.BooleanField(default=False)
    thu_is_holiday = models.BooleanField(default=False)
    fri_is_holiday = models.BooleanField(default=False)
    sat_is_holiday = models.BooleanField(default=True)
    sun_is_holiday = models.BooleanField(default=True)
    rank = models.IntegerField(default=3)

    class Meta:
        db_table = "user_setting"


class Approval(models.Model):
    userid = models.CharField(max_length=20, null=True)
    date = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=100, null=True)
    detail = models.TextField()
    status = models.IntegerField(default=0)
    status_complete = models.IntegerField(default=0)

    class Meta:
        db_table = "approval"


class Approval_route(models.Model):
    approval_id = models.IntegerField()
    userid = models.CharField(max_length=20)
    approved_date = models.DateField(null=True)
    status = models.IntegerField(default=0)

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
    author_id = models.CharField(max_length=20, null=True)
    created_datetime = models.DateTimeField(null=True)
    title = models.TextField()
    detail = models.TextField()
    category_id = models.IntegerField(null=True)
    good_count = models.IntegerField(default=0)

    class Meta:
        db_table = "board"


class Board_comment(models.Model):
    author_id = models.CharField(max_length=20, null=True)
    created_datetime = models.DateTimeField(null=True)
    detail = models.TextField()
    board_id = models.IntegerField(null=False)

    class Meta:
        db_table = "board_comment"


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
