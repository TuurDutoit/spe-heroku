# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from salesforce import models as sf
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib import admin
from operator import itemgetter
from math import exp, log
import datetime
from app.util import clamp
import logging

logger = logging.getLogger(__name__)

DEFAULT=0
NO_DEFAULT=object()
UNITS = {
    'seconds': 1,
    'minutes': 60,
    'hours': 60*60,
    'days': 60*60*24,
    'weeks': 60*60*24*7
}
SOURCE_SCORES = {
    'Web': 50,
    'Phone Inquiry': 70,
    'Partner Referral': 100,
    'Purchased List': 70,
    'Other': 30,
}
INDUSTRY_SCORES = {
    'Banking': 70,
    'Biotechnology': 75,
    'Communications': 80,
    'Consulting': 100,
    'Electronics': 80,
    'Energy': 85,
    'Engineering': 70,
    'Entertainment': 50,
    'Finance': 85,
    'Food & Beverage': 100,
    'Healthcare': 90,
    'Government': 30,
    'Insurance': 75,
    'Not For Profit': 10,
    'Hospitality': 35,
    'Retail': 85,
    'Technology': 100,
    'Telecommunications': 95,
}
ACCOUNT_TYPE_SCORES = {
    'Prospect': 100,
    'Customer - Direct': 80,
    'Customer - Channel': 70,
}
LEAD_STATUS_SCORES = {
    'Open - Not Contacted': 100,
    'Working - Contacted': 50,
    'Closed - Converted': 0,
    'Closed - Not Converted': 0,
}
OPP_STAGE_SCORES = {
    'Prospecting': 90,
    'Qualification': 30,
    'Needs Analysis': 70,
    'Value Proposition': 50,
    'Id. Decision Makers': 20,
    'Perception Analysis': 60,
    'Proposal/Price Quote': 90,
    'Negotiation/Review': 100,
}

def passthrough(val):
    return float(val)

def with_default(processor, default=DEFAULT):
    def calc_with_default(val):
        if val == None:
            return default
        return processor(val)
    
    return calc_with_default

def div(denominator, default=DEFAULT):
    def calc_div(val):
        return int(val) / denominator
    
    return with_default(calc_div, default)


# Formula: f(x) = scale * e^((x/-b) + d) + c
# b: defines the shape of the curve
# c: defines the horizontal asymptote, i.e. moves curve up/down
#        Default: 0, to have score go to 0
# d: moves the curve from left to right
#       Default: ln(100), which ensures the graph passes through (0, 100), i.e. the max score is 100
# scale: scales the graph. Can be used to turn it upside down for example (scale = -1)
def exponential(b, d=log(100), c=0, scale=1, default=DEFAULT):
    def calc_exponential(val):
        return scale * exp(int(val) / (-b) + d) + c
    
    return with_default(calc_exponential, default)

def exponential_point(p, d=log(100), c=0, scale=1, default=DEFAULT):
    b = -p[0] / ( log((p[1] - c) / scale) - d )
    return exponential(b, d, c, scale, default)

def exponential_20(x20, *args):
    return exponential_point((x20, 20), *args)
    

# Formula: f(x) = -e^((x/-b) + d) + c
# b: defines the shape of the curve
# c: defines the horizontal asymptote, i.e. moves curve up/down
#       Default: 100, to cap scores at 100
# d: moves the curve from left to right
#       Default: ln(c), which ensures the graph passes through (0, 0)
def inv_exp(b, d=None, c=100, default=DEFAULT):
    if d == None:
        d = log(c)
    
    return exponential(b, d, c, -1, default)

def inv_exp_point(p, d=None, c=100, default=DEFAULT):
    if d == None:
        d = log(c)
    
    return exponential_point(p, d, c, -1, default)

def inv_exp_80(x80, *args):
    return inv_exp_point((x80, 80), *args)

def has(val):
    return 0 if val == None else 100

def expect(expected=True):
    def calc_expected(val):
        return 100 if val == expected else 0
    
    return calc_expected

def choose(score_map, default=DEFAULT):
    def calc_choose(val):
        return score_map.get(val, default)
    
    return calc_choose

def rank(values, default=DEFAULT):
    score_per = 100 / (len(values) - 1)
    
    if default == NO_DEFAULT:
        default = score_per
    
    def calc_rank(val):
        if val in values:
            index = values.index(val)
            return index * score_per
        else:
            return default
    
    return calc_rank

def date_diff(end=None, unit='days', future=False, default=DEFAULT):
    if end == None:
        end = datetime.datetime.now()
        
    def calc_date_diff(start):
        e = end
        # Start is a date, not datetime -> convert end to date
        if not isinstance(start, datetime.datetime):
            e = end.date()
        # Start is aware -> add timezone to end
        elif start.tzinfo != None:
            e = e.astimezone(datetime.timezone.utc)
        
        if future:
            diff = start - e
        else:
            diff = e - start
            
        return diff.total_seconds() / UNITS[unit]
    
    return with_default(calc_date_diff, default)

def combine(*processors):
    def calc_combine(val):
        for processor in processors:
            val = processor(val)
        
        return val
    
    return with_default(calc_combine)

def score(record, props):
    factor_sum = sum(map(itemgetter(0), props))
    prop_scores = sorted(
        map(
            lambda prop: (prop[1], subscore(record, *prop[1:]) * prop[0]),
            props
        ),
        key=itemgetter(1),
        reverse=True
    )
    subscores = map(itemgetter(1), prop_scores)
    record.best_attrs = map(itemgetter(0), prop_scores)
    
    return int(sum(subscores) / factor_sum)

def subscore(record, propname, processor=passthrough):
    val = getattr(record, propname)
    s = clamp(0, processor(val), 100)
    return s
        
    

