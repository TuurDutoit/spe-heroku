# Generated by Django 2.2.1 on 2019-05-14 09:17

from django.db import migrations, models
import heroku_connect.db.models.base
import heroku_connect.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_auto_20190509_1258'),
    ]

    operations = [
        migrations.CreateModel(
            name='Engine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': [('recalculate', "Can start a recalculation of a user's recommendations")],
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Opportunity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sf_id', heroku_connect.db.models.fields.ID(db_column='sfid', db_index=True, editable=False, max_length=18, null=True, sf_field_name='Id', unique=True, upsert=False)),
                ('system_mod_stamp', heroku_connect.db.models.fields.DateTime(db_column='systemmodstamp', db_index=True, null=True, sf_field_name='SystemModstamp', upsert=False)),
                ('is_deleted', heroku_connect.db.models.fields.Checkbox(db_column='isdeleted', sf_field_name='IsDeleted', upsert=False)),
                ('_hc_lastop', models.CharField(editable=False, help_text='Indicates the last sync operation Heroku Connect performed on the record', max_length=32, null=True)),
                ('_hc_err', models.TextField(editable=False, help_text='If the last sync operation by Heroku Connect resulted in an error then this column will contain a JSON object containing more information about the error', max_length=1024, null=True)),
                ('Amount', heroku_connect.db.models.fields.Currency(db_column='amount', decimal_places=2, max_digits=18, null=True, sf_field_name='Amount', upsert=False)),
                ('CloseDate', heroku_connect.db.models.fields.Date(db_column='closedate', null=True, sf_field_name='CloseDate', upsert=False)),
                ('CreatedDate', heroku_connect.db.models.fields.Date(db_column='createddate', null=True, sf_field_name='CreatedDate', upsert=False)),
                ('CurrentGenerators', heroku_connect.db.models.fields.Text(db_column='currentgenerators__c', max_length=100, null=True, sf_field_name='CurrentGenerators__c', upsert=False)),
                ('DeliveryInstallationStatus', heroku_connect.db.models.fields.Picklist(choices=[('In progress', 'In progress'), ('Yet to begin', 'Yet to begin'), ('Completed', 'Completed')], db_column='deliveryinstallationstatus__c', max_length=255, null=True, sf_field_name='DeliveryInstallationStatus__c', upsert=False)),
                ('ExpectedRevenue', heroku_connect.db.models.fields.Currency(db_column='expectedrevenue', decimal_places=2, max_digits=18, null=True, sf_field_name='ExpectedRevenue', upsert=False)),
                ('HasOpenActivity', heroku_connect.db.models.fields.Checkbox(db_column='hasopenactivity', sf_field_name='HasOpenActivity', upsert=False)),
                ('HasOverdueTask', heroku_connect.db.models.fields.Checkbox(db_column='hasoverduetask', sf_field_name='HasOverdueTask', upsert=False)),
                ('IsClosed', heroku_connect.db.models.fields.Checkbox(db_column='isclosed', sf_field_name='IsClosed', upsert=False)),
                ('IsPrivate', heroku_connect.db.models.fields.Checkbox(db_column='isprivate', sf_field_name='IsPrivate', upsert=False)),
                ('IsWon', heroku_connect.db.models.fields.Checkbox(db_column='iswon', sf_field_name='IsWon', upsert=False)),
                ('LastActivityDate', heroku_connect.db.models.fields.Date(db_column='lastactivitydate', null=True, sf_field_name='LastActivityDate', upsert=False)),
                ('LastReferencedDate', heroku_connect.db.models.fields.DateTime(db_column='lastreferenceddate', null=True, sf_field_name='LastReferencedDate', upsert=False)),
                ('LastViewedDate', heroku_connect.db.models.fields.DateTime(db_column='lastvieweddate', null=True, sf_field_name='LastViewedDate', upsert=False)),
                ('LeadSource', heroku_connect.db.models.fields.Picklist(choices=[('Web', 'Web'), ('Phone Inquiry', 'Phone Inquiry'), ('Partner Referral', 'Partner Referral'), ('Purchased List', 'Purchased List'), ('Other', 'Other')], db_column='leadsource', max_length=255, null=True, sf_field_name='LeadSource', upsert=False)),
                ('MainCompetitors', heroku_connect.db.models.fields.Text(db_column='maincompetitors__c', max_length=100, null=True, sf_field_name='MainCompetitors__c', upsert=False)),
                ('Name', heroku_connect.db.models.fields.Text(db_column='name', max_length=120, null=True, sf_field_name='Name', upsert=False)),
                ('NextStep', heroku_connect.db.models.fields.Text(db_column='nextstep', max_length=255, null=True, sf_field_name='NextStep', upsert=False)),
                ('OrderNumber', heroku_connect.db.models.fields.Text(db_column='ordernumber__c', max_length=8, null=True, sf_field_name='OrderNumber__c', upsert=False)),
                ('Probability', heroku_connect.db.models.fields.Percent(db_column='probability', decimal_places=0, max_digits=3, null=True, sf_field_name='Probability', upsert=False)),
                ('StageName', heroku_connect.db.models.fields.Picklist(choices=[('Prospecting', 'Prospecting'), ('Qualification', 'Qualification'), ('Needs Analysis', 'Needs Analysis'), ('Value Proposition', 'Value Proposition'), ('Id. Decision Makers', 'Id. Decision Makers'), ('Perception Analysis', 'Perception Analysis'), ('Proposal/Price Quote', 'Proposal/Price Quote'), ('Negotiation/Review', 'Negotiation/Review'), ('Closed Won', 'Closed Won'), ('Closed Lost', 'Closed Lost')], db_column='stagename', max_length=255, null=True, sf_field_name='StageName', upsert=False)),
                ('TotalOpportunityQuantity', heroku_connect.db.models.fields.Number(db_column='totalopportunityquantity', decimal_places=2, max_digits=18, null=True, sf_field_name='TotalOpportunityQuantity', upsert=False)),
                ('TrackingNumber', heroku_connect.db.models.fields.Text(db_column='trackingnumber__c', max_length=12, null=True, sf_field_name='TrackingNumber__c', upsert=False)),
                ('Type', heroku_connect.db.models.fields.Picklist(choices=[('Existing Customer - Upgrade', 'Existing Customer - Upgrade'), ('Existing Customer - Replacement', 'Existing Customer - Replacement'), ('Existing Customer - Downgrade', 'Existing Customer - Downgrade'), ('New Customer', 'New Customer')], db_column='type', max_length=255, null=True, sf_field_name='Type', upsert=False)),
            ],
            options={
                'verbose_name_plural': 'Opportunities',
                'db_table': 'salesforce"."opportunity',
                'managed': False,
            },
            bases=(heroku_connect.db.models.base._HerokuConnectSnitchMixin, models.Model),
        ),
    ]
