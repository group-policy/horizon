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

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tabs

from openstack_dashboard import api
import tables
from openstack_dashboard.dashboards.project.instances.tables import is_deleting

EPGsTable = tables.EPGsTable
L2PolicyTable = tables.L2PolicyTable
L3PolicyTable = tables.L3PolicyTable


class EPGsTab(tabs.TableTab):
    table_classes = (EPGsTable,)
    name = _("Groups")
    slug = "endpoint_groups"
    template_name = "horizon/common/_detail_table.html"

    def get_epgstable_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            epgs = api.group_policy.epg_list(self.tab_group.request,
                                            tenant_id=tenant_id)
        except Exception:
            epgs = []
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve epg list.'))

        for epg in epgs:
            epg.set_id_as_name_if_empty()

        return epgs

class L2PolicyTab(tabs.TableTab):
	table_classes = (L2PolicyTable,)
	name = _("L2 Policy")
	slug = "l2policy"
	template_name = "horizon/common/_detail_table.html"

	def get_l2policy_table_data(self):
		policies = []
		try:
			tenant_id = self.request.user.tenant_id
			policies = api.group_policy.l2policy_list(self.request,tenant_id=tenant_id)
		except Exception:
			policies = []
			exceptions.handle(self.tab_group.request,
							_('Unable to retrieve l2 policy list.'))
		return policies

class L3PolicyTab(tabs.TableTab):
	table_classes = (L3PolicyTable,)
	name = _("L3 Policy")
	slug = "l3policy"
	template_name = "horizon/common/_detail_table.html"

	def get_l3policy_table_data(self):
		policies = []
 		try:
			tenant_id = self.request.user.tenant_id
			policies = api.group_policy.l3policy_list(self.request,tenant_id=tenant_id)
		except Exception:
			policies = []
			exceptions.handle(self.tab_group.request,
							_('Unable to retrieve l3 policy list.'))
		return policies 


class EPGTabs(tabs.TabGroup):
    slug = "epgtabs"
    tabs = (EPGsTab,L2PolicyTab,L3PolicyTab)
    sticky = True

class EPGDetailsTab(tabs.Tab):
    name = _("Group Details")
    slug = "epgdetails"
    template_name = "project/endpoint_groups/_epg_details.html"
    failure_url = reverse_lazy('horizon:project:endpoint_group:index')

    def get_context_data(self, request):
        epgid = self.tab_group.kwargs['epg_id']
        try:
            epg = api.group_policy.epg_get(request, epgid)
            l3list = api.group_policy.l3policy_list(request)
            l2list = api.group_policy.l2policy_list(request)
        except Exception:
            exceptions.handle(request, _('Unable to retrieve group details.'), redirect=self.failure_url)
        return {'epg': epg, 'l3list':l3list,'l2list':l2list}

class L2PolicyDetailsTab(tabs.Tab):
	name = _("L2 Policy Details")
	slug = "l2_policy_details"
	template_name = "project/endpoint_groups/_l2_policy_details.html"
	failure_url = reverse_lazy('horizon:project:endpoint_group:index')

	def get_context_data(self,request):
		l2policy_id = self.tab_group.kwargs['l2policy_id']
		try:
			l2policy = api.group_policy.l2policy_get(request,l2policy_id)
		except Exception:
			exceptions.handle(request, _('Unable to retrieve l2 policy details.'), redirect=self.failure_url)
		return {'l2policy':l2policy}

class L3PolicyDetailsTab(tabs.Tab):
	name = _("L3 Policy Details")
	slug = "l3_policy_details"
	template_name = "project/endpoint_groups/_l3_policy_details.html"
	failure_url = reverse_lazy('horizon:project:endpoint_group:index')

	def get_context_data(self,request):
		l3policy_id = self.tab_group.kwargs['l3policy_id']
		try:
			l3policy = api.group_policy.l3policy_get(request,l3policy_id)
		except Exception:
			exceptions.handle(request, _('Unable to retrieve l3 policy details.'), redirect=self.failure_url)
		return {'l3policy':l3policy}

class L2PolicyDetailsTabs(tabs.TabGroup):
	slug = "l2policy_tabs"
	tabs = (L2PolicyDetailsTab,)

class L3PolicyDetailsTabs(tabs.TabGroup):
	slug = "l3policy_tabs"
	tabs = (L3PolicyDetailsTab,) 
 

class EPGDetailsTabs(tabs.TabGroup):
    slug = "epgtabs"
    tabs = (EPGDetailsTab,)

class InstancesTab(tabs.TableTab):
    name = _("Members")
    slug = "members_tab"
    table_classes = (tables.InstancesTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = True

    def get_instances_data(self):
        epgid = self.tab_group.kwargs['epg_id']
        filtered_instances = []
        try:
            eps = api.group_policy.ep_list(self.request,
                                           endpoint_group_id=epgid)
            epg_ports = [x.port_id for x in eps]
            marker = self.request.GET.get(
                tables.InstancesTable._meta.pagination_param, None)
            instances, self._has_more = api.nova.server_list(
                self.request, search_opts={'marker': marker, 'paginate': True})
            instances = [item for item in instances if not is_deleting(item)]
            for item in instances:
                for port in api.neutron.port_list(self.request,
                                                  device_id=item.id):
                    if port.id in epg_ports:
                        filtered_instances.append(item)
                        break
        except Exception as e:
            self._has_more = False
            error_message = _('Unable to get instances')
            exceptions.handle(self.request, error_message)
            filtered_instances = []
        return filtered_instances


class ConsumedTab(tabs.TableTab):
    name = _('Consumed Contracts')
    slug = 'consumed_contracts_tab'
    table_classes = (tables.ConsumedContractsTable,)
    template_name = ("horizon/common/_detail_table.html")

    def get_consumed_contracts_data(self):
        epgid = self.tab_group.kwargs['epg_id']
        epg = api.group_policy.epg_get(self.request, epgid)
        consumed_contract_ids = epg.get('consumed_contracts')
        consumed_contracts = []
        for _id in consumed_contract_ids:
            consumed_contracts.append(api.group_policy.contract_get(self.request, _id))
        return consumed_contracts

class ProvidedTab(tabs.TableTab):
    name = _('Provided Contracts')
    slug = 'provided_contracts_tab'
    table_classes = (tables.ProvidedContractsTable,)
    template_name = ("horizon/common/_detail_table.html")
    
    def get_provided_contracts_data(self):
        epgid = self.tab_group.kwargs['epg_id']
        epg = api.group_policy.epg_get(self.request, epgid)
        provided_contract_ids = epg.get('provided_contracts')
        provided_contracts = []
        for _id in provided_contract_ids:
            provided_contracts.append(api.group_policy.contract_get(self.request, _id))
        return provided_contracts

class EPGMemberTabs(tabs.TabGroup):
    slug = 'member_tabs'
    tabs = (InstancesTab, ProvidedTab, ConsumedTab, EPGDetailsTab,)
    stiky = True