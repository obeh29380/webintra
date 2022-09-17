from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time

@shared_task
def add(x, y):
    print("処理中")
    z = x + y
    time.sleep(10)
    print("処理完了")
    return z