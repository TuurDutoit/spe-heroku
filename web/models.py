from django.db import models
from heroku_connect.db import models as salesforce

# Create your models here.
class User(salesforce.HerokuConnectModel):
    sf_object_name = 'User'
    
    username = salesforce.Text(sf_field_name='Username', max_length=80)
    email = salesforce.Email(sf_field_name='Email')

class Account(salesforce.HerokuConnectModel):
    sf_object_name = 'Account'
    
    name = salesforce.Text(sf_field_name='Name', max_length=255)
    active = salesforce.Picklist(sf_field_name='Active__c', choices=(('Yes','Yes'), ('No','No')))
    rating = salesforce.Picklist(sf_field_name='Rating', choices=(('Hot','Hot'), ('Warm','Warm'), ('Cold','Cold')))
    numEmployees = salesforce.Number(sf_field_name='NumberOfEmployees', max_digits=8, decimal_places=0)
    
    @property
    def is_active():
        return self.active_str == 'Yes'

class Recommendation(models.Model):
    score = models.FloatField()
    reason1 = models.CharField(max_length=50)
    reason2 = models.CharField(max_length=50)
    reason3 = models.CharField(max_length=50)
    account = models.ForeignKey(Account, to_field='sf_id', on_delete=models.CASCADE, db_constraint=False)
    owner = models.ForeignKey(User, to_field='sf_id', on_delete=models.CASCADE, db_constraint=False)
