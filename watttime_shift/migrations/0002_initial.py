# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ShiftRequest'
        db.create_table(u'watttime_shift_shiftrequest', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('requested_by', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('usage_hours', self.gf('django.db.models.fields.FloatField')(default=3.0)),
            ('time_range_hours', self.gf('django.db.models.fields.FloatField')(default=12.0)),
            ('recommended_start', self.gf('django.db.models.fields.DateTimeField')()),
            ('fraction_green', self.gf('django.db.models.fields.FloatField')()),
            ('ba', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'watttime_shift', ['ShiftRequest'])


    def backwards(self, orm):
        # Deleting model 'ShiftRequest'
        db.delete_table(u'watttime_shift_shiftrequest')


    models = {
        u'watttime_shift.shiftrequest': {
            'Meta': {'object_name': 'ShiftRequest'},
            'ba': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'fraction_green': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recommended_start': ('django.db.models.fields.DateTimeField', [], {}),
            'requested_by': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'time_range_hours': ('django.db.models.fields.FloatField', [], {'default': '12.0'}),
            'usage_hours': ('django.db.models.fields.FloatField', [], {'default': '3.0'})
        }
    }

    complete_apps = ['watttime_shift']