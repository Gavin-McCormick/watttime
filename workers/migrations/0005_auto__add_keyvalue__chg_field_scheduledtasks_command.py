# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'KeyValue'
        db.create_table(u'workers_keyvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.TextField')(unique=True)),
            ('value', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('tipo', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'workers', ['KeyValue'])


        # Changing field 'ScheduledTasks.command'
        db.alter_column(u'workers_scheduledtasks', 'command', self.gf('django.db.models.fields.TextField')())

    def backwards(self, orm):
        # Deleting model 'KeyValue'
        db.delete_table(u'workers_keyvalue')


        # Changing field 'ScheduledTasks.command'
        db.alter_column(u'workers_scheduledtasks', 'command', self.gf('django.db.models.fields.CharField')(max_length=300))

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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['workers']