# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'accounts_user')

        # Deleting field 'UserProfile.ac'
        db.delete_column(u'accounts_userprofile', 'ac')

        # Deleting field 'UserProfile.goal'
        db.delete_column(u'accounts_userprofile', 'goal')

        # Deleting field 'UserProfile.water_heater'
        db.delete_column(u'accounts_userprofile', 'water_heater')

        # Deleting field 'UserProfile.furnace'
        db.delete_column(u'accounts_userprofile', 'furnace')

        # Deleting field 'UserProfile.userid'
        db.delete_column(u'accounts_userprofile', 'userid_id')

        # Deleting field 'UserProfile.channel'
        db.delete_column(u'accounts_userprofile', 'channel')

        # Deleting field 'UserProfile.text_freq'
        db.delete_column(u'accounts_userprofile', 'text_freq')

        # Adding field 'UserProfile.user'
        db.add_column(u'accounts_userprofile', 'user',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=67, to=orm['auth.User'], unique=True),
                      keep_default=False)

        # Adding field 'UserProfile.magic_login_code'
        db.add_column(u'accounts_userprofile', 'magic_login_code',
                      self.gf('django.db.models.fields.IntegerField')(default=42),
                      keep_default=False)

        # Adding field 'UserProfile.name'
        db.add_column(u'accounts_userprofile', 'name',
                      self.gf('django.db.models.fields.CharField')(default='Hiya', max_length=100),
                      keep_default=False)

        # Adding field 'UserProfile.email'
        db.add_column(u'accounts_userprofile', 'email',
                      self.gf('django.db.models.fields.EmailField')(default='Not an email @ adsf', max_length=75),
                      keep_default=False)

        # Adding field 'UserProfile.phone'
        db.add_column(u'accounts_userprofile', 'phone',
                      self.gf('django_localflavor_us.models.PhoneNumberField')(default='12233213', max_length=20),
                      keep_default=False)

        # Adding field 'UserProfile.verification_code'
        db.add_column(u'accounts_userprofile', 'verification_code',
                      self.gf('django.db.models.fields.IntegerField')(default=123213),
                      keep_default=False)

        # Adding field 'UserProfile.is_verified'
        db.add_column(u'accounts_userprofile', 'is_verified',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'UserProfile.state'
        db.add_column(u'accounts_userprofile', 'state',
                      self.gf('django_localflavor_us.models.USStateField')(default='CA', max_length=2),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'User'
        db.create_table(u'accounts_user', (
            ('phone', self.gf('django_localflavor_us.models.PhoneNumberField')(max_length=20)),
            ('state', self.gf('django_localflavor_us.models.USStateField')(default='MA', max_length=2)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('verification_code', self.gf('django.db.models.fields.IntegerField')()),
            ('is_verified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('userid', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
        ))
        db.send_create_signal(u'accounts', ['User'])

        # Adding field 'UserProfile.ac'
        db.add_column(u'accounts_userprofile', 'ac',
                      self.gf('django.db.models.fields.IntegerField')(default=3),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'UserProfile.goal'
        raise RuntimeError("Cannot reverse this migration. 'UserProfile.goal' and its values cannot be restored.")
        # Adding field 'UserProfile.water_heater'
        db.add_column(u'accounts_userprofile', 'water_heater',
                      self.gf('django.db.models.fields.IntegerField')(default=3),
                      keep_default=False)

        # Adding field 'UserProfile.furnace'
        db.add_column(u'accounts_userprofile', 'furnace',
                      self.gf('django.db.models.fields.IntegerField')(default=3),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'UserProfile.userid'
        raise RuntimeError("Cannot reverse this migration. 'UserProfile.userid' and its values cannot be restored.")
        # Adding field 'UserProfile.channel'
        db.add_column(u'accounts_userprofile', 'channel',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'UserProfile.text_freq'
        db.add_column(u'accounts_userprofile', 'text_freq',
                      self.gf('django.db.models.fields.IntegerField')(default=3),
                      keep_default=False)

        # Deleting field 'UserProfile.user'
        db.delete_column(u'accounts_userprofile', 'user_id')

        # Deleting field 'UserProfile.magic_login_code'
        db.delete_column(u'accounts_userprofile', 'magic_login_code')

        # Deleting field 'UserProfile.name'
        db.delete_column(u'accounts_userprofile', 'name')

        # Deleting field 'UserProfile.email'
        db.delete_column(u'accounts_userprofile', 'email')

        # Deleting field 'UserProfile.phone'
        db.delete_column(u'accounts_userprofile', 'phone')

        # Deleting field 'UserProfile.verification_code'
        db.delete_column(u'accounts_userprofile', 'verification_code')

        # Deleting field 'UserProfile.is_verified'
        db.delete_column(u'accounts_userprofile', 'is_verified')

        # Deleting field 'UserProfile.state'
        db.delete_column(u'accounts_userprofile', 'state')


    models = {
        u'accounts.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'magic_login_code': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone': ('django_localflavor_us.models.PhoneNumberField', [], {'max_length': '20'}),
            'state': ('django_localflavor_us.models.USStateField', [], {'default': "'CA'", 'max_length': '2'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'verification_code': ('django.db.models.fields.IntegerField', [], {})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['accounts']
