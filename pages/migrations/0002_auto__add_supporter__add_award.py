# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Supporter'
        db.create_table(u'pages_supporter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal(u'pages', ['Supporter'])

        # Adding model 'Award'
        db.create_table(u'pages_award', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('award_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('contest_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal(u'pages', ['Award'])

        # Adding M2M table for field supporters on 'Award'
        m2m_table_name = db.shorten_name(u'pages_award_supporters')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('award', models.ForeignKey(orm[u'pages.award'], null=False)),
            ('supporter', models.ForeignKey(orm[u'pages.supporter'], null=False))
        ))
        db.create_unique(m2m_table_name, ['award_id', 'supporter_id'])


    def backwards(self, orm):
        # Deleting model 'Supporter'
        db.delete_table(u'pages_supporter')

        # Deleting model 'Award'
        db.delete_table(u'pages_award')

        # Removing M2M table for field supporters on 'Award'
        db.delete_table(db.shorten_name(u'pages_award_supporters'))


    models = {
        u'pages.article': {
            'Meta': {'ordering': "['-published_on']", 'object_name': 'Article'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'outlet': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'published_on': ('django.db.models.fields.DateField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'pages.award': {
            'Meta': {'ordering': "('order',)", 'object_name': 'Award'},
            'award_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'contest_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'supporters': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['pages.Supporter']", 'symmetrical': 'False'})
        },
        u'pages.supporter': {
            'Meta': {'object_name': 'Supporter'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['pages']