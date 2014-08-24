# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Article'
        db.create_table(u'pages_article', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('published_on', self.gf('django.db.models.fields.DateField')()),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('outlet', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'pages', ['Article'])


    def backwards(self, orm):
        # Deleting model 'Article'
        db.delete_table(u'pages_article')


    models = {
        u'pages.article': {
            'Meta': {'ordering': "['-published_on']", 'object_name': 'Article'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'outlet': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'published_on': ('django.db.models.fields.DateField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        }
    }

    complete_apps = ['pages']