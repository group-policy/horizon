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

from gbp_ui import client
import tables
import tables as ns_tables

class ServiceChainSpecTab(tabs.TableTab):
    name = _("Service Chain Specs")
    table_classes = (ns_tables.ServiceChainSpecTable,)
    slug = "service_chain_specs"
    template_name = "horizon/common/_detail_table.html"

    def get_service_chain_spec_table_data(self):
        return []

class ServiceChainNodeTab(tabs.TableTab):
	name = _("Service Chain Nodes")
	table_classes = (ns_tables.ServiceChainNodeTable,)
	slug = "service_chain_node"
	template_name = "horizon/common/_detail_table.html"

	def get_service_chain_node_table_data(self):
		return []

class ServiceChainInstanceTab(tabs.TableTab):
	name = _("Service Chain Instances")
	table_classes = (ns_tables.ServiceChainInstanceTable,)
	slug = "service_chain_instance"
	template_name = "horizon/common/_detail_table.html"

	def get_service_chain_instance_table_data(self):
		return []

class ServiceChainTabs(tabs.TabGroup):
    slug = "service_chain_spec_tabs"
    tabs = (ServiceChainSpecTab,
			ServiceChainNodeTab,
			ServiceChainInstanceTab,)
    sticky = True
