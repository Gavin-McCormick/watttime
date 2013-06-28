# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SMSLog'
        db.create_table(u'workers_smslog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.User'])),
            ('localtime', self.gf('django.db.models.fields.DateTimeField')()),
            ('utctime', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal(u'workers', ['SMSLog'])


    def backwards(self, orm):
        # Deleting model 'SMSLog'
        db.delete_table(u'workers_smslog')


    models = {
        u'accounts.user': {
            'Meta': {'object_name': 'User'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone': ('django_localflavor_us.models.PhoneNumberField', [], {'max_length': '20'}),
            'state': ('django_localflavor_us.models.USStateField', [], {'default': "'MA'", 'max_length': '2'}),
            'userid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'verification_code': ('django.db.models.fields.IntegerField', [], {})
        },
        u'workers.smslog': {
            'Meta': {'object_name': 'SMSLog'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'localtime': ('django.db.models.fields.DateTimeField', [], {}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.User']"}),
            'utctime': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['workers']