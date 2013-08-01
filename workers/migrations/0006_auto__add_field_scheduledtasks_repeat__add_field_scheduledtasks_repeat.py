# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ScheduledTasks.repeat'
        db.add_column(u'workers_scheduledtasks', 'repeat',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'ScheduledTasks.repeat_interval'
        db.add_column(u'workers_scheduledtasks', 'repeat_interval',
                      self.gf('django.db.models.fields.IntegerField')(default=86400),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ScheduledTasks.repeat'
        db.delete_column(u'workers_scheduledtasks', 'repeat')

        # Deleting field 'ScheduledTasks.repeat_interval'
        db.delete_column(u'workers_scheduledtasks', 'repeat_interval')


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
        u'workers.keyvalue': {
            'Meta': {'object_name': 'KeyValue'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.TextField', [], {'unique': 'True'}),
            'tipo': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'value': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'})
        },
        u'workers.lastmessagesent': {
            'Meta': {'object_name': 'LastMessageSent'},
            'category': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'workers.scheduledtasks': {
            'Meta': {'object_name': 'ScheduledTasks'},
            'command': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'repeat': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'repeat_interval': ('django.db.models.fields.IntegerField', [], {'default': '86400'})
        }
    }

    complete_apps = ['workers']