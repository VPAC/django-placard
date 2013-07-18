# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

import placard.ldap_bonds

class Migration(DataMigration):

    def forwards(self, orm):
        if db.dry_run:
            return

        master = placard.ldap_bonds.master

        last_uid = None
        for obj in master.accounts():
            if last_uid is None or obj.uidNumber > last_uid:
                last_uid = obj.uidNumber
        if last_uid is not None:
            entry, created = orm.counters.objects.get_or_create(name="uidNumber", defaults = { 'count': last_uid + 1 })
            if not created:
                entry.count = last_uid + 1
                entry.save()

        last_gid = None
        for obj in master.groups():
            if last_gid is None or obj.gidNumber > last_gid:
                last_gid = obj.gidNumber
        if last_gid is not None:
            entry, created = orm.counters.objects.get_or_create(name="gidNumber", defaults = { 'count': last_gid + 1 })
            if not created:
                entry.count = last_gid + 1
                entry.save()

    def backwards(self, orm):
        pass


    models = {
        'placard.counters': {
            'Meta': {'object_name': 'counters'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'})
        }
    }

    complete_apps = ['placard']
    symmetrical = True
