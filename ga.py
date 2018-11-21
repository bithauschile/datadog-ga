"""
Google Analytics check
Collects metrics from the Analytics API.
Jonathan Makuc - Bithaus Chile (Datadog Partner) - jmakuc@bithaus.cl

2016-04-13
- Support for pageViews metric
- Metric value is read from "1 minute ago" instead of "during the last minute"
  in order to obtain a consistent value to report to Datadog. Using "during the last 
  minute" result in reading zeros while waiting for visitors to view pages in that time 
  frame.
- Dimensions and tags can be controlled on yaml file


"""

# the following try/except block will make the custom check compatible with any Agent version
try:
    # first, try to import the base class from old versions of the Agent...
    from checks import AgentCheck, CheckException
except ImportError:
    # ...if the above failed, the check is running in Agent version 6 or later
    from datadog_checks.checks import AgentCheck, CheckException

from google.oauth2 import service_account
import googleapiclient.discovery


class GoogleAnalyticsCheck(AgentCheck):
  """ Collects as many metrics as instances defined in ga.yaml
  """

  scope = ['https://www.googleapis.com/auth/analytics.readonly']
  service = 0
  apiName = 'analytics'
  version = 'v3'

  def check(self, instance):
    self.log.info('profile: %s, tags: %s, pageview_dimensions: %s' % (instance.get('profile'), instance.get('tags'), instance.get('pageview_dimensions')))        
    
    profile = instance.get('profile')
    instanceTags = instance.get('tags')
    instanceTags.append("profile:" + profile)

    # pageview collection
    metricName = 'rt:pageviews'
    pageviewsDims = ['rt:minutesAgo']
    confDims = instance.get('pageview_dimensions');
    if isinstance(confDims, list):
      pageviewsDims = pageviewsDims + confDims
    result = self.get_results(profile, metricName, pageviewsDims)
    headers = result.get('columnHeaders')
    rows = result.get('rows')

    if len(rows) < 1:
      return
      
    pvMetricsSent = 0

    for row in rows:
      # In order to have a consistent metric, we look for the value 1 minute ago
      # and not during the last minute.
      if int(row[0]) == 1:
        tags = []
        tags.extend(instanceTags)
        for i in xrange(len(headers)-1):
          if i > 0:
            # we remove the "rt" from the dimension name
            tags.append(headers[i].get('name')[3:] + ":" + row[i])
            
        self.gauge("googleanalytics.rt.pageviews", 
          row[len(row)-1], 
          tags=tags,
          hostname=None,
          device_name=None)
        
        pvMetricsSent = pvMetricsSent + 1
        
    self.log.info("Pageview Metrics sent %s" % pvMetricsSent)

    # activeUsers collection
    metricName = 'rt:activeUsers'
    activeuserDims = []
    tags = []
    tags.extend(instanceTags)
    
    result = self.get_results(profile, metricName, activeuserDims)

    activeUsers = int(result.get("totalsForAllResults").get(metricName))
   
    self.gauge("googleanalytics.rt.activeUsers",
               activeUsers,
               tags=tags,
               hostname=None,
               device_name=None)
     
    self.log.info("Active users %s" % activeUsers);

  def __init__(self, *args, **kwargs):
    AgentCheck.__init__(self, *args, **kwargs)
    self.log.info('key_file_location: %s' % self.init_config.get('key_file_location'))
    
    self.service = self.get_service(
      self.apiName, 
      self.version, 
      self.scope, 
      self.init_config.get('key_file_location'))

  def get_service(self, api_name, api_version, scope, key_file_location):
    credentials = service_account.Credentials.from_service_account_file(key_file_location, scopes=scope)
    service = googleapiclient.discovery.build(api_name, api_version, credentials=credentials)
    return service

  def get_results(self, profile_id, the_metric, dims):
    if len(dims) > 0:
      return self.service.data().realtime().get(
        ids=profile_id,
        metrics=the_metric,
        dimensions=','.join(dims)).execute() 
    else:
      return self.service.data().realtime().get(
        ids=profile_id,
        metrics=the_metric).execute()
