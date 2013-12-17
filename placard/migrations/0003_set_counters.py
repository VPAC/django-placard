# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):
    depends_on = (
        ("methods", "0001_initial"),
    )

    # the following update changes the schema and breaks this update
    needed_by = (
        ("methods", "0002_auto__add_field_counters_scheme"),
    )

    def forwards(self, orm):
        "Write your forwards methods here."
        if db.dry_run:
            return

        for i in orm.counters.objects.all():
            orm['methods.counters'].objects.get_or_create(name=i.name, defaults = { 'count':  i.count })

    def backwards(self, orm):
        "Write your backwards methods here."
        if db.dry_run:
            return

        for i in orm['methods.counters'].objects.all():
            orm.counters.objects.get_or_create(name=i.name, defaults = { 'count':  i.count })

    models = {
        u'methods.counters': {
            'Meta': {'object_name': 'counters', 'db_table': "'tldap_counters'"},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'})
        },
        u'placard.counters': {
            'Meta': {'object_name': 'counters'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'})
        },
    }

    complete_apps = ['methods', 'placard']
    symmetrical = True
