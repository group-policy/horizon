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


class UpdateEPGLink(tables.LinkAction):
    name = "updateepg"
    verbose_name = _("Edit EPG")
    classes = ("ajax-modal", "btn-update",)

    def get_link_url(self, epg):
        base_url = reverse("horizon:project:endpoint_groups:updateepg",
                           kwargs={'epg_id': epg.id})
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
