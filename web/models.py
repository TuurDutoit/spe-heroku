from django.db import models
from django.db.models import Case, When, Value
from django.db.models.functions import Cast
from heroku_connect.db import models as sf
from computed_field.fields import ComputedField

STAGES = (
    ('Prospecting', 'Prospecting'),
    ('Qualification', 'Qualification'),
    ('Needs Analysis', 'Needs Analysis'),
    ('Value Proposition', 'Value Proposition'),
    ('Id. Decision Makers', 'Id. Decision Makers'),
    ('Perception Analysis', 'Perception Analysis'),
    ('Proposal/Price Quote', 'Proposal/Price Quote'),
    ('Negotiation/Review', 'Negotiation/Review'),
    ('Closed Won', 'Closed Won'),
    ('Closed Lost', 'Closed Lost')
)

DELIVERY_INSTALLATION_STATES = (
    ('In progress', 'In progress'),
    ('Yet to begin', 'Yet to begin'),
    ('Completed', 'Completed')
)

SOURCES = (
    ('Web', 'Web'),
    ('Phone Inquiry', 'Phone Inquiry'),
    ('Partner Referral', 'Partner Referral'),
    ('Purchased List', 'Purchased List'),
    ('Other', 'Other')
)

CUSTOMER_PRIORITIES = (
    ('Low', 'Low'),
    ('MEDIUM', 'MEDIUM'),
    ('HIGH', 'HIGH')
)

RATINGS = (
    ('Hot', 'Hot'),
    ('Warm', 'Warm'),
    ('Cold', 'Cold')
)

SLAS = (
    ('Gold', 'Gold'),
    ('Silver', 'Silver'),
    ('Platinum', 'Platinum'),
    ('Bronze', 'Bronze')
)

ACCOUNT_TYPES = (
    ('Prospect', 'Prospect'),
    ('Customer - Direct', 'Customer - Direct'),
    ('Customer - Channel', 'Customer - Channel'),
    ('Channel Partner / Reseller', 'Channel Partner / Reseller'),
    ('Installation Partner', 'Installation Partner'),
    ('Technology Partner', 'Technology Partner'),
    ('Other', 'Other')
)

OPP_TYPES = (
    ('Existing Customer - Upgrade', 'Existing Customer - Upgrade'),
    ('Existing Customer - Replacement', 'Existing Customer - Replacement'),
    ('Existing Customer - Downgrade', 'Existing Customer - Downgrade'),
    ('New Customer', 'New Customer')
)

BOOL_PICKLIST = (
    ('Yes', 'Yes'),
    ('No', 'No')
)

MAYBE_BOOL_PICKLIST = (
    ('Yes', 'Yes'),
    ('No', 'No'),
    ('Maybe', 'Maybe')
)

# Taken from https://github.com/heroku/django-heroku-connect/blob/master/connect_client/models.py#L60-L96
ADDR_SUBFIELDS = (
    ('Street', sf.Text, {
        'max_length': 255,
        'null': True,
        'blank': True,
    }),
    ('City', sf.Text, {
        'max_length': 40,
        'null': True,
        'blank': True,
    }),
    ('State', sf.Text, {
        'max_length': 80,
        'null': True,
        'blank': True,
    }),
    ('PostalCode', sf.Text, {
        'max_length': 20,
        'null': True,
        'blank': True,
    }),
    ('Country', sf.Text, {
        'max_length': 80,
        'null': True,
        'blank': True,
    }),
    ('Latitude', sf.Number, {
        'max_digits': 9,
        'decimal_places': 6,
        'null': True,
        'blank': True
    }),
    ('Longitude', sf.Number, {
        'max_digits': 9,
        'decimal_places': 6,
        'null': True,
        'blank': True
    }),
)


def add_fields(model_class, fields):
    for fname, ftype, args in fields:
        kwargs = args or {}
        model_class.add_to_class(fname, ftype(sf_field_name=fname, **kwargs))

