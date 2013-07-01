# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TwilioSMSEvent'
        db.create_table(u'sms_tools_twiliosmsevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.User'])),
            ('response_to', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sms_tools.TwilioSMSEvent'], null=True)),
            ('to_number', self.gf('django_localflavor_us.models.PhoneNumberField')(max_length=20)),
            ('from_number', self.gf('django_localflavor_us.models.PhoneNumberField')(max_length=20)),
            ('body', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('msg_type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'sms_tools', ['TwilioSMSEvent'])


    def backwards(self, orm):
        # Deleting model 'TwilioSMSEvent'
        db.delete_table(u'sms_tools_twiliosmsevent')


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
        u'sms_tools.twiliosmsevent': {
            'Meta': {'object_name': 'TwilioSMSEvent'},
            'body': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_number': ('django_localflavor_us.models.PhoneNumberField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'msg_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'response_to': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sms_tools.TwilioSMSEvent']", 'null': 'True'}),
            'to_number': ('django_localflavor_us.models.PhoneNumberField', [], {'max_length': '20'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.User']"})
        }
    }

    complete_apps = ['sms_tools']