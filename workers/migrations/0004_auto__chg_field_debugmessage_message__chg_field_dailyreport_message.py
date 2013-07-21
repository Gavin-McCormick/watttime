# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'DebugMessage.message'
        db.alter_column(u'workers_debugmessage', 'message', self.gf('django.db.models.fields.TextField')())

        # Changing field 'DailyReport.message'
        db.alter_column(u'workers_dailyreport', 'message', self.gf('django.db.models.fields.TextField')())

    def backwards(self, orm):

        # Changing field 'DebugMessage.message'
        db.alter_column(u'workers_debugmessage', 'message', self.gf('django.db.models.fields.CharField')(max_length=300))

        # Changing field 'DailyReport.message'
        db.alter_column(u'workers_dailyreport', 'message', self.gf('django.db.models.fields.CharField')(max_length=300))

    models = {
        u'workers.dailyreport': {
            'Meta': {'object_name': 'DailyReport'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {})
        },
        u'workers.debugmessage': {
            'Meta': {'object_name': 'DebugMessage'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {})
        },
        u'workers.lastmessagesent': {
            'Meta': {'object_name': 'LastMessageSent'},
            'category': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'workers.scheduledtasks': {
            'Meta': {'object_name': 'ScheduledTasks'},
            'command': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['workers']