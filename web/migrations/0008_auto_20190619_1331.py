# Generated by Django 2.2.1 on 2019-06-19 13:31

from django.db import migrations, models
import django.db.models.deletion
import salesforce.fields


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0007_auto_20190611_1044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='owner_id',
            field=models.CharField(blank=True, max_length=18, null=True),
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', salesforce.fields.SalesforceAutoField(auto_created=True, db_column='Id', primary_key=True, serialize=False, verbose_name='ID')),
                ('name', salesforce.fields.CharField(max_length=80)),
                ('division', salesforce.fields.CharField(blank=True, max_length=80, null=True)),
                ('street', salesforce.fields.TextField(blank=True, null=True)),
                ('city', salesforce.fields.CharField(blank=True, max_length=40, null=True)),
                ('state', salesforce.fields.CharField(blank=True, max_length=80, null=True, verbose_name='State/Province')),
                ('postal_code', salesforce.fields.CharField(blank=True, max_length=20, null=True, verbose_name='Zip/Postal Code')),
                ('country', salesforce.fields.CharField(blank=True, max_length=80, null=True)),
                ('latitude', salesforce.fields.DecimalField(blank=True, decimal_places=15, max_digits=18, null=True)),
                ('longitude', salesforce.fields.DecimalField(blank=True, decimal_places=15, max_digits=18, null=True)),
                ('geocode_accuracy', salesforce.fields.CharField(blank=True, choices=[('Address', 'Address'), ('NearAddress', 'NearAddress'), ('Block', 'Block'), ('Street', 'Street'), ('ExtendedZip', 'ExtendedZip'), ('Zip', 'Zip'), ('Neighborhood', 'Neighborhood'), ('City', 'City'), ('County', 'County'), ('State', 'State'), ('Unknown', 'Unknown')], max_length=40, null=True)),
                ('address', salesforce.fields.TextField(blank=True, null=True)),
                ('phone', salesforce.fields.CharField(blank=True, max_length=40, null=True)),
                ('fax', salesforce.fields.CharField(blank=True, max_length=40, null=True)),
                ('primary_contact', salesforce.fields.CharField(blank=True, max_length=80, null=True)),
                ('default_locale_sid_key', salesforce.fields.CharField(choices=[('af_ZA', 'Afrikaans (South Africa)'), ('sq_AL', 'Albanian (Albania)'), ('ar_DZ', 'Arabic (Algeria)'), ('ar_BH', 'Arabic (Bahrain)'), ('ar_EG', 'Arabic (Egypt)'), ('ar_IQ', 'Arabic (Iraq)'), ('ar_JO', 'Arabic (Jordan)'), ('ar_KW', 'Arabic (Kuwait)'), ('ar_LB', 'Arabic (Lebanon)'), ('ar_LY', 'Arabic (Libya)'), ('ar_MA', 'Arabic (Morocco)'), ('ar_OM', 'Arabic (Oman)'), ('ar_QA', 'Arabic (Qatar)'), ('ar_SA', 'Arabic (Saudi Arabia)'), ('ar_SD', 'Arabic (Sudan)'), ('ar_SY', 'Arabic (Syria)'), ('ar_TN', 'Arabic (Tunisia)'), ('ar_AE', 'Arabic (United Arab Emirates)'), ('ar_YE', 'Arabic (Yemen)'), ('hy_AM', 'Armenian (Armenia)'), ('az_AZ', 'Azerbaijani (Azerbaijan)'), ('bn_BD', 'Bangla (Bangladesh)'), ('bn_IN', 'Bangla (India)'), ('eu_ES', 'Basque (Spain)'), ('be_BY', 'Belarusian (Belarus)'), ('bs_BA', 'Bosnian (Bosnia & Herzegovina)'), ('bg_BG', 'Bulgarian (Bulgaria)'), ('my_MM', 'Burmese (Myanmar (Burma))'), ('ca_ES', 'Catalan (Spain)'), ('zh_CN_PINYIN', 'Chinese (China, Pinyin Ordering)'), ('zh_CN_STROKE', 'Chinese (China, Stroke Ordering)'), ('zh_CN', 'Chinese (China)'), ('zh_HK_STROKE', 'Chinese (Hong Kong SAR China, Stroke Ordering)'), ('zh_HK', 'Chinese (Hong Kong SAR China)'), ('zh_MO', 'Chinese (Macau SAR China)'), ('zh_SG', 'Chinese (Singapore)'), ('zh_TW_STROKE', 'Chinese (Taiwan, Stroke Ordering)'), ('zh_TW', 'Chinese (Taiwan)'), ('hr_HR', 'Croatian (Croatia)'), ('cs_CZ', 'Czech (Czechia)'), ('da_DK', 'Danish (Denmark)'), ('nl_AW', 'Dutch (Aruba)'), ('nl_BE', 'Dutch (Belgium)'), ('nl_NL', 'Dutch (Netherlands)'), ('nl_SR', 'Dutch (Suriname)'), ('dz_BT', 'Dzongkha (Bhutan)'), ('en_AG', 'English (Antigua & Barbuda)'), ('en_AU', 'English (Australia)'), ('en_BS', 'English (Bahamas)'), ('en_BB', 'English (Barbados)'), ('en_BZ', 'English (Belize)'), ('en_BM', 'English (Bermuda)'), ('en_BW', 'English (Botswana)'), ('en_CM', 'English (Cameroon)'), ('en_CA', 'English (Canada)'), ('en_KY', 'English (Cayman Islands)'), ('en_ER', 'English (Eritrea)'), ('en_FK', 'English (Falkland Islands)'), ('en_FJ', 'English (Fiji)'), ('en_GM', 'English (Gambia)'), ('en_GH', 'English (Ghana)'), ('en_GI', 'English (Gibraltar)'), ('en_GY', 'English (Guyana)'), ('en_HK', 'English (Hong Kong SAR China)'), ('en_IN', 'English (India)'), ('en_ID', 'English (Indonesia)'), ('en_IE', 'English (Ireland)'), ('en_JM', 'English (Jamaica)'), ('en_KE', 'English (Kenya)'), ('en_LR', 'English (Liberia)'), ('en_MG', 'English (Madagascar)'), ('en_MW', 'English (Malawi)'), ('en_MY', 'English (Malaysia)'), ('en_MU', 'English (Mauritius)'), ('en_NA', 'English (Namibia)'), ('en_NZ', 'English (New Zealand)'), ('en_NG', 'English (Nigeria)'), ('en_PK', 'English (Pakistan)'), ('en_PG', 'English (Papua New Guinea)'), ('en_PH', 'English (Philippines)'), ('en_RW', 'English (Rwanda)'), ('en_WS', 'English (Samoa)'), ('en_SC', 'English (Seychelles)'), ('en_SL', 'English (Sierra Leone)'), ('en_SG', 'English (Singapore)'), ('en_SX', 'English (Sint Maarten)'), ('en_SB', 'English (Solomon Islands)'), ('en_ZA', 'English (South Africa)'), ('en_SH', 'English (St. Helena)'), ('en_SZ', 'English (Swaziland)'), ('en_TZ', 'English (Tanzania)'), ('en_TO', 'English (Tonga)'), ('en_TT', 'English (Trinidad & Tobago)'), ('en_UG', 'English (Uganda)'), ('en_GB', 'English (United Kingdom)'), ('en_US', 'English (United States)'), ('en_VU', 'English (Vanuatu)'), ('et_EE', 'Estonian (Estonia)'), ('fi_FI', 'Finnish (Finland)'), ('fr_BE', 'French (Belgium)'), ('fr_CA', 'French (Canada)'), ('fr_KM', 'French (Comoros)'), ('fr_FR', 'French (France)'), ('fr_GN', 'French (Guinea)'), ('fr_HT', 'French (Haiti)'), ('fr_LU', 'French (Luxembourg)'), ('fr_MR', 'French (Mauritania)'), ('fr_MC', 'French (Monaco)'), ('fr_CH', 'French (Switzerland)'), ('fr_WF', 'French (Wallis & Futuna)'), ('ka_GE', 'Georgian (Georgia)'), ('de_AT', 'German (Austria)'), ('de_BE', 'German (Belgium)'), ('de_DE', 'German (Germany)'), ('de_LU', 'German (Luxembourg)'), ('de_CH', 'German (Switzerland)'), ('el_GR', 'Greek (Greece)'), ('gu_IN', 'Gujarati (India)'), ('iw_IL', 'Hebrew (Israel)'), ('hi_IN', 'Hindi (India)'), ('hu_HU', 'Hungarian (Hungary)'), ('is_IS', 'Icelandic (Iceland)'), ('in_ID', 'Indonesian (Indonesia)'), ('ga_IE', 'Irish (Ireland)'), ('it_IT', 'Italian (Italy)'), ('it_CH', 'Italian (Switzerland)'), ('ja_JP', 'Japanese (Japan)'), ('kn_IN', 'Kannada (India)'), ('kk_KZ', 'Kazakh (Kazakhstan)'), ('km_KH', 'Khmer (Cambodia)'), ('ko_KP', 'Korean (North Korea)'), ('ko_KR', 'Korean (South Korea)'), ('ky_KG', 'Kyrgyz (Kyrgyzstan)'), ('lo_LA', 'Lao (Laos)'), ('lv_LV', 'Latvian (Latvia)'), ('lt_LT', 'Lithuanian (Lithuania)'), ('lu_CD', 'Luba-Katanga (Congo - Kinshasa)'), ('lb_LU', 'Luxembourgish (Luxembourg)'), ('mk_MK', 'Macedonian (Macedonia)'), ('ms_BN', 'Malay (Brunei)'), ('ms_MY', 'Malay (Malaysia)'), ('ml_IN', 'Malayalam (India)'), ('mt_MT', 'Maltese (Malta)'), ('mr_IN', 'Marathi (India)'), ('sh_ME', 'Montenegrin (Montenegro)'), ('ne_NP', 'Nepali (Nepal)'), ('no_NO', 'Norwegian (Norway)'), ('ps_AF', 'Pashto (Afghanistan)'), ('fa_IR', 'Persian (Iran)'), ('pl_PL', 'Polish (Poland)'), ('pt_AO', 'Portuguese (Angola)'), ('pt_BR', 'Portuguese (Brazil)'), ('pt_CV', 'Portuguese (Cape Verde)'), ('pt_MZ', 'Portuguese (Mozambique)'), ('pt_PT', 'Portuguese (Portugal)'), ('pt_ST', 'Portuguese (São Tomé & Príncipe)'), ('ro_MD', 'Romanian (Moldova)'), ('ro_RO', 'Romanian (Romania)'), ('rm_CH', 'Romansh (Switzerland)'), ('rn_BI', 'Rundi (Burundi)'), ('ru_KZ', 'Russian (Kazakhstan)'), ('ru_RU', 'Russian (Russia)'), ('sr_BA', 'Serbian (Cyrillic) (Bosnia and Herzegovina)'), ('sr_CS', 'Serbian (Cyrillic) (Serbia)'), ('sh_BA', 'Serbian (Latin) (Bosnia and Herzegovina)'), ('sh_CS', 'Serbian (Latin) (Serbia)'), ('sr_RS', 'Serbian (Serbia)'), ('sk_SK', 'Slovak (Slovakia)'), ('sl_SI', 'Slovenian (Slovenia)'), ('so_DJ', 'Somali (Djibouti)'), ('so_SO', 'Somali (Somalia)'), ('es_AR', 'Spanish (Argentina)'), ('es_BO', 'Spanish (Bolivia)'), ('es_CL', 'Spanish (Chile)'), ('es_CO', 'Spanish (Colombia)'), ('es_CR', 'Spanish (Costa Rica)'), ('es_CU', 'Spanish (Cuba)'), ('es_DO', 'Spanish (Dominican Republic)'), ('es_EC', 'Spanish (Ecuador)'), ('es_SV', 'Spanish (El Salvador)'), ('es_GT', 'Spanish (Guatemala)'), ('es_HN', 'Spanish (Honduras)'), ('es_MX', 'Spanish (Mexico)'), ('es_NI', 'Spanish (Nicaragua)'), ('es_PA', 'Spanish (Panama)'), ('es_PY', 'Spanish (Paraguay)'), ('es_PE', 'Spanish (Peru)'), ('es_PR', 'Spanish (Puerto Rico)'), ('es_ES', 'Spanish (Spain)'), ('es_US', 'Spanish (United States)'), ('es_UY', 'Spanish (Uruguay)'), ('es_VE', 'Spanish (Venezuela)'), ('sw_KE', 'Swahili (Kenya)'), ('sv_SE', 'Swedish (Sweden)'), ('tl_PH', 'Tagalog (Philippines)'), ('tg_TJ', 'Tajik (Tajikistan)'), ('ta_IN', 'Tamil (India)'), ('ta_LK', 'Tamil (Sri Lanka)'), ('te_IN', 'Telugu (India)'), ('th_TH', 'Thai (Thailand)'), ('ti_ET', 'Tigrinya (Ethiopia)'), ('tr_TR', 'Turkish (Turkey)'), ('uk_UA', 'Ukrainian (Ukraine)'), ('ur_PK', 'Urdu (Pakistan)'), ('uz_LATN_UZ', 'Uzbek (LATN,UZ)'), ('vi_VN', 'Vietnamese (Vietnam)'), ('cy_GB', 'Welsh (United Kingdom)'), ('xh_ZA', 'Xhosa (South Africa)'), ('yo_BJ', 'Yoruba (Benin)'), ('zu_ZA', 'Zulu (South Africa)')], max_length=40, verbose_name='Locale')),
                ('time_zone_sid_key', salesforce.fields.CharField(choices=[('Pacific/Kiritimati', '(GMT+14:00) Line Islands Time (Pacific/Kiritimati)'), ('Pacific/Enderbury', '(GMT+13:00) Phoenix Islands Time (Pacific/Enderbury)'), ('Pacific/Tongatapu', '(GMT+13:00) Tonga Standard Time (Pacific/Tongatapu)'), ('Pacific/Chatham', '(GMT+12:45) Chatham Standard Time (Pacific/Chatham)'), ('Asia/Kamchatka', '(GMT+12:00) Petropavlovsk-Kamchatski Standard Time (Asia/Kamchatka)'), ('Pacific/Auckland', '(GMT+12:00) New Zealand Standard Time (Pacific/Auckland)'), ('Pacific/Fiji', '(GMT+12:00) Fiji Standard Time (Pacific/Fiji)'), ('Pacific/Guadalcanal', '(GMT+11:00) Solomon Islands Time (Pacific/Guadalcanal)'), ('Pacific/Norfolk', '(GMT+11:00) Norfolk Island Time (Pacific/Norfolk)'), ('Australia/Lord_Howe', '(GMT+10:30) Lord Howe Standard Time (Australia/Lord_Howe)'), ('Australia/Brisbane', '(GMT+10:00) Australian Eastern Standard Time (Australia/Brisbane)'), ('Australia/Sydney', '(GMT+10:00) Australian Eastern Standard Time (Australia/Sydney)'), ('Australia/Adelaide', '(GMT+09:30) Australian Central Standard Time (Australia/Adelaide)'), ('Australia/Darwin', '(GMT+09:30) Australian Central Standard Time (Australia/Darwin)'), ('Asia/Seoul', '(GMT+09:00) Korean Standard Time (Asia/Seoul)'), ('Asia/Tokyo', '(GMT+09:00) Japan Standard Time (Asia/Tokyo)'), ('Asia/Hong_Kong', '(GMT+08:00) Hong Kong Standard Time (Asia/Hong_Kong)'), ('Asia/Kuala_Lumpur', '(GMT+08:00) Malaysia Time (Asia/Kuala_Lumpur)'), ('Asia/Manila', '(GMT+08:00) Philippine Standard Time (Asia/Manila)'), ('Asia/Shanghai', '(GMT+08:00) China Standard Time (Asia/Shanghai)'), ('Asia/Singapore', '(GMT+08:00) Singapore Standard Time (Asia/Singapore)'), ('Asia/Taipei', '(GMT+08:00) Taipei Standard Time (Asia/Taipei)'), ('Australia/Perth', '(GMT+08:00) Australian Western Standard Time (Australia/Perth)'), ('Asia/Bangkok', '(GMT+07:00) Indochina Time (Asia/Bangkok)'), ('Asia/Ho_Chi_Minh', '(GMT+07:00) Indochina Time (Asia/Ho_Chi_Minh)'), ('Asia/Jakarta', '(GMT+07:00) Western Indonesia Time (Asia/Jakarta)'), ('Asia/Rangoon', '(GMT+06:30) Myanmar Time (Asia/Rangoon)'), ('Asia/Dhaka', '(GMT+06:00) Bangladesh Standard Time (Asia/Dhaka)'), ('Asia/Kathmandu', '(GMT+05:45) Nepal Time (Asia/Kathmandu)'), ('Asia/Colombo', '(GMT+05:30) India Standard Time (Asia/Colombo)'), ('Asia/Kolkata', '(GMT+05:30) India Standard Time (Asia/Kolkata)'), ('Asia/Karachi', '(GMT+05:00) Pakistan Standard Time (Asia/Karachi)'), ('Asia/Tashkent', '(GMT+05:00) Uzbekistan Standard Time (Asia/Tashkent)'), ('Asia/Yekaterinburg', '(GMT+05:00) Yekaterinburg Standard Time (Asia/Yekaterinburg)'), ('Asia/Kabul', '(GMT+04:30) Afghanistan Time (Asia/Kabul)'), ('Asia/Tehran', '(GMT+04:30) Iran Daylight Time (Asia/Tehran)'), ('Asia/Baku', '(GMT+04:00) Azerbaijan Standard Time (Asia/Baku)'), ('Asia/Dubai', '(GMT+04:00) Gulf Standard Time (Asia/Dubai)'), ('Asia/Tbilisi', '(GMT+04:00) Georgia Standard Time (Asia/Tbilisi)'), ('Asia/Yerevan', '(GMT+04:00) Armenia Standard Time (Asia/Yerevan)'), ('Africa/Nairobi', '(GMT+03:00) East Africa Time (Africa/Nairobi)'), ('Asia/Baghdad', '(GMT+03:00) Arabian Standard Time (Asia/Baghdad)'), ('Asia/Beirut', '(GMT+03:00) Eastern European Summer Time (Asia/Beirut)'), ('Asia/Jerusalem', '(GMT+03:00) Israel Daylight Time (Asia/Jerusalem)'), ('Asia/Kuwait', '(GMT+03:00) Arabian Standard Time (Asia/Kuwait)'), ('Asia/Riyadh', '(GMT+03:00) Arabian Standard Time (Asia/Riyadh)'), ('Europe/Athens', '(GMT+03:00) Eastern European Summer Time (Europe/Athens)'), ('Europe/Bucharest', '(GMT+03:00) Eastern European Summer Time (Europe/Bucharest)'), ('Europe/Helsinki', '(GMT+03:00) Eastern European Summer Time (Europe/Helsinki)'), ('Europe/Istanbul', '(GMT+03:00) Europe/Istanbul'), ('Europe/Minsk', '(GMT+03:00) Moscow Standard Time (Europe/Minsk)'), ('Europe/Moscow', '(GMT+03:00) Moscow Standard Time (Europe/Moscow)'), ('Africa/Cairo', '(GMT+02:00) Eastern European Standard Time (Africa/Cairo)'), ('Africa/Johannesburg', '(GMT+02:00) South Africa Standard Time (Africa/Johannesburg)'), ('Europe/Amsterdam', '(GMT+02:00) Central European Summer Time (Europe/Amsterdam)'), ('Europe/Berlin', '(GMT+02:00) Central European Summer Time (Europe/Berlin)'), ('Europe/Brussels', '(GMT+02:00) Central European Summer Time (Europe/Brussels)'), ('Europe/Paris', '(GMT+02:00) Central European Summer Time (Europe/Paris)'), ('Europe/Prague', '(GMT+02:00) Central European Summer Time (Europe/Prague)'), ('Europe/Rome', '(GMT+02:00) Central European Summer Time (Europe/Rome)'), ('Africa/Algiers', '(GMT+01:00) Central European Standard Time (Africa/Algiers)'), ('Africa/Casablanca', '(GMT+01:00) Western European Standard Time (Africa/Casablanca)'), ('Europe/Dublin', '(GMT+01:00) Greenwich Mean Time (Europe/Dublin)'), ('Europe/Lisbon', '(GMT+01:00) Western European Summer Time (Europe/Lisbon)'), ('Europe/London', '(GMT+01:00) British Summer Time (Europe/London)'), ('America/Scoresbysund', '(GMT+00:00) East Greenland Summer Time (America/Scoresbysund)'), ('Atlantic/Azores', '(GMT+00:00) Azores Summer Time (Atlantic/Azores)'), ('GMT', '(GMT+00:00) Greenwich Mean Time (GMT)'), ('Atlantic/Cape_Verde', '(GMT-01:00) Cape Verde Standard Time (Atlantic/Cape_Verde)'), ('Atlantic/South_Georgia', '(GMT-02:00) South Georgia Time (Atlantic/South_Georgia)'), ('America/St_Johns', '(GMT-02:30) Newfoundland Daylight Time (America/St_Johns)'), ('America/Argentina/Buenos_Aires', '(GMT-03:00) Argentina Standard Time (America/Argentina/Buenos_Aires)'), ('America/Halifax', '(GMT-03:00) Atlantic Daylight Time (America/Halifax)'), ('America/Sao_Paulo', '(GMT-03:00) Brasilia Standard Time (America/Sao_Paulo)'), ('Atlantic/Bermuda', '(GMT-03:00) Atlantic Daylight Time (Atlantic/Bermuda)'), ('America/Caracas', '(GMT-04:00) Venezuela Time (America/Caracas)'), ('America/Indiana/Indianapolis', '(GMT-04:00) Eastern Daylight Time (America/Indiana/Indianapolis)'), ('America/New_York', '(GMT-04:00) Eastern Daylight Time (America/New_York)'), ('America/Puerto_Rico', '(GMT-04:00) Atlantic Standard Time (America/Puerto_Rico)'), ('America/Santiago', '(GMT-04:00) Chile Standard Time (America/Santiago)'), ('America/Bogota', '(GMT-05:00) Colombia Standard Time (America/Bogota)'), ('America/Chicago', '(GMT-05:00) Central Daylight Time (America/Chicago)'), ('America/Lima', '(GMT-05:00) Peru Standard Time (America/Lima)'), ('America/Mexico_City', '(GMT-05:00) Central Daylight Time (America/Mexico_City)'), ('America/Panama', '(GMT-05:00) Eastern Standard Time (America/Panama)'), ('America/Denver', '(GMT-06:00) Mountain Daylight Time (America/Denver)'), ('America/El_Salvador', '(GMT-06:00) Central Standard Time (America/El_Salvador)'), ('America/Mazatlan', '(GMT-06:00) Mexican Pacific Daylight Time (America/Mazatlan)'), ('America/Los_Angeles', '(GMT-07:00) Pacific Daylight Time (America/Los_Angeles)'), ('America/Phoenix', '(GMT-07:00) Mountain Standard Time (America/Phoenix)'), ('America/Tijuana', '(GMT-07:00) Pacific Daylight Time (America/Tijuana)'), ('America/Anchorage', '(GMT-08:00) Alaska Daylight Time (America/Anchorage)'), ('Pacific/Pitcairn', '(GMT-08:00) Pitcairn Time (Pacific/Pitcairn)'), ('America/Adak', '(GMT-09:00) Hawaii-Aleutian Daylight Time (America/Adak)'), ('Pacific/Gambier', '(GMT-09:00) Gambier Time (Pacific/Gambier)'), ('Pacific/Marquesas', '(GMT-09:30) Marquesas Time (Pacific/Marquesas)'), ('Pacific/Honolulu', '(GMT-10:00) Hawaii-Aleutian Standard Time (Pacific/Honolulu)'), ('Pacific/Niue', '(GMT-11:00) Niue Time (Pacific/Niue)'), ('Pacific/Pago_Pago', '(GMT-11:00) Samoa Standard Time (Pacific/Pago_Pago)')], max_length=40, verbose_name='Time Zone')),
                ('language_locale_key', salesforce.fields.CharField(choices=[('en_US', 'English'), ('de', 'German'), ('es', 'Spanish'), ('fr', 'French'), ('it', 'Italian'), ('ja', 'Japanese'), ('sv', 'Swedish'), ('ko', 'Korean'), ('zh_TW', 'Chinese (Traditional)'), ('zh_CN', 'Chinese (Simplified)'), ('pt_BR', 'Portuguese (Brazil)'), ('nl_NL', 'Dutch'), ('da', 'Danish'), ('th', 'Thai'), ('fi', 'Finnish'), ('ru', 'Russian'), ('es_MX', 'Spanish (Mexico)'), ('no', 'Norwegian')], max_length=40, verbose_name='Language')),
                ('receives_info_emails', salesforce.fields.BooleanField(default=False, verbose_name='Info Emails')),
                ('receives_admin_info_emails', salesforce.fields.BooleanField(default=False, verbose_name='Info Emails Admin')),
                ('preferences_require_opportunity_products', salesforce.fields.BooleanField(default=False, verbose_name='RequireOpportunityProducts')),
                ('preferences_transaction_security_policy', salesforce.fields.BooleanField(default=False, verbose_name='TransactionSecurityPolicy')),
                ('preferences_terminate_oldest_session', salesforce.fields.BooleanField(default=False, verbose_name='TerminateOldestSession')),
                ('preferences_consent_management_enabled', salesforce.fields.BooleanField(default=False, verbose_name='ConsentManagementEnabled')),
                ('preferences_individual_auto_create_enabled', salesforce.fields.BooleanField(default=False, verbose_name='IndividualAutoCreateEnabled')),
                ('preferences_auto_select_individual_on_merge', salesforce.fields.BooleanField(default=False, verbose_name='AutoSelectIndividualOnMerge')),
                ('preferences_activity_analytics_enabled', salesforce.fields.BooleanField(default=False, verbose_name='ActivityAnalyticsEnabled')),
                ('preferences_lightning_login_enabled', salesforce.fields.BooleanField(default=False, verbose_name='LightningLoginEnabled')),
                ('preferences_only_llperm_user_allowed', salesforce.fields.BooleanField(db_column='PreferencesOnlyLLPermUserAllowed', default=False, verbose_name='OnlyLLPermUserAllowed')),
                ('fiscal_year_start_month', salesforce.fields.IntegerField(blank=True, null=True, verbose_name='Fiscal Year Starts In')),
                ('uses_start_date_as_fiscal_year_name', salesforce.fields.BooleanField(default=False, verbose_name='Fiscal Year Name by Start')),
                ('default_account_access', salesforce.fields.CharField(blank=True, choices=[('None', 'Private'), ('Read', 'Read Only'), ('Edit', 'Read/Write'), ('ControlledByLeadOrContact', 'ControlledByLeadOrContact'), ('ControlledByCampaign', 'ControlledByCampaign')], max_length=40, null=True)),
                ('default_contact_access', salesforce.fields.CharField(blank=True, choices=[('None', 'Private'), ('Read', 'Read Only'), ('Edit', 'Read/Write'), ('ControlledByParent', 'Controlled By Parent')], max_length=40, null=True)),
                ('default_opportunity_access', salesforce.fields.CharField(blank=True, choices=[('None', 'Private'), ('Read', 'Read Only'), ('Edit', 'Read/Write'), ('ControlledByLeadOrContact', 'ControlledByLeadOrContact'), ('ControlledByCampaign', 'ControlledByCampaign')], max_length=40, null=True)),
                ('default_lead_access', salesforce.fields.CharField(blank=True, choices=[('None', 'Private'), ('Read', 'Read Only'), ('Edit', 'Read/Write'), ('ReadEditTransfer', 'Read/Write/Transfer')], max_length=40, null=True)),
                ('default_case_access', salesforce.fields.CharField(blank=True, choices=[('None', 'Private'), ('Read', 'Read Only'), ('Edit', 'Read/Write'), ('ReadEditTransfer', 'Read/Write/Transfer')], max_length=40, null=True)),
                ('default_calendar_access', salesforce.fields.CharField(blank=True, choices=[('HideDetails', 'Hide Details'), ('HideDetailsInsert', 'Hide Details and Add Events'), ('ShowDetails', 'Show Details'), ('ShowDetailsInsert', 'Show Details and Add Events'), ('AllowEdits', 'Full Access')], default='HideDetailsInsert', max_length=40, null=True)),
                ('default_pricebook_access', salesforce.fields.CharField(blank=True, choices=[('None', 'No Access'), ('Read', 'View Only'), ('ReadSelect', 'Use')], max_length=40, null=True, verbose_name='Default Price Book Access')),
                ('default_campaign_access', salesforce.fields.CharField(blank=True, choices=[('None', 'Private'), ('Read', 'Read Only'), ('Edit', 'Read/Write'), ('All', 'Owner')], max_length=40, null=True)),
                ('system_modstamp', salesforce.fields.DateTimeField()),
                ('compliance_bcc_email', salesforce.fields.EmailField(blank=True, max_length=254, null=True, verbose_name='Compliance BCC Email')),
                ('ui_skin', salesforce.fields.CharField(blank=True, choices=[('Theme1', 'salesforce.com Classic'), ('Theme2', 'Salesforce'), ('PortalDefault', 'Portal Default'), ('Webstore', 'Webstore'), ('Theme3', 'Aloha')], default='Theme3', max_length=40, null=True, verbose_name='UI Skin')),
                ('signup_country_iso_code', salesforce.fields.CharField(blank=True, max_length=2, null=True, verbose_name='Signup Country')),
                ('trial_expiration_date', salesforce.fields.DateTimeField(blank=True, null=True)),
                ('num_knowledge_service', salesforce.fields.IntegerField(blank=True, null=True, verbose_name='Knowledge Licenses')),
                ('organization_type', salesforce.fields.CharField(blank=True, choices=[('Team Edition', None), ('Professional Edition', None), ('Enterprise Edition', None), ('Developer Edition', None), ('Personal Edition', None), ('Unlimited Edition', None), ('Contact Manager Edition', None), ('Base Edition', None)], max_length=40, null=True, verbose_name='Edition')),
                ('namespace_prefix', salesforce.fields.CharField(blank=True, max_length=15, null=True)),
                ('instance_name', salesforce.fields.CharField(blank=True, max_length=5, null=True)),
                ('is_sandbox', salesforce.fields.BooleanField(default=False)),
                ('web_to_case_default_origin', salesforce.fields.CharField(blank=True, max_length=40, null=True, verbose_name='Web to Cases Default Origin')),
                ('monthly_page_views_used', salesforce.fields.IntegerField(blank=True, null=True)),
                ('monthly_page_views_entitlement', salesforce.fields.IntegerField(blank=True, null=True, verbose_name='Monthly Page Views Allowed')),
                ('is_read_only', salesforce.fields.BooleanField(default=False)),
                ('created_date', salesforce.fields.DateTimeField()),
                ('last_modified_date', salesforce.fields.DateTimeField()),
                ('created_by', salesforce.fields.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='organization_createdby_set', to='web.User')),
                ('last_modified_by', salesforce.fields.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='organization_lastmodifiedby_set', to='web.User')),
            ],
            options={
                'verbose_name': 'Organization',
                'verbose_name_plural': 'Organizations',
                'db_table': 'Organization',
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
    ]