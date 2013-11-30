# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        for row in orm.NE.objects.all():
            row.total_MW = row.gas + row.nuclear + row.hydro + row.coal + row.other_renewable + row.other_fossil
            row.save()
        for row in orm.CAISO.objects.all():
            row.total_MW = row.load
            row.save()
        for row in orm.BPA.objects.all():
            row.total_MW = row.wind + row.hydro + row.thermal
            row.save()
        for row in orm.MISO.objects.all():
            row.total_MW = row.gas + row.coal + row.nuclear + row.wind + row.other_gen
            row.save()
        for row in orm.PJM.objects.all():
            row.total_MW = row.load
            row.save()

    def backwards(self, orm):
        "Write your backwards methods here."
        pass

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
    symmetrical = True
