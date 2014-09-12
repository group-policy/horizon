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
            exceptions.handle(request,
                              _('Unable to retrieve epg details.'),
                              redirect=self.failure_url)
        return {'epg': epg}


class EPGDetailsTabs(tabs.TabGroup):
    slug = "epgtabs"
    tabs = (EPGDetailsTab,)
