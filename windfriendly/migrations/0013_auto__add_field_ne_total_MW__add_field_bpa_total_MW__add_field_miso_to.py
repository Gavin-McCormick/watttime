# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'NE.total_MW'
        db.add_column(u'windfriendly_ne', 'total_MW',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'BPA.total_MW'
        db.add_column(u'windfriendly_bpa', 'total_MW',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'MISO.total_MW'
        db.add_column(u'windfriendly_miso', 'total_MW',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'PJM.total_MW'
        db.add_column(u'windfriendly_pjm', 'total_MW',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)

        # Adding field 'CAISO.total_MW'
        db.add_column(u'windfriendly_caiso', 'total_MW',
                      self.gf('django.db.models.fields.FloatField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'NE.total_MW'
        db.delete_column(u'windfriendly_ne', 'total_MW')

        # Deleting field 'BPA.total_MW'
        db.delete_column(u'windfriendly_bpa', 'total_MW')

        # Deleting field 'MISO.total_MW'
        db.delete_column(u'windfriendly_miso', 'total_MW')

        # Deleting field 'PJM.total_MW'
        db.delete_column(u'windfriendly_pjm', 'total_MW')

        # Deleting field 'CAISO.total_MW'
        db.delete_column(u'windfriendly_caiso', 'total_MW')


    models = {
        u'windfriendly.bpa': {
            'Meta': {'object_name': 'BPA'},
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'date_extracted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'forecast_code': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fraction_clean': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'hydro': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'load': ('django.db.models.fields.IntegerField', [], {}),
            'thermal': ('django.db.models.fields.IntegerField', [], {}),
            'total_MW': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'wind': ('django.db.models.fields.IntegerField', [], {})
        },
        u'windfriendly.caiso': {
            'Meta': {'object_name': 'CAISO'},
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'date_extracted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'forecast_code': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fraction_clean': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'load': ('django.db.models.fields.FloatField', [], {}),
            'solar': ('django.db.models.fields.FloatField', [], {}),
            'total_MW': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'wind': ('django.db.models.fields.FloatField', [], {})
        },
        u'windfriendly.meterreading': {
            'Meta': {'object_name': 'MeterReading'},
            'cost': ('django.db.models.fields.FloatField', [], {}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'energy': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'userid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['windfriendly.User']"})
        },
        u'windfriendly.miso': {
            'Meta': {'object_name': 'MISO'},
            'coal': ('django.db.models.fields.FloatField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'date_extracted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'forecast_code': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fraction_clean': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'gas': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'load': ('django.db.models.fields.FloatField', [], {}),
            'nuclear': ('django.db.models.fields.FloatField', [], {}),
            'other_gen': ('django.db.models.fields.FloatField', [], {}),
            'total_MW': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'wind': ('django.db.models.fields.FloatField', [], {})
        },
        u'windfriendly.ne': {
            'Meta': {'object_name': 'NE'},
            'coal': ('django.db.models.fields.FloatField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'date_extracted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'forecast_code': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fraction_clean': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'gas': ('django.db.models.fields.FloatField', [], {}),
            'hydro': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marginal_fuel': ('django.db.models.fields.IntegerField', [], {}),
            'nuclear': ('django.db.models.fields.FloatField', [], {}),
            'other_fossil': ('django.db.models.fields.FloatField', [], {}),
            'other_renewable': ('django.db.models.fields.FloatField', [], {}),
            'total_MW': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'windfriendly.pjm': {
            'Meta': {'object_name': 'PJM'},
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'date_extracted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'forecast_code': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fraction_clean': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'load': ('django.db.models.fields.IntegerField', [], {}),
            'total_MW': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'wind': ('django.db.models.fields.IntegerField', [], {})
        },
        u'windfriendly.user': {
            'Meta': {'object_name': 'User'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['windfriendly']