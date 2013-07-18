# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'counters'
        db.delete_table(u'placard_counters')


    def backwards(self, orm):
        # Adding model 'counters'
        db.create_table(u'placard_counters', (
            ('count', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20, db_index=True)),
        ))
        db.send_create_signal('placard', ['counters'])


    models = {
        
    }

    complete_apps = ['placard']