# Copyright 2018 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Health Check Template."""
import compute_constants
import compute_resource_util
from compute_resource_util import ComputeResource
from compute_resource_util import Resources


def GenerateConfig(context):
  """Generate template config based on python objects."""
  compute_resource_util.SetContext(context)

  health_check = ComputeResource('hc', compute_constants.HTTPSHEALTHCHECKS, {
      'type': 'tcp',
      'tcpHealthCheck': {
          'host': 'localhost',
          'requestPath': '/path/to/my/service',
          'description': 'Integration test http health check',
          'portName': 'hc-port',
          'port': 8080,
          'checkIntervalSec': 3,
          'unhealthyThreshold': 5,
          'healthyThreshold': 2
      }
  })
  bs1 = ComputeResource('bs1', compute_constants.BACKENDSERVICES, {
      'healthChecks': [health_check.SelfLink()],
      'port': 80,
      'portName': 'http',
      'protocol': 'HTTPS',
      'timeoutSec': 30
  })
  bs2 = ComputeResource('bs2', compute_constants.BACKENDSERVICES, {
      'healthChecks': [health_check.SelfLink()],
      'port': 80,
      'portName': 'http',
      'protocol': 'HTTPS',
      'timeoutSec': 30
  })
  url_map = ComputeResource('url-map', compute_constants.URLMAPS, {
      'pathMatchers': [{
          'defaultService': bs1.SelfLink(),
          'description': 'URL Map Description',
          'name': 'url-set-' + context.env['deployment']
      }],
      'defaultService': bs2.SelfLink(),
      'hostRules': [{
          'description': 'test host rule',
          'hosts': ['*'],
          'pathMatcher': 'url-set-' + context.env['deployment']
      }]

  })
  # Please don't normally do this, we have generated these keys/certs purely for
  # testing and they are not used anywhere else in the universe.
  ssl_certificate = ComputeResource('crt', compute_constants.SSLCERTIFICATES, {
      'certificate': context.imports[context.properties['certificateFile']],
      'privateKey': context.imports[context.properties['privateKeyFile']]
  })
  ComputeResource('thttps', compute_constants.TARGETHTTPSPROXIES, {
      'urlMap': url_map.SelfLink(),
      'sslCertificates': [ssl_certificate.SelfLink()]
  })
  return Resources()
