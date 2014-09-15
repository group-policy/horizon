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

from horizon import tables
from horizon.utils import filters

from openstack_dashboard.dashboards.project.instances.tables import *
import pdb

class UpdateEPGLink(tables.LinkAction):
    name = "updateepg"
    verbose_name = _("Edit EPG")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, epg):
        base_url = reverse("horizon:project:endpoint_groups:updateepg", kwargs={'epg_id': epg.id})
        return base_url


class DeleteEPGLink(tables.DeleteAction):
    name = "deleteepg"
    action_present = _("Delete")
    action_past = _("Scheduled deletion of %(data_type)s")
    data_type_singular = _("EPG")
    data_type_plural = _("EPGs")


class AddEPGLink(tables.LinkAction):
    name = "addepg"
    verbose_name = _("Create EPG")
    url = "horizon:project:endpoint_groups:addepg"
    classes = ("ajax-modal", "btn-addepg",)


class EPGsTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link="horizon:project:endpoint_groups:epgdetails")

    class Meta:
        name = "epgstable"
        verbose_name = _("EPGs")
        table_actions = (AddEPGLink, DeleteEPGLink)
        row_actions = (UpdateEPGLink, DeleteEPGLink)

class LaunchVMLink(tables.LinkAction):
    name = "launch_vm"
    verbose_name = _("Create Member")
    classes = ("ajax-modal", "btn-addvm",)
    
    def get_link_url(self):
        return reverse("horizon:project:endpoint_groups:addvm", kwargs={'epg_id': self.table.kwargs['epg_id']})

class RemoveVMLink(tables.LinkAction):
    name = "delete_vm"
    verbose_name = _("Delete Instance")

    def get_link_url(self,vm):
        return reverse("horizon:project:endpoint_groups:delvm", kwargs={'vmid': vm.id})

class ConsoleLink(tables.LinkAction):
    name = "console"
    verbose_name = _("Console")
    url = "horizon:project:instances:detail"
    classes = ("btn-console",)
    policy_rules = (("compute", "compute_extension:consoles"),)

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, 'tenant_id', None)
        return {"project_id": project_id}

    def allowed(self, request, instance=None):
        # We check if ConsoleLink is allowed only if settings.CONSOLE_TYPE is
        # not set at all, or if it's set to any value other than None or False.
        return bool(getattr(settings, 'CONSOLE_TYPE', True)) and \
            instance.status in ACTIVE_STATES and not is_deleting(instance)

    def get_link_url(self, datum):
        base_url = super(ConsoleLink, self).get_link_url(datum)
        tab_query_string = tabs.ConsoleTab(
            tabs.InstanceDetailTabs).get_query_string()
        return "?".join([base_url, tab_query_string])
 
class CreateContractLink(tables.LinkAction):
     name = "launch_vm"
     verbose_name = _("Create Contract")
     classes = ("ajax-modal", "btn-addvm",)
     
     def get_link_url(self):
        return reverse("horizon:project:endpoint_groups:add_contract", kwargs={'epg_id': self.table.kwargs['epg_id']}) 

class InstancesTable(tables.DataTable):
    name = tables.Column("name", link="horizon:project:instances:detail", verbose_name=_("Instance Name"))
    image_name = tables.Column("image_name", verbose_name=_("Image Name"))
    az = tables.Column("availability_zone", verbose_name=_("Availability Zone"))
    ip = tables.Column(get_ips, verbose_name=_("IP Address"), attrs={'data-type': "ip"})


    class Meta:
        name = "instances"
        verbose_name = _("Members")
        table_actions = (LaunchVMLink,)
        row_actions = (RemoveVMLink,ConsoleLink,)

class ConsumedContractsTable(tables.DataTable):
    name = tables.Column("name",link="horizon:project:contracts:contractdetails",verbose_name=_("Contract Name"))
    description = tables.Column("description",verbose_name=_("Description"))

    class Meta:
        name = 'consumed_contracts'
        verbose_name = _("Consumed Contracts")
        table_actions = (CreateContractLink,)

class ProvidedContractsTable(tables.DataTable):
    name = tables.Column("name", link=("horizon:project:instances:detail"), verbose_name=_("Contract Name"))
    
    class Meta:
        name = 'provided_contracts'
        verbose_name = _("Provided Contracts")
        table_actions = (CreateContractLink,)