def get_addr_fields(names):
    fields = []
    
    if type(names) == type(str()):
        names = [names]
    
    for name in names:
        for suffix, ftype, args in ADDR_SUBFIELDS:
            fields.append((name + suffix, ftype, args))
    
    return fields

def add_addr_fields(model_class, names):
    add_fields(model_class, get_addr_fields(names))



# Create your models here.
class User(sf.HerokuConnectModel):
    sf_object_name = 'User'
    
    Alias = sf.Text(sf_field_name='Alias', max_length=8)
    CommunityNickname = sf.Text(sf_field_name='CommunityNickname', max_length=40)
    CompanyName = sf.Text(sf_field_name='CompanyName', max_length=80)
    Department = sf.Text(sf_field_name='Department', max_length=80)
    Division = sf.Text(sf_field_name='Division', max_length=80)
    Email = sf.Email(sf_field_name='Email')
    EmployeeNumber = sf.Text(sf_field_name='EmployeeNumber', max_length=20)
    FirstName = sf.Text(sf_field_name='FirstName', max_length=40)
    IsActive = sf.Checkbox(sf_field_name='IsActive')
    LastName = sf.Text(sf_field_name='LastName', max_length=80)
    Manager = sf.related.Lookup('self', sf_field_name='ManagerId', to_field='sf_id', on_delete=models.SET_NULL)
    MobilePhone = sf.Phone(sf_field_name='MobilePhone')
    Name = sf.Text(sf_field_name='Name', max_length=121)
    Phone = sf.Phone(sf_field_name='Phone')
    Title = sf.Text(sf_field_name='Title', max_length=80)
    Username = sf.Text(sf_field_name='Username', max_length=80)
    
add_addr_fields(User, [''])


class Account(sf.HerokuConnectModel):
    sf_object_name = 'Account'
    
    AccountNumber = sf.Text(sf_field_name='AccountNumber', max_length=40)
    AccountSource = sf.Picklist(sf_field_name='AccountSource', choices=SOURCES)
    Active_str = sf.Picklist(sf_field_name='Active__c', choices=BOOL_PICKLIST)
    Active = ComputedField(Case(
        When(Active_str='Yes', then=Value(True)),
        default=Value(False),
        output_field=models.BooleanField()
    ))
    AnnualRevenue = sf.Currency(sf_field_name='AnnualRevenue', max_digits=18, decimal_places=0)
    CustomerPriority = sf.Picklist(sf_field_name='CustomerPriority__c', choices=CUSTOMER_PRIORITIES)
    DandbCompanyId = sf.ID(sf_field_name='DandbCompanyId')
    DunsNumber = sf.Text(sf_field_name='DunsNumber', max_length=9)
    Fax = sf.Phone(sf_field_name='Fax')
    Industry = sf.Text(sf_field_name='Industry', max_length=40)
    LastReferencedDate = sf.DateTime(sf_field_name='LastReferencedDate')
    MasterRecord = sf.related.Lookup('self', sf_field_name='MasterRecordId', to_field='sf_id', on_delete=models.SET_NULL)
    NaicsCode = sf.Text(sf_field_name='NaicsCode', max_length=8)
    Name = sf.Text(sf_field_name='Name', max_length=255)
    NumberOfEmployees = sf.Number(sf_field_name='NumberOfEmployees', max_digits=8, decimal_places=0)
    NumberofLocations = sf.Number(sf_field_name='NumberofLocations__c', max_digits=3, decimal_places=0)
    Owner = sf.related.Lookup(User, sf_field_name='OwnerId', to_field='sf_id', on_delete=models.PROTECT)
    Phone = sf.Phone(sf_field_name='Phone')
    PhotoUrl = sf.URL(sf_field_name='PhotoUrl', max_length=255)
    Rating = sf.Picklist(sf_field_name='Rating', choices=RATINGS)
    SLAExpirationDate = sf.Date(sf_field_name='SLAExpirationDate__c')
    SLASerialNumber = sf.Text(sf_field_name='SLASerialNumber__c', max_length=10)
    SLA = sf.Picklist(sf_field_name='SLA__c', choices=SLAS)
    Sic = sf.Text(sf_field_name='Sic', max_length=20)
    Site = sf.Text(sf_field_name='Site', max_length=80)
    Tradestyle = sf.Text(sf_field_name='Tradestyle', max_length=255)
    Type = sf.Picklist(sf_field_name='Type', choices=ACCOUNT_TYPES)
    UpsellOpportunity = sf.Picklist(sf_field_name='UpsellOpportunity__c', choices=MAYBE_BOOL_PICKLIST)
    Website = sf.URL(sf_field_name='Website', max_length=255)
    YearStarted = sf.Text(sf_field_name='YearStarted', max_length=4)
    YearStartedNum = ComputedField(Cast('YearStarted', models.IntegerField()))

