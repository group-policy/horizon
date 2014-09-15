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
from openstack_dashboard.dashboards.project.endpoint_groups import tables

EPGsTable = tables.EPGsTable


class EPGsTab(tabs.TableTab):
    table_classes = (EPGsTable,)
    name = _("EPGs")
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


class EPGTabs(tabs.TabGroup):
    slug = "epgtabs"
    tabs = (EPGsTab,)
    sticky = True


class EPGDetailsTab(tabs.Tab):
    name = _("EPG Details")
    slug = "epgdetails"
    template_name = "project/endpoint_groups/_epg_details.html"
    failure_url = reverse_lazy('horizon:project:endpoint_group:index')

    def get_context_data(self, request):
        epgid = self.tab_group.kwargs['epg_id']
        try:
            epg = api.group_policy.epg_get(request, epgid)
        except Exception:
            exceptions.handle(request, _('Unable to retrieve epg details.'), redirect=self.failure_url)
        return {'epg': epg}



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
        instances = []
        try:
            marker = self.request.GET.get(tables.InstancesTable._meta.pagination_param, None)
            instances, self._has_more = api.nova.server_list(self.request,search_opts={'marker': marker, 'paginate': True})
            for item in instances:
                setattr(item,'epgid',epgid)
            instances = instances
        except Exception as e:
            self._has_more = False
            error_message = _('Unable to get instances')
            exceptions.handle(self.request, error_message)
            instances = []
        return instances

class ConsumedTab(tabs.TableTab):
    name = _('Consumed')
    slug = 'consumed_contracts_tab'
    table_classes = (tables.ConsumedContractsTable,)
    template_name = ("horizon/common/_detail_table.html")

    def get_consumed_contracts_data(self):
        epgid = self.tab_group.kwargs['epg_id']
        items = api.group_policy.contract_list(self.request)
        return items


class ProvidedTab(tabs.TableTab):
    name = _('Provided')
    slug = 'provided_contracts_tab'
    table_classes = (tables.ProvidedContractsTable,)
    template_name = ("horizon/common/_detail_table.html")
    
    def get_provided_contracts_data(self):
        epgid = self.tab_group.kwargs['epg_id']
        items = []
        return []

class EPGMemberTabs(tabs.TabGroup):
    slug = 'member_tabs'
    tabs = (EPGDetailsTab, InstancesTab,ConsumedTab,ProvidedTab,)
    stiky = True
