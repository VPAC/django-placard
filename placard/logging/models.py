from django.contrib.auth.models import User
from django.db import models


class LogEntryManager(models.Manager):
    def log_action(self, user, obj, action, change_message):
        assert action == 'A' or action == 'C' or action == 'D' or action == 'T'

        e = self.model(
            user=user,
            object_dn=obj.dn, object_pk=obj.pk,
            object_type=type(obj).__name__, object_repr=unicode(obj),
            action=action, change_message=change_message)

        e.save()


class LogEntry(models.Model):
    action_time = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name="ldap_logs")
    object_dn = models.CharField(max_length=50)
    object_pk = models.CharField(max_length=20)
    object_type = models.CharField(max_length=20)
    object_repr = models.CharField(max_length=200)
    action = models.CharField(max_length=1)
    change_message = models.TextField()

    objects = LogEntryManager()

    class Meta:
        verbose_name = 'log entry'
        verbose_name_plural = 'log entries'
        ordering = ('-action_time',)

    def is_addition(self):
        return self.action == 'A'

    def is_change(self):
        return self.action == 'C'

    def is_deletion(self):
        return self.action == 'D'

    def is_task(self):
        return self.action == 'T'
