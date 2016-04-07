import logging

from django.utils import timezone
from django.db import models
from django.db.utils import OperationalError, ProgrammingError
from django.core.cache import cache

from django_redis import get_redis_connection

log = logging.getLogger('vrcloud.{}'.format(__name__))

class DatabaseStatus(models.Model):
    """
    A dummy model. Write to the database to make sure that we can.
    Then, read from the database to make sure that we can.
    """
    created = models.DateTimeField()

    def save(self):
        if not self.id:
            self.created = timezone.now()
        super().save()

    @classmethod
    def ok(cls) -> bool:
        s = DatabaseStatus()
        try:
            s.save()
        except OperationalError as e:
            log.error(e)
            return False
        except ProgrammingError as e:
            log.error(e)
            return False

        try:
            a = DatabaseStatus.objects.all().order_by('-created')[0]
        except IndexError:
            log.error("Database write succeeded but read failed.")
            return False
        return True


def database_ok():
    return DatabaseStatus.ok()


def cache_ok():
    cache.set("foo", "bar", timeout=1)
    foo = cache.get("foo")
    return foo == "bar"


def data_ok():
    con = get_redis_connection("data")
    con.set("foo", "bar")
    foo = con.get("foo")
    log.info(foo)
    return True

