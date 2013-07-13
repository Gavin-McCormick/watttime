# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'SMSLog'
        db.delete_table(u'workers_smslog')

        # Adding model 'ScheduledTasks'
        db.create_table(u'workers_scheduledtasks', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('command', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal(u'workers', ['ScheduledTasks'])

        # Adding model 'DailyReport'
        db.create_table(u'workers_dailyreport', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal(u'workers', ['DailyReport'])

        # Adding model 'DebugMessage'
        db.create_table(u'workers_debugmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal(u'workers', ['DebugMessage'])


    def backwards(self, orm):
        # Adding model 'SMSLog'
        db.create_table(u'workers_smslog', (
            ('utctime', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.User'])),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=150)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('localtime', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'workers', ['SMSLog'])

        # Deleting model 'ScheduledTasks'
        db.delete_table(u'workers_scheduledtasks')

        # Deleting model 'DailyReport'
        db.delete_table(u'workers_dailyreport')

        # Deleting model 'DebugMessage'
        db.delete_table(u'workers_debugmessage')


    models = {
        u'workers.dailyreport': {
            'Meta': {'object_name': 'DailyReport'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        u'workers.debugmessage': {
            'Meta': {'object_name': 'DebugMessage'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        u'workers.scheduledtasks': {
            'Meta': {'object_name': 'ScheduledTasks'},
            'command': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['workers']