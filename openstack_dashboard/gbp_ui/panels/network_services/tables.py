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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django import http
from django.template import defaultfilters as dfilters

from horizon import tables
from horizon.utils import filters

from gbp_ui import column_filters

class CreateServiceChainSpecLink(tables.LinkAction):
    name = "create_scspec_link"
    verbose_name = _("Create Service Chain Spec")
    url = "horizon:project:network_services:create_sc_spec"
    classes = ("ajax-modal","btn-create_scspec")

class EditServiceChainSpecLink(tables.LinkAction):
    name = "edit_sc_spec"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, scspec):
        base_url = reverse("horizon:project:network_services:update_sc_spec", kwargs={'scspec_id': scspec.id})
        return base_url
 
 
class ServiceChainSpecTable(tables.DataTable):
	name = tables.Column("name",
			verbose_name=_("Name"))
	description = tables.Column("description", 
			verbose_name=_("Description"))
	nodes = tables.Column("nodes",
			verbose_name=_("Nodes"),
			filters=(column_filters.list_column_filter,dfilters.unordered_list,))

	class Meta:
		name = "service_chain_spec_table"
		verbose_name = _("Service Chain Specs")
		table_actions = (CreateServiceChainSpecLink,)
		row_actions = (EditServiceChainSpecLink,)


class CreateServiceChainNodeLink(tables.LinkAction):
    name = "create_scnode_link"
    verbose_name = _("Create Service Chain Node")
    url = "horizon:project:network_services:create_sc_spec"
    classes = ("ajax-modal","btn-create_scnode")

class EditServiceChainNodeLink(tables.LinkAction):
    name = "edit_sc_node"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, scnode):
        base_url = reverse("horizon:project:network_services:update_sc_node", kwargs={'scnode_id': scnode.id})
        return base_url
 
class ServiceChainNodeTable(tables.DataTable):
	name = tables.Column("name",
			verbose_name=_("Name"))
	description = tables.Column("description", 
			verbose_name=_("Description"))
	service_type = tables.Column("service_type",
			verbose_name=_("Service Type"))

	class Meta:
		name = "service_chain_node_table"
		verbose_name = _("Service Chain Node") 
		table_actions = (CreateServiceChainNodeLink,)
		row_actions = (EditServiceChainNodeLink,)


class CreateServiceChainInstanceLink(tables.LinkAction):
    name = "create_scinstance_link"
    verbose_name = _("Create Service Chain Instance")
    url = "horizon:project:network_services:create_sc_instance"
    classes = ("ajax-modal","btn-create_scinstance") 

class EditServiceChainInstanceLink(tables.LinkAction):
    name = "edit_sc_instance"
    verbose_name = _("Edit")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, scinstance):
        base_url = reverse("horizon:project:network_services:update_sc_instance", kwargs={'scinstance_id': scinstance.id})
        return base_url
 
class ServiceChainInstanceTable(tables.DataTable):
	name = tables.Column("name",
			verbose_name=_("Name"))
	description = tables.Column("description", 
			verbose_name=_("Description"))

	class Meta:
		name = "service_chain_instance_table"
		verbose_name = _("Service Chain Instance")  
		table_actions = (CreateServiceChainInstanceLink,)
		row_actions = (EditServiceChainInstanceLink,)
