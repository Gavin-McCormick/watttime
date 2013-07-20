# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ShiftRequest.baseline_fraction_green'
        db.add_column(u'watttime_shift_shiftrequest', 'baseline_fraction_green',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ShiftRequest.baseline_fraction_green'
        db.delete_column(u'watttime_shift_shiftrequest', 'baseline_fraction_green')


    models = {
        u'watttime_shift.shiftrequest': {
            'Meta': {'object_name': 'ShiftRequest'},
            'ba': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'baseline_fraction_green': ('django.db.models.fields.FloatField', [], {}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recommended_fraction_green': ('django.db.models.fields.FloatField', [], {}),
            'recommended_start': ('django.db.models.fields.DateTimeField', [], {}),
            'requested_by': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'time_range_hours': ('django.db.models.fields.FloatField', [], {'default': '12.0'}),
            'usage_hours': ('django.db.models.fields.FloatField', [], {'default': '3.0'})
        }
    }

    complete_apps = ['watttime_shift']