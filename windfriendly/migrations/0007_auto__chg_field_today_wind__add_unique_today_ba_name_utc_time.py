# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Today', fields ['utc_time']
        db.delete_unique(u'windfriendly_today', ['utc_time'])

        # Removing unique constraint on 'Today', fields ['local_time']
        db.delete_unique(u'windfriendly_today', ['local_time'])


        # Changing field 'Today.wind'
        db.alter_column(u'windfriendly_today', 'wind', self.gf('django.db.models.fields.FloatField')(null=True))
        # Adding unique constraint on 'Today', fields ['ba_name', 'utc_time']
        db.create_unique(u'windfriendly_today', ['ba_name', 'utc_time'])


    def backwards(self, orm):
        # Removing unique constraint on 'Today', fields ['ba_name', 'utc_time']
        db.delete_unique(u'windfriendly_today', ['ba_name', 'utc_time'])


        # Changing field 'Today.wind'
        db.alter_column(u'windfriendly_today', 'wind', self.gf('django.db.models.fields.FloatField')(default=0))
        # Adding unique constraint on 'Today', fields ['local_time']
        db.create_unique(u'windfriendly_today', ['local_time'])

        # Adding unique constraint on 'Today', fields ['utc_time']
        db.create_unique(u'windfriendly_today', ['utc_time'])


    models = {
        'windfriendly.bpa': {
            'Meta': {'object_name': 'BPA'},
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'hydro': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'load': ('django.db.models.fields.IntegerField', [], {}),
            'thermal': ('django.db.models.fields.IntegerField', [], {}),
            'wind': ('django.db.models.fields.IntegerField', [], {})
        },
        'windfriendly.caiso': {
            'Meta': {'object_name': 'CAISO'},
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'date_extracted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'forecast_code': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'load': ('django.db.models.fields.FloatField', [], {}),
            'solar': ('django.db.models.fields.FloatField', [], {}),
            'wind': ('django.db.models.fields.FloatField', [], {})
        },
        'windfriendly.meterreading': {
            'Meta': {'object_name': 'MeterReading'},
            'cost': ('django.db.models.fields.FloatField', [], {}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'energy': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'userid': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['windfriendly.User']"})
        },
        'windfriendly.miso': {
            'Meta': {'object_name': 'MISO'},
            'coal': ('django.db.models.fields.FloatField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'date_extracted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'forecast_code': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'gas': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'load': ('django.db.models.fields.FloatField', [], {}),
            'nuclear': ('django.db.models.fields.FloatField', [], {}),
            'other_gen': ('django.db.models.fields.FloatField', [], {}),
            'wind': ('django.db.models.fields.FloatField', [], {})
        },
        'windfriendly.ne': {
            'Meta': {'object_name': 'NE'},
            'coal': ('django.db.models.fields.FloatField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'gas': ('django.db.models.fields.FloatField', [], {}),
            'hydro': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marginal_fuel': ('django.db.models.fields.IntegerField', [], {}),
            'nuclear': ('django.db.models.fields.FloatField', [], {}),
            'other_fossil': ('django.db.models.fields.FloatField', [], {}),
            'other_renewable': ('django.db.models.fields.FloatField', [], {})
        },
        'windfriendly.pjm': {
            'Meta': {'object_name': 'PJM'},
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'date_extracted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'forecast_code': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'load': ('django.db.models.fields.IntegerField', [], {}),
            'wind': ('django.db.models.fields.IntegerField', [], {})
        },
        'windfriendly.today': {
            'Meta': {'unique_together': "(('utc_time', 'ba_name'),)", 'object_name': 'Today'},
            'ba_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'coal': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'forecast_code': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'hydro': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_time': ('django.db.models.fields.DateTimeField', [], {}),
            'marginal_fuel': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'natgas': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'nuclear': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'other_clean': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'other_fossil': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'other_unknown': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'percent_dirty': ('django.db.models.fields.FloatField', [], {}),
            'percent_green': ('django.db.models.fields.FloatField', [], {}),
            'solar': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'total_gen': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'total_load': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'utc_time': ('django.db.models.fields.DateTimeField', [], {}),
            'wind': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'windfriendly.user': {
            'Meta': {'object_name': 'User'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['windfriendly']