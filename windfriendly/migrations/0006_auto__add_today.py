# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Today'
        db.create_table(u'windfriendly_today', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ba_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('total_load', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('total_gen', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('wind', self.gf('django.db.models.fields.FloatField')()),
            ('solar', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('hydro', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('other_clean', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('coal', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('natgas', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('other_fossil', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('nuclear', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('other_unknown', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('percent_green', self.gf('django.db.models.fields.FloatField')()),
            ('percent_dirty', self.gf('django.db.models.fields.FloatField')()),
            ('forecast_code', self.gf('django.db.models.fields.IntegerField')()),
            ('marginal_fuel', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('utc_time', self.gf('django.db.models.fields.DateTimeField')(unique=True)),
            ('local_time', self.gf('django.db.models.fields.DateTimeField')(unique=True)),
        ))
        db.send_create_signal('windfriendly', ['Today'])


    def backwards(self, orm):
        # Deleting model 'Today'
        db.delete_table(u'windfriendly_today')


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
            'Meta': {'object_name': 'Today'},
            'ba_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'coal': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'forecast_code': ('django.db.models.fields.IntegerField', [], {}),
            'hydro': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_time': ('django.db.models.fields.DateTimeField', [], {'unique': 'True'}),
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
            'utc_time': ('django.db.models.fields.DateTimeField', [], {'unique': 'True'}),
            'wind': ('django.db.models.fields.FloatField', [], {})
        },
        'windfriendly.user': {
            'Meta': {'object_name': 'User'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['windfriendly']