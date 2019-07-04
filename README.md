# Sales Planning Engine

This is the actual engine part of the Sales Planning Engine for Salesforce. Because of technical limitations of the Salesforce platform, it runs on Heroku and integrates with Salesforce using the REST API, callouts, Apex REST and Heroku Connect. Below are instructions on how to set it up and run it (both locally and on Heroku).  
This project is based on the [Getting Started](https://github.com/heroku/python-getting-started) project for Python by Heroku.

## Deploying to Heroku
Because of the deep integration between this project running on Heroku and the Salesforce platform, getting the whole app to run is no small feat. You will have to alternate between the Salesforce and Heroku setup, setting up different interaction endpoints on both sides.  
Let's get started.

### Install tools
Before you begin, make sure you have all the necessary tools installed on your machine:
* [Python 3.7](http://install.python-guide.org)
* [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
* [SFDX CLI](https://developer.salesforce.com/tools/sfdxcli)
* [git](https://git-scm.com/)

Also, make sure you have access to the `spe-heroku` and `spe-salesforce` repos on GitHub.

### Clone repos
Clone the `spe-heroku` and `spe-salesforce` repos to your machine (and `cd` into the Heroku project):

```sh
$ git clone git@github.com:TuurDutoit/spe-heroku.git
$ git clone git@github.com:TuurDutoit/spe-salesforce.git
$ cd spe-heroku
```

### Create Heroku app
Create a new app on Heroku via the CLI:

```sh
$ heroku create
```

Don't push anything to it yet, just note down the URL (usually in the form `https://xxx-xxx-12345.herokuapp.com`).  
This should have added a remote to the git repo called `heroku`. This is very useful because that means the Heroku CLI can find the name of your app automatically (if it's invoked from this directory), which means you don't have to pass the `-a <app name>` flag every time. If this doesn't work for some reason, you can use the following command to fix this (run this from within the `spe-heroku` project folder):

```sh
$ heroku git:remote -a <app name>
```

### Provision add-ons (Heroku)
Provision the (free) [Postgres add-on](https://elements.heroku.com/addons/heroku-postgresql) via the CLI:

```sh
$ heroku addons:create heroku-postgresql:hobby-dev
```

A very useful (but not required) add-on is [Papertrail](https://elements.heroku.com/addons/papertrail), which gathers the engine's logs:

```sh
$ heroku addons:create papertrail:choklad
```

### Create a Salesforce org
A standard [Developer org](https://developer.salesforce.com/signup) will do. Make sure Einstein Next Best Action is enabled though.

### Add remote site (Salesforce)
This allows Salesforce to callout to the engine, which is required to notify it of changes and to retrieve recommendation records.

To add the remote site, navigate to `Setup > Remote Site Settings` in Salesforce and click `New Remote Site`. Fill in the following details:
* Name: doesn't matter (e.g. `Recommendations_Engine`)
* Remote Site URL: the URL of the Heroku app you just created
* Disable protocol security: unchecked
* Active: checked

Click `Save`.

### Add Connected App (Salesforce)
This allows the engine to login to Salesforce in order to fetch relevant records during recalculation.

To add the connected app, navigate to `Setup > App Manager`, click `New Connected App` and fill in the following details (leave the rest as-is):
* Connected App Name and API Name: doesn't matter (e.g. `Recommendations Engine`)
* Contact email: your email address
* Enable OAuth Settings: checked
* Callback URL: `<heroku app URL>/auth/oauth2/callback` (fill in the URL of the app you created earlier)
* Selected OAuth Scopes:
    * Access and manage your data (api)
* Require Secret for Web Server Flow: checked

Click `Save`.  
Note down the Consumer Key and Client Secret. You will need to add them to your environment variables (in the Heroku UI, or in `.env` if running locally).

### Create API User (Salesforce)
The engine on Heroku logs in to Salesforce using the credentials of a specific user. The quick and dirty way is to simply use your own credentials (as System Administrator). This is however a terrible idea security-wise, so here's instructions on how to set up a new user that is to be used only for the Heroku -> Salesforce integration. Note that I used the first option myself and haven't tested the second one...  
If you do plan to use your own credentials, make sure you have the right permissions and settings.

1. Create a new user in Salesforce: navigate to `Setup > Users`, click `New User` and fill in the required details. This user needs a full `Salesforce` license as its needs access to Sales Cloud objects.
2. Harden security: for tighter security, it is advisable to create a new profile for this user with the following required permissions:
    * `View All` permissions on the following objects (including all fields, unless specified otherwise):
        * `User` (only the `time_zone_sid_key` field should be enough)
        * `Account`
        * `Contact`
        * `Lead`
        * `Opportunity`
        * `Event`
        * `Organization` (only the `Address` field should be enough)
    * Connected App Access
        * Enabled for the connected app you created earlier
    * Administrative Permissions
        * API Enabled
3. Note down the user's username and password, and get a security token by following [these instructions](https://help.salesforce.com/articleView?id=user_security_token.htm&type=5)

### Get a Google Maps API Key (Google)
Follow the instructions on the [Google Maps website](https://cloud.google.com/maps-platform#get-started). Make sure the API key has access to the Google Maps Directions API. Be aware that the engine might make quite a few requests to this API!

### Add environment variables (Heroku)
From the [Heroku dashboard](https://dashboard.heroku.com), open your newly created app, go to the Setting tab and click `Reveal Config Vars`. Create new variables here as described in the `.env.example` file in this repo.  
Normally, the `DATABASE_URL` variable should be populated already (this happened when you provisioned the Postgres add-on). For `SECRET_KEY`, generate a random string. For `SF_CONSUMER_KEY` and `SF_CONSUMER_SECRET`, fill in the consumer key and client secret of the Connected App you created earlier. For `SF_USERNAME`, `SF_PASSWORD` and `SF_SECURITY_TOKEN`, fill in the credentials of the user you just created. Fill in the Google Maps API key.  
You can adjust lots of different parameters and features with environment variables. Because there are way too many to document here, just take a look at the code.

### Deploy app (Heroku)
Deploying the app to Heroku can be done in 2 ways:
* Deploy directy to Heroku using Git: you push your code to the master branch on a remote on Heroku. Heroku automatically redeploys your app.
* Push your code to GitHub: by connecting Heroku to GitHub, it will be notified when you push your code and redeploy the app.

#### Directly to Heroku
If you followed the previous steps, you should already have the `heroku` remote in your `spe-heroku` repo, which means you're all set!  
Any code you push to the master branch on this remote will be deployed. You can do so now:

```sh
$ git push heroku master
```

#### GitHub
To have Heroku automatically redeploy your app when you push to GitHub, navigate to the `Deploy` tab in the Heroku dashboard and select `GitHub` as deployment method. Login to GitHub and select the right repo (`spe-heroku`). Don't forget to enable automatic deploys in the Heroku UI!  
Any code pushed to the master branch on GitHub will automatically be deployed on Heroku.

This is the technique I used, so if you have access to my GitHub repo (`TuurDutoit/spe-heroku`), you can deploy updates to my Heroku app by pushing to this repo.

### Django setup (Heroku)
Django requires a bit of setup before it can run; more specifically, it expects the database to be set up and static files to be present in a certain directory. Heroku automatically takes care of the static files (by running `python manage.py collectstatic`) and the `Procfile` of this project is set up to automatically migrate the database when you deploy a new version (see the `release` process in `Procfile`).  
If any of this doesn't work, run the following commands:

```sh
heroku run python manage.py collectstatic
heroku run python manage.py migrate
```

If this also fails due to Heroku setup, you can run these on your local machine:

```sh
heroku local:run python manage.py collectstatic
heroku local:run python manage.py migrate
```

Make sure you have the right environment variables in `.env` and `python` points to a Python 3 installation! If that is not the case, use `python3` instead of `python`.

### Check deployment (Heroku)
The Heroku app should be up and running. Click `Open App` in the Heroku UI or run `$ heroku open` to open it. You should see a very basic webpage telling you you are seeing the Sales Planning Engine.  
Note that when you deploy, it might take a minute for that process to finish and the app to start up.

At this point, you have the engine running and ready to accept change notifications. It can fetch relevant data from Salesforce (using the REST API and logging in through the Connected App and API user you created) and driving distances from Google Maps.

Now, let's set up the Salesforce side.

### Create admin (Heroku)
Use the following command to create a user for the Django admin site:

```sh
heroku run python manage.py createsuperuser
```

You will be prompted for a username, email address and password for the admin user. This is the user you will use yourself to administer the Django environment (don't worry, it's not much).

### Create API user (Heroku)
In order for Salesforce to notify the engine of changes, it needs the credentials of a Django user. Lets created one:
1. Navigate to the Django admin site. You can find this at `https://<app name>.herokuapp.com/admin`
2. Log in using the username and password of the user you created earlier on (using the `createsuperuser` command)
3. Next to `Users`, click `Add`
4. Fill in a username and strong password and click `Save`
5. Optionally fill in a descriptive name. An email address is not required.
6. Make sure the user is active, but not staff or superuser
7. Add the permission `web | engine | Can start recalculation of recommendations`
8. Click `Save`

### Provision the Heroku Connect add-on (Heroku)
Add the [Heroku Connect add-on](https://elements.heroku.com/addons/herokuconnect) to your app:

```sh
$ heroku addons:create herokuconnect:demo
```

To configure the add-on, follow these steps:
1. Open the add-on's settings (either from the `Resources` tab in the UI or using the `$ heroku addons:open` command)
2. Click `Setup Connection`
3. Select the right Postgres database (there should only be one though...) and click `Next`, then `Authorize`
4. This will ask you to log in to Salesforce. It doesn't really matter which user you use here: this app won't actually use this connection, as only the 'External Objects' functionality is used, not the Salesforce sync. Just make sure this user can view all object/field settings.
5. After successfully authenticating, you can configure Heroku Connect. As I just said, you can leave the `Mappings` empty; we don't sync Salesforce data to Heroku
6. Go to the `External Objects` tab and click `Create Credentials`, then `Show Credentials`. Note down the username, password and server URL
7. Under `Data Sources`, select the `web_recommendation` and `web_location` tables

### Deploy app (Salesforce)
You can now follow the instructions in the `spe-salesforce` repo to finish the setup of the Salesforce side. You have completed the steps up to and including `Add remote site`, so you should start with `Create named credential`.  
When you're done, everything should be up and running!


## Running Locally
You can run the engine locally, on your own machine, which is sometimes useful for debugging. In this configuration, it can connect to Salesforce and Google Maps (and a Postgres DB, either local or on Heroku), but Salesforce won't be able to connect to the engine! This means your app running locally won't receive change notifications from Salesforce. You can, of course, send them yourself using a tool like Postman.  
If you connect to the Heroku database (not a local Postgres DB) and you still have an instance of the engine running on Heroku, Salesforce will still be able to retrieve recommendation records, even the ones generated by your locally running app.

Make sure you have [Python 3.7](http://install.python-guide.org) and the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed locally. You can also install [Postgres](https://devcenter.heroku.com/articles/heroku-postgresql#local-setup) if you want to use a local database, though it is often easier to simply use the Heroku DB. Even when running locally, a connection to a Salesforce org (including all related setup) and the Google Maps API is required!

First, clone the project and install dependencies:

```sh
$ git clone https://github.com/TuurDutoti/spe-heroku
$ cd spe-heroku
$ python3 -m venv spe
$ pip install -r requirements.txt
```

Then, configure your environment: copy the `.env.example` file and name it `.env`. Fill in the details as described in this file.  
Finally, setup the database and start the engine:

```sh
$ python manage.py migrate
$ python manage.py collectstatic
$ heroku local web
```

Your app should now be running on [localhost:5000](http://localhost:5000/).

## Resources
For more information about the project, take a look at the following documents:
- [research findings](https://tinyurl.com/y4452prm)
- [wireframes](https://tinyurl.com/y2ayb36g)
- [functional requirements](https://tinyurl.com/y3d3mtml)
- [milestone onepagers](https://tinyurl.com/y4744ldk)

For more information about using Python on Heroku, see these Dev Center articles:
- [Python on Heroku](https://devcenter.heroku.com/categories/python)
