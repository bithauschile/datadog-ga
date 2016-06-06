# datadog-ga
**Datadog custom check for collecting Google Analytics Real Time data.**

This custom check allows you to retrieve Google Analytics information from the Real Time API and send it as a regular metric to Datadog.

- Support for multiple profiles (views) 
- Handles Active users (rt:activeUsers) and Pageviews (rt:pageviews) metrics
- Allows for custom tagging for each profile
- Allows for dimension-tag mapping for pageviews metric. Example: adding rt:country dimension, generate the #country:<COUNTRY> tag. 

## Installation
In order for the integration to work you must create a Service Account, obtain it's API key and give permission to access Analytics API by adding the Service Account e-mail to the Authorised users in that Property. 
If you are ready with this, go directly to Step 3: Installing the check.

### Step 1 : Get a service account and API key
1. Create a project
  1. Go to [https://console.developers.google.com](https://console.developers.google.com)
  2. Upper right > Select a project
  3. Create a project or select an existing one
2. Enable Google Analytics API
  1. In the left menu "API Manager", go to Overview
  2. In the search box type "analytics"
  3. Click on Analytics API
  4. Enable
3. Create Access Credentials
  1. In the left menu "API Manager", go to Credentials
  2. Create credential > Service Account keys
  3. Select "New service account" and type in the name of it
  4. Select json for key file
  5. When done, **don't forget to save the key json file**
  6. **Take note of service account email** (ie: *my-svc-account@my-project.12345.iam.gserviceaccount.com*)

### Step 2 : Authorize service account to query analytics
1. Go into [https://analytics.google.com](https://analytics.google.com) and log in
2. Go to Admin option in header menu
3. Select the account you want to integrate. You may also select the specific property you want to give access.
4. Goto to *User Management*
5. Add permissions for the service account email address (Read & Analyze)
6. Select the property and the view you wish to collect metrics from
7. **Take note of the View ID for later** (ie: 12345678)

### Step 3: Install the check (Finally!)
> This steps are based on Ubuntu Linux.

1. Clone or download from [https://github.com/bithauschile/datadog-ga](https://github.com/bithauschile/datadog-ga)
2. Install python libraries
  1. Use pip to install the Google API client for Python: `/opt/datadog-agent/embedded/bin/pip install --upgrade google-api-python-client`
3. Install the check:
  - Copy ga.yaml to /etc/dd-agent/conf.d/
  - Copy ga.py to /etc/dd-agent/checks.d/
  - Copy the api key json file to the server in a directory the agent can access *(ie: /etc/dd-agent/conf.d/)*
4. Configure by adding the account information and the properties (views) you want to integrate in `/etc/dd-agent/conf.d/ga.yaml`. 
  - In the following example, the query divides the pageviews in 3 dimensions (country, city, device). For more information about available dimensions go to [this page](https://developers.google.com/analytics/devguides/reporting/realtime/dimsmets/).
  - Be carefull with the *min_collection_interval* paramter. Google Analytics generate a by-minute result in the Real Time response with no timestamp. The only way to correlate Analytics data with the other metrics is running every 60 seconds aprox.

<pre>
  init_config:
    min_collection_interval: 55
    service_account_email: my-svc-account@my-project.12345.iam.gserviceaccount.com
    key_file_location: /opt/datadog-agent/etc/conf.d/key.json

  instances:

    - profile: ga:123456789
      tags:
       - env:test
      pageview_dimensions:
       - rt:country
       - rt:city
       - rt:deviceCategory 
</pre>

## Done!

> Check that everything went right: `/etc/init.d/datadog-agent check ga`.

* Restart the agent: `/etc/init.d/datadog-agent restart`.


##References
- [Google Analytics Real Time API](https://developers.google.com/analytics/devguides/reporting/realtime/v3/reference/)
- [Google API Explorer - Analytics Real Time](https://developers.google.com/apis-explorer/#p/analytics/v3/analytics.data.realtime.get)
- [Datadog - Writing an Agent Check](http://docs.datadoghq.com/guides/agent_checks/)


##Licence
The code is licensed under the MIT License.
