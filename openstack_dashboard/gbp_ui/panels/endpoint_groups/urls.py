#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# @author: Ronak Shah


from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

import views

urlpatterns = patterns( '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^addepg$', views.AddEPGView.as_view(), name='addepg'),
    url(r'^updateepg/(?P<epg_id>[^/]+)/$', views.UpdateEPGView.as_view(), name='updateepg'),
    url(r'^epg/(?P<epg_id>[^/]+)/$', views.EPGDetailsView.as_view(), name='epgdetails'),
    url(r'^addvm/(?P<epg_id>[^/]+)/$', views.LaunchVMView.as_view(), name='addvm'),
    url(r'^add_contract/(?P<epg_id>[^/]+)/$', views.CreateContractView.as_view(), name='add_contract'),
    url(r'^remove_contract/(?P<epg_id>[^/]+)/$', views.RemoveContractView.as_view(), name='remove_contract'),
    url(r'^add_consumed/(?P<epg_id>[^/]+)/$', views.AddConsumedView.as_view(), name='add_consumed'),
    url(r'^remove_consumed/(?P<epg_id>[^/]+)/$', views.RemoveConsumedView.as_view(), name='remove_consumed'),
    url(r'^addl2policy$', views.AddL2policyView.as_view(), name='addl2policy'),
    url(r'^addl3policy$', views.AddL3policyView.as_view(), name='addl3policy'),
    url(r'^l2policy_details/(?P<l2policy_id>[^/]+)/$', views.L2PolicyDetailsView.as_view(), name='l2policy_details'),
    url(r'^l3policy_details/(?P<l3policy_id>[^/]+)/$', views.L3PolicyDetailsView.as_view(), name='l3policy_details'),
	)