from web.salesforce.models import Account

def get_accounts_for(userId):
    return Account.objects.filter(owner_id=userId)