class User(sf.Model):
    about_me = sf.TextField(blank=True, null=True)
    account = sf.ForeignKey('Account', sf.DO_NOTHING, sf_read_only=sf.READ_ONLY, blank=True, null=True)
    address = sf.TextField(sf_read_only=sf.READ_ONLY, blank=True, null=True)  # This field type is a guess.
    alias = sf.CharField(max_length=8)
    badge_text = sf.CharField(max_length=80, verbose_name='User Photo badge text overlay', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    banner_photo_url = sf.URLField(verbose_name='Url for banner photo', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    #call_center = sf.ForeignKey('CallCenter', sf.DO_NOTHING, blank=True, null=True)
    city = sf.CharField(max_length=40, blank=True, null=True)
    community_nickname = sf.CharField(max_length=40, verbose_name='Nickname')
    company_name = sf.CharField(max_length=80, blank=True, null=True)
    contact = sf.ForeignKey('Contact', sf.DO_NOTHING, blank=True, null=True)
    country = sf.CharField(max_length=80, blank=True, null=True)
    created_by = sf.ForeignKey('self', sf.DO_NOTHING, related_name='user_createdby_set', sf_read_only=sf.READ_ONLY)
    created_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    default_group_notification_frequency = sf.CharField(max_length=40, verbose_name='Default Notification Frequency when Joining Groups', default=sf.DEFAULTED_ON_CREATE, choices=[('P', 'Email on Each Post'), ('D', 'Daily Digests'), ('W', 'Weekly Digests'), ('N', 'Never')])
    #delegated_approver = sf.ForeignKey('Group', sf.DO_NOTHING, blank=True, null=True)  # Reference to tables [Group, User]
    department = sf.CharField(max_length=80, blank=True, null=True)
    digest_frequency = sf.CharField(max_length=40, verbose_name='Chatter Email Highlights Frequency', default=sf.DEFAULTED_ON_CREATE, choices=[('D', 'Daily'), ('W', 'Weekly'), ('N', 'Never')])
    division = sf.CharField(max_length=80, blank=True, null=True)
    email = sf.EmailField()
    email_encoding_key = sf.CharField(max_length=40, verbose_name='Email Encoding', choices=[('UTF-8', 'Unicode (UTF-8)'), ('ISO-8859-1', 'General US & Western Europe (ISO-8859-1, ISO-LATIN-1)'), ('Shift_JIS', 'Japanese (Shift-JIS)'), ('ISO-2022-JP', 'Japanese (JIS)'), ('EUC-JP', 'Japanese (EUC)'), ('ks_c_5601-1987', 'Korean (ks_c_5601-1987)'), ('Big5', 'Traditional Chinese (Big5)'), ('GB2312', 'Simplified Chinese (GB2312)'), ('Big5-HKSCS', 'Traditional Chinese Hong Kong (Big5-HKSCS)'), ('x-SJIS_0213', 'Japanese (Shift-JIS_2004)')])
    email_preferences_auto_bcc = sf.BooleanField(verbose_name='AutoBcc')
    email_preferences_auto_bcc_stay_in_touch = sf.BooleanField(verbose_name='AutoBccStayInTouch')
    email_preferences_stay_in_touch_reminder = sf.BooleanField(verbose_name='StayInTouchReminder')
    employee_number = sf.CharField(max_length=20, blank=True, null=True)
    extension = sf.CharField(max_length=40, blank=True, null=True)
    fax = sf.CharField(max_length=40, blank=True, null=True)
    federation_identifier = sf.CharField(max_length=512, verbose_name='SAML Federation ID', blank=True, null=True)
    first_name = sf.CharField(max_length=40, blank=True, null=True)
    forecast_enabled = sf.BooleanField(verbose_name='Allow Forecasting', default=sf.DEFAULTED_ON_CREATE)
    full_photo_url = sf.URLField(verbose_name='Url for full-sized Photo', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    geocode_accuracy = sf.CharField(max_length=40, choices=[('Address', 'Address'), ('NearAddress', 'NearAddress'), ('Block', 'Block'), ('Street', 'Street'), ('ExtendedZip', 'ExtendedZip'), ('Zip', 'Zip'), ('Neighborhood', 'Neighborhood'), ('City', 'City'), ('County', 'County'), ('State', 'State'), ('Unknown', 'Unknown')], blank=True, null=True)
    is_active = sf.BooleanField(verbose_name='Active', default=sf.DEFAULTED_ON_CREATE)
    is_ext_indicator_visible = sf.BooleanField(verbose_name='Show external indicator', sf_read_only=sf.READ_ONLY, default=False)
    is_profile_photo_active = sf.BooleanField(verbose_name='Has Profile Photo', sf_read_only=sf.READ_ONLY, default=False)
    jigsaw_import_limit_override = sf.IntegerField(verbose_name='Data.com Monthly Addition Limit', blank=True, null=True)
    language_locale_key = sf.CharField(max_length=40, verbose_name='Language', choices=[('en_US', 'English'), ('de', 'German'), ('es', 'Spanish'), ('fr', 'French'), ('it', 'Italian'), ('ja', 'Japanese'), ('sv', 'Swedish'), ('ko', 'Korean'), ('zh_TW', 'Chinese (Traditional)'), ('zh_CN', 'Chinese (Simplified)'), ('pt_BR', 'Portuguese (Brazil)'), ('nl_NL', 'Dutch'), ('da', 'Danish'), ('th', 'Thai'), ('fi', 'Finnish'), ('ru', 'Russian'), ('es_MX', 'Spanish (Mexico)'), ('no', 'Norwegian')])
    last_login_date = sf.DateTimeField(verbose_name='Last Login', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    last_modified_by = sf.ForeignKey('self', sf.DO_NOTHING, related_name='user_lastmodifiedby_set', sf_read_only=sf.READ_ONLY)
    last_modified_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    last_name = sf.CharField(max_length=80)
    last_password_change_date = sf.DateTimeField(verbose_name='Last Password Change or Reset', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    last_referenced_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY, blank=True, null=True)
    last_viewed_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY, blank=True, null=True)
    latitude = sf.DecimalField(max_digits=18, decimal_places=15, blank=True, null=True)
    locale_sid_key = sf.CharField(max_length=40, verbose_name='Locale', choices=[('af_ZA', 'Afrikaans (South Africa)'), ('sq_AL', 'Albanian (Albania)'), ('ar_DZ', 'Arabic (Algeria)'), ('ar_BH', 'Arabic (Bahrain)'), ('ar_EG', 'Arabic (Egypt)'), ('ar_IQ', 'Arabic (Iraq)'), ('ar_JO', 'Arabic (Jordan)'), ('ar_KW', 'Arabic (Kuwait)'), ('ar_LB', 'Arabic (Lebanon)'), ('ar_LY', 'Arabic (Libya)'), ('ar_MA', 'Arabic (Morocco)'), ('ar_OM', 'Arabic (Oman)'), ('ar_QA', 'Arabic (Qatar)'), ('ar_SA', 'Arabic (Saudi Arabia)'), ('ar_SD', 'Arabic (Sudan)'), ('ar_SY', 'Arabic (Syria)'), ('ar_TN', 'Arabic (Tunisia)'), ('ar_AE', 'Arabic (United Arab Emirates)'), ('ar_YE', 'Arabic (Yemen)'), ('hy_AM', 'Armenian (Armenia)'), ('az_AZ', 'Azerbaijani (Azerbaijan)'), ('bn_BD', 'Bangla (Bangladesh)'), ('bn_IN', 'Bangla (India)'), ('eu_ES', 'Basque (Spain)'), ('be_BY', 'Belarusian (Belarus)'), ('bs_BA', 'Bosnian (Bosnia & Herzegovina)'), ('bg_BG', 'Bulgarian (Bulgaria)'), ('my_MM', 'Burmese (Myanmar (Burma))'), ('ca_ES', 'Catalan (Spain)'), ('zh_CN_PINYIN', 'Chinese (China, Pinyin Ordering)'), ('zh_CN_STROKE', 'Chinese (China, Stroke Ordering)'), ('zh_CN', 'Chinese (China)'), ('zh_HK_STROKE', 'Chinese (Hong Kong SAR China, Stroke Ordering)'), ('zh_HK', 'Chinese (Hong Kong SAR China)'), ('zh_MO', 'Chinese (Macau SAR China)'), ('zh_SG', 'Chinese (Singapore)'), ('zh_TW_STROKE', 'Chinese (Taiwan, Stroke Ordering)'), ('zh_TW', 'Chinese (Taiwan)'), ('hr_HR', 'Croatian (Croatia)'), ('cs_CZ', 'Czech (Czechia)'), ('da_DK', 'Danish (Denmark)'), ('nl_AW', 'Dutch (Aruba)'), ('nl_BE', 'Dutch (Belgium)'), ('nl_NL', 'Dutch (Netherlands)'), ('nl_SR', 'Dutch (Suriname)'), ('dz_BT', 'Dzongkha (Bhutan)'), ('en_AG', 'English (Antigua & Barbuda)'), ('en_AU', 'English (Australia)'), ('en_BS', 'English (Bahamas)'), ('en_BB', 'English (Barbados)'), ('en_BZ', 'English (Belize)'), ('en_BM', 'English (Bermuda)'), ('en_BW', 'English (Botswana)'), ('en_CM', 'English (Cameroon)'), ('en_CA', 'English (Canada)'), ('en_KY', 'English (Cayman Islands)'), ('en_ER', 'English (Eritrea)'), ('en_FK', 'English (Falkland Islands)'), ('en_FJ', 'English (Fiji)'), ('en_GM', 'English (Gambia)'), ('en_GH', 'English (Ghana)'), ('en_GI', 'English (Gibraltar)'), ('en_GY', 'English (Guyana)'), ('en_HK', 'English (Hong Kong SAR China)'), ('en_IN', 'English (India)'), ('en_ID', 'English (Indonesia)'), ('en_IE', 'English (Ireland)'), ('en_JM', 'English (Jamaica)'), ('en_KE', 'English (Kenya)'), ('en_LR', 'English (Liberia)'), ('en_MG', 'English (Madagascar)'), ('en_MW', 'English (Malawi)'), ('en_MY', 'English (Malaysia)'), ('en_MU', 'English (Mauritius)'), ('en_NA', 'English (Namibia)'), ('en_NZ', 'English (New Zealand)'), ('en_NG', 'English (Nigeria)'), ('en_PK', 'English (Pakistan)'), ('en_PG', 'English (Papua New Guinea)'), ('en_PH', 'English (Philippines)'), ('en_RW', 'English (Rwanda)'), ('en_WS', 'English (Samoa)'), ('en_SC', 'English (Seychelles)'), ('en_SL', 'English (Sierra Leone)'), ('en_SG', 'English (Singapore)'), ('en_SX', 'English (Sint Maarten)'), ('en_SB', 'English (Solomon Islands)'), ('en_ZA', 'English (South Africa)'), ('en_SH', 'English (St. Helena)'), ('en_SZ', 'English (Swaziland)'), ('en_TZ', 'English (Tanzania)'), ('en_TO', 'English (Tonga)'), ('en_TT', 'English (Trinidad & Tobago)'), ('en_UG', 'English (Uganda)'), ('en_GB', 'English (United Kingdom)'), ('en_US', 'English (United States)'), ('en_VU', 'English (Vanuatu)'), ('et_EE', 'Estonian (Estonia)'), ('fi_FI', 'Finnish (Finland)'), ('fr_BE', 'French (Belgium)'), ('fr_CA', 'French (Canada)'), ('fr_KM', 'French (Comoros)'), ('fr_FR', 'French (France)'), ('fr_GN', 'French (Guinea)'), ('fr_HT', 'French (Haiti)'), ('fr_LU', 'French (Luxembourg)'), ('fr_MR', 'French (Mauritania)'), ('fr_MC', 'French (Monaco)'), ('fr_CH', 'French (Switzerland)'), ('fr_WF', 'French (Wallis & Futuna)'), ('ka_GE', 'Georgian (Georgia)'), ('de_AT', 'German (Austria)'), ('de_BE', 'German (Belgium)'), ('de_DE', 'German (Germany)'), ('de_LU', 'German (Luxembourg)'), ('de_CH', 'German (Switzerland)'), ('el_GR', 'Greek (Greece)'), ('gu_IN', 'Gujarati (India)'), ('iw_IL', 'Hebrew (Israel)'), ('hi_IN', 'Hindi (India)'), ('hu_HU', 'Hungarian (Hungary)'), ('is_IS', 'Icelandic (Iceland)'), ('in_ID', 'Indonesian (Indonesia)'), ('ga_IE', 'Irish (Ireland)'), ('it_IT', 'Italian (Italy)'), ('it_CH', 'Italian (Switzerland)'), ('ja_JP', 'Japanese (Japan)'), ('kn_IN', 'Kannada (India)'), ('kk_KZ', 'Kazakh (Kazakhstan)'), ('km_KH', 'Khmer (Cambodia)'), ('ko_KP', 'Korean (North Korea)'), ('ko_KR', 'Korean (South Korea)'), ('ky_KG', 'Kyrgyz (Kyrgyzstan)'), ('lo_LA', 'Lao (Laos)'), ('lv_LV', 'Latvian (Latvia)'), ('lt_LT', 'Lithuanian (Lithuania)'), ('lu_CD', 'Luba-Katanga (Congo - Kinshasa)'), ('lb_LU', 'Luxembourgish (Luxembourg)'), ('mk_MK', 'Macedonian (Macedonia)'), ('ms_BN', 'Malay (Brunei)'), ('ms_MY', 'Malay (Malaysia)'), ('ml_IN', 'Malayalam (India)'), ('mt_MT', 'Maltese (Malta)'), ('mr_IN', 'Marathi (India)'), ('sh_ME', 'Montenegrin (Montenegro)'), ('ne_NP', 'Nepali (Nepal)'), ('no_NO', 'Norwegian (Norway)'), ('ps_AF', 'Pashto (Afghanistan)'), ('fa_IR', 'Persian (Iran)'), ('pl_PL', 'Polish (Poland)'), ('pt_AO', 'Portuguese (Angola)'), ('pt_BR', 'Portuguese (Brazil)'), ('pt_CV', 'Portuguese (Cape Verde)'), ('pt_MZ', 'Portuguese (Mozambique)'), ('pt_PT', 'Portuguese (Portugal)'), ('pt_ST', 'Portuguese (São Tomé & Príncipe)'), ('ro_MD', 'Romanian (Moldova)'), ('ro_RO', 'Romanian (Romania)'), ('rm_CH', 'Romansh (Switzerland)'), ('rn_BI', 'Rundi (Burundi)'), ('ru_KZ', 'Russian (Kazakhstan)'), ('ru_RU', 'Russian (Russia)'), ('sr_BA', 'Serbian (Cyrillic) (Bosnia and Herzegovina)'), ('sr_CS', 'Serbian (Cyrillic) (Serbia)'), ('sh_BA', 'Serbian (Latin) (Bosnia and Herzegovina)'), ('sh_CS', 'Serbian (Latin) (Serbia)'), ('sr_RS', 'Serbian (Serbia)'), ('sk_SK', 'Slovak (Slovakia)'), ('sl_SI', 'Slovenian (Slovenia)'), ('so_DJ', 'Somali (Djibouti)'), ('so_SO', 'Somali (Somalia)'), ('es_AR', 'Spanish (Argentina)'), ('es_BO', 'Spanish (Bolivia)'), ('es_CL', 'Spanish (Chile)'), ('es_CO', 'Spanish (Colombia)'), ('es_CR', 'Spanish (Costa Rica)'), ('es_CU', 'Spanish (Cuba)'), ('es_DO', 'Spanish (Dominican Republic)'), ('es_EC', 'Spanish (Ecuador)'), ('es_SV', 'Spanish (El Salvador)'), ('es_GT', 'Spanish (Guatemala)'), ('es_HN', 'Spanish (Honduras)'), ('es_MX', 'Spanish (Mexico)'), ('es_NI', 'Spanish (Nicaragua)'), ('es_PA', 'Spanish (Panama)'), ('es_PY', 'Spanish (Paraguay)'), ('es_PE', 'Spanish (Peru)'), ('es_PR', 'Spanish (Puerto Rico)'), ('es_ES', 'Spanish (Spain)'), ('es_US', 'Spanish (United States)'), ('es_UY', 'Spanish (Uruguay)'), ('es_VE', 'Spanish (Venezuela)'), ('sw_KE', 'Swahili (Kenya)'), ('sv_SE', 'Swedish (Sweden)'), ('tl_PH', 'Tagalog (Philippines)'), ('tg_TJ', 'Tajik (Tajikistan)'), ('ta_IN', 'Tamil (India)'), ('ta_LK', 'Tamil (Sri Lanka)'), ('te_IN', 'Telugu (India)'), ('th_TH', 'Thai (Thailand)'), ('ti_ET', 'Tigrinya (Ethiopia)'), ('tr_TR', 'Turkish (Turkey)'), ('uk_UA', 'Ukrainian (Ukraine)'), ('ur_PK', 'Urdu (Pakistan)'), ('uz_LATN_UZ', 'Uzbek (LATN,UZ)'), ('vi_VN', 'Vietnamese (Vietnam)'), ('cy_GB', 'Welsh (United Kingdom)'), ('xh_ZA', 'Xhosa (South Africa)'), ('yo_BJ', 'Yoruba (Benin)'), ('zu_ZA', 'Zulu (South Africa)')])
    longitude = sf.DecimalField(max_digits=18, decimal_places=15, blank=True, null=True)
    manager = sf.ForeignKey('self', sf.DO_NOTHING, related_name='user_manager_set', blank=True, null=True)
    medium_banner_photo_url = sf.URLField(verbose_name='Url for Android banner photo', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    medium_photo_url = sf.URLField(verbose_name='Url for medium profile photo', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    mobile_phone = sf.CharField(max_length=40, verbose_name='Mobile', blank=True, null=True)
    name = sf.CharField(max_length=121, verbose_name='Full Name', sf_read_only=sf.READ_ONLY)
    offline_pda_trial_expiration_date = sf.DateTimeField(verbose_name='Sales Anywhere Trial Expiration Date', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    offline_trial_expiration_date = sf.DateTimeField(verbose_name='Offline Edition Trial Expiration Date', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    out_of_office_message = sf.CharField(max_length=40, verbose_name='Out of office message', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    phone = sf.CharField(max_length=40, blank=True, null=True)
    postal_code = sf.CharField(max_length=20, verbose_name='Zip/Postal Code', blank=True, null=True)
    #profile = sf.ForeignKey('Profile', sf.DO_NOTHING)
    receives_admin_info_emails = sf.BooleanField(verbose_name='Admin Info Emails', default=sf.DEFAULTED_ON_CREATE)
    receives_info_emails = sf.BooleanField(verbose_name='Info Emails', default=sf.DEFAULTED_ON_CREATE)
    sender_email = sf.EmailField(verbose_name='Email Sender Address', blank=True, null=True)
    sender_name = sf.CharField(max_length=80, verbose_name='Email Sender Name', blank=True, null=True)
    signature = sf.TextField(verbose_name='Email Signature', blank=True, null=True)
    small_banner_photo_url = sf.URLField(verbose_name='Url for IOS banner photo', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    small_photo_url = sf.URLField(verbose_name='Photo', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    state = sf.CharField(max_length=80, verbose_name='State/Province', blank=True, null=True)
    stay_in_touch_note = sf.CharField(max_length=512, verbose_name='Stay-in-Touch Email Note', blank=True, null=True)
    stay_in_touch_signature = sf.TextField(verbose_name='Stay-in-Touch Email Signature', blank=True, null=True)
    stay_in_touch_subject = sf.CharField(max_length=80, verbose_name='Stay-in-Touch Email Subject', blank=True, null=True)
    street = sf.TextField(blank=True, null=True)
    system_modstamp = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    time_zone_sid_key = sf.CharField(max_length=40, verbose_name='Time Zone', choices=[('Pacific/Kiritimati', '(GMT+14:00) Line Is. Time (Pacific/Kiritimati)'), ('Pacific/Enderbury', '(GMT+13:00) Phoenix Is. Time (Pacific/Enderbury)'), ('Pacific/Tongatapu', '(GMT+13:00) Tonga Time (Pacific/Tongatapu)'), ('Pacific/Chatham', '(GMT+12:45) Chatham Standard Time (Pacific/Chatham)'), ('Asia/Kamchatka', '(GMT+12:00) Petropavlovsk-Kamchatski Time (Asia/Kamchatka)'), ('Pacific/Auckland', '(GMT+12:00) New Zealand Standard Time (Pacific/Auckland)'), ('Pacific/Fiji', '(GMT+12:00) Fiji Time (Pacific/Fiji)'), ('Pacific/Guadalcanal', '(GMT+11:00) Solomon Is. Time (Pacific/Guadalcanal)'), ('Pacific/Norfolk', '(GMT+11:00) Norfolk Time (Pacific/Norfolk)'), ('Australia/Lord_Howe', '(GMT+10:30) Lord Howe Standard Time (Australia/Lord_Howe)'), ('Australia/Brisbane', '(GMT+10:00) Australian Eastern Standard Time (Queensland) (Australia/Brisbane)'), ('Australia/Sydney', '(GMT+10:00) Australian Eastern Standard Time (New South Wales) (Australia/Sydney)'), ('Australia/Adelaide', '(GMT+09:30) Australian Central Standard Time (South Australia) (Australia/Adelaide)'), ('Australia/Darwin', '(GMT+09:30) Australian Central Standard Time (Northern Territory) (Australia/Darwin)'), ('Asia/Seoul', '(GMT+09:00) Korea Standard Time (Asia/Seoul)'), ('Asia/Tokyo', '(GMT+09:00) Japan Standard Time (Asia/Tokyo)'), ('Asia/Hong_Kong', '(GMT+08:00) Hong Kong Time (Asia/Hong_Kong)'), ('Asia/Kuala_Lumpur', '(GMT+08:00) Malaysia Time (Asia/Kuala_Lumpur)'), ('Asia/Manila', '(GMT+08:00) Philippines Time (Asia/Manila)'), ('Asia/Shanghai', '(GMT+08:00) China Standard Time (Asia/Shanghai)'), ('Asia/Singapore', '(GMT+08:00) Singapore Time (Asia/Singapore)'), ('Asia/Taipei', '(GMT+08:00) China Standard Time (Asia/Taipei)'), ('Australia/Perth', '(GMT+08:00) Australian Western Standard Time (Australia/Perth)'), ('Asia/Bangkok', '(GMT+07:00) Indochina Time (Asia/Bangkok)'), ('Asia/Ho_Chi_Minh', '(GMT+07:00) Indochina Time (Asia/Ho_Chi_Minh)'), ('Asia/Jakarta', '(GMT+07:00) West Indonesia Time (Asia/Jakarta)'), ('Asia/Rangoon', '(GMT+06:30) Myanmar Time (Asia/Rangoon)'), ('Asia/Dhaka', '(GMT+06:00) Bangladesh Time (Asia/Dhaka)'), ('Asia/Kathmandu', '(GMT+05:45) Nepal Time (Asia/Kathmandu)'), ('Asia/Colombo', '(GMT+05:30) India Standard Time (Asia/Colombo)'), ('Asia/Kolkata', '(GMT+05:30) India Standard Time (Asia/Kolkata)'), ('Asia/Karachi', '(GMT+05:00) Pakistan Time (Asia/Karachi)'), ('Asia/Tashkent', '(GMT+05:00) Uzbekistan Time (Asia/Tashkent)'), ('Asia/Yekaterinburg', '(GMT+05:00) Yekaterinburg Time (Asia/Yekaterinburg)'), ('Asia/Kabul', '(GMT+04:30) Afghanistan Time (Asia/Kabul)'), ('Asia/Tehran', '(GMT+04:30) Iran Daylight Time (Asia/Tehran)'), ('Asia/Baku', '(GMT+04:00) Azerbaijan Time (Asia/Baku)'), ('Asia/Dubai', '(GMT+04:00) Gulf Standard Time (Asia/Dubai)'), ('Asia/Tbilisi', '(GMT+04:00) Georgia Time (Asia/Tbilisi)'), ('Asia/Yerevan', '(GMT+04:00) Armenia Time (Asia/Yerevan)'), ('Africa/Nairobi', '(GMT+03:00) Eastern African Time (Africa/Nairobi)'), ('Asia/Baghdad', '(GMT+03:00) Arabia Standard Time (Asia/Baghdad)'), ('Asia/Beirut', '(GMT+03:00) Eastern European Summer Time (Asia/Beirut)'), ('Asia/Jerusalem', '(GMT+03:00) Israel Daylight Time (Asia/Jerusalem)'), ('Asia/Kuwait', '(GMT+03:00) Arabia Standard Time (Asia/Kuwait)'), ('Asia/Riyadh', '(GMT+03:00) Arabia Standard Time (Asia/Riyadh)'), ('Europe/Athens', '(GMT+03:00) Eastern European Summer Time (Europe/Athens)'), ('Europe/Bucharest', '(GMT+03:00) Eastern European Summer Time (Europe/Bucharest)'), ('Europe/Helsinki', '(GMT+03:00) Eastern European Summer Time (Europe/Helsinki)'), ('Europe/Istanbul', '(GMT+03:00) Eastern European Time (Europe/Istanbul)'), ('Europe/Minsk', '(GMT+03:00) Moscow Standard Time (Europe/Minsk)'), ('Europe/Moscow', '(GMT+03:00) Moscow Standard Time (Europe/Moscow)'), ('Africa/Cairo', '(GMT+02:00) Eastern European Time (Africa/Cairo)'), ('Africa/Johannesburg', '(GMT+02:00) South Africa Standard Time (Africa/Johannesburg)'), ('Europe/Amsterdam', '(GMT+02:00) Central European Summer Time (Europe/Amsterdam)'), ('Europe/Berlin', '(GMT+02:00) Central European Summer Time (Europe/Berlin)'), ('Europe/Brussels', '(GMT+02:00) Central European Summer Time (Europe/Brussels)'), ('Europe/Paris', '(GMT+02:00) Central European Summer Time (Europe/Paris)'), ('Europe/Prague', '(GMT+02:00) Central European Summer Time (Europe/Prague)'), ('Europe/Rome', '(GMT+02:00) Central European Summer Time (Europe/Rome)'), ('Africa/Algiers', '(GMT+01:00) Central European Time (Africa/Algiers)'), ('Africa/Casablanca', '(GMT+01:00) Western European Time (Africa/Casablanca)'), ('Europe/Dublin', '(GMT+01:00) Greenwich Mean Time (Europe/Dublin)'), ('Europe/Lisbon', '(GMT+01:00) Western European Summer Time (Europe/Lisbon)'), ('Europe/London', '(GMT+01:00) British Summer Time (Europe/London)'), ('America/Scoresbysund', '(GMT+00:00) Eastern Greenland Summer Time (America/Scoresbysund)'), ('Atlantic/Azores', '(GMT+00:00) Azores Summer Time (Atlantic/Azores)'), ('GMT', '(GMT+00:00) Greenwich Mean Time (GMT)'), ('Atlantic/Cape_Verde', '(GMT-01:00) Cape Verde Time (Atlantic/Cape_Verde)'), ('Atlantic/South_Georgia', '(GMT-02:00) South Georgia Standard Time (Atlantic/South_Georgia)'), ('America/St_Johns', '(GMT-02:30) Newfoundland Daylight Time (America/St_Johns)'), ('America/Argentina/Buenos_Aires', '(GMT-03:00) Argentine Time (America/Argentina/Buenos_Aires)'), ('America/Halifax', '(GMT-03:00) Atlantic Daylight Time (America/Halifax)'), ('America/Sao_Paulo', '(GMT-03:00) Brasilia Time (America/Sao_Paulo)'), ('Atlantic/Bermuda', '(GMT-03:00) Atlantic Daylight Time (Atlantic/Bermuda)'), ('America/Caracas', '(GMT-04:00) Venezuela Time (America/Caracas)'), ('America/Indiana/Indianapolis', '(GMT-04:00) Eastern Daylight Time (America/Indiana/Indianapolis)'), ('America/New_York', '(GMT-04:00) Eastern Daylight Time (America/New_York)'), ('America/Puerto_Rico', '(GMT-04:00) Atlantic Standard Time (America/Puerto_Rico)'), ('America/Santiago', '(GMT-04:00) Chile Time (America/Santiago)'), ('America/Bogota', '(GMT-05:00) Colombia Time (America/Bogota)'), ('America/Chicago', '(GMT-05:00) Central Daylight Time (America/Chicago)'), ('America/Lima', '(GMT-05:00) Peru Time (America/Lima)'), ('America/Mexico_City', '(GMT-05:00) Central Daylight Time (America/Mexico_City)'), ('America/Panama', '(GMT-05:00) Eastern Standard Time (America/Panama)'), ('America/Denver', '(GMT-06:00) Mountain Daylight Time (America/Denver)'), ('America/El_Salvador', '(GMT-06:00) Central Standard Time (America/El_Salvador)'), ('America/Mazatlan', '(GMT-06:00) Mountain Daylight Time (America/Mazatlan)'), ('America/Los_Angeles', '(GMT-07:00) Pacific Daylight Time (America/Los_Angeles)'), ('America/Phoenix', '(GMT-07:00) Mountain Standard Time (America/Phoenix)'), ('America/Tijuana', '(GMT-07:00) Pacific Daylight Time (America/Tijuana)'), ('America/Anchorage', '(GMT-08:00) Alaska Daylight Time (America/Anchorage)'), ('Pacific/Pitcairn', '(GMT-08:00) Pitcairn Standard Time (Pacific/Pitcairn)'), ('America/Adak', '(GMT-09:00) Hawaii-Aleutian Daylight Time (America/Adak)'), ('Pacific/Gambier', '(GMT-09:00) Gambier Time (Pacific/Gambier)'), ('Pacific/Marquesas', '(GMT-09:30) Marquesas Time (Pacific/Marquesas)'), ('Pacific/Honolulu', '(GMT-10:00) Hawaii-Aleutian Standard Time (Pacific/Honolulu)'), ('Pacific/Niue', '(GMT-11:00) Niue Time (Pacific/Niue)'), ('Pacific/Pago_Pago', '(GMT-11:00) Samoa Standard Time (Pacific/Pago_Pago)')])
    title = sf.CharField(max_length=80, blank=True, null=True)
    user_permissions_call_center_auto_login = sf.BooleanField(verbose_name='Auto-login To Call Center')
    user_permissions_interaction_user = sf.BooleanField(verbose_name='Flow User')
    user_permissions_jigsaw_prospecting_user = sf.BooleanField(verbose_name='Data.com User')
    user_permissions_knowledge_user = sf.BooleanField(verbose_name='Knowledge User')
    user_permissions_marketing_user = sf.BooleanField(verbose_name='Marketing User')
    user_permissions_mobile_user = sf.BooleanField(verbose_name='Apex Mobile User')
    user_permissions_offline_user = sf.BooleanField(verbose_name='Offline User')
    user_permissions_sfcontent_user = sf.BooleanField(db_column='UserPermissionsSFContentUser', verbose_name='Salesforce CRM Content User')
    user_permissions_siteforce_contributor_user = sf.BooleanField(verbose_name='Site.com Contributor User')
    user_permissions_siteforce_publisher_user = sf.BooleanField(verbose_name='Site.com Publisher User')
    user_permissions_support_user = sf.BooleanField(verbose_name='Service Cloud User')
    user_permissions_work_dot_com_user_feature = sf.BooleanField(verbose_name='Work.com User')
    user_preferences_activity_reminders_popup = sf.BooleanField(verbose_name='ActivityRemindersPopup')
    user_preferences_apex_pages_developer_mode = sf.BooleanField(verbose_name='ApexPagesDeveloperMode')
    user_preferences_cache_diagnostics = sf.BooleanField(verbose_name='CacheDiagnostics')
    user_preferences_content_email_as_and_when = sf.BooleanField(verbose_name='ContentEmailAsAndWhen')
    user_preferences_content_no_email = sf.BooleanField(verbose_name='ContentNoEmail')
    user_preferences_create_lexapps_wtshown = sf.BooleanField(db_column='UserPreferencesCreateLEXAppsWTShown', verbose_name='CreateLEXAppsWTShown')
    user_preferences_dis_comment_after_like_email = sf.BooleanField(verbose_name='DisCommentAfterLikeEmail')
    user_preferences_dis_mentions_comment_email = sf.BooleanField(verbose_name='DisMentionsCommentEmail')
    user_preferences_dis_prof_post_comment_email = sf.BooleanField(verbose_name='DisProfPostCommentEmail')
    user_preferences_disable_all_feeds_email = sf.BooleanField(verbose_name='DisableAllFeedsEmail')
    user_preferences_disable_bookmark_email = sf.BooleanField(verbose_name='DisableBookmarkEmail')
    user_preferences_disable_change_comment_email = sf.BooleanField(verbose_name='DisableChangeCommentEmail')
    user_preferences_disable_endorsement_email = sf.BooleanField(verbose_name='DisableEndorsementEmail')
    user_preferences_disable_feedback_email = sf.BooleanField(verbose_name='DisableFeedbackEmail')
    user_preferences_disable_file_share_notifications_for_api = sf.BooleanField(verbose_name='DisableFileShareNotificationsForApi')
    user_preferences_disable_followers_email = sf.BooleanField(verbose_name='DisableFollowersEmail')
    user_preferences_disable_later_comment_email = sf.BooleanField(verbose_name='DisableLaterCommentEmail')
    user_preferences_disable_like_email = sf.BooleanField(verbose_name='DisableLikeEmail')
    user_preferences_disable_mentions_post_email = sf.BooleanField(verbose_name='DisableMentionsPostEmail')
    user_preferences_disable_message_email = sf.BooleanField(verbose_name='DisableMessageEmail')
    user_preferences_disable_profile_post_email = sf.BooleanField(verbose_name='DisableProfilePostEmail')
    user_preferences_disable_share_post_email = sf.BooleanField(verbose_name='DisableSharePostEmail')
    user_preferences_disable_work_email = sf.BooleanField(verbose_name='DisableWorkEmail')
    user_preferences_enable_auto_sub_for_feeds = sf.BooleanField(verbose_name='EnableAutoSubForFeeds')
    user_preferences_event_reminders_checkbox_default = sf.BooleanField(verbose_name='EventRemindersCheckboxDefault')
    user_preferences_exclude_mail_app_attachments = sf.BooleanField(verbose_name='ExcludeMailAppAttachments')
    user_preferences_favorites_show_top_favorites = sf.BooleanField(verbose_name='FavoritesShowTopFavorites')
    user_preferences_favorites_wtshown = sf.BooleanField(db_column='UserPreferencesFavoritesWTShown', verbose_name='FavoritesWTShown')
    user_preferences_global_nav_bar_wtshown = sf.BooleanField(db_column='UserPreferencesGlobalNavBarWTShown', verbose_name='GlobalNavBarWTShown')
    user_preferences_global_nav_grid_menu_wtshown = sf.BooleanField(db_column='UserPreferencesGlobalNavGridMenuWTShown', verbose_name='GlobalNavGridMenuWTShown')
    user_preferences_has_celebration_badge = sf.BooleanField(verbose_name='HasCelebrationBadge')
    user_preferences_hide_bigger_photo_callout = sf.BooleanField(verbose_name='HideBiggerPhotoCallout')
    user_preferences_hide_chatter_onboarding_splash = sf.BooleanField(verbose_name='HideChatterOnboardingSplash')
    user_preferences_hide_csndesktop_task = sf.BooleanField(db_column='UserPreferencesHideCSNDesktopTask', verbose_name='HideCSNDesktopTask')
    user_preferences_hide_csnget_chatter_mobile_task = sf.BooleanField(db_column='UserPreferencesHideCSNGetChatterMobileTask', verbose_name='HideCSNGetChatterMobileTask')
    user_preferences_hide_end_user_onboarding_assistant_modal = sf.BooleanField(verbose_name='HideEndUserOnboardingAssistantModal')
    user_preferences_hide_lightning_migration_modal = sf.BooleanField(verbose_name='HideLightningMigrationModal')
    user_preferences_hide_s1_browser_ui = sf.BooleanField(db_column='UserPreferencesHideS1BrowserUI', verbose_name='HideS1BrowserUI')
    user_preferences_hide_second_chatter_onboarding_splash = sf.BooleanField(verbose_name='HideSecondChatterOnboardingSplash')
    user_preferences_hide_sfx_welcome_mat = sf.BooleanField(verbose_name='HideSfxWelcomeMat')
    user_preferences_jigsaw_list_user = sf.BooleanField(verbose_name='JigsawListUser')
    user_preferences_lightning_experience_preferred = sf.BooleanField(verbose_name='LightningExperiencePreferred')
    user_preferences_new_lightning_report_run_page_enabled = sf.BooleanField(verbose_name='NewLightningReportRunPageEnabled')
    user_preferences_path_assistant_collapsed = sf.BooleanField(verbose_name='PathAssistantCollapsed')
    user_preferences_pipeline_view_hide_help_popover = sf.BooleanField(verbose_name='PipelineViewHideHelpPopover')
    user_preferences_preview_custom_theme = sf.BooleanField(verbose_name='PreviewCustomTheme')
    user_preferences_preview_lightning = sf.BooleanField(verbose_name='PreviewLightning')
    user_preferences_record_home_reserved_wtshown = sf.BooleanField(db_column='UserPreferencesRecordHomeReservedWTShown', verbose_name='RecordHomeReservedWTShown')
    user_preferences_record_home_section_collapse_wtshown = sf.BooleanField(db_column='UserPreferencesRecordHomeSectionCollapseWTShown', verbose_name='RecordHomeSectionCollapseWTShown')
    user_preferences_reminder_sound_off = sf.BooleanField(verbose_name='ReminderSoundOff')
    user_preferences_show_city_to_external_users = sf.BooleanField(verbose_name='ShowCityToExternalUsers')
    user_preferences_show_city_to_guest_users = sf.BooleanField(verbose_name='ShowCityToGuestUsers')
    user_preferences_show_country_to_external_users = sf.BooleanField(verbose_name='ShowCountryToExternalUsers')
    user_preferences_show_country_to_guest_users = sf.BooleanField(verbose_name='ShowCountryToGuestUsers')
    user_preferences_show_email_to_external_users = sf.BooleanField(verbose_name='ShowEmailToExternalUsers')
    user_preferences_show_email_to_guest_users = sf.BooleanField(verbose_name='ShowEmailToGuestUsers')
    user_preferences_show_fax_to_external_users = sf.BooleanField(verbose_name='ShowFaxToExternalUsers')
    user_preferences_show_fax_to_guest_users = sf.BooleanField(verbose_name='ShowFaxToGuestUsers')
    user_preferences_show_manager_to_external_users = sf.BooleanField(verbose_name='ShowManagerToExternalUsers')
    user_preferences_show_manager_to_guest_users = sf.BooleanField(verbose_name='ShowManagerToGuestUsers')
    user_preferences_show_mobile_phone_to_external_users = sf.BooleanField(verbose_name='ShowMobilePhoneToExternalUsers')
    user_preferences_show_mobile_phone_to_guest_users = sf.BooleanField(verbose_name='ShowMobilePhoneToGuestUsers')
    user_preferences_show_postal_code_to_external_users = sf.BooleanField(verbose_name='ShowPostalCodeToExternalUsers')
    user_preferences_show_postal_code_to_guest_users = sf.BooleanField(verbose_name='ShowPostalCodeToGuestUsers')
    user_preferences_show_profile_pic_to_guest_users = sf.BooleanField(verbose_name='ShowProfilePicToGuestUsers')
    user_preferences_show_state_to_external_users = sf.BooleanField(verbose_name='ShowStateToExternalUsers')
    user_preferences_show_state_to_guest_users = sf.BooleanField(verbose_name='ShowStateToGuestUsers')
    user_preferences_show_street_address_to_external_users = sf.BooleanField(verbose_name='ShowStreetAddressToExternalUsers')
    user_preferences_show_street_address_to_guest_users = sf.BooleanField(verbose_name='ShowStreetAddressToGuestUsers')
    user_preferences_show_title_to_external_users = sf.BooleanField(verbose_name='ShowTitleToExternalUsers')
    user_preferences_show_title_to_guest_users = sf.BooleanField(verbose_name='ShowTitleToGuestUsers')
    user_preferences_show_work_phone_to_external_users = sf.BooleanField(verbose_name='ShowWorkPhoneToExternalUsers')
    user_preferences_show_work_phone_to_guest_users = sf.BooleanField(verbose_name='ShowWorkPhoneToGuestUsers')
    user_preferences_sort_feed_by_comment = sf.BooleanField(verbose_name='SortFeedByComment')
    user_preferences_suppress_event_sfxreminders = sf.BooleanField(db_column='UserPreferencesSuppressEventSFXReminders', verbose_name='SuppressEventSFXReminders')
    user_preferences_suppress_task_sfxreminders = sf.BooleanField(db_column='UserPreferencesSuppressTaskSFXReminders', verbose_name='SuppressTaskSFXReminders')
    user_preferences_task_reminders_checkbox_default = sf.BooleanField(verbose_name='TaskRemindersCheckboxDefault')
    user_preferences_user_debug_mode_pref = sf.BooleanField(verbose_name='UserDebugModePref')
    #user_role = sf.ForeignKey('UserRole', sf.DO_NOTHING, blank=True, null=True)
    user_type = sf.CharField(max_length=40, sf_read_only=sf.READ_ONLY, choices=[('Standard', 'Standard'), ('PowerPartner', 'Partner'), ('PowerCustomerSuccess', 'Customer Portal Manager'), ('CustomerSuccess', 'Customer Portal User'), ('Guest', 'Guest'), ('CspLitePortal', 'High Volume Portal'), ('CsnOnly', 'CSN Only'), ('SelfService', 'Self Service')], blank=True, null=True)
    username = sf.CharField(max_length=80)
    class Meta(sf.Model.Meta):
        db_table = 'User'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        # keyPrefix = '005'




class DandBcompany(sf.Model):
    address = sf.TextField(verbose_name='Primary Address', sf_read_only=sf.READ_ONLY, blank=True, null=True)  # This field type is a guess.
    city = sf.CharField(max_length=40, blank=True, null=True)
    company_currency_iso_code = sf.CharField(max_length=255, verbose_name='Local Currency ISO Code', choices=[('AED', 'AED - UAE Dirham'), ('AFN', 'AFN - Afghanistan Afghani (New)'), ('ALL', 'ALL - Albanian Lek'), ('AMD', 'AMD - Armenian Dram'), ('ANG', 'ANG - Neth Antilles Guilder'), ('AOA', 'AOA - Angola Kwanza'), ('ARS', 'ARS - Argentine Peso'), ('AUD', 'AUD - Australian Dollar'), ('AWG', 'AWG - Aruba Florin'), ('AZN', 'AZN - Azerbaijan Manat'), ('BAM', 'BAM - Convertible Marks'), ('BBD', 'BBD - Barbados Dollar'), ('BDT', 'BDT - Bangladesh Taka'), ('BGN', 'BGN - Bulgarian Lev'), ('BHD', 'BHD - Bahraini Dinar'), ('BIF', 'BIF - Burundi Franc'), ('BMD', 'BMD - Bermuda Dollar'), ('BND', 'BND - Brunei Dollar'), ('BOB', 'BOB - Bolivian Boliviano'), ('BOV', 'BOV - Bolivia Mvdol'), ('BRB', 'BRB - Brazilian Cruzeiro (old)'), ('BRL', 'BRL - Brazilian Real'), ('BSD', 'BSD - Bahamian Dollar'), ('BTN', 'BTN - Bhutan Ngultrum'), ('BWP', 'BWP - Botswana Pula'), ('BYN', 'BYN - Belarusian Ruble'), ('BYR', 'BYR - Belarusian Ruble'), ('BZD', 'BZD - Belize Dollar'), ('CAD', 'CAD - Canadian Dollar'), ('CDF', 'CDF - Franc Congolais'), ('CHF', 'CHF - Swiss Franc'), ('CLF', 'CLF - Unidades de fomento'), ('CLP', 'CLP - Chilean Peso'), ('CNY', 'CNY - Chinese Yuan'), ('COP', 'COP - Colombian Peso'), ('CRC', 'CRC - Costa Rica Colon'), ('CUC', 'CUC - Cuban Peso Convertible'), ('CUP', 'CUP - Cuban Peso'), ('CVE', 'CVE - Cape Verde Escudo'), ('CZK', 'CZK - Czech Koruna'), ('DJF', 'DJF - Dijibouti Franc'), ('DKK', 'DKK - Danish Krone'), ('DOP', 'DOP - Dominican Peso'), ('DZD', 'DZD - Algerian Dinar'), ('EEK', 'EEK - Estonian Kroon'), ('EGP', 'EGP - Egyptian Pound'), ('ERN', 'ERN - Eritrea Nakfa'), ('ETB', 'ETB - Ethiopian Birr'), ('EUR', 'EUR - Euro'), ('FJD', 'FJD - Fiji Dollar'), ('FKP', 'FKP - Falkland Islands Pound'), ('GBP', 'GBP - British Pound'), ('GEL', 'GEL - Georgia Lari'), ('GHS', 'GHS - Ghanaian Cedi'), ('GIP', 'GIP - Gibraltar Pound'), ('GMD', 'GMD - Gambian Dalasi'), ('GNF', 'GNF - Guinean Franc'), ('GTQ', 'GTQ - Guatemala Quetzal'), ('GYD', 'GYD - Guyana Dollar'), ('HKD', 'HKD - Hong Kong Dollar'), ('HNL', 'HNL - Honduras Lempira'), ('HRD', 'HRD - Croatian Dinar (Old)'), ('HRK', 'HRK - Kuna'), ('HTG', 'HTG - Haiti Gourde'), ('HUF', 'HUF - Hungarian Forint'), ('IDR', 'IDR - Indonesian Rupiah'), ('ILS', 'ILS - Israeli Shekel'), ('INR', 'INR - Indian Rupee'), ('IQD', 'IQD - Iraqi Dinar'), ('IRR', 'IRR - Iranian Rial'), ('ISK', 'ISK - Iceland Krona'), ('JMD', 'JMD - Jamaican Dollar'), ('JOD', 'JOD - Jordanian Dinar'), ('JPY', 'JPY - Japanese Yen'), ('KES', 'KES - Kenyan Shilling'), ('KGS', 'KGS - Kyrgyzstan Som'), ('KHR', 'KHR - Cambodia Riel'), ('KMF', 'KMF - Comorian Franc'), ('KPW', 'KPW - North Korean Won'), ('KRW', 'KRW - Korean Won'), ('KWD', 'KWD - Kuwaiti Dinar'), ('KYD', 'KYD - Cayman Islands Dollar'), ('KZT', 'KZT - Kazakhstan Tenge'), ('LAK', 'LAK - Lao Kip'), ('LBP', 'LBP - Lebanese Pound'), ('LKR', 'LKR - Sri Lanka Rupee'), ('LRD', 'LRD - Liberian Dollar'), ('LSL', 'LSL - Lesotho Loti'), ('LYD', 'LYD - Libyan Dinar'), ('MAD', 'MAD - Moroccan Dirham'), ('MDL', 'MDL - Moldovan Leu'), ('MGA', 'MGA - Malagasy Ariary'), ('MKD', 'MKD - Macedonian Denar'), ('MMK', 'MMK - Myanmar Kyat'), ('MNT', 'MNT - Mongolian Tugrik'), ('MOP', 'MOP - Macau Pataca'), ('MRO', 'MRO - Mauritanian Ougulya'), ('MRU', 'MRU - Mauritanian Ougulya'), ('MUR', 'MUR - Mauritius Rupee'), ('MVR', 'MVR - Maldives Rufiyaa'), ('MWK', 'MWK - Malawi Kwacha'), ('MXN', 'MXN - Mexican Peso'), ('MXV', 'MXV - Mexican Unidad de Inversion (UDI)'), ('MYR', 'MYR - Malaysian Ringgit'), ('MZN', 'MZN - Mozambique New Metical'), ('NAD', 'NAD - Namibian Dollar'), ('NGN', 'NGN - Nigerian Naira'), ('NIO', 'NIO - Nicaragua Cordoba'), ('NOK', 'NOK - Norwegian Krone'), ('NPR', 'NPR - Nepalese Rupee'), ('NZD', 'NZD - New Zealand Dollar'), ('OMR', 'OMR - Omani Rial'), ('PAB', 'PAB - Panama Balboa'), ('PEN', 'PEN - Peruvian Sol'), ('PGK', 'PGK - Papua New Guinea Kina'), ('PHP', 'PHP - Philippine Peso'), ('PKR', 'PKR - Pakistani Rupee'), ('PLN', 'PLN - Polish Zloty'), ('PYG', 'PYG - Paraguayan Guarani'), ('QAR', 'QAR - Qatar Rial'), ('RON', 'RON - Romanian Leu'), ('RSD', 'RSD - Serbian Dinar'), ('RUB', 'RUB - Russian Rouble'), ('RWF', 'RWF - Rwanda Franc'), ('SAR', 'SAR - Saudi Arabian Riyal'), ('SBD', 'SBD - Solomon Islands Dollar'), ('SCR', 'SCR - Seychelles Rupee'), ('SDG', 'SDG - Sudanese Pound'), ('SEK', 'SEK - Swedish Krona'), ('SGD', 'SGD - Singapore Dollar'), ('SHP', 'SHP - St Helena Pound'), ('SLL', 'SLL - Sierra Leone Leone'), ('SOS', 'SOS - Somali Shilling'), ('SRD', 'SRD - Surinam Dollar'), ('SSP', 'SSP - South Sudan Pound'), ('STD', 'STD - São Tomé and Príncipe Dobra'), ('STN', 'STN - São Tomé and Príncipe Dobra'), ('SYP', 'SYP - Syrian Pound'), ('SZL', 'SZL - Swaziland Lilageni'), ('THB', 'THB - Thai Baht'), ('TJS', 'TJS - Tajik Somoni'), ('TMT', 'TMT - Turkmenistan New Manat'), ('TND', 'TND - Tunisian Dinar'), ('TOP', "TOP - Tonga Pa'anga"), ('TRY', 'TRY - Turkish Lira (New)'), ('TTD', 'TTD - Trinidad&Tobago Dollar'), ('TWD', 'TWD - Taiwan Dollar'), ('TZS', 'TZS - Tanzanian Shilling'), ('UAH', 'UAH - Ukraine Hryvnia'), ('UGX', 'UGX - Ugandan Shilling'), ('USD', 'USD - U.S. Dollar'), ('UYU', 'UYU - Uruguayan Peso'), ('UZS', 'UZS - Uzbekistan Sum'), ('VEF', 'VEF - Venezuelan Bolivar Fuerte'), ('VES', 'VES - Venezuelan Bolívar Soberano'), ('VND', 'VND - Vietnam Dong'), ('VUV', 'VUV - Vanuatu Vatu'), ('WST', 'WST - Samoa Tala'), ('XAF', 'XAF - CFA Franc (BEAC)'), ('XCD', 'XCD - East Caribbean Dollar'), ('XOF', 'XOF - CFA Franc (BCEAO)'), ('XPF', 'XPF - Pacific Franc'), ('YER', 'YER - Yemen Riyal'), ('ZAR', 'ZAR - South African Rand'), ('ZMW', 'ZMW - Zambian Kwacha (New)'), ('ZWL', 'ZWL - Zimbabwe Dollar')], blank=True, null=True)
    country = sf.CharField(max_length=80, blank=True, null=True)
    country_access_code = sf.CharField(max_length=4, verbose_name='International Dialing Code', blank=True, null=True)
    created_by = sf.ForeignKey('User', sf.DO_NOTHING, related_name='dandbcompany_createdby_set', sf_read_only=sf.READ_ONLY)
    created_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    currency_code = sf.CharField(max_length=255, verbose_name='Local Currency Code', choices=[('0010', 'Canadian Dollar'), ('0020', 'U.S. Dollar'), ('0030', 'Argentine Peso'), ('0040', 'Aruban Florin'), ('0050', 'Australian Dollar'), ('0070', 'Barbados Dollar'), ('0075', 'St Helena Pound'), ('0090', 'Bermudian Dollar'), ('0095', 'Denar'), ('0100', 'Brazilian Cruzeiro (old)'), ('0105', 'Bosnia-Herzegovina Convertible Mark'), ('0110', 'Chinese Yuan Renminbi'), ('0120', 'Danish Krone'), ('0140', 'Eastern Caribbean Dollar'), ('0150', 'Egyptian Pound'), ('0155', 'Eritrean Nakfa'), ('0160', 'Pound Sterling'), ('0190', 'CFP Franc'), ('0220', 'Hong Kong Dollar'), ('0230', 'Indian Rupee'), ('0250', 'Israeli Sheqel (new)'), ('0270', 'Jamaican Dollar'), ('0280', 'Yen'), ('0290', 'Kenyan Shilling'), ('0305', 'Mongolian Tugrik'), ('0310', 'Moroccan Dirham'), ('0320', 'New Zealand Dollar'), ('0330', 'Norwegian Krone'), ('0370', 'Swedish Krona'), ('0380', 'Swiss Franc'), ('0390', 'New Taiwanese Dollar'), ('0400', 'Thai Baht'), ('0410', 'Afghani'), ('0420', 'Algerian Dinar'), ('0430', 'Bangladeshi Taka'), ('0440', 'Bahraini Dinar'), ('0450', 'Bahamian Dollar'), ('0460', 'Belize Dollar'), ('0470', 'Bolivian Boliviano'), ('0480', 'Botswani Pula'), ('0490', 'Brunei Dollar'), ('0500', 'Bulgarian Lev'), ('0520', 'Burundi Franc'), ('0530', 'Cape Verde Escudo'), ('0540', 'Cayman Islands Dollar'), ('0550', 'CFA Franc BCEAO'), ('0552', 'CFA Franc (BEAC)'), ('0560', 'Chilean Peso'), ('0580', 'Colombian Peso'), ('0585', 'Comoro Franc'), ('0590', 'Costa Rican Colon'), ('0595', 'Croatian Dinar (Old)'), ('0600', 'Cuban Peso'), ('0605', 'Cuban Peso Convertible'), ('0620', 'Czech Koruna'), ('0630', 'Djibouti Franc'), ('0640', 'Dominican Peso'), ('0650', 'Netherlands Antillean Guilder'), ('0690', 'Ethiopian Bir'), ('0700', 'Fiji Dollar'), ('0710', 'Dalasi'), ('0720', 'Ghana Cedi'), ('0730', 'Gibraltar Pound'), ('0750', 'Guinean Franc'), ('0760', 'Guyana Dollar'), ('0770', 'Gourde'), ('0780', 'Lempira'), ('0790', 'Forint'), ('0800', 'Icelandic Krona'), ('0820', 'Rupiah'), ('0830', 'Iraqi Dinar'), ('0840', 'Iranian Rial'), ('0860', 'Jordanian Dinar'), ('0870', 'Kuwaiti Dinar'), ('0880', 'Kip'), ('0890', 'Lebanese Pound'), ('0900', 'Loti'), ('0910', 'Liberian Dollar'), ('0920', 'Libyan Dinar'), ('0940', 'Malagasy Ariary'), ('0960', 'Kwacha'), ('0970', 'Malaysian Ringgit'), ('1000', 'Ouguiya'), ('1010', 'Mauritius Rupee'), ('1020', 'Mozambique Metical'), ('1030', 'Nepalese Rupee'), ('1040', 'Cordoba Oro'), ('1060', 'Rial Omani'), ('1070', 'Pakistan Rupee'), ('1080', 'Balboa'), ('1090', 'Kina'), ('2000', 'Guarani'), ('2010', 'Neuvo Sol'), ('2020', 'Philippine Peso'), ('2040', 'Qatari Riyal'), ('2060', 'Rwanda Franc'), ('2070', 'Dobra'), ('2080', 'Saudi Riyal'), ('2090', 'Seychelles Rupee'), ('3000', 'Singapore Dollar'), ('3010', 'Solomon Islands Dollar'), ('3020', 'Somali Shilling'), ('3030', 'Rand'), ('3040', 'Won'), ('3060', 'Sri Lanka Rupee'), ('3070', 'Sudanese Pound'), ('3075', 'South Sudanese Pound'), ('3085', 'Surinam Dollar'), ('3090', 'Lilangeni'), ('4000', 'Syrian Pound'), ('4010', 'Tanzanian Shilling'), ('4020', "Pa'anga"), ('4030', 'Trinidad & Tobago Dollar'), ('4040', 'Tunisian Dinar'), ('4060', 'UAE Dirham'), ('4070', 'Uganda Shilling'), ('4090', 'Vatu'), ('5005', 'Bolivar Fuerte'), ('5010', 'Dong'), ('5020', 'Yemenese Rial'), ('5030', 'Tala'), ('5040', 'Serbian Dinar'), ('5080', 'Euro'), ('5090', 'Angolan Kwanza'), ('6000', 'Leone'), ('6030', 'Congolese Franc'), ('6040', 'Peso Uruguayo'), ('6050', 'Lari'), ('6060', 'Hryvnia'), ('6100', 'Bhutan Ngultrum'), ('6200', 'Quetzal'), ('6300', 'Cambodian Riel'), ('6400', 'North Korean Won'), ('6500', 'Rufiyaa'), ('6600', 'Naira'), ('6800', 'Croatian Kuna'), ('6900', 'Falkland Islands Pound'), ('7200', 'Pataca'), ('7500', 'Mexican Peso (new)'), ('7600', 'Albanian Lek'), ('8000', 'Estonian Kroon'), ('8100', 'Belarussian Ruble'), ('8300', 'Moldovan Leu'), ('8500', 'Armenian Dram'), ('8700', 'Tenge'), ('8800', 'Turkmenistan Manat'), ('8900', 'Som'), ('9000', 'Uzbekistan Sum'), ('9100', 'Russian Ruble'), ('9300', 'Brazilian Real'), ('9410', 'Polish New Zloty'), ('9430', 'Myanmar Kyat'), ('9440', 'Turkish Lira (new)'), ('9450', 'Romanian Leu (new)'), ('9460', 'Azerbaijanian Manat (new)'), ('9470', 'Namibia Dollar')], blank=True, null=True)
    description = sf.TextField(verbose_name='Company Description', blank=True, null=True)
    domestic_ultimate_business_name = sf.CharField(max_length=255, blank=True, null=True)
    domestic_ultimate_duns_number = sf.CharField(max_length=9, verbose_name='Domestic Ultimate D-U-N-S Number', blank=True, null=True)
    duns_number = sf.CharField(unique=True, max_length=9, verbose_name='D-U-N-S Number')
    employee_quantity_growth_rate = sf.DecimalField(max_digits=18, decimal_places=6, verbose_name='Employee Growth', blank=True, null=True)
    employees_here = sf.DecimalField(max_digits=18, decimal_places=0, verbose_name='Number of Employees - Location', blank=True, null=True)
    employees_here_reliability = sf.CharField(max_length=255, verbose_name='Number of Employees - Location Indicator', choices=[('0', 'Actual number'), ('1', 'Low'), ('2', 'Estimated (for all records)'), ('3', 'Modeled (for non-US records)')], blank=True, null=True)
    employees_total = sf.DecimalField(max_digits=18, decimal_places=0, verbose_name='Number of Employees - Total', blank=True, null=True)
    employees_total_reliability = sf.CharField(max_length=255, verbose_name='Number of Employees - Total Indicator', choices=[('0', 'Actual number'), ('1', 'Low'), ('2', 'Estimated (for all records)'), ('3', 'Modeled (for non-US records)')], blank=True, null=True)
    family_members = sf.IntegerField(verbose_name='Number of Business Family Members', blank=True, null=True)
    fax = sf.CharField(max_length=40, verbose_name='Facsimile Number', blank=True, null=True)
    fifth_naics = sf.CharField(max_length=6, verbose_name='Fifth NAICS Code', blank=True, null=True)
    fifth_naics_desc = sf.CharField(max_length=120, verbose_name='Fifth NAICS Description', blank=True, null=True)
    fifth_sic = sf.CharField(max_length=4, verbose_name='Fifth SIC Code', blank=True, null=True)
    fifth_sic_desc = sf.CharField(max_length=80, verbose_name='Fifth SIC Description', blank=True, null=True)
    fifth_sic8 = sf.CharField(max_length=8, verbose_name='Fifth SIC8 Code', blank=True, null=True)
    fifth_sic8_desc = sf.CharField(max_length=80, verbose_name='Fifth SIC8 Description', blank=True, null=True)
    fips_msa_code = sf.CharField(max_length=5, verbose_name='FIPS MSA Code', blank=True, null=True)
    fips_msa_desc = sf.CharField(max_length=255, verbose_name='FIPS MSA Code Description', blank=True, null=True)
    fortune_rank = sf.IntegerField(verbose_name='Fortune 1000 Rank', blank=True, null=True)
    fourth_naics = sf.CharField(max_length=6, verbose_name='Fourth NAICS Code', blank=True, null=True)
    fourth_naics_desc = sf.CharField(max_length=120, verbose_name='Fourth NAICS Description', blank=True, null=True)
    fourth_sic = sf.CharField(max_length=4, verbose_name='Fourth SIC Code', blank=True, null=True)
    fourth_sic_desc = sf.CharField(max_length=80, verbose_name='Fourth SIC Description', blank=True, null=True)
    fourth_sic8 = sf.CharField(max_length=8, verbose_name='Fourth SIC8 Code', blank=True, null=True)
    fourth_sic8_desc = sf.CharField(max_length=80, verbose_name='Fourth SIC8 Description', blank=True, null=True)
    geo_code_accuracy = sf.CharField(max_length=255, verbose_name='Geocode Accuracy', choices=[('D', 'Rooftop level. Precise physical address'), ('S', 'Street level. Correct street and within a range of street numbers. Accuracy .1 to .2 miles'), ('B', 'Block level. (ZIP+4 Centroid) Correct street and within a range of blocks. Accuracy .2 to .4 miles'), ('T', 'Census tract level. (ZIP+2 Centroid) Correct street and within a range of census tracts. Accuracy .4 to .6 miles'), ('M', 'Mailing address level. Physical address not valid or not present'), ('Z', 'ZIP code level. Correct 5-digit ZIP code'), ('0', 'Geocode could not be assigned'), ('C', 'Places the address in the correct city'), ('N', 'Not matched'), ('I', 'Street intersection'), ('P', 'PO Box location'), ('A', 'Non-US rooftop accuracy'), ('H', 'State or Province Centroid'), ('K', 'County Centroid'), ('G', 'Sub Locality-Street Level'), ('L', 'Locality Centroid')], blank=True, null=True)
    geocode_accuracy_standard = sf.CharField(max_length=255, verbose_name='Geocode Accuracy', choices=[('Address', 'Address'), ('NearAddress', 'NearAddress'), ('Block', 'Block'), ('Street', 'Street'), ('ExtendedZip', 'ExtendedZip'), ('Zip', 'Zip'), ('Neighborhood', 'Neighborhood'), ('City', 'City'), ('County', 'County'), ('State', 'State'), ('Unknown', 'Unknown')], blank=True, null=True)
    global_ultimate_business_name = sf.CharField(max_length=255, blank=True, null=True)
    global_ultimate_duns_number = sf.CharField(max_length=9, verbose_name='Global Ultimate D-U-N-S Number', blank=True, null=True)
    global_ultimate_total_employees = sf.DecimalField(max_digits=18, decimal_places=0, verbose_name='Number of Employees - Global', blank=True, null=True)
    import_export_agent = sf.CharField(max_length=255, verbose_name='Import/Export', choices=[('A', 'Importer/Exporter/Agent'), ('B', 'Importer/Exporter'), ('C', 'Importer'), ('D', 'Importer/Agent'), ('E', 'Exporter/Agent'), ('F', 'Agent. Keeps no inventory and does not take title goods'), ('G', 'None or Data Not Available'), ('H', 'Exporter')], blank=True, null=True)
    included_in_sn_p500 = sf.CharField(max_length=10, verbose_name='S&P 500', blank=True, null=True)
    is_deleted = sf.BooleanField(verbose_name='Deleted', sf_read_only=sf.READ_ONLY, default=False)
    last_modified_by = sf.ForeignKey('User', sf.DO_NOTHING, related_name='dandbcompany_lastmodifiedby_set', sf_read_only=sf.READ_ONLY)
    last_modified_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    last_referenced_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY, blank=True, null=True)
    last_viewed_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY, blank=True, null=True)
    latitude = sf.CharField(max_length=11, blank=True, null=True)
    legal_status = sf.CharField(max_length=255, verbose_name='Legal Structure', choices=[('100', 'Cooperative'), ('101', 'Nonprofit organization'), ('118', 'Local government body'), ('012', 'Partnership of unknown type'), ('120', 'Foreign company'), ('013', 'Proprietorship'), ('003', 'Corporation'), ('050', 'Government body'), ('008', 'Joint venture'), ('000', 'Not available'), ('009', 'Master limited partnership'), ('010', 'General partnership'), ('011', 'Limited partnership'), ('014', 'Limited liability'), ('015', 'Friendly society'), ('030', 'Trust'), ('070', 'Crown corporation'), ('080', 'Institution'), ('090', 'Estate'), ('099', 'Industry cooperative'), ('102', 'Private limited company'), ('103', 'Partnership partially limited by shares'), ('104', 'Temporary association'), ('105', 'Registered proprietorship'), ('106', 'Limited partnership with shares'), ('107', 'Unregistered proprietorship'), ('108', 'Community of goods'), ('109', 'Reciprocal guarantee company'), ('110', 'Cooperative society with limited liability'), ('111', 'Civil company'), ('112', 'De facto partnership'), ('113', 'Foundation'), ('114', 'Association'), ('115', 'Public company'), ('116', 'Civil law partnership'), ('117', 'Incorporated by act of Parliament'), ('119', 'Private unlimited company'), ('121', 'Private company limited by guarantee'), ('122', 'Civil partnership'), ('125', 'Public limited company'), ('126', 'Registered partnership'), ('127', 'Society'), ('128', 'Government-owned company'), ('129', 'Government institute'), ('130', 'Public institute'), ('131', 'Plant'), ('132', 'Hotel'), ('133', 'Division'), ('140', 'Joint shipping company'), ('142', 'Limited-liability corporation'), ('143', 'Branch'), ('144', 'Concern address'), ('145', 'Insurance company'), ('146', 'Private foundation'), ('147', 'County institution'), ('148', 'Municipal institution'), ('149', 'Vestry'), ('150', 'Public undertaking'), ('151', 'Faeroese company'), ('152', 'Greenland limited'), ('153', 'Greenland private limited'), ('154', 'Sole proprietorship'), ('155', 'Sole proprietorship or partnership'), ('160', 'Unregistered partnership'), ('161', 'Civil association'), ('162', 'Association in participation'), ('163', 'Mutual insurance association'), ('164', 'Stock company with variable capital'), ('166', 'Cooperative production society'), ('167', 'Joint stock company'), ('168', 'Limited responsibility cooperative society'), ('169', 'National credit society'), ('170', 'Offene erwerbsgesellschaft'), ('171', 'Limited liability company with variable cap'), ('180', 'Kommandit erwerbsgesellschaft'), ('185', 'Public credit institution'), ('186', 'Working group'), ('190', 'Union'), ('200', 'Personal partnership'), ('202', 'Unlimited liability rural production company'), ('204', 'Named collective company with variable capital'), ('206', 'Individual with business activity'), ('208', 'Association with shares in the stock market'), ('210', 'Real estate partnership'), ('212', 'Association with shares in the stock market with variable capital'), ('214', 'Association with shares with variable capital (investment company)'), ('216', 'Association with shares with variable capital (investment company with debt instruments)'), ('218', 'Association with shares with variable capital investment company with variable rent)'), ('220', 'Agricultural collective interest company'), ('222', 'Association with shares with variable capital (financial company with limited object)'), ('224', 'Association with shares with variable capital (financial company with multiple objects non-regulated entity)'), ('226', 'Association with shares with variable capital (financial company with multiple objects regulated entity)'), ('228', 'Association with shares investment promotor'), ('230', 'Defacto business organization'), ('232', 'Association with shares in the stock market (investment promotor)'), ('234', 'Association with shares in the stock market (investment promotor with variable capital)'), ('236', 'Association with shares with variable capital (investment promotor) '), ('238', 'Association with shares (capital investment company)'), ('240', 'Government/municipal establishment'), ('242', 'Association with shares (investment company with debt instruments)'), ('244', 'Association with shares (investment company with variable rent)'), ('246', 'Association with shares (financial company with limited object)'), ('248', 'Association with shares (financial company with multiple objects non-regulated entity)'), ('250', 'Housing company'), ('252', 'Association with shares (financial company with multiple objects regulated entity)'), ('254', 'Cooperative production society of variable capital of limited Responsibility'), ('256', 'Limited liability rural production company'), ('260', 'Voluntary association'), ('270', 'Mortgage association'), ('280', 'Cooperative society'), ('290', 'Cooperative bank'), ('300', 'Savings bank'), ('301', 'Small individual business'), ('302', 'Private company'), ('304', 'Unregistered'), ('306', 'Government department/city council'), ('308', 'State government'), ('310', 'Economic association'), ('312', 'Class order'), ('314', 'Business name'), ('316', 'Sole trader'), ('318', 'Trustee company'), ('320', 'Insurance limited company'), ('322', 'Listed public company (limited)'), ('324', 'Unlisted public company'), ('326', 'limited by guarantee'), ('328', 'Listed public company (no liability) '), ('330', 'Government authority'), ('332', 'Professional organization/association'), ('334', 'Registered Australian body'), ('336', 'Corporate partnership'), ('338', 'Industrial and provident societies'), ('340', 'Group'), ('342', 'Charitable trust'), ('344', 'Overseas company'), ('346', 'Proprietary company'), ('350', 'Housing cooperative society'), ('360', 'Mutual assistance business organization'), ('370', 'Provident business organization'), ('380', 'Limited company'), ('390', 'Simple partnership'), ('410', 'Commercial collective company'), ('420', 'Commercial company'), ('430', 'Representative office'), ('440', 'Bank'), ('450', 'Industry and equity company'), ('451', 'Trading society'), ('452', 'Government institution'), ('460', 'Open stock corporation'), ('470', 'Trusteeship'), ('480', 'Private business'), ('490', 'Decentralized public organization'), ('500', 'Stock company'), ('502', "Tenant owner's society"), ('510', 'Civil society'), ('520', 'Society for capitalization of savings'), ('530', 'Limited cooperative company'), ('540', 'Mutual insurance society'), ('550', 'Simple limited partnership'), ('560', 'Named collective company'), ('570', 'Non-profit association'), ('580', 'Corporation with variable capital'), ('590', 'Joint corporation'), ('600', 'Consortium'), ('610', 'Personal firm'), ('620', 'Corporation with authorized capital'), ('630', 'Corporation with open capital'), ('640', 'Bank for capitalization of savings'), ('650', 'Closed stock corporation'), ('660', 'Commercial and industrial corporation'), ('670', 'Commercial corporation'), ('680', 'Industrial corporation'), ('690', 'Financial institution'), ('700', 'Contract mining company'), ('710', 'Contracting company'), ('720', 'Non-profit international organization'), ('730', 'International organization'), ('740', 'Limited co auth capital-regd co open cap'), ('750', 'Organization'), ('755', 'Unlimited company'), ('760', "Farmer's association"), ('770', "Economic assoc/tenant owners' society"), ('780', 'Mining company'), ('790', 'Shipping company'), ('800', 'Simple company'), ('810', 'Private firm'), ('820', 'Family foundation'), ('830', 'County'), ('840', 'County association'), ('850', 'County council'), ('860', 'Regional social insurance office'), ('870', 'Unit within the Swedish church'), ('880', 'Public corporation/institution'), ('881', 'Statutory body'), ('890', 'Mortgage/security association'), ('891', 'Government agency'), ('892', 'Mutual company'), ('893', 'Special corporation'), ('894', 'Central bank for agriculture & forestry'), ('895', 'Austrian legal entity'), ('896', 'Establishment'), ('900', 'Supporting association'), ('905', 'Administration'), ('910', 'Unemployment office'), ('915', 'Liaison office'), ('920', 'Foreign legal person'), ('925', 'Cooperative union with guaranteed liab'), ('930', 'Swedish legal person'), ('935', 'Cooperative union with limited liability'), ('940', 'Unlimited partnership'), ('945', 'Cooperative society with unlimited liability'), ('950', 'Foreign branch'), ('955', 'Cooperative society with guaranteed liability'), ('960', 'Incorporated foundation'), ('965', 'Business not formally registered'), ('970', 'Incorporated non-profit association'), ('971', 'State-owned enterprise'), ('972', 'Free trade zone entp. proc. prvd. smpl.'), ('973', 'Limited holding company'), ('974', 'Government department or non-profit organization'), ('975', 'Government department'), ('976', 'Collectively owned enterprise'), ('977', 'Domestic and foreign joint venture'), ('978', 'Domestic and foreign cooperative venture'), ('980', 'Educational foundation'), ('985', 'Unlimited company ltd. liab. shareholder'), ('990', 'Medical corporation'), ('991', 'Private limited liability company'), ('992', 'Public limited liability company'), ('993', 'Exempt limited liability company'), ('994', 'Deemed public limited company'), ('995', 'Private company limited by shares'), ('999', 'Securities fund')], blank=True, null=True)
    location_status = sf.CharField(max_length=255, verbose_name='Location Type', choices=[('0', 'Single Location. No other entities report to the business'), ('1', 'Headquarters/Parent. Branches and/or subsidiaries report to the business'), ('2', 'Branch. Secondary location to a headquarters location')], blank=True, null=True)
    longitude = sf.CharField(max_length=11, blank=True, null=True)
    mailing_address = sf.TextField(sf_read_only=sf.READ_ONLY, blank=True, null=True)  # This field type is a guess.
    mailing_city = sf.CharField(max_length=40, blank=True, null=True)
    mailing_country = sf.CharField(max_length=80, blank=True, null=True)
    mailing_geocode_accuracy = sf.CharField(max_length=255, choices=[('Address', 'Address'), ('NearAddress', 'NearAddress'), ('Block', 'Block'), ('Street', 'Street'), ('ExtendedZip', 'ExtendedZip'), ('Zip', 'Zip'), ('Neighborhood', 'Neighborhood'), ('City', 'City'), ('County', 'County'), ('State', 'State'), ('Unknown', 'Unknown')], blank=True, null=True)
    mailing_postal_code = sf.CharField(max_length=20, blank=True, null=True)
    mailing_state = sf.CharField(max_length=80, blank=True, null=True)
    mailing_street = sf.TextField(verbose_name='Mailing Street Address', blank=True, null=True)
    marketing_pre_screen = sf.CharField(max_length=255, verbose_name='Delinquency Risk', choices=[('L', 'Low risk of delinquency'), ('M', 'Moderate risk of delinquency'), ('H', 'High risk of delinquency')], blank=True, null=True)
    marketing_segmentation_cluster = sf.CharField(max_length=255, choices=[('1', 'High-Tension Branches of Insurance/Utility Industries'), ('2', 'Bustling Manufacturers & Business Services'), ('3', 'The Withering Branch Company'), ('4', 'Rapid-Growth Large Businesses'), ('5', 'Sunny Branches of Insurance/Utility Industries'), ('6', 'Labor-Intensive Giants'), ('7', 'Entrepreneur & Co.'), ('8', 'Frugal & Associates'), ('9', 'Spartans'), ('10', 'Struggling Startups'), ('11', 'The Hectic Venture Company'), ('12', 'The Established Shingle Company'), ('13', 'Industry, Inc.'), ('14', 'Landmark Business Services'), ('15', 'The Test Of Time Company'), ('16', 'Powerhouse 6000'), ('17', 'In Good Hands'), ('18', 'Sudden-Growth Giants'), ('19', 'Active Traders'), ('20', 'Old Core Proprietors'), ('21', 'Solid & Sons'), ('22', 'Main Street USA')], blank=True, null=True)
    minority_owned = sf.CharField(max_length=255, verbose_name='Minority-Owned Indicator', choices=[('Y', 'Minority-owned'), ('N', 'Not minority-owned')], blank=True, null=True)
    name = sf.CharField(max_length=255, verbose_name='Primary Business Name')
    national_id = sf.CharField(max_length=255, verbose_name='National Identification Number', blank=True, null=True)
    national_id_type = sf.CharField(max_length=255, verbose_name='National Identification System', choices=[('00010', 'Belgium Enterprise Number'), ('00011', 'Belgium Branch Unit Number'), ('00100', 'Tokyo Shoko Research Business Identifier'), ('00102', 'Emc Entered Registration Number'), ('00103', 'Emc Entered Tax Registration Number'), ('00104', 'Emc Entered Chamber of Commerce Number'), ('00105', 'Emc Government Gazette Number'), ('00106', 'Sweden Registration Number'), ('00107', 'Finnish Registration Number'), ('00108', 'Costa Rican Judicial Number'), ('00109', 'El Salvadoran Patron'), ('00110', 'Hungarian Tax Identifier'), ('00111', 'Sweden Branch Number'), ('00112', 'Jamaican Tax Identification Number'), ('00113', 'Trinidadian Tax Identification Number'), ('00115', 'Dominican Republic National Commercial Registry Number'), ('00119', 'Peruvian Sole Commercial Registry Number'), ('00012', 'UK Cro Number'), ('00120', 'Hungarian Registration Number'), ('00125', 'Venezuelan National Tributary ID Number'), ('00127', 'Nicaraguan Sole Commercial Registry Number'), ('00013', 'Ireland Cro Number'), ('00130', 'Polish Tax Identifier'), ('00135', 'Costa Rican Tax Registration Number'), ('00014', 'France Siren Number'), ('00140', 'Polish Registration Number'), ('00145', 'Colombian National Trubutary ID Number'), ('00155', 'El Salvadoran National Tributary ID Number'), ('00016', 'Monte Carlo Siren Number'), ('00165', 'Bolivian Sole Commercial Registry Number'), ('00017', 'France Siret Number'), ('00175', 'Ecuadorian Sole Commercial Registry Number'), ('00018', 'Europe Standard VAT Number'), ('00185', 'Sole Commercial Registry Nbr Unk Ctry'), ('00019', 'Netherland Chamber Of Commerce Number'), ('00195', 'National Tributary ID Number Unk Country'), ('00020', 'Germany Registration Number'), ('00200', 'Argentinian Unique Tax ID Key'), ('00021', 'Italy Chamber of Commerce Number'), ('00210', 'Paraguayan Unique Tax Registration'), ('00211', 'Brazilian State Registry Number'), ('00212', 'Brazilian Municipal Registry Number'), ('00022', 'Taiwan Business Registration Number'), ('00220', 'Uruguayan Unique Tax Registration'), ('00230', 'Mexican Federal Tax Registration'), ('00024', 'Spain Fiscal Code'), ('00240', 'Chilean Unique Tax ID'), ('00025', 'Andorra Fiscal Code'), ('00250', 'Venezuelan Registry of Fiscal Info'), ('00026', 'Portugal Fiscal Code'), ('00260', 'Brazilian General Record of Taxpayers'), ('00270', 'Norwegian Government Organization Number'), ('00281', 'Hong Kong Business Registration Number'), ('00282', 'Macao Cmcl Registry Company ID Number'), ('00283', 'Macao Cmcl Registry Bus Regn Number'), ('00284', 'So Korean St Cmcl Registry Bus Regn Number'), ('00285', 'So Korean Trad Assn Expt/Impt Regn Number'), ('00286', 'Czech Republic ICO'), ('00290', 'Czech VAT Number'), ('00030', 'CUSIP Number'), ('00300', 'Bangladesh Company Incorporation Number'), ('00301', 'Brunei Registration Number'), ('00302', 'India Company Incorporation Number'), ('00303', 'Indonesia Legalization Number'), ('00304', 'Indonesia President Decree Number'), ('00305', 'Malaysia Company Registration Number'), ('00306', 'Malaysia Business Registration Number'), ('00307', 'Nepal Company Incorporation Number'), ('00308', 'Pakistan Company Incorporation Number'), ('00309', 'Philippines Registration Number'), ('00031', 'Australia Company Number'), ('00310', 'Sri Lanka Company Incorporation Number'), ('00311', 'Thailand Registration Number'), ('00312', 'Vietnam Business Registration Number'), ('00313', 'Vietnam Investment License Code'), ('00314', 'Vietnam License for the Establishment'), ('00315', 'Vietnam License Number'), ('00316', 'Maldives Registration Number'), ('00317', 'Bhutan Registration Number'), ('00318', 'Myanmar Registration Number'), ('00032', 'Singapore Registration File Number'), ('00320', 'Hungarian VAT Number'), ('00321', 'New Zealand National Company Number - Ncn'), ('00322', 'Australia Business Registration Number'), ('00323', 'Australian Business Number'), ('00324', 'South African Registration Number'), ('00325', 'Greek Business Registration Number'), ('00033', 'Hong Kong Co Registry Company ID Number'), ('00034', 'CINS Number'), ('00035', 'Panamanian Sole Commercial Registry Number'), ('00036', 'Portugal Chamber of Commerce Number'), ('00040', 'Mexico Iva'), ('00045', 'Israel Registration Number'), ('00050', 'Israel VAT Number'), ('00521', 'Denmark CVR Number'), ('00522', 'United Arab Emirates Registration Number'), ('00523', 'Bahrain Registration Number'), ('00524', 'Iraq Registration Number'), ('00525', 'Iran Registration Number'), ('00526', 'Jordan Registration Number'), ('00527', 'Kuwait Registration Number'), ('00528', 'Lebanon Registration Number'), ('00529', 'Oman Registration Number'), ('00530', 'Qatar Registration Number'), ('00531', 'Saudi Arabia Registration Number'), ('00532', 'Syria Registration Number'), ('00533', 'Yemen Registration Number'), ('00534', 'United Arab Emirates Chamber of Commerce Number'), ('00535', 'Bahrain Chamber of Commerce Number'), ('00536', 'Iran Chamber of Commerce Number'), ('00537', 'Jordan Chamber of Commerce Number'), ('00538', 'Kuwait Chamber of Commerce Number'), ('00539', 'Lebanon Chamber of Commerce Number'), ('00540', 'Oman Chamber of Commerce Number'), ('00541', 'Qatar Chamber of Commerce Number'), ('00542', 'Saudi Arabia Chamber of Commerce Number'), ('00543', 'Syria Chamber of Commerce Number'), ('00544', 'Yemen Chamber of Commerce Number'), ('00545', 'Angola Registration Number'), ('00546', 'Burkino Faso Registration Number'), ('00547', 'Burundi Registration Number'), ('00548', 'Benin Registration Number'), ('00549', 'Central African Republic Registration Number'), ('00055', 'Liechtenstein Registration Number'), ('00550', 'Congo Registration Number'), ('00551', 'Ivory Coast Registration Number'), ('00552', 'Cameroon Registration Number'), ('00553', 'Cape Verde Registration Number'), ('00554', 'Djibouti Registration Number'), ('00555', 'Algeria Registration Number'), ('00556', 'Egypt Registration Number'), ('00557', 'Eritrea Registration Number'), ('00558', 'Ethiopia Registration Number'), ('00559', 'Falkland Islands Registration Number'), ('00560', 'Gabon Registration Number'), ('00561', 'Ghana Registration Number'), ('00562', 'Gambia Registration Number'), ('00563', 'Guinea Registration Number'), ('00564', 'Equatorial Guinea Registration Number'), ('00565', 'Guinea-Bissau Registration Number'), ('00566', 'Kenya Registration Number'), ('00567', 'Comoros Registration Number'), ('00568', 'Liberia Registration Number'), ('00569', 'Morocco Registration Number'), ('00570', 'Madagascar Registration Number'), ('00571', 'Mali Registration Number'), ('00572', 'Mauritania Registration Number'), ('00573', 'Mauritius Registration Number'), ('00574', 'Malawi Registration Number'), ('00575', 'Mozambique Registration Number'), ('00576', 'Niger Registration Number'), ('00577', 'Nigeria Registration Number'), ('00578', 'Rwanda Registration Number'), ('00579', 'Seychelles Registration Number'), ('00580', 'Sudan Registration Number'), ('00581', 'St Helena Registration Number'), ('00582', 'Sierra Leone Registration Number'), ('00583', 'Senegal Registration Number'), ('00584', 'Somalia Registration Number'), ('00585', 'Chad Registration Number'), ('00586', 'Togo Registration Number'), ('00587', 'Tanzania Registration Number'), ('00588', 'Uganda Registration Number'), ('00589', 'Zambia Registration Number'), ('00590', 'Ivory Coast Chamber of Commerce Number'), ('00591', 'Cameroon Chamber of Commerce Number'), ('00592', 'Algeria Chamber of Commerce Number'), ('00593', 'Egypt Chamber of Commerce Number'), ('00594', 'Gabon Chamber of Commerce Number'), ('00595', 'Morocco Chamber of Commerce Number'), ('00596', 'Seychelles Chamber of Commerce Number'), ('00597', 'Senegal Chamber of Commerce Number'), ('00598', 'Ivory Coast Tax Registration Number'), ('00599', 'Cameroon Tax Registration Number'), ('00060', 'Italy Fiscal Code'), ('00600', 'Egypt Tax Registration Number'), ('00601', 'Gabon Tax Registration Number'), ('00602', 'Ghana Tax Registration Number'), ('00603', 'Morocco Tax Registration Number'), ('00604', 'Mauritius Tax Registration Number'), ('00605', 'Senegal Tax Registration Number'), ('00610', 'Botswana Tax Registration Number'), ('00620', 'Lesotho Tax Registration Number'), ('00630', 'Namibia Tax Registration Number'), ('00640', 'Swaziland Tax Registration Number'), ('00065', 'Denmark Registration Number'), ('00650', 'South Africa Value Added Tax Number'), ('00660', 'South Africa Tax Registration Number'), ('00670', 'South Africa Pay As You Earn Registration Number'), ('00070', 'Austria Trade Register Number'), ('00702', 'Switzerland Registration Number'), ('00075', 'Zimbabwe Organization Registration Number'), ('00080', 'Zimbabwe Individual Registration Number'), ('00090', 'Guatemalan Sole Commercial Registry Number'), ('00095', 'Colombian Registry of Fiscal Info'), ('00042', 'Netherlands Branch Unit Number'), ('00043', 'Netherlands Legal Entity And Partnership Information Number'), ('00122', 'East Timor Tax Identification Number'), ('00330', 'Philippinies Securities & Exchange Commission Number'), ('00335', 'India Society Registration Number'), ('00340', 'India Trade Registration Number'), ('00342', 'India Goods & Services (GST) ID'), ('00345', 'Pakistan Securites & Exchange Commission Number'), ('00350', 'Thailand Commercial Registration Number'), ('00355', 'Thailand Securities & Exchange Commission Number'), ('00360', 'Austria Association Registration Number'), ('00400', 'Value Added Tax Number (IN)'), ('00519', 'Value Added Tax Number (AE)'), ('00520', 'Value Added Tax Number (SA)'), ('00710', 'China National Organization Code'), ('00711', 'United Social Credit Code'), ('00712', 'Tax Identification Number (CN)'), ('00715', 'China Business Registration Number'), ('00720', 'Swiss Uniform Identification Number'), ('00740', 'Slovakia ICO Number'), ('00753', 'Tax Identification Number (IN)'), ('00362', 'Monaco Trade & Industry Registration Number'), ('00142', 'Polish National Court Council Number'), ('00143', 'Polish License Number'), ('00293', 'Czech Republic Tax Registration Number'), ('00735', 'Slovakia Tax Registration Number'), ('00730', 'Slovakia Court Number of Registration'), ('00099', 'Japan Corporate Number'), ('00101', 'Japan Stock Exchange Number')], blank=True, null=True)
    out_of_business = sf.CharField(max_length=255, verbose_name='Out Of Business Indicator', choices=[('Y', 'Out of Business'), ('N', 'Not Out of Business')], blank=True, null=True)
    own_or_rent = sf.CharField(max_length=255, verbose_name='Location Ownership Indicator', choices=[('0', 'Unknown or Not Applicable'), ('1', 'Owns'), ('2', 'Rents')], blank=True, null=True)
    parent_or_hq_business_name = sf.CharField(max_length=255, verbose_name='Parent Company Business Name', blank=True, null=True)
    parent_or_hq_duns_number = sf.CharField(max_length=9, verbose_name='Parent Company D-U-N-S Number', blank=True, null=True)
    phone = sf.CharField(max_length=40, verbose_name='Telephone Number', blank=True, null=True)
    postal_code = sf.CharField(max_length=20, blank=True, null=True)
    premises_measure = sf.IntegerField(verbose_name='Location Size', blank=True, null=True)
    premises_measure_reliability = sf.CharField(max_length=64, verbose_name='Location Size Accuracy', blank=True, null=True)
    premises_measure_unit = sf.CharField(max_length=64, verbose_name='Location Size Unit of Measure', blank=True, null=True)
    primary_naics = sf.CharField(max_length=6, verbose_name='Primary NAICS Code', blank=True, null=True)
    primary_naics_desc = sf.CharField(max_length=120, verbose_name='Primary NAICS Description', blank=True, null=True)
    primary_sic = sf.CharField(max_length=4, verbose_name='Primary SIC Code', blank=True, null=True)
    primary_sic_desc = sf.CharField(max_length=80, verbose_name='Primary SIC Description', blank=True, null=True)
    primary_sic8 = sf.CharField(max_length=8, verbose_name='Primary SIC8 Code', blank=True, null=True)
    primary_sic8_desc = sf.CharField(max_length=80, verbose_name='Primary SIC8 Description', blank=True, null=True)
    prior_year_employees = sf.IntegerField(verbose_name='Prior Year Number of Employees - Total', blank=True, null=True)
    prior_year_revenue = sf.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    public_indicator = sf.CharField(max_length=255, verbose_name='Ownership Type Indicator', choices=[('Y', 'Public'), ('N', 'Private')], blank=True, null=True)
    sales_turnover_growth_rate = sf.DecimalField(max_digits=18, decimal_places=6, verbose_name='Annual Revenue Growth', blank=True, null=True)
    sales_volume = sf.DecimalField(max_digits=18, decimal_places=0, verbose_name='Annual Sales Volume', blank=True, null=True)
    sales_volume_reliability = sf.CharField(max_length=255, verbose_name='Annual Sales Volume Indicator', choices=[('0', 'Actual number'), ('1', 'Low'), ('2', 'Estimated (for all records)'), ('3', 'Modeled (for non-US records)')], blank=True, null=True)
    second_naics = sf.CharField(max_length=6, verbose_name='Second NAICS Code', blank=True, null=True)
    second_naics_desc = sf.CharField(max_length=120, verbose_name='Second NAICS Description', blank=True, null=True)
    second_sic = sf.CharField(max_length=4, verbose_name='Second SIC Code', blank=True, null=True)
    second_sic_desc = sf.CharField(max_length=80, verbose_name='Second SIC Description', blank=True, null=True)
    second_sic8 = sf.CharField(max_length=8, verbose_name='Second SIC8 Code', blank=True, null=True)
    second_sic8_desc = sf.CharField(max_length=80, verbose_name='Second SIC8 Description ', blank=True, null=True)
    sixth_naics = sf.CharField(max_length=6, verbose_name='Sixth NAICS Code', blank=True, null=True)
    sixth_naics_desc = sf.CharField(max_length=120, verbose_name='Sixth NAICS Description', blank=True, null=True)
    sixth_sic = sf.CharField(max_length=4, verbose_name='Sixth SIC Code', blank=True, null=True)
    sixth_sic_desc = sf.CharField(max_length=80, verbose_name='Sixth SIC Description', blank=True, null=True)
    sixth_sic8 = sf.CharField(max_length=8, verbose_name='Sixth SIC8 Code', blank=True, null=True)
    sixth_sic8_desc = sf.CharField(max_length=80, verbose_name='Sixth SIC8 Description', blank=True, null=True)
    small_business = sf.CharField(max_length=255, verbose_name='Small Business Indicator', choices=[('Y', 'Small business site'), ('N', 'Not small business site')], blank=True, null=True)
    state = sf.CharField(max_length=80, blank=True, null=True)
    stock_exchange = sf.CharField(max_length=16, blank=True, null=True)
    stock_symbol = sf.CharField(max_length=6, verbose_name='Ticker Symbol', blank=True, null=True)
    street = sf.TextField(verbose_name='Street Address', blank=True, null=True)
    subsidiary = sf.CharField(max_length=255, verbose_name='Subsidiary Indicator', choices=[('0', 'Not subsidiary of another organization'), ('3', 'Subsidiary of another organization')], blank=True, null=True)
    system_modstamp = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    third_naics = sf.CharField(max_length=6, verbose_name='Third NAICS Code', blank=True, null=True)
    third_naics_desc = sf.CharField(max_length=120, verbose_name='Third NAICS Description', blank=True, null=True)
    third_sic = sf.CharField(max_length=4, verbose_name='Third SIC Code', blank=True, null=True)
    third_sic_desc = sf.CharField(max_length=80, verbose_name='Third SIC Description', blank=True, null=True)
    third_sic8 = sf.CharField(max_length=8, verbose_name='Third SIC8 Code', blank=True, null=True)
    third_sic8_desc = sf.CharField(max_length=80, verbose_name='Third SIC8 Description', blank=True, null=True)
    trade_style1 = sf.CharField(max_length=255, verbose_name='Primary Tradestyle', blank=True, null=True)
    trade_style2 = sf.CharField(max_length=255, verbose_name='Second Tradestyle', blank=True, null=True)
    trade_style3 = sf.CharField(max_length=255, verbose_name='Third Tradestyle', blank=True, null=True)
    trade_style4 = sf.CharField(max_length=255, verbose_name='Fourth Tradestyle', blank=True, null=True)
    trade_style5 = sf.CharField(max_length=255, verbose_name='Fifth Tradestyle', blank=True, null=True)
    url = sf.URLField(db_column='URL', verbose_name='URL', blank=True, null=True)
    us_tax_id = sf.CharField(max_length=9, verbose_name='US Tax ID Number', blank=True, null=True)
    women_owned = sf.CharField(max_length=255, verbose_name='Woman-Owned Indicator', choices=[('Y', 'Owned by a woman'), ('N', 'Not owned by a woman or unknown')], blank=True, null=True)
    year_started = sf.CharField(max_length=4, blank=True, null=True)
    class Meta(sf.Model.Meta):
        db_table = 'DandBCompany'
        verbose_name = 'D&B Company'
        verbose_name_plural = 'D&B Companies'
        # keyPrefix = '06E'




class Account(sf.Model):
    account_number = sf.CharField(max_length=40, blank=True, null=True)
    account_source = sf.CharField(max_length=40, choices=[('Web', 'Web'), ('Phone Inquiry', 'Phone Inquiry'), ('Partner Referral', 'Partner Referral'), ('Purchased List', 'Purchased List'), ('Other', 'Other')], blank=True, null=True)
    active = sf.CharField(custom=True, max_length=255, choices=[('No', 'No'), ('Yes', 'Yes')], blank=True, null=True)
    annual_revenue = sf.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    billing_address = sf.TextField(sf_read_only=sf.READ_ONLY, blank=True, null=True)  # This field type is a guess.
    billing_city = sf.CharField(max_length=40, blank=True, null=True)
    billing_country = sf.CharField(max_length=80, blank=True, null=True)
    billing_geocode_accuracy = sf.CharField(max_length=40, choices=[('Address', 'Address'), ('NearAddress', 'NearAddress'), ('Block', 'Block'), ('Street', 'Street'), ('ExtendedZip', 'ExtendedZip'), ('Zip', 'Zip'), ('Neighborhood', 'Neighborhood'), ('City', 'City'), ('County', 'County'), ('State', 'State'), ('Unknown', 'Unknown')], blank=True, null=True)
    billing_latitude = sf.DecimalField(max_digits=18, decimal_places=15, blank=True, null=True)
    billing_longitude = sf.DecimalField(max_digits=18, decimal_places=15, blank=True, null=True)
    billing_postal_code = sf.CharField(max_length=20, verbose_name='Billing Zip/Postal Code', blank=True, null=True)
    billing_state = sf.CharField(max_length=80, verbose_name='Billing State/Province', blank=True, null=True)
    billing_street = sf.TextField(blank=True, null=True)
    clean_status = sf.CharField(max_length=40, choices=[('Matched', 'In Sync'), ('Different', 'Different'), ('Acknowledged', 'Reviewed'), ('NotFound', 'Not Found'), ('Inactive', 'Inactive'), ('Pending', 'Not Compared'), ('SelectMatch', 'Select Match'), ('Skipped', 'Skipped')], blank=True, null=True)
    created_by = sf.ForeignKey('User', sf.DO_NOTHING, related_name='account_createdby_set', sf_read_only=sf.READ_ONLY)
    created_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    customer_priority = sf.CharField(custom=True, max_length=255, choices=[('High', 'High'), ('Low', 'Low'), ('Medium', 'Medium')], blank=True, null=True)
    dandb_company = sf.ForeignKey('DandBcompany', sf.DO_NOTHING, blank=True, null=True)
    description = sf.TextField(verbose_name='Account Description', blank=True, null=True)
    duns_number = sf.CharField(max_length=9, verbose_name='D-U-N-S Number', blank=True, null=True)
    fax = sf.CharField(max_length=40, verbose_name='Account Fax', blank=True, null=True)
    industry = sf.CharField(max_length=40, choices=[('Agriculture', 'Agriculture'), ('Apparel', 'Apparel'), ('Banking', 'Banking'), ('Biotechnology', 'Biotechnology'), ('Chemicals', 'Chemicals'), ('Communications', 'Communications'), ('Construction', 'Construction'), ('Consulting', 'Consulting'), ('Education', 'Education'), ('Electronics', 'Electronics'), ('Energy', 'Energy'), ('Engineering', 'Engineering'), ('Entertainment', 'Entertainment'), ('Environmental', 'Environmental'), ('Finance', 'Finance'), ('Food & Beverage', 'Food & Beverage'), ('Government', 'Government'), ('Healthcare', 'Healthcare'), ('Hospitality', 'Hospitality'), ('Insurance', 'Insurance'), ('Machinery', 'Machinery'), ('Manufacturing', 'Manufacturing'), ('Media', 'Media'), ('Not For Profit', 'Not For Profit'), ('Recreation', 'Recreation'), ('Retail', 'Retail'), ('Shipping', 'Shipping'), ('Technology', 'Technology'), ('Telecommunications', 'Telecommunications'), ('Transportation', 'Transportation'), ('Utilities', 'Utilities'), ('Other', 'Other')], blank=True, null=True)
    is_active = sf.BooleanField(custom=True, sf_read_only=sf.READ_ONLY)
    is_deleted = sf.BooleanField(verbose_name='Deleted', sf_read_only=sf.READ_ONLY, default=False)
    jigsaw = sf.CharField(max_length=20, verbose_name='Data.com Key', blank=True, null=True)
    jigsaw_company_id = sf.CharField(max_length=20, verbose_name='Jigsaw Company ID', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    last_activity_date = sf.DateField(verbose_name='Last Activity', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    last_modified_by = sf.ForeignKey('User', sf.DO_NOTHING, related_name='account_lastmodifiedby_set', sf_read_only=sf.READ_ONLY)
    last_modified_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    last_referenced_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY, blank=True, null=True)
    last_viewed_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY, blank=True, null=True)
    master_record = sf.ForeignKey('self', sf.DO_NOTHING, related_name='account_masterrecord_set', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    naics_code = sf.CharField(max_length=8, verbose_name='NAICS Code', blank=True, null=True)
    naics_desc = sf.CharField(max_length=120, verbose_name='NAICS Description', blank=True, null=True)
    name = sf.CharField(max_length=255, verbose_name='Account Name')
    number_of_employees = sf.IntegerField(verbose_name='Employees', blank=True, null=True)
    numberof_locations = sf.DecimalField(custom=True, max_digits=3, decimal_places=0, verbose_name='Number of Locations', blank=True, null=True)
    owner = sf.ForeignKey('User', sf.DO_NOTHING, related_name='account_owner_set')
    ownership = sf.CharField(max_length=40, choices=[('Public', 'Public'), ('Private', 'Private'), ('Subsidiary', 'Subsidiary'), ('Other', 'Other')], blank=True, null=True)
    parent = sf.ForeignKey('self', sf.DO_NOTHING, related_name='account_parent_set', blank=True, null=True)
    phone = sf.CharField(max_length=40, verbose_name='Account Phone', blank=True, null=True)
    photo_url = sf.URLField(verbose_name='Photo URL', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    rating = sf.CharField(max_length=40, verbose_name='Account Rating', choices=[('Hot', 'Hot'), ('Warm', 'Warm'), ('Cold', 'Cold')], blank=True, null=True)
    shipping_address = sf.TextField(sf_read_only=sf.READ_ONLY, blank=True, null=True)  # This field type is a guess.
    shipping_city = sf.CharField(max_length=40, blank=True, null=True)
    shipping_country = sf.CharField(max_length=80, blank=True, null=True)
    shipping_geocode_accuracy = sf.CharField(max_length=40, choices=[('Address', 'Address'), ('NearAddress', 'NearAddress'), ('Block', 'Block'), ('Street', 'Street'), ('ExtendedZip', 'ExtendedZip'), ('Zip', 'Zip'), ('Neighborhood', 'Neighborhood'), ('City', 'City'), ('County', 'County'), ('State', 'State'), ('Unknown', 'Unknown')], blank=True, null=True)
    shipping_latitude = sf.DecimalField(max_digits=18, decimal_places=15, blank=True, null=True)
    shipping_longitude = sf.DecimalField(max_digits=18, decimal_places=15, blank=True, null=True)
    shipping_postal_code = sf.CharField(max_length=20, verbose_name='Shipping Zip/Postal Code', blank=True, null=True)
    shipping_state = sf.CharField(max_length=80, verbose_name='Shipping State/Province', blank=True, null=True)
    shipping_street = sf.TextField(blank=True, null=True)
    sic = sf.CharField(max_length=20, verbose_name='SIC Code', blank=True, null=True)
    sic_desc = sf.CharField(max_length=80, verbose_name='SIC Description', blank=True, null=True)
    site = sf.CharField(max_length=80, verbose_name='Account Site', blank=True, null=True)
    sla = sf.CharField(custom=True, db_column='SLA__c', max_length=255, verbose_name='SLA', choices=[('Gold', 'Gold'), ('Silver', 'Silver'), ('Platinum', 'Platinum'), ('Bronze', 'Bronze')], blank=True, null=True)
    slaexpiration_date = sf.DateField(custom=True, db_column='SLAExpirationDate__c', verbose_name='SLA Expiration Date', blank=True, null=True)
    slaserial_number = sf.CharField(custom=True, db_column='SLASerialNumber__c', max_length=10, verbose_name='SLA Serial Number', blank=True, null=True)
    system_modstamp = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    ticker_symbol = sf.CharField(max_length=20, blank=True, null=True)
    tradestyle = sf.CharField(max_length=255, blank=True, null=True)
    type = sf.CharField(max_length=40, verbose_name='Account Type', choices=[('Prospect', 'Prospect'), ('Customer - Direct', 'Customer - Direct'), ('Customer - Channel', 'Customer - Channel'), ('Channel Partner / Reseller', 'Channel Partner / Reseller'), ('Installation Partner', 'Installation Partner'), ('Technology Partner', 'Technology Partner'), ('Other', 'Other')], blank=True, null=True)
    upsell_opportunity = sf.CharField(custom=True, max_length=255, choices=[('Maybe', 'Maybe'), ('No', 'No'), ('Yes', 'Yes')], blank=True, null=True)
    website = sf.URLField(blank=True, null=True)
    year_started = sf.CharField(max_length=4, blank=True, null=True)
    
    class Meta(sf.Model.Meta):
        db_table = 'Account'
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        # keyPrefix = '001'
        
    @property
    def score(self):
        if not self.is_active or self.is_deleted:
            return 0
        
        return score(self, [
            #(1, 'account_number', has),
            (1, 'account_source', choose(SOURCE_SCORES)),
            (5, 'annual_revenue', inv_exp(239000000)),
            (10, 'customer_priority', rank(('Low', 'Medium', 'High'))),
            #(1, 'description', has),
            #(1, 'duns_number', has),
            (3, 'industry', choose(INDUSTRY_SCORES)),
            (10, 'last_activity_date', combine(date_diff(), inv_exp_80(20))),
            (5, 'last_referenced_date', combine(date_diff(), inv_exp_80(30))),
            (5, 'last_viewed_date', combine(date_diff(), inv_exp_80(14))),
            #(1, 'naics_code', has),
            (4, 'number_of_employees', inv_exp_80(200)),
            (4, 'numberof_locations', inv_exp_80(10)),
            #(1, 'phone', has),
            (10, 'rating', rank(('Cold', 'Warm', 'Hot'))),
            #(1, 'sic', has),
            (5, 'sla', rank(('Bronze', 'Platinum', 'Silver', 'Gold'))),
            (10, 'slaexpiration_date', combine(date_diff(future=True), exponential_20(20))),
            (10, 'type', choose(ACCOUNT_TYPE_SCORES)),
            (10, 'upsell_opportunity', rank(('No', 'Maybe', 'Yes'))),
            #(1, 'website', has),
            #(1, 'year_started', has),
        ])



class Contact(sf.Model):
    account = sf.ForeignKey(Account, sf.DO_NOTHING, blank=True, null=True)  # Master Detail Relationship *
    assistant_name = sf.CharField(max_length=40, verbose_name="Assistant's Name", blank=True, null=True)
    assistant_phone = sf.CharField(max_length=40, verbose_name='Asst. Phone', blank=True, null=True)
    birthdate = sf.DateField(blank=True, null=True)
    clean_status = sf.CharField(max_length=40, choices=[('Matched', 'In Sync'), ('Different', 'Different'), ('Acknowledged', 'Reviewed'), ('NotFound', 'Not Found'), ('Inactive', 'Inactive'), ('Pending', 'Not Compared'), ('SelectMatch', 'Select Match'), ('Skipped', 'Skipped')], blank=True, null=True)
    created_by = sf.ForeignKey('User', sf.DO_NOTHING, related_name='contact_createdby_set', sf_read_only=sf.READ_ONLY)
    created_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    department = sf.CharField(max_length=80, blank=True, null=True)
    description = sf.TextField(verbose_name='Contact Description', blank=True, null=True)
    email = sf.EmailField(blank=True, null=True)
    email_bounced_date = sf.DateTimeField(blank=True, null=True)
    email_bounced_reason = sf.CharField(max_length=255, blank=True, null=True)
    fax = sf.CharField(max_length=40, verbose_name='Business Fax', blank=True, null=True)
    first_name = sf.CharField(max_length=40, blank=True, null=True)
    home_phone = sf.CharField(max_length=40, blank=True, null=True)
    is_deleted = sf.BooleanField(verbose_name='Deleted', sf_read_only=sf.READ_ONLY, default=False)
    is_email_bounced = sf.BooleanField(sf_read_only=sf.READ_ONLY, default=False)
    jigsaw = sf.CharField(max_length=20, verbose_name='Data.com Key', blank=True, null=True)
    jigsaw_contact_id = sf.CharField(max_length=20, verbose_name='Jigsaw Contact ID', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    languages = sf.CharField(custom=True, max_length=100, blank=True, null=True)
    last_activity_date = sf.DateField(verbose_name='Last Activity', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    last_curequest_date = sf.DateTimeField(db_column='LastCURequestDate', verbose_name='Last Stay-in-Touch Request Date', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    last_cuupdate_date = sf.DateTimeField(db_column='LastCUUpdateDate', verbose_name='Last Stay-in-Touch Save Date', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    last_modified_by = sf.ForeignKey('User', sf.DO_NOTHING, related_name='contact_lastmodifiedby_set', sf_read_only=sf.READ_ONLY)
    last_modified_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    last_name = sf.CharField(max_length=80)
    last_referenced_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY, blank=True, null=True)
    last_viewed_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY, blank=True, null=True)
    lead_source = sf.CharField(max_length=40, choices=[('Web', 'Web'), ('Phone Inquiry', 'Phone Inquiry'), ('Partner Referral', 'Partner Referral'), ('Purchased List', 'Purchased List'), ('Other', 'Other')], blank=True, null=True)
    level = sf.CharField(custom=True, max_length=255, choices=[('Secondary', 'Secondary'), ('Tertiary', 'Tertiary'), ('Primary', 'Primary')], blank=True, null=True)
    mailing_address = sf.TextField(sf_read_only=sf.READ_ONLY, blank=True, null=True)  # This field type is a guess.
    mailing_city = sf.CharField(max_length=40, blank=True, null=True)
    mailing_country = sf.CharField(max_length=80, blank=True, null=True)
    mailing_geocode_accuracy = sf.CharField(max_length=40, choices=[('Address', 'Address'), ('NearAddress', 'NearAddress'), ('Block', 'Block'), ('Street', 'Street'), ('ExtendedZip', 'ExtendedZip'), ('Zip', 'Zip'), ('Neighborhood', 'Neighborhood'), ('City', 'City'), ('County', 'County'), ('State', 'State'), ('Unknown', 'Unknown')], blank=True, null=True)
    mailing_latitude = sf.DecimalField(max_digits=18, decimal_places=15, blank=True, null=True)
    mailing_longitude = sf.DecimalField(max_digits=18, decimal_places=15, blank=True, null=True)
    mailing_postal_code = sf.CharField(max_length=20, verbose_name='Mailing Zip/Postal Code', blank=True, null=True)
    mailing_state = sf.CharField(max_length=80, verbose_name='Mailing State/Province', blank=True, null=True)
    mailing_street = sf.TextField(blank=True, null=True)
    master_record = sf.ForeignKey('self', sf.DO_NOTHING, related_name='contact_masterrecord_set', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    mobile_phone = sf.CharField(max_length=40, blank=True, null=True)
    name = sf.CharField(max_length=121, verbose_name='Full Name', sf_read_only=sf.READ_ONLY)
    other_address = sf.TextField(sf_read_only=sf.READ_ONLY, blank=True, null=True)  # This field type is a guess.
    other_city = sf.CharField(max_length=40, blank=True, null=True)
    other_country = sf.CharField(max_length=80, blank=True, null=True)
    other_geocode_accuracy = sf.CharField(max_length=40, choices=[('Address', 'Address'), ('NearAddress', 'NearAddress'), ('Block', 'Block'), ('Street', 'Street'), ('ExtendedZip', 'ExtendedZip'), ('Zip', 'Zip'), ('Neighborhood', 'Neighborhood'), ('City', 'City'), ('County', 'County'), ('State', 'State'), ('Unknown', 'Unknown')], blank=True, null=True)
    other_latitude = sf.DecimalField(max_digits=18, decimal_places=15, blank=True, null=True)
    other_longitude = sf.DecimalField(max_digits=18, decimal_places=15, blank=True, null=True)
    other_phone = sf.CharField(max_length=40, blank=True, null=True)
    other_postal_code = sf.CharField(max_length=20, verbose_name='Other Zip/Postal Code', blank=True, null=True)
    other_state = sf.CharField(max_length=80, verbose_name='Other State/Province', blank=True, null=True)
    other_street = sf.TextField(blank=True, null=True)
    owner = sf.ForeignKey('User', sf.DO_NOTHING, related_name='contact_owner_set')
    phone = sf.CharField(max_length=40, verbose_name='Business Phone', blank=True, null=True)
    photo_url = sf.URLField(verbose_name='Photo URL', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    reports_to = sf.ForeignKey('self', sf.DO_NOTHING, related_name='contact_reportsto_set', blank=True, null=True)
    salutation = sf.CharField(max_length=40, choices=[('Mr.', 'Mr.'), ('Ms.', 'Ms.'), ('Mrs.', 'Mrs.'), ('Dr.', 'Dr.'), ('Prof.', 'Prof.')], blank=True, null=True)
    system_modstamp = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    title = sf.CharField(max_length=128, blank=True, null=True)
    
    class Meta(sf.Model.Meta):
        db_table = 'Contact'
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        # keyPrefix = '003'
    
    @property
    def score(self):
        if self.is_deleted:
            return False
        
        return score(self, [
            #(3, 'assistant_name', has),
            #(3, 'assistant_phone', has),
            #(3, 'department', has),
            #(3, 'description', has),
            #(3, 'email', has),
            (20, 'email_bounced_date', combine(date_diff(), exponential_20(7))),
            #(3, 'first_name', has),
            (15, 'last_activity_date', combine(date_diff(), inv_exp_80(20))),
            #(3, 'last_name', has),
            (5, 'last_referenced_date', combine(date_diff(), inv_exp_80(30))),
            (5, 'last_viewed_date', combine(date_diff(), inv_exp_80(14))),
            (5, 'lead_source', choose(SOURCE_SCORES)),
            (10, 'level', rank(('Tertiary', 'Secondary', 'Primary'))),
            #(3, 'mobile_phone', has),
            #(3, 'phone', has),
            #(3, 'title', has),
        ])



class Lead(sf.Model):
    address = sf.TextField(sf_read_only=sf.READ_ONLY, blank=True, null=True)  # This field type is a guess.
    annual_revenue = sf.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    city = sf.CharField(max_length=40, blank=True, null=True)
    clean_status = sf.CharField(max_length=40, choices=[('Matched', 'In Sync'), ('Different', 'Different'), ('Acknowledged', 'Reviewed'), ('NotFound', 'Not Found'), ('Inactive', 'Inactive'), ('Pending', 'Not Compared'), ('SelectMatch', 'Select Match'), ('Skipped', 'Skipped')], blank=True, null=True)
    company = sf.CharField(max_length=255)
    company_duns_number = sf.CharField(max_length=9, verbose_name='Company D-U-N-S Number', blank=True, null=True)
    converted_account = sf.ForeignKey(Account, sf.DO_NOTHING, sf_read_only=sf.READ_ONLY, blank=True, null=True)
    converted_contact = sf.ForeignKey(Contact, sf.DO_NOTHING, sf_read_only=sf.READ_ONLY, blank=True, null=True)
    converted_date = sf.DateField(sf_read_only=sf.READ_ONLY, blank=True, null=True)
    converted_opportunity = sf.ForeignKey('Opportunity', sf.DO_NOTHING, sf_read_only=sf.READ_ONLY, blank=True, null=True)
    country = sf.CharField(max_length=80, blank=True, null=True)
    created_by = sf.ForeignKey('User', sf.DO_NOTHING, related_name='lead_createdby_set', sf_read_only=sf.READ_ONLY)
    created_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    current_generators = sf.CharField(custom=True, max_length=100, verbose_name='Current Generator(s)', blank=True, null=True)
    dandb_company = sf.ForeignKey('DandBcompany', sf.DO_NOTHING, blank=True, null=True)
    description = sf.TextField(blank=True, null=True)
    email = sf.EmailField(blank=True, null=True)
    email_bounced_date = sf.DateTimeField(sf_read_only=sf.NOT_CREATEABLE, blank=True, null=True)
    email_bounced_reason = sf.CharField(max_length=255, sf_read_only=sf.NOT_CREATEABLE, blank=True, null=True)
    fax = sf.CharField(max_length=40, blank=True, null=True)
    first_name = sf.CharField(max_length=40, blank=True, null=True)
    geocode_accuracy = sf.CharField(max_length=40, choices=[('Address', 'Address'), ('NearAddress', 'NearAddress'), ('Block', 'Block'), ('Street', 'Street'), ('ExtendedZip', 'ExtendedZip'), ('Zip', 'Zip'), ('Neighborhood', 'Neighborhood'), ('City', 'City'), ('County', 'County'), ('State', 'State'), ('Unknown', 'Unknown')], blank=True, null=True)
    industry = sf.CharField(max_length=40, choices=[('Agriculture', 'Agriculture'), ('Apparel', 'Apparel'), ('Banking', 'Banking'), ('Biotechnology', 'Biotechnology'), ('Chemicals', 'Chemicals'), ('Communications', 'Communications'), ('Construction', 'Construction'), ('Consulting', 'Consulting'), ('Education', 'Education'), ('Electronics', 'Electronics'), ('Energy', 'Energy'), ('Engineering', 'Engineering'), ('Entertainment', 'Entertainment'), ('Environmental', 'Environmental'), ('Finance', 'Finance'), ('Food & Beverage', 'Food & Beverage'), ('Government', 'Government'), ('Healthcare', 'Healthcare'), ('Hospitality', 'Hospitality'), ('Insurance', 'Insurance'), ('Machinery', 'Machinery'), ('Manufacturing', 'Manufacturing'), ('Media', 'Media'), ('Not For Profit', 'Not For Profit'), ('Recreation', 'Recreation'), ('Retail', 'Retail'), ('Shipping', 'Shipping'), ('Technology', 'Technology'), ('Telecommunications', 'Telecommunications'), ('Transportation', 'Transportation'), ('Utilities', 'Utilities'), ('Other', 'Other')], blank=True, null=True)
    is_converted = sf.BooleanField(verbose_name='Converted', sf_read_only=sf.NOT_UPDATEABLE, default=sf.DEFAULTED_ON_CREATE)
    is_deleted = sf.BooleanField(verbose_name='Deleted', sf_read_only=sf.READ_ONLY, default=False)
    is_unread_by_owner = sf.BooleanField(verbose_name='Unread By Owner', default=sf.DEFAULTED_ON_CREATE)
    jigsaw = sf.CharField(max_length=20, verbose_name='Data.com Key', blank=True, null=True)
    jigsaw_contact_id = sf.CharField(max_length=20, verbose_name='Jigsaw Contact ID', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    last_activity_date = sf.DateField(verbose_name='Last Activity', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    last_modified_by = sf.ForeignKey('User', sf.DO_NOTHING, related_name='lead_lastmodifiedby_set', sf_read_only=sf.READ_ONLY)
    last_modified_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    last_name = sf.CharField(max_length=80)
    last_referenced_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY, blank=True, null=True)
    last_viewed_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY, blank=True, null=True)
    latitude = sf.DecimalField(max_digits=18, decimal_places=15, blank=True, null=True)
    lead_source = sf.CharField(max_length=40, choices=[('Web', 'Web'), ('Phone Inquiry', 'Phone Inquiry'), ('Partner Referral', 'Partner Referral'), ('Purchased List', 'Purchased List'), ('Other', 'Other')], blank=True, null=True)
    longitude = sf.DecimalField(max_digits=18, decimal_places=15, blank=True, null=True)
    master_record = sf.ForeignKey('self', sf.DO_NOTHING, sf_read_only=sf.READ_ONLY, blank=True, null=True)
    mobile_phone = sf.CharField(max_length=40, blank=True, null=True)
    name = sf.CharField(max_length=121, verbose_name='Full Name', sf_read_only=sf.READ_ONLY)
    number_of_employees = sf.IntegerField(verbose_name='Employees', blank=True, null=True)
    numberof_locations = sf.DecimalField(custom=True, max_digits=3, decimal_places=0, verbose_name='Number of Locations', blank=True, null=True)
    owner = sf.ForeignKey('User', sf.DO_NOTHING)  # Reference to tables [Group, User]
    phone = sf.CharField(max_length=40, blank=True, null=True)
    photo_url = sf.URLField(verbose_name='Photo URL', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    postal_code = sf.CharField(max_length=20, verbose_name='Zip/Postal Code', blank=True, null=True)
    primary = sf.CharField(custom=True, max_length=255, choices=[('No', 'No'), ('Yes', 'Yes')], blank=True, null=True)
    product_interest = sf.CharField(custom=True, max_length=255, choices=[('GC1000 series', 'GC1000 series'), ('GC5000 series', 'GC5000 series'), ('GC3000 series', 'GC3000 series')], blank=True, null=True)
    rating = sf.CharField(max_length=40, choices=[('Hot', 'Hot'), ('Warm', 'Warm'), ('Cold', 'Cold')], blank=True, null=True)
    salutation = sf.CharField(max_length=40, choices=[('Mr.', 'Mr.'), ('Ms.', 'Ms.'), ('Mrs.', 'Mrs.'), ('Dr.', 'Dr.'), ('Prof.', 'Prof.')], blank=True, null=True)
    siccode = sf.CharField(custom=True, db_column='SICCode__c', max_length=15, verbose_name='SIC Code', blank=True, null=True)
    state = sf.CharField(max_length=80, verbose_name='State/Province', blank=True, null=True)
    status = sf.CharField(max_length=40, default=sf.DEFAULTED_ON_CREATE, choices=[('Open - Not Contacted', 'Open - Not Contacted'), ('Working - Contacted', 'Working - Contacted'), ('Closed - Converted', 'Closed - Converted'), ('Closed - Not Converted', 'Closed - Not Converted')])
    street = sf.TextField(blank=True, null=True)
    system_modstamp = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    title = sf.CharField(max_length=128, blank=True, null=True)
    website = sf.URLField(blank=True, null=True)
    
    class Meta(sf.Model.Meta):
        db_table = 'Lead'
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        # keyPrefix = '00Q'
    
    @property
    def score(self):
        if self.is_converted or self.is_deleted:
            return 0
        
        return score(self, [
            #(1, 'address', has),
            (5, 'annual_revenue', inv_exp(239000000)),
            #(1, 'company', has),
            #(1, 'company_duns_number', has),
            #(1, 'dandb_company', has),
            #(1, 'description', has),
            #(1, 'email', has),
            (20, 'email_bounced_date', combine(date_diff(), exponential_20(7))),
            #(1, 'first_name', has),
            (5, 'industry', choose(INDUSTRY_SCORES)),
            (15, 'last_activity_date', combine(date_diff(), inv_exp_80(20))),
            #(1, 'last_name', has),
            (5, 'last_referenced_date', combine(date_diff(), inv_exp_80(30))),
            (5, 'last_viewed_date', combine(date_diff(), inv_exp_80(14))),
            (5, 'lead_source', choose(SOURCE_SCORES)),
            #(1, 'mobile_phone', has),
            (3, 'number_of_employees', inv_exp_80(200)),
            (3, 'numberof_locations', inv_exp_80(10)),
            #(1, 'phone', has),
            (5, 'primary', rank(('No', 'Yes'))),
            (8, 'rating', rank(('Cold', 'Warm', 'Hot'))),
            #(1, 'siccode', has),
            (20, 'status', choose(LEAD_STATUS_SCORES)),
            #(1, 'title', has),
            #(1, 'website', has),
        ])



class Opportunity(sf.Model):
    account = sf.ForeignKey(Account, sf.DO_NOTHING, blank=True, null=True)  # Master Detail Relationship *
    amount = sf.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    #campaign = sf.ForeignKey('Campaign', sf.DO_NOTHING, blank=True, null=True)
    close_date = sf.DateField()
    created_by = sf.ForeignKey('User', sf.DO_NOTHING, related_name='opportunity_createdby_set', sf_read_only=sf.READ_ONLY)
    created_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    current_generators = sf.CharField(custom=True, max_length=100, verbose_name='Current Generator(s)', blank=True, null=True)
    delivery_installation_status = sf.CharField(custom=True, max_length=255, verbose_name='Delivery/Installation Status', choices=[('In progress', 'In progress'), ('Yet to begin', 'Yet to begin'), ('Completed', 'Completed')], blank=True, null=True)
    description = sf.TextField(blank=True, null=True)
    expected_revenue = sf.DecimalField(max_digits=18, decimal_places=2, verbose_name='Expected Amount', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    fiscal = sf.CharField(max_length=6, verbose_name='Fiscal Period', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    fiscal_quarter = sf.IntegerField(sf_read_only=sf.READ_ONLY, blank=True, null=True)
    fiscal_year = sf.IntegerField(sf_read_only=sf.READ_ONLY, blank=True, null=True)
    forecast_category = sf.CharField(max_length=40, sf_read_only=sf.READ_ONLY, choices=[('Omitted', 'Omitted'), ('Pipeline', 'Pipeline'), ('BestCase', 'Best Case'), ('Forecast', 'Commit'), ('Closed', 'Closed')])
    forecast_category_name = sf.CharField(max_length=40, verbose_name='Forecast Category', choices=[('Omitted', 'Omitted'), ('Pipeline', 'Pipeline'), ('Best Case', 'Best Case'), ('Commit', 'Commit'), ('Closed', 'Closed')], default=sf.DEFAULTED_ON_CREATE, blank=True, null=True)
    has_open_activity = sf.BooleanField(sf_read_only=sf.READ_ONLY, default=False)
    has_opportunity_line_item = sf.BooleanField(verbose_name='Has Line Item', sf_read_only=sf.READ_ONLY, default=False)
    has_overdue_task = sf.BooleanField(sf_read_only=sf.READ_ONLY, default=False)
    is_closed = sf.BooleanField(verbose_name='Closed', sf_read_only=sf.READ_ONLY, default=False)
    is_deleted = sf.BooleanField(verbose_name='Deleted', sf_read_only=sf.READ_ONLY, default=False)
    is_private = sf.BooleanField(verbose_name='Private', default=sf.DEFAULTED_ON_CREATE)
    is_won = sf.BooleanField(verbose_name='Won', sf_read_only=sf.READ_ONLY, default=False)
    last_activity_date = sf.DateField(verbose_name='Last Activity', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    last_modified_by = sf.ForeignKey('User', sf.DO_NOTHING, related_name='opportunity_lastmodifiedby_set', sf_read_only=sf.READ_ONLY)
    last_modified_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    last_referenced_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY, blank=True, null=True)
    last_viewed_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY, blank=True, null=True)
    lead_source = sf.CharField(max_length=40, choices=[('Web', 'Web'), ('Phone Inquiry', 'Phone Inquiry'), ('Partner Referral', 'Partner Referral'), ('Purchased List', 'Purchased List'), ('Other', 'Other')], blank=True, null=True)
    main_competitors = sf.CharField(custom=True, max_length=100, verbose_name='Main Competitor(s)', blank=True, null=True)
    name = sf.CharField(max_length=120)
    next_step = sf.CharField(max_length=255, blank=True, null=True)
    order_number = sf.CharField(custom=True, max_length=8, blank=True, null=True)
    owner = sf.ForeignKey('User', sf.DO_NOTHING, related_name='opportunity_owner_set')
    #pricebook2 = sf.ForeignKey('Pricebook2', sf.DO_NOTHING, blank=True, null=True)
    probability = sf.DecimalField(max_digits=3, decimal_places=0, verbose_name='Probability (%)', default=sf.DEFAULTED_ON_CREATE, blank=True, null=True)
    stage_name = sf.CharField(max_length=40, verbose_name='Stage', choices=[('Prospecting', 'Prospecting'), ('Qualification', 'Qualification'), ('Needs Analysis', 'Needs Analysis'), ('Value Proposition', 'Value Proposition'), ('Id. Decision Makers', 'Id. Decision Makers'), ('Perception Analysis', 'Perception Analysis'), ('Proposal/Price Quote', 'Proposal/Price Quote'), ('Negotiation/Review', 'Negotiation/Review'), ('Closed Won', 'Closed Won'), ('Closed Lost', 'Closed Lost')])
    system_modstamp = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    total_opportunity_quantity = sf.DecimalField(max_digits=18, decimal_places=2, verbose_name='Quantity', blank=True, null=True)
    tracking_number = sf.CharField(custom=True, max_length=12, blank=True, null=True)
    type = sf.CharField(max_length=40, verbose_name='Opportunity Type', choices=[('Existing Customer - Upgrade', 'Existing Customer - Upgrade'), ('Existing Customer - Replacement', 'Existing Customer - Replacement'), ('Existing Customer - Downgrade', 'Existing Customer - Downgrade'), ('New Customer', 'New Customer')], blank=True, null=True)
    
    class Meta(sf.Model.Meta):
        db_table = 'Opportunity'
        verbose_name = 'Opportunity'
        verbose_name_plural = 'Opportunities'
        # keyPrefix = '006'
    
    @property
    def score(self):
        if self.is_closed or self.is_deleted:
            return 0
        
        return score(self, [
            (5, 'amount', inv_exp_80(400_000)),
            (30, 'close_date', combine(date_diff(future=True), exponential_20(30))),
            #(1, 'description', has),
            (15, 'has_open_activity', expect()),
            (15, 'has_overdue_task', expect()),
            (20, 'last_activity_date', combine(date_diff(), inv_exp_80(20))),
            (5, 'last_referenced_date', combine(date_diff(), inv_exp_80(30))),
            (5, 'last_viewed_date', combine(date_diff(), inv_exp_80(14))),
            (5, 'lead_source', choose(SOURCE_SCORES)),
            #(1, 'main_competitors', has),
            #(1, 'name', has),
            #(1, 'order_number', has),
            (8, 'probability'),
            (10, 'stage_name', choose(OPP_STAGE_SCORES)),
            #(1, 'tracking_number', has),
            (5, 'type', rank(('Existing Customer - Downgrade', 'Existing Customer - Replacement', 'Existing Customer - Upgrade', 'New Customer')))
        ])
        


class Calendar(sf.Model):
    created_by = sf.ForeignKey('User', sf.DO_NOTHING, related_name='calendar_createdby_set', sf_read_only=sf.READ_ONLY)
    created_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    is_active = sf.BooleanField(verbose_name='Active', sf_read_only=sf.READ_ONLY, default=False)
    last_modified_by = sf.ForeignKey('User', sf.DO_NOTHING, related_name='calendar_lastmodifiedby_set', sf_read_only=sf.READ_ONLY)
    last_modified_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    name = sf.CharField(max_length=80, verbose_name='Calendar Name', sf_read_only=sf.READ_ONLY)
    system_modstamp = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    type = sf.CharField(max_length=40, verbose_name='Calendar Type', sf_read_only=sf.READ_ONLY, choices=[('User', 'User Calendar'), ('Public', 'Public Calendar'), ('Resource', 'Resource Calendar'), ('Holiday', 'Holiday Calendar')])
    user = sf.ForeignKey('User', sf.DO_NOTHING, related_name='calendar_user_set', sf_read_only=sf.READ_ONLY, blank=True, null=True)  # Master Detail Relationship *
    class Meta(sf.Model.Meta):
        db_table = 'Calendar'
        verbose_name = 'Calendar'
        verbose_name_plural = 'Calendars'
        # keyPrefix = '023'



class Event(sf.Model):
    account = sf.ForeignKey('Account', sf.DO_NOTHING, related_name='event_account_set', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    activity_date = sf.DateField(verbose_name='Due Date Only', blank=True, null=True)
    activity_date_time = sf.DateTimeField(verbose_name='Due Date Time', blank=True, null=True)
    created_by = sf.ForeignKey('User', sf.DO_NOTHING, related_name='event_createdby_set', sf_read_only=sf.READ_ONLY)
    created_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    description = sf.TextField(blank=True, null=True)
    duration_in_minutes = sf.IntegerField(verbose_name='Duration', blank=True, null=True)
    end_date_time = sf.DateTimeField(blank=True, null=True)
    event_subtype = sf.CharField(max_length=40, sf_read_only=sf.NOT_UPDATEABLE, choices=[('Event', 'Event')], blank=True, null=True)
    group_event_type = sf.CharField(max_length=40, sf_read_only=sf.READ_ONLY, default='0', choices=[('0', 'Non-group Event'), ('1', 'Group Event'), ('2', 'Proposed Event'), ('3', 'IsRecurrence2 Series Pattern')], blank=True, null=True)
    is_all_day_event = sf.BooleanField(verbose_name='All-Day Event', default=sf.DEFAULTED_ON_CREATE)
    is_archived = sf.BooleanField(verbose_name='Archived', sf_read_only=sf.READ_ONLY, default=False)
    is_child = sf.BooleanField(sf_read_only=sf.READ_ONLY, default=False)
    is_deleted = sf.BooleanField(verbose_name='Deleted', sf_read_only=sf.READ_ONLY, default=False)
    is_group_event = sf.BooleanField(sf_read_only=sf.READ_ONLY, default=False)
    is_private = sf.BooleanField(verbose_name='Private', default=sf.DEFAULTED_ON_CREATE)
    is_recurrence = sf.BooleanField(verbose_name='Create Recurring Series of Events', sf_read_only=sf.NOT_UPDATEABLE, default=sf.DEFAULTED_ON_CREATE)
    is_recurrence2 = sf.BooleanField(verbose_name='Repeat', sf_read_only=sf.READ_ONLY, default=False)
    is_recurrence2_exception = sf.BooleanField(verbose_name='Is Exception', sf_read_only=sf.READ_ONLY, default=False)
    is_recurrence2_exclusion = sf.BooleanField(verbose_name='Historical Event, Not Following Recurrence', sf_read_only=sf.READ_ONLY, default=False)
    is_reminder_set = sf.BooleanField(verbose_name='Reminder Set', default=sf.DEFAULTED_ON_CREATE)
    last_modified_by = sf.ForeignKey('User', sf.DO_NOTHING, related_name='event_lastmodifiedby_set', sf_read_only=sf.READ_ONLY)
    last_modified_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    location = sf.CharField(max_length=255, blank=True, null=True)
    owner = sf.ForeignKey(User, sf.DO_NOTHING)  # Reference to tables [User, Calendar]
    recurrence_activity = sf.ForeignKey('self', sf.DO_NOTHING, sf_read_only=sf.READ_ONLY, blank=True, null=True)
    recurrence_day_of_month = sf.IntegerField(verbose_name='Recurrence Day of Month', blank=True, null=True)
    recurrence_day_of_week_mask = sf.IntegerField(verbose_name='Recurrence Day of Week Mask', blank=True, null=True)
    recurrence_end_date_only = sf.DateField(verbose_name='Recurrence End', blank=True, null=True)
    recurrence_instance = sf.CharField(max_length=40, choices=[('First', '1st'), ('Second', '2nd'), ('Third', '3rd'), ('Fourth', '4th'), ('Last', 'last')], blank=True, null=True)
    recurrence_interval = sf.IntegerField(blank=True, null=True)
    recurrence_month_of_year = sf.CharField(max_length=40, verbose_name='Recurrence Month of Year', choices=[('January', 'January'), ('February', 'February'), ('March', 'March'), ('April', 'April'), ('May', 'May'), ('June', 'June'), ('July', 'July'), ('August', 'August'), ('September', 'September'), ('October', 'October'), ('November', 'November'), ('December', 'December')], blank=True, null=True)
    recurrence_start_date_time = sf.DateTimeField(verbose_name='Recurrence Start', blank=True, null=True)
    recurrence_time_zone_sid_key = sf.CharField(max_length=40, verbose_name='Recurrence Time Zone', choices=[('Pacific/Kiritimati', '(GMT+14:00) Line Is. Time (Pacific/Kiritimati)'), ('Pacific/Enderbury', '(GMT+13:00) Phoenix Is. Time (Pacific/Enderbury)'), ('Pacific/Tongatapu', '(GMT+13:00) Tonga Time (Pacific/Tongatapu)'), ('Pacific/Chatham', '(GMT+12:45) Chatham Standard Time (Pacific/Chatham)'), ('Asia/Kamchatka', '(GMT+12:00) Petropavlovsk-Kamchatski Time (Asia/Kamchatka)'), ('Pacific/Auckland', '(GMT+12:00) New Zealand Standard Time (Pacific/Auckland)'), ('Pacific/Fiji', '(GMT+12:00) Fiji Time (Pacific/Fiji)'), ('Pacific/Guadalcanal', '(GMT+11:00) Solomon Is. Time (Pacific/Guadalcanal)'), ('Pacific/Norfolk', '(GMT+11:00) Norfolk Time (Pacific/Norfolk)'), ('Australia/Lord_Howe', '(GMT+10:30) Lord Howe Standard Time (Australia/Lord_Howe)'), ('Australia/Brisbane', '(GMT+10:00) Australian Eastern Standard Time (Queensland) (Australia/Brisbane)'), ('Australia/Sydney', '(GMT+10:00) Australian Eastern Standard Time (New South Wales) (Australia/Sydney)'), ('Australia/Adelaide', '(GMT+09:30) Australian Central Standard Time (South Australia) (Australia/Adelaide)'), ('Australia/Darwin', '(GMT+09:30) Australian Central Standard Time (Northern Territory) (Australia/Darwin)'), ('Asia/Seoul', '(GMT+09:00) Korea Standard Time (Asia/Seoul)'), ('Asia/Tokyo', '(GMT+09:00) Japan Standard Time (Asia/Tokyo)'), ('Asia/Hong_Kong', '(GMT+08:00) Hong Kong Time (Asia/Hong_Kong)'), ('Asia/Kuala_Lumpur', '(GMT+08:00) Malaysia Time (Asia/Kuala_Lumpur)'), ('Asia/Manila', '(GMT+08:00) Philippines Time (Asia/Manila)'), ('Asia/Shanghai', '(GMT+08:00) China Standard Time (Asia/Shanghai)'), ('Asia/Singapore', '(GMT+08:00) Singapore Time (Asia/Singapore)'), ('Asia/Taipei', '(GMT+08:00) China Standard Time (Asia/Taipei)'), ('Australia/Perth', '(GMT+08:00) Australian Western Standard Time (Australia/Perth)'), ('Asia/Bangkok', '(GMT+07:00) Indochina Time (Asia/Bangkok)'), ('Asia/Ho_Chi_Minh', '(GMT+07:00) Indochina Time (Asia/Ho_Chi_Minh)'), ('Asia/Jakarta', '(GMT+07:00) West Indonesia Time (Asia/Jakarta)'), ('Asia/Rangoon', '(GMT+06:30) Myanmar Time (Asia/Rangoon)'), ('Asia/Dhaka', '(GMT+06:00) Bangladesh Time (Asia/Dhaka)'), ('Asia/Kathmandu', '(GMT+05:45) Nepal Time (Asia/Kathmandu)'), ('Asia/Colombo', '(GMT+05:30) India Standard Time (Asia/Colombo)'), ('Asia/Kolkata', '(GMT+05:30) India Standard Time (Asia/Kolkata)'), ('Asia/Karachi', '(GMT+05:00) Pakistan Time (Asia/Karachi)'), ('Asia/Tashkent', '(GMT+05:00) Uzbekistan Time (Asia/Tashkent)'), ('Asia/Yekaterinburg', '(GMT+05:00) Yekaterinburg Time (Asia/Yekaterinburg)'), ('Asia/Kabul', '(GMT+04:30) Afghanistan Time (Asia/Kabul)'), ('Asia/Tehran', '(GMT+04:30) Iran Daylight Time (Asia/Tehran)'), ('Asia/Baku', '(GMT+04:00) Azerbaijan Time (Asia/Baku)'), ('Asia/Dubai', '(GMT+04:00) Gulf Standard Time (Asia/Dubai)'), ('Asia/Tbilisi', '(GMT+04:00) Georgia Time (Asia/Tbilisi)'), ('Asia/Yerevan', '(GMT+04:00) Armenia Time (Asia/Yerevan)'), ('Africa/Nairobi', '(GMT+03:00) Eastern African Time (Africa/Nairobi)'), ('Asia/Baghdad', '(GMT+03:00) Arabia Standard Time (Asia/Baghdad)'), ('Asia/Beirut', '(GMT+03:00) Eastern European Summer Time (Asia/Beirut)'), ('Asia/Jerusalem', '(GMT+03:00) Israel Daylight Time (Asia/Jerusalem)'), ('Asia/Kuwait', '(GMT+03:00) Arabia Standard Time (Asia/Kuwait)'), ('Asia/Riyadh', '(GMT+03:00) Arabia Standard Time (Asia/Riyadh)'), ('Europe/Athens', '(GMT+03:00) Eastern European Summer Time (Europe/Athens)'), ('Europe/Bucharest', '(GMT+03:00) Eastern European Summer Time (Europe/Bucharest)'), ('Europe/Helsinki', '(GMT+03:00) Eastern European Summer Time (Europe/Helsinki)'), ('Europe/Istanbul', '(GMT+03:00) Eastern European Time (Europe/Istanbul)'), ('Europe/Minsk', '(GMT+03:00) Moscow Standard Time (Europe/Minsk)'), ('Europe/Moscow', '(GMT+03:00) Moscow Standard Time (Europe/Moscow)'), ('Africa/Cairo', '(GMT+02:00) Eastern European Time (Africa/Cairo)'), ('Africa/Johannesburg', '(GMT+02:00) South Africa Standard Time (Africa/Johannesburg)'), ('Europe/Amsterdam', '(GMT+02:00) Central European Summer Time (Europe/Amsterdam)'), ('Europe/Berlin', '(GMT+02:00) Central European Summer Time (Europe/Berlin)'), ('Europe/Brussels', '(GMT+02:00) Central European Summer Time (Europe/Brussels)'), ('Europe/Paris', '(GMT+02:00) Central European Summer Time (Europe/Paris)'), ('Europe/Prague', '(GMT+02:00) Central European Summer Time (Europe/Prague)'), ('Europe/Rome', '(GMT+02:00) Central European Summer Time (Europe/Rome)'), ('Africa/Algiers', '(GMT+01:00) Central European Time (Africa/Algiers)'), ('Africa/Casablanca', '(GMT+01:00) Western European Time (Africa/Casablanca)'), ('Europe/Dublin', '(GMT+01:00) Greenwich Mean Time (Europe/Dublin)'), ('Europe/Lisbon', '(GMT+01:00) Western European Summer Time (Europe/Lisbon)'), ('Europe/London', '(GMT+01:00) British Summer Time (Europe/London)'), ('America/Scoresbysund', '(GMT+00:00) Eastern Greenland Summer Time (America/Scoresbysund)'), ('Atlantic/Azores', '(GMT+00:00) Azores Summer Time (Atlantic/Azores)'), ('GMT', '(GMT+00:00) Greenwich Mean Time (GMT)'), ('Atlantic/Cape_Verde', '(GMT-01:00) Cape Verde Time (Atlantic/Cape_Verde)'), ('Atlantic/South_Georgia', '(GMT-02:00) South Georgia Standard Time (Atlantic/South_Georgia)'), ('America/St_Johns', '(GMT-02:30) Newfoundland Daylight Time (America/St_Johns)'), ('America/Argentina/Buenos_Aires', '(GMT-03:00) Argentine Time (America/Argentina/Buenos_Aires)'), ('America/Halifax', '(GMT-03:00) Atlantic Daylight Time (America/Halifax)'), ('America/Sao_Paulo', '(GMT-03:00) Brasilia Time (America/Sao_Paulo)'), ('Atlantic/Bermuda', '(GMT-03:00) Atlantic Daylight Time (Atlantic/Bermuda)'), ('America/Caracas', '(GMT-04:00) Venezuela Time (America/Caracas)'), ('America/Indiana/Indianapolis', '(GMT-04:00) Eastern Daylight Time (America/Indiana/Indianapolis)'), ('America/New_York', '(GMT-04:00) Eastern Daylight Time (America/New_York)'), ('America/Puerto_Rico', '(GMT-04:00) Atlantic Standard Time (America/Puerto_Rico)'), ('America/Santiago', '(GMT-04:00) Chile Time (America/Santiago)'), ('America/Bogota', '(GMT-05:00) Colombia Time (America/Bogota)'), ('America/Chicago', '(GMT-05:00) Central Daylight Time (America/Chicago)'), ('America/Lima', '(GMT-05:00) Peru Time (America/Lima)'), ('America/Mexico_City', '(GMT-05:00) Central Daylight Time (America/Mexico_City)'), ('America/Panama', '(GMT-05:00) Eastern Standard Time (America/Panama)'), ('America/Denver', '(GMT-06:00) Mountain Daylight Time (America/Denver)'), ('America/El_Salvador', '(GMT-06:00) Central Standard Time (America/El_Salvador)'), ('America/Mazatlan', '(GMT-06:00) Mountain Daylight Time (America/Mazatlan)'), ('America/Los_Angeles', '(GMT-07:00) Pacific Daylight Time (America/Los_Angeles)'), ('America/Phoenix', '(GMT-07:00) Mountain Standard Time (America/Phoenix)'), ('America/Tijuana', '(GMT-07:00) Pacific Daylight Time (America/Tijuana)'), ('America/Anchorage', '(GMT-08:00) Alaska Daylight Time (America/Anchorage)'), ('Pacific/Pitcairn', '(GMT-08:00) Pitcairn Standard Time (Pacific/Pitcairn)'), ('America/Adak', '(GMT-09:00) Hawaii-Aleutian Daylight Time (America/Adak)'), ('Pacific/Gambier', '(GMT-09:00) Gambier Time (Pacific/Gambier)'), ('Pacific/Marquesas', '(GMT-09:30) Marquesas Time (Pacific/Marquesas)'), ('Pacific/Honolulu', '(GMT-10:00) Hawaii-Aleutian Standard Time (Pacific/Honolulu)'), ('Pacific/Niue', '(GMT-11:00) Niue Time (Pacific/Niue)'), ('Pacific/Pago_Pago', '(GMT-11:00) Samoa Standard Time (Pacific/Pago_Pago)')], blank=True, null=True)
    recurrence_type = sf.CharField(max_length=40, choices=[('RecursDaily', 'Recurs Daily'), ('RecursEveryWeekday', 'Recurs Every Weekday'), ('RecursMonthly', 'Recurs Monthly'), ('RecursMonthlyNth', 'Recurs Monthy Nth'), ('RecursWeekly', 'Recurs Weekly'), ('RecursYearly', 'Recurs Yearly'), ('RecursYearlyNth', 'Recurs Yearly Nth')], blank=True, null=True)
    recurrence2_pattern_start_date = sf.DateTimeField(verbose_name='Recurrence Pattern Start Date', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    recurrence2_pattern_text = sf.TextField(verbose_name='Recurrence Pattern', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    recurrence2_pattern_time_zone = sf.CharField(max_length=255, verbose_name='Recurrence Pattern Time Zone Reference', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    recurrence2_pattern_version = sf.CharField(max_length=40, verbose_name='Pattern Version', sf_read_only=sf.READ_ONLY, choices=[('1', 'RFC 5545 v4 RRULE')], blank=True, null=True)
    reminder_date_time = sf.DateTimeField(verbose_name='Reminder Date/Time', blank=True, null=True)
    show_as = sf.CharField(max_length=40, verbose_name='Show Time As', default=sf.DEFAULTED_ON_CREATE, choices=[('Busy', 'Busy'), ('OutOfOffice', 'Out of Office'), ('Free', 'Free')], blank=True, null=True)
    start_date_time = sf.DateTimeField(blank=True, null=True)
    subject = sf.CharField(max_length=255, blank=True, null=True)
    system_modstamp = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    what = sf.ForeignKey('Account', sf.DO_NOTHING, related_name='event_what_set', blank=True, null=True)  # Reference to tables [Account, Asset, AssetRelationship, Campaign, Case, Contract, ListEmail, Opportunity, Order, Product2, Solution] Master Detail Relationship *
    who = sf.ForeignKey('Contact', sf.DO_NOTHING, blank=True, null=True)  # Reference to tables [Contact, Lead] Master Detail Relationship *
    class Meta(sf.Model.Meta):
        db_table = 'Event'
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        # keyPrefix = '00U'



class Organization(sf.Model):
    address = sf.TextField(sf_read_only=sf.READ_ONLY, blank=True, null=True)  # This field type is a guess.
    city = sf.CharField(max_length=40, sf_read_only=sf.NOT_CREATEABLE, blank=True, null=True)
    compliance_bcc_email = sf.EmailField(verbose_name='Compliance BCC Email', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    country = sf.CharField(max_length=80, sf_read_only=sf.READ_ONLY, blank=True, null=True)
    created_by = sf.ForeignKey('User', sf.DO_NOTHING, related_name='organization_createdby_set', sf_read_only=sf.READ_ONLY)
    created_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    default_account_access = sf.CharField(max_length=40, sf_read_only=sf.READ_ONLY, choices=[('None', 'Private'), ('Read', 'Read Only'), ('Edit', 'Read/Write'), ('ControlledByLeadOrContact', 'ControlledByLeadOrContact'), ('ControlledByCampaign', 'ControlledByCampaign')], blank=True, null=True)
    default_calendar_access = sf.CharField(max_length=40, sf_read_only=sf.READ_ONLY, default='HideDetailsInsert', choices=[('HideDetails', 'Hide Details'), ('HideDetailsInsert', 'Hide Details and Add Events'), ('ShowDetails', 'Show Details'), ('ShowDetailsInsert', 'Show Details and Add Events'), ('AllowEdits', 'Full Access')], blank=True, null=True)
    default_campaign_access = sf.CharField(max_length=40, sf_read_only=sf.READ_ONLY, choices=[('None', 'Private'), ('Read', 'Read Only'), ('Edit', 'Read/Write'), ('All', 'Owner')], blank=True, null=True)
    default_case_access = sf.CharField(max_length=40, sf_read_only=sf.READ_ONLY, choices=[('None', 'Private'), ('Read', 'Read Only'), ('Edit', 'Read/Write'), ('ReadEditTransfer', 'Read/Write/Transfer')], blank=True, null=True)
    default_contact_access = sf.CharField(max_length=40, sf_read_only=sf.READ_ONLY, choices=[('None', 'Private'), ('Read', 'Read Only'), ('Edit', 'Read/Write'), ('ControlledByParent', 'Controlled By Parent')], blank=True, null=True)
    default_lead_access = sf.CharField(max_length=40, sf_read_only=sf.READ_ONLY, choices=[('None', 'Private'), ('Read', 'Read Only'), ('Edit', 'Read/Write'), ('ReadEditTransfer', 'Read/Write/Transfer')], blank=True, null=True)
    default_locale_sid_key = sf.CharField(max_length=40, verbose_name='Locale', sf_read_only=sf.NOT_CREATEABLE, choices=[('af_ZA', 'Afrikaans (South Africa)'), ('sq_AL', 'Albanian (Albania)'), ('ar_DZ', 'Arabic (Algeria)'), ('ar_BH', 'Arabic (Bahrain)'), ('ar_EG', 'Arabic (Egypt)'), ('ar_IQ', 'Arabic (Iraq)'), ('ar_JO', 'Arabic (Jordan)'), ('ar_KW', 'Arabic (Kuwait)'), ('ar_LB', 'Arabic (Lebanon)'), ('ar_LY', 'Arabic (Libya)'), ('ar_MA', 'Arabic (Morocco)'), ('ar_OM', 'Arabic (Oman)'), ('ar_QA', 'Arabic (Qatar)'), ('ar_SA', 'Arabic (Saudi Arabia)'), ('ar_SD', 'Arabic (Sudan)'), ('ar_SY', 'Arabic (Syria)'), ('ar_TN', 'Arabic (Tunisia)'), ('ar_AE', 'Arabic (United Arab Emirates)'), ('ar_YE', 'Arabic (Yemen)'), ('hy_AM', 'Armenian (Armenia)'), ('az_AZ', 'Azerbaijani (Azerbaijan)'), ('bn_BD', 'Bangla (Bangladesh)'), ('bn_IN', 'Bangla (India)'), ('eu_ES', 'Basque (Spain)'), ('be_BY', 'Belarusian (Belarus)'), ('bs_BA', 'Bosnian (Bosnia & Herzegovina)'), ('bg_BG', 'Bulgarian (Bulgaria)'), ('my_MM', 'Burmese (Myanmar (Burma))'), ('ca_ES', 'Catalan (Spain)'), ('zh_CN_PINYIN', 'Chinese (China, Pinyin Ordering)'), ('zh_CN_STROKE', 'Chinese (China, Stroke Ordering)'), ('zh_CN', 'Chinese (China)'), ('zh_HK_STROKE', 'Chinese (Hong Kong SAR China, Stroke Ordering)'), ('zh_HK', 'Chinese (Hong Kong SAR China)'), ('zh_MO', 'Chinese (Macau SAR China)'), ('zh_SG', 'Chinese (Singapore)'), ('zh_TW_STROKE', 'Chinese (Taiwan, Stroke Ordering)'), ('zh_TW', 'Chinese (Taiwan)'), ('hr_HR', 'Croatian (Croatia)'), ('cs_CZ', 'Czech (Czechia)'), ('da_DK', 'Danish (Denmark)'), ('nl_AW', 'Dutch (Aruba)'), ('nl_BE', 'Dutch (Belgium)'), ('nl_NL', 'Dutch (Netherlands)'), ('nl_SR', 'Dutch (Suriname)'), ('dz_BT', 'Dzongkha (Bhutan)'), ('en_AG', 'English (Antigua & Barbuda)'), ('en_AU', 'English (Australia)'), ('en_BS', 'English (Bahamas)'), ('en_BB', 'English (Barbados)'), ('en_BZ', 'English (Belize)'), ('en_BM', 'English (Bermuda)'), ('en_BW', 'English (Botswana)'), ('en_CM', 'English (Cameroon)'), ('en_CA', 'English (Canada)'), ('en_KY', 'English (Cayman Islands)'), ('en_ER', 'English (Eritrea)'), ('en_FK', 'English (Falkland Islands)'), ('en_FJ', 'English (Fiji)'), ('en_GM', 'English (Gambia)'), ('en_GH', 'English (Ghana)'), ('en_GI', 'English (Gibraltar)'), ('en_GY', 'English (Guyana)'), ('en_HK', 'English (Hong Kong SAR China)'), ('en_IN', 'English (India)'), ('en_ID', 'English (Indonesia)'), ('en_IE', 'English (Ireland)'), ('en_JM', 'English (Jamaica)'), ('en_KE', 'English (Kenya)'), ('en_LR', 'English (Liberia)'), ('en_MG', 'English (Madagascar)'), ('en_MW', 'English (Malawi)'), ('en_MY', 'English (Malaysia)'), ('en_MU', 'English (Mauritius)'), ('en_NA', 'English (Namibia)'), ('en_NZ', 'English (New Zealand)'), ('en_NG', 'English (Nigeria)'), ('en_PK', 'English (Pakistan)'), ('en_PG', 'English (Papua New Guinea)'), ('en_PH', 'English (Philippines)'), ('en_RW', 'English (Rwanda)'), ('en_WS', 'English (Samoa)'), ('en_SC', 'English (Seychelles)'), ('en_SL', 'English (Sierra Leone)'), ('en_SG', 'English (Singapore)'), ('en_SX', 'English (Sint Maarten)'), ('en_SB', 'English (Solomon Islands)'), ('en_ZA', 'English (South Africa)'), ('en_SH', 'English (St. Helena)'), ('en_SZ', 'English (Swaziland)'), ('en_TZ', 'English (Tanzania)'), ('en_TO', 'English (Tonga)'), ('en_TT', 'English (Trinidad & Tobago)'), ('en_UG', 'English (Uganda)'), ('en_GB', 'English (United Kingdom)'), ('en_US', 'English (United States)'), ('en_VU', 'English (Vanuatu)'), ('et_EE', 'Estonian (Estonia)'), ('fi_FI', 'Finnish (Finland)'), ('fr_BE', 'French (Belgium)'), ('fr_CA', 'French (Canada)'), ('fr_KM', 'French (Comoros)'), ('fr_FR', 'French (France)'), ('fr_GN', 'French (Guinea)'), ('fr_HT', 'French (Haiti)'), ('fr_LU', 'French (Luxembourg)'), ('fr_MR', 'French (Mauritania)'), ('fr_MC', 'French (Monaco)'), ('fr_CH', 'French (Switzerland)'), ('fr_WF', 'French (Wallis & Futuna)'), ('ka_GE', 'Georgian (Georgia)'), ('de_AT', 'German (Austria)'), ('de_BE', 'German (Belgium)'), ('de_DE', 'German (Germany)'), ('de_LU', 'German (Luxembourg)'), ('de_CH', 'German (Switzerland)'), ('el_GR', 'Greek (Greece)'), ('gu_IN', 'Gujarati (India)'), ('iw_IL', 'Hebrew (Israel)'), ('hi_IN', 'Hindi (India)'), ('hu_HU', 'Hungarian (Hungary)'), ('is_IS', 'Icelandic (Iceland)'), ('in_ID', 'Indonesian (Indonesia)'), ('ga_IE', 'Irish (Ireland)'), ('it_IT', 'Italian (Italy)'), ('it_CH', 'Italian (Switzerland)'), ('ja_JP', 'Japanese (Japan)'), ('kn_IN', 'Kannada (India)'), ('kk_KZ', 'Kazakh (Kazakhstan)'), ('km_KH', 'Khmer (Cambodia)'), ('ko_KP', 'Korean (North Korea)'), ('ko_KR', 'Korean (South Korea)'), ('ky_KG', 'Kyrgyz (Kyrgyzstan)'), ('lo_LA', 'Lao (Laos)'), ('lv_LV', 'Latvian (Latvia)'), ('lt_LT', 'Lithuanian (Lithuania)'), ('lu_CD', 'Luba-Katanga (Congo - Kinshasa)'), ('lb_LU', 'Luxembourgish (Luxembourg)'), ('mk_MK', 'Macedonian (Macedonia)'), ('ms_BN', 'Malay (Brunei)'), ('ms_MY', 'Malay (Malaysia)'), ('ml_IN', 'Malayalam (India)'), ('mt_MT', 'Maltese (Malta)'), ('mr_IN', 'Marathi (India)'), ('sh_ME', 'Montenegrin (Montenegro)'), ('ne_NP', 'Nepali (Nepal)'), ('no_NO', 'Norwegian (Norway)'), ('ps_AF', 'Pashto (Afghanistan)'), ('fa_IR', 'Persian (Iran)'), ('pl_PL', 'Polish (Poland)'), ('pt_AO', 'Portuguese (Angola)'), ('pt_BR', 'Portuguese (Brazil)'), ('pt_CV', 'Portuguese (Cape Verde)'), ('pt_MZ', 'Portuguese (Mozambique)'), ('pt_PT', 'Portuguese (Portugal)'), ('pt_ST', 'Portuguese (São Tomé & Príncipe)'), ('ro_MD', 'Romanian (Moldova)'), ('ro_RO', 'Romanian (Romania)'), ('rm_CH', 'Romansh (Switzerland)'), ('rn_BI', 'Rundi (Burundi)'), ('ru_KZ', 'Russian (Kazakhstan)'), ('ru_RU', 'Russian (Russia)'), ('sr_BA', 'Serbian (Cyrillic) (Bosnia and Herzegovina)'), ('sr_CS', 'Serbian (Cyrillic) (Serbia)'), ('sh_BA', 'Serbian (Latin) (Bosnia and Herzegovina)'), ('sh_CS', 'Serbian (Latin) (Serbia)'), ('sr_RS', 'Serbian (Serbia)'), ('sk_SK', 'Slovak (Slovakia)'), ('sl_SI', 'Slovenian (Slovenia)'), ('so_DJ', 'Somali (Djibouti)'), ('so_SO', 'Somali (Somalia)'), ('es_AR', 'Spanish (Argentina)'), ('es_BO', 'Spanish (Bolivia)'), ('es_CL', 'Spanish (Chile)'), ('es_CO', 'Spanish (Colombia)'), ('es_CR', 'Spanish (Costa Rica)'), ('es_CU', 'Spanish (Cuba)'), ('es_DO', 'Spanish (Dominican Republic)'), ('es_EC', 'Spanish (Ecuador)'), ('es_SV', 'Spanish (El Salvador)'), ('es_GT', 'Spanish (Guatemala)'), ('es_HN', 'Spanish (Honduras)'), ('es_MX', 'Spanish (Mexico)'), ('es_NI', 'Spanish (Nicaragua)'), ('es_PA', 'Spanish (Panama)'), ('es_PY', 'Spanish (Paraguay)'), ('es_PE', 'Spanish (Peru)'), ('es_PR', 'Spanish (Puerto Rico)'), ('es_ES', 'Spanish (Spain)'), ('es_US', 'Spanish (United States)'), ('es_UY', 'Spanish (Uruguay)'), ('es_VE', 'Spanish (Venezuela)'), ('sw_KE', 'Swahili (Kenya)'), ('sv_SE', 'Swedish (Sweden)'), ('tl_PH', 'Tagalog (Philippines)'), ('tg_TJ', 'Tajik (Tajikistan)'), ('ta_IN', 'Tamil (India)'), ('ta_LK', 'Tamil (Sri Lanka)'), ('te_IN', 'Telugu (India)'), ('th_TH', 'Thai (Thailand)'), ('ti_ET', 'Tigrinya (Ethiopia)'), ('tr_TR', 'Turkish (Turkey)'), ('uk_UA', 'Ukrainian (Ukraine)'), ('ur_PK', 'Urdu (Pakistan)'), ('uz_LATN_UZ', 'Uzbek (LATN,UZ)'), ('vi_VN', 'Vietnamese (Vietnam)'), ('cy_GB', 'Welsh (United Kingdom)'), ('xh_ZA', 'Xhosa (South Africa)'), ('yo_BJ', 'Yoruba (Benin)'), ('zu_ZA', 'Zulu (South Africa)')])
    default_opportunity_access = sf.CharField(max_length=40, sf_read_only=sf.READ_ONLY, choices=[('None', 'Private'), ('Read', 'Read Only'), ('Edit', 'Read/Write'), ('ControlledByLeadOrContact', 'ControlledByLeadOrContact'), ('ControlledByCampaign', 'ControlledByCampaign')], blank=True, null=True)
    default_pricebook_access = sf.CharField(max_length=40, verbose_name='Default Price Book Access', sf_read_only=sf.READ_ONLY, choices=[('None', 'No Access'), ('Read', 'View Only'), ('ReadSelect', 'Use')], blank=True, null=True)
    division = sf.CharField(max_length=80, sf_read_only=sf.NOT_CREATEABLE, blank=True, null=True)
    fax = sf.CharField(max_length=40, sf_read_only=sf.NOT_CREATEABLE, blank=True, null=True)
    fiscal_year_start_month = sf.IntegerField(verbose_name='Fiscal Year Starts In', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    geocode_accuracy = sf.CharField(max_length=40, sf_read_only=sf.NOT_CREATEABLE, choices=[('Address', 'Address'), ('NearAddress', 'NearAddress'), ('Block', 'Block'), ('Street', 'Street'), ('ExtendedZip', 'ExtendedZip'), ('Zip', 'Zip'), ('Neighborhood', 'Neighborhood'), ('City', 'City'), ('County', 'County'), ('State', 'State'), ('Unknown', 'Unknown')], blank=True, null=True)
    instance_name = sf.CharField(max_length=5, sf_read_only=sf.READ_ONLY, blank=True, null=True)
    is_read_only = sf.BooleanField(sf_read_only=sf.READ_ONLY, default=False)
    is_sandbox = sf.BooleanField(sf_read_only=sf.READ_ONLY, default=False)
    language_locale_key = sf.CharField(max_length=40, verbose_name='Language', sf_read_only=sf.NOT_CREATEABLE, choices=[('en_US', 'English'), ('de', 'German'), ('es', 'Spanish'), ('fr', 'French'), ('it', 'Italian'), ('ja', 'Japanese'), ('sv', 'Swedish'), ('ko', 'Korean'), ('zh_TW', 'Chinese (Traditional)'), ('zh_CN', 'Chinese (Simplified)'), ('pt_BR', 'Portuguese (Brazil)'), ('nl_NL', 'Dutch'), ('da', 'Danish'), ('th', 'Thai'), ('fi', 'Finnish'), ('ru', 'Russian'), ('es_MX', 'Spanish (Mexico)'), ('no', 'Norwegian')])
    last_modified_by = sf.ForeignKey('User', sf.DO_NOTHING, related_name='organization_lastmodifiedby_set', sf_read_only=sf.READ_ONLY)
    last_modified_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    latitude = sf.DecimalField(max_digits=18, decimal_places=15, sf_read_only=sf.NOT_CREATEABLE, blank=True, null=True)
    longitude = sf.DecimalField(max_digits=18, decimal_places=15, sf_read_only=sf.NOT_CREATEABLE, blank=True, null=True)
    monthly_page_views_entitlement = sf.IntegerField(verbose_name='Monthly Page Views Allowed', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    monthly_page_views_used = sf.IntegerField(sf_read_only=sf.READ_ONLY, blank=True, null=True)
    name = sf.CharField(max_length=80, sf_read_only=sf.NOT_CREATEABLE)
    namespace_prefix = sf.CharField(max_length=15, sf_read_only=sf.READ_ONLY, blank=True, null=True)
    num_knowledge_service = sf.IntegerField(verbose_name='Knowledge Licenses', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    organization_type = sf.CharField(max_length=40, verbose_name='Edition', sf_read_only=sf.READ_ONLY, choices=[('Team Edition', None), ('Professional Edition', None), ('Enterprise Edition', None), ('Developer Edition', None), ('Personal Edition', None), ('Unlimited Edition', None), ('Contact Manager Edition', None), ('Base Edition', None)], blank=True, null=True)
    phone = sf.CharField(max_length=40, sf_read_only=sf.NOT_CREATEABLE, blank=True, null=True)
    postal_code = sf.CharField(max_length=20, verbose_name='Zip/Postal Code', sf_read_only=sf.NOT_CREATEABLE, blank=True, null=True)
    preferences_activity_analytics_enabled = sf.BooleanField(verbose_name='ActivityAnalyticsEnabled', sf_read_only=sf.NOT_CREATEABLE)
    preferences_auto_select_individual_on_merge = sf.BooleanField(verbose_name='AutoSelectIndividualOnMerge', sf_read_only=sf.NOT_CREATEABLE)
    preferences_consent_management_enabled = sf.BooleanField(verbose_name='ConsentManagementEnabled', sf_read_only=sf.NOT_CREATEABLE)
    preferences_individual_auto_create_enabled = sf.BooleanField(verbose_name='IndividualAutoCreateEnabled', sf_read_only=sf.NOT_CREATEABLE)
    preferences_lightning_login_enabled = sf.BooleanField(verbose_name='LightningLoginEnabled', sf_read_only=sf.NOT_CREATEABLE)
    preferences_only_llperm_user_allowed = sf.BooleanField(db_column='PreferencesOnlyLLPermUserAllowed', verbose_name='OnlyLLPermUserAllowed', sf_read_only=sf.NOT_CREATEABLE)
    preferences_require_opportunity_products = sf.BooleanField(verbose_name='RequireOpportunityProducts', sf_read_only=sf.NOT_CREATEABLE)
    preferences_terminate_oldest_session = sf.BooleanField(verbose_name='TerminateOldestSession', sf_read_only=sf.NOT_CREATEABLE)
    preferences_transaction_security_policy = sf.BooleanField(verbose_name='TransactionSecurityPolicy', sf_read_only=sf.NOT_CREATEABLE)
    primary_contact = sf.CharField(max_length=80, sf_read_only=sf.NOT_CREATEABLE, blank=True, null=True)
    receives_admin_info_emails = sf.BooleanField(verbose_name='Info Emails Admin', sf_read_only=sf.NOT_CREATEABLE, default=False)
    receives_info_emails = sf.BooleanField(verbose_name='Info Emails', sf_read_only=sf.NOT_CREATEABLE, default=False)
    signup_country_iso_code = sf.CharField(max_length=2, verbose_name='Signup Country', sf_read_only=sf.READ_ONLY, blank=True, null=True)
    state = sf.CharField(max_length=80, verbose_name='State/Province', sf_read_only=sf.NOT_CREATEABLE, blank=True, null=True)
    street = sf.TextField(sf_read_only=sf.NOT_CREATEABLE, blank=True, null=True)
    system_modstamp = sf.DateTimeField(sf_read_only=sf.READ_ONLY)
    time_zone_sid_key = sf.CharField(max_length=40, verbose_name='Time Zone', sf_read_only=sf.NOT_CREATEABLE, choices=[('Pacific/Kiritimati', '(GMT+14:00) Line Islands Time (Pacific/Kiritimati)'), ('Pacific/Enderbury', '(GMT+13:00) Phoenix Islands Time (Pacific/Enderbury)'), ('Pacific/Tongatapu', '(GMT+13:00) Tonga Standard Time (Pacific/Tongatapu)'), ('Pacific/Chatham', '(GMT+12:45) Chatham Standard Time (Pacific/Chatham)'), ('Asia/Kamchatka', '(GMT+12:00) Petropavlovsk-Kamchatski Standard Time (Asia/Kamchatka)'), ('Pacific/Auckland', '(GMT+12:00) New Zealand Standard Time (Pacific/Auckland)'), ('Pacific/Fiji', '(GMT+12:00) Fiji Standard Time (Pacific/Fiji)'), ('Pacific/Guadalcanal', '(GMT+11:00) Solomon Islands Time (Pacific/Guadalcanal)'), ('Pacific/Norfolk', '(GMT+11:00) Norfolk Island Time (Pacific/Norfolk)'), ('Australia/Lord_Howe', '(GMT+10:30) Lord Howe Standard Time (Australia/Lord_Howe)'), ('Australia/Brisbane', '(GMT+10:00) Australian Eastern Standard Time (Australia/Brisbane)'), ('Australia/Sydney', '(GMT+10:00) Australian Eastern Standard Time (Australia/Sydney)'), ('Australia/Adelaide', '(GMT+09:30) Australian Central Standard Time (Australia/Adelaide)'), ('Australia/Darwin', '(GMT+09:30) Australian Central Standard Time (Australia/Darwin)'), ('Asia/Seoul', '(GMT+09:00) Korean Standard Time (Asia/Seoul)'), ('Asia/Tokyo', '(GMT+09:00) Japan Standard Time (Asia/Tokyo)'), ('Asia/Hong_Kong', '(GMT+08:00) Hong Kong Standard Time (Asia/Hong_Kong)'), ('Asia/Kuala_Lumpur', '(GMT+08:00) Malaysia Time (Asia/Kuala_Lumpur)'), ('Asia/Manila', '(GMT+08:00) Philippine Standard Time (Asia/Manila)'), ('Asia/Shanghai', '(GMT+08:00) China Standard Time (Asia/Shanghai)'), ('Asia/Singapore', '(GMT+08:00) Singapore Standard Time (Asia/Singapore)'), ('Asia/Taipei', '(GMT+08:00) Taipei Standard Time (Asia/Taipei)'), ('Australia/Perth', '(GMT+08:00) Australian Western Standard Time (Australia/Perth)'), ('Asia/Bangkok', '(GMT+07:00) Indochina Time (Asia/Bangkok)'), ('Asia/Ho_Chi_Minh', '(GMT+07:00) Indochina Time (Asia/Ho_Chi_Minh)'), ('Asia/Jakarta', '(GMT+07:00) Western Indonesia Time (Asia/Jakarta)'), ('Asia/Rangoon', '(GMT+06:30) Myanmar Time (Asia/Rangoon)'), ('Asia/Dhaka', '(GMT+06:00) Bangladesh Standard Time (Asia/Dhaka)'), ('Asia/Kathmandu', '(GMT+05:45) Nepal Time (Asia/Kathmandu)'), ('Asia/Colombo', '(GMT+05:30) India Standard Time (Asia/Colombo)'), ('Asia/Kolkata', '(GMT+05:30) India Standard Time (Asia/Kolkata)'), ('Asia/Karachi', '(GMT+05:00) Pakistan Standard Time (Asia/Karachi)'), ('Asia/Tashkent', '(GMT+05:00) Uzbekistan Standard Time (Asia/Tashkent)'), ('Asia/Yekaterinburg', '(GMT+05:00) Yekaterinburg Standard Time (Asia/Yekaterinburg)'), ('Asia/Kabul', '(GMT+04:30) Afghanistan Time (Asia/Kabul)'), ('Asia/Tehran', '(GMT+04:30) Iran Daylight Time (Asia/Tehran)'), ('Asia/Baku', '(GMT+04:00) Azerbaijan Standard Time (Asia/Baku)'), ('Asia/Dubai', '(GMT+04:00) Gulf Standard Time (Asia/Dubai)'), ('Asia/Tbilisi', '(GMT+04:00) Georgia Standard Time (Asia/Tbilisi)'), ('Asia/Yerevan', '(GMT+04:00) Armenia Standard Time (Asia/Yerevan)'), ('Africa/Nairobi', '(GMT+03:00) East Africa Time (Africa/Nairobi)'), ('Asia/Baghdad', '(GMT+03:00) Arabian Standard Time (Asia/Baghdad)'), ('Asia/Beirut', '(GMT+03:00) Eastern European Summer Time (Asia/Beirut)'), ('Asia/Jerusalem', '(GMT+03:00) Israel Daylight Time (Asia/Jerusalem)'), ('Asia/Kuwait', '(GMT+03:00) Arabian Standard Time (Asia/Kuwait)'), ('Asia/Riyadh', '(GMT+03:00) Arabian Standard Time (Asia/Riyadh)'), ('Europe/Athens', '(GMT+03:00) Eastern European Summer Time (Europe/Athens)'), ('Europe/Bucharest', '(GMT+03:00) Eastern European Summer Time (Europe/Bucharest)'), ('Europe/Helsinki', '(GMT+03:00) Eastern European Summer Time (Europe/Helsinki)'), ('Europe/Istanbul', '(GMT+03:00) Europe/Istanbul'), ('Europe/Minsk', '(GMT+03:00) Moscow Standard Time (Europe/Minsk)'), ('Europe/Moscow', '(GMT+03:00) Moscow Standard Time (Europe/Moscow)'), ('Africa/Cairo', '(GMT+02:00) Eastern European Standard Time (Africa/Cairo)'), ('Africa/Johannesburg', '(GMT+02:00) South Africa Standard Time (Africa/Johannesburg)'), ('Europe/Amsterdam', '(GMT+02:00) Central European Summer Time (Europe/Amsterdam)'), ('Europe/Berlin', '(GMT+02:00) Central European Summer Time (Europe/Berlin)'), ('Europe/Brussels', '(GMT+02:00) Central European Summer Time (Europe/Brussels)'), ('Europe/Paris', '(GMT+02:00) Central European Summer Time (Europe/Paris)'), ('Europe/Prague', '(GMT+02:00) Central European Summer Time (Europe/Prague)'), ('Europe/Rome', '(GMT+02:00) Central European Summer Time (Europe/Rome)'), ('Africa/Algiers', '(GMT+01:00) Central European Standard Time (Africa/Algiers)'), ('Africa/Casablanca', '(GMT+01:00) Western European Standard Time (Africa/Casablanca)'), ('Europe/Dublin', '(GMT+01:00) Greenwich Mean Time (Europe/Dublin)'), ('Europe/Lisbon', '(GMT+01:00) Western European Summer Time (Europe/Lisbon)'), ('Europe/London', '(GMT+01:00) British Summer Time (Europe/London)'), ('America/Scoresbysund', '(GMT+00:00) East Greenland Summer Time (America/Scoresbysund)'), ('Atlantic/Azores', '(GMT+00:00) Azores Summer Time (Atlantic/Azores)'), ('GMT', '(GMT+00:00) Greenwich Mean Time (GMT)'), ('Atlantic/Cape_Verde', '(GMT-01:00) Cape Verde Standard Time (Atlantic/Cape_Verde)'), ('Atlantic/South_Georgia', '(GMT-02:00) South Georgia Time (Atlantic/South_Georgia)'), ('America/St_Johns', '(GMT-02:30) Newfoundland Daylight Time (America/St_Johns)'), ('America/Argentina/Buenos_Aires', '(GMT-03:00) Argentina Standard Time (America/Argentina/Buenos_Aires)'), ('America/Halifax', '(GMT-03:00) Atlantic Daylight Time (America/Halifax)'), ('America/Sao_Paulo', '(GMT-03:00) Brasilia Standard Time (America/Sao_Paulo)'), ('Atlantic/Bermuda', '(GMT-03:00) Atlantic Daylight Time (Atlantic/Bermuda)'), ('America/Caracas', '(GMT-04:00) Venezuela Time (America/Caracas)'), ('America/Indiana/Indianapolis', '(GMT-04:00) Eastern Daylight Time (America/Indiana/Indianapolis)'), ('America/New_York', '(GMT-04:00) Eastern Daylight Time (America/New_York)'), ('America/Puerto_Rico', '(GMT-04:00) Atlantic Standard Time (America/Puerto_Rico)'), ('America/Santiago', '(GMT-04:00) Chile Standard Time (America/Santiago)'), ('America/Bogota', '(GMT-05:00) Colombia Standard Time (America/Bogota)'), ('America/Chicago', '(GMT-05:00) Central Daylight Time (America/Chicago)'), ('America/Lima', '(GMT-05:00) Peru Standard Time (America/Lima)'), ('America/Mexico_City', '(GMT-05:00) Central Daylight Time (America/Mexico_City)'), ('America/Panama', '(GMT-05:00) Eastern Standard Time (America/Panama)'), ('America/Denver', '(GMT-06:00) Mountain Daylight Time (America/Denver)'), ('America/El_Salvador', '(GMT-06:00) Central Standard Time (America/El_Salvador)'), ('America/Mazatlan', '(GMT-06:00) Mexican Pacific Daylight Time (America/Mazatlan)'), ('America/Los_Angeles', '(GMT-07:00) Pacific Daylight Time (America/Los_Angeles)'), ('America/Phoenix', '(GMT-07:00) Mountain Standard Time (America/Phoenix)'), ('America/Tijuana', '(GMT-07:00) Pacific Daylight Time (America/Tijuana)'), ('America/Anchorage', '(GMT-08:00) Alaska Daylight Time (America/Anchorage)'), ('Pacific/Pitcairn', '(GMT-08:00) Pitcairn Time (Pacific/Pitcairn)'), ('America/Adak', '(GMT-09:00) Hawaii-Aleutian Daylight Time (America/Adak)'), ('Pacific/Gambier', '(GMT-09:00) Gambier Time (Pacific/Gambier)'), ('Pacific/Marquesas', '(GMT-09:30) Marquesas Time (Pacific/Marquesas)'), ('Pacific/Honolulu', '(GMT-10:00) Hawaii-Aleutian Standard Time (Pacific/Honolulu)'), ('Pacific/Niue', '(GMT-11:00) Niue Time (Pacific/Niue)'), ('Pacific/Pago_Pago', '(GMT-11:00) Samoa Standard Time (Pacific/Pago_Pago)')])
    trial_expiration_date = sf.DateTimeField(sf_read_only=sf.READ_ONLY, blank=True, null=True)
    ui_skin = sf.CharField(max_length=40, verbose_name='UI Skin', sf_read_only=sf.NOT_CREATEABLE, default='Theme3', choices=[('Theme1', 'salesforce.com Classic'), ('Theme2', 'Salesforce'), ('PortalDefault', 'Portal Default'), ('Webstore', 'Webstore'), ('Theme3', 'Aloha')], blank=True, null=True)
    uses_start_date_as_fiscal_year_name = sf.BooleanField(verbose_name='Fiscal Year Name by Start', sf_read_only=sf.READ_ONLY, default=False)
    web_to_case_default_origin = sf.CharField(max_length=40, verbose_name='Web to Cases Default Origin', sf_read_only=sf.NOT_CREATEABLE, blank=True, null=True)
    class Meta(sf.Model.Meta):
        db_table = 'Organization'
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        # keyPrefix = '00D'





WHAT_TYPES = [
    ('account', 'Account'),
    ('opportunity', 'Opportunity'),
    ('lead', 'Lead'),
    ('contact', 'Contact')
]
SERVICE_TYPES = [
    ('meeting', 'Meeting'),
    ('call', 'Call'),
    ('email', 'Email'),
]


class Location(models.Model):
    address = models.CharField(max_length=255)
    is_valid = models.BooleanField()
    is_office = models.BooleanField()
    related_to = models.CharField(max_length=20)
    related_to_id = models.CharField(max_length=18)
    related_to_component = models.CharField(max_length=20, null=True)
    owner_id = models.CharField(max_length=18, null=True, blank=True)

    class Meta:
        unique_together = [
            ('related_to', 'related_to_component', 'related_to_id')
        ]

class Recommendation(models.Model):
    score = models.FloatField()
    reason1 = models.CharField(max_length=60)
    reason2 = models.CharField(max_length=60)
    reason3 = models.CharField(max_length=60)
    service_type = models.CharField(choices=SERVICE_TYPES, max_length=10)
    service_time = models.IntegerField()
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    what_type = models.CharField(choices=WHAT_TYPES, max_length=11)
    what_id = models.CharField(max_length=18)
    owner_id = models.CharField(max_length=18)
    
    class Meta:
        verbose_name = 'Recommendation'
        verbose_name_plural = 'Recommendations'
    


class Route(models.Model):
    start = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='routes_from')
    end = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='routes_to')
    distance = models.IntegerField()
    
    class Meta:
        indexes = [
            models.Index(fields=['start', 'end'])
        ]
        unique_together = [
            ('start', 'end')
        ]
        permissions = [
            ('refresh_routes', 'Refresh routes')
        ]


# This model is only used for permissions
class Engine(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = [
            ('engine_recalculate', 'Can start recalculation of recommendations')
        ]
