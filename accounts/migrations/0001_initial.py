# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'accounts_user', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('phone', self.gf('django_localflavor_us.models.PhoneNumberField')(max_length=20)),
            ('verification_code', self.gf('django.db.models.fields.IntegerField')()),
            ('is_verified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('userid', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('state', self.gf('django_localflavor_us.models.USStateField')(default='MA', max_length=2)),
        ))
        db.send_create_signal(u'accounts', ['User'])

        # Adding model 'UserProfile'
        db.create_table(u'accounts_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.User'])),
            ('goal', self.gf('accounts.multi_choice.MultiSelectField')(max_length=100)),
            ('text_freq', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('channel', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('ac', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('furnace', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('water_heater', self.gf('django.db.models.fields.IntegerField')(default=3)),
        ))
        db.send_create_signal(u'accounts', ['UserProfile'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'accounts_user')

        # Deleting model 'UserProfile'
        db.delete_table(u'accounts_userprofile')


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
        u'accounts.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'ac': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'channel': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'furnace': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'goal': ('accounts.multi_choice.MultiSelectField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text_freq': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'userid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['accounts.User']"}),
            'water_heater': ('django.db.models.fields.IntegerField', [], {'default': '3'})
        }
    }

    complete_apps = ['accounts']