# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DebugMessage'
        db.create_table(u'windfriendly_debugmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal(u'windfriendly', ['DebugMessage'])

        # Adding model 'CAISO'
        db.create_table(u'windfriendly_caiso', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('load', self.gf('django.db.models.fields.FloatField')()),
            ('wind', self.gf('django.db.models.fields.FloatField')()),
            ('solar', self.gf('django.db.models.fields.FloatField')()),
            ('forecast_code', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('date_extracted', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
        ))
        db.send_create_signal(u'windfriendly', ['CAISO'])

        # Adding model 'BPA'
        db.create_table(u'windfriendly_bpa', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('load', self.gf('django.db.models.fields.IntegerField')()),
            ('wind', self.gf('django.db.models.fields.IntegerField')()),
            ('thermal', self.gf('django.db.models.fields.IntegerField')()),
            ('hydro', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
        ))
        db.send_create_signal(u'windfriendly', ['BPA'])

        # Adding model 'NE'
        db.create_table(u'windfriendly_ne', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('gas', self.gf('django.db.models.fields.FloatField')()),
            ('nuclear', self.gf('django.db.models.fields.FloatField')()),
            ('hydro', self.gf('django.db.models.fields.FloatField')()),
            ('coal', self.gf('django.db.models.fields.FloatField')()),
            ('other_renewable', self.gf('django.db.models.fields.FloatField')()),
            ('other_fossil', self.gf('django.db.models.fields.FloatField')()),
            ('marginal_fuel', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
        ))
        db.send_create_signal(u'windfriendly', ['NE'])

        # Adding model 'Normalized'
        db.create_table(u'windfriendly_normalized', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('balancing_authority', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('total_watts', self.gf('django.db.models.fields.IntegerField')()),
            ('percent_clean', self.gf('django.db.models.fields.FloatField')()),
            ('curtailed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
        ))
        db.send_create_signal(u'windfriendly', ['Normalized'])

        # Adding model 'User'
        db.create_table(u'windfriendly_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'windfriendly', ['User'])

        # Adding model 'MeterReading'
        db.create_table(u'windfriendly_meterreading', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['windfriendly.User'])),
            ('energy', self.gf('django.db.models.fields.FloatField')()),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
            ('start', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('cost', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'windfriendly', ['MeterReading'])


    def backwards(self, orm):
        # Deleting model 'DebugMessage'
        db.delete_table(u'windfriendly_debugmessage')

        # Deleting model 'CAISO'
        db.delete_table(u'windfriendly_caiso')

        # Deleting model 'BPA'
        db.delete_table(u'windfriendly_bpa')

        # Deleting model 'NE'
        db.delete_table(u'windfriendly_ne')

        # Deleting model 'Normalized'
        db.delete_table(u'windfriendly_normalized')

        # Deleting model 'User'
        db.delete_table(u'windfriendly_user')

        # Deleting model 'MeterReading'
        db.delete_table(u'windfriendly_meterreading')


    models = {
        u'windfriendly.bpa': {
            'Meta': {'object_name': 'BPA'},
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'hydro': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'load': ('django.db.models.fields.IntegerField', [], {}),
            'thermal': ('django.db.models.fields.IntegerField', [], {}),
            'wind': ('django.db.models.fields.IntegerField', [], {})
        },
        u'windfriendly.caiso': {
            'Meta': {'object_name': 'CAISO'},
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'date_extracted': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'forecast_code': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'load': ('django.db.models.fields.FloatField', [], {}),
            'solar': ('django.db.models.fields.FloatField', [], {}),
            'wind': ('django.db.models.fields.FloatField', [], {})
        },
        u'windfriendly.debugmessage': {
            'Meta': {'object_name': 'DebugMessage'},
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '300'})
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
        u'windfriendly.ne': {
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
        u'windfriendly.normalized': {
            'Meta': {'object_name': 'Normalized'},
            'balancing_authority': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'curtailed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent_clean': ('django.db.models.fields.FloatField', [], {}),
            'total_watts': ('django.db.models.fields.IntegerField', [], {})
        },
        u'windfriendly.user': {
            'Meta': {'object_name': 'User'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['windfriendly']