add_addr_fields(Account, ('Billing', 'Shipping'))


class Opportunity(sf.HerokuConnectModel):
    sf_object_name = 'Opportunity'
    
    Account = sf.related.Lookup(Account, sf_field_name='AccountId', to_field='sf_id', on_delete=models.CASCADE)
    Amount = sf.Currency(sf_field_name='Amount', max_digits=18, decimal_places=2)
    CloseDate = sf.Date(sf_field_name='CloseDate')
    CreatedDate = sf.Date(sf_field_name='CreatedDate')
    CurrentGenerators = sf.Text(sf_field_name='CurrentGenerators__c', max_length=100)
    DeliveryInstallationStatus = sf.Picklist(
        sf_field_name='DeliveryInstallationStatus__c', choices=DELIVERY_INSTALLATION_STATES)
    ExpectedRevenue = sf.Currency(sf_field_name='ExpectedRevenue', max_digits=18, decimal_places=2)
    HasOpenActivity = sf.Checkbox(sf_field_name='HasOpenActivity')
    HasOverdueTask = sf.Checkbox(sf_field_name='HasOverdueTask')
    IsClosed = sf.Checkbox(sf_field_name='IsClosed')
    IsPrivate = sf.Checkbox(sf_field_name='IsPrivate')
    IsWon = sf.Checkbox(sf_field_name='IsWon')
    LastActivityDate = sf.Date(sf_field_name='LastActivityDate')
    LastReferencedDate = sf.DateTime(sf_field_name='LastReferencedDate')
    LastViewedDate = sf.DateTime(sf_field_name='LastViewedDate')
    LeadSource = sf.Picklist(sf_field_name='LeadSource', choices=SOURCES)
    MainCompetitors = sf.Text(sf_field_name='MainCompetitors__c', max_length=100)
    Name = sf.Text(sf_field_name='Name', max_length=120)
    NextStep = sf.Text(sf_field_name='NextStep', max_length=255)
    OrderNumber = sf.Text(sf_field_name='OrderNumber__c', max_length=8)
    Owner = sf.related.Lookup(User, sf_field_name='OwnerId', to_field='sf_id', on_delete=models.PROTECT)
    Probability = sf.Percent(sf_field_name='Probability', max_digits=3, decimal_places=0)
    StageName = sf.Picklist(sf_field_name='StageName', choices=STAGES)
    TotalOpportunityQuantity = sf.Number(sf_field_name='TotalOpportunityQuantity', max_digits=18, decimal_places=2)
    TrackingNumber = sf.Text(sf_field_name='TrackingNumber__c', max_length=12)
    Type = sf.Picklist(sf_field_name='Type', choices=OPP_TYPES)
    

class Recommendation(models.Model):
    score = models.FloatField()
    reason1 = models.CharField(max_length=50)
    reason2 = models.CharField(max_length=50)
    reason3 = models.CharField(max_length=50)
    account = models.ForeignKey(Account, to_field='sf_id', on_delete=models.CASCADE, db_constraint=False)
    owner = models.ForeignKey(User, to_field='sf_id', on_delete=models.CASCADE, db_constraint=False)
