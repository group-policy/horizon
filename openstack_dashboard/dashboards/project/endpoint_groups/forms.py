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

import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard import api

LOG = logging.getLogger(__name__)
from openstack_dashboard.dashboards.project.instances import utils


class UpdateEPG(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80,
                           label=_("Name"),
                           required=False)
    description = forms.CharField(max_length=80,
                                  label=_("Description"),
                                  required=False)
    #l2_policy_id = forms.ChoiceField(label=_("L2 Policy"), required=False)
    provided_contracts = forms.ChoiceField(
        label=_("Provided Contracts"), required=False)
    consumed_contracts = forms.ChoiceField(
        label=_("Consumed Contracts"), required=False)

    failure_url = 'horizon:project:endpoint_groups:index'

    def __init__(self, request, *args, **kwargs):
        super(UpdateEPG, self).__init__(request, *args, **kwargs)

        try:
            tenant_id = self.request.user.tenant_id
            #l2_pol_id = api.group_policy.l2policy_list(request, tenant_id=tenant_id)
            provided_contracts = api.group_policy.contract_list(request,
                                                                tenant_id=tenant_id)
            consumed_contracts = api.group_policy.contract_list(request,
                                                                tenant_id=tenant_id)
        except Exception:
            exceptions.handle(request,
                              _('Unable to retrieve EPG info.'))
            provided_contracts = []
            consumed_contracts = []

        #TODO - (Ronak)

    def handle(self, request, context):
        epg_id = self.initial['epg_id']
        name_or_id = context.get('name') or epg_id
        try:
            epg = api.group_policy.epg_update(request, epg_id,
                                              **context)
            msg = _('EPG %s was successfully updated.') % name_or_id
            LOG.debug(msg)
            messages.success(request, msg)
            return epg
        except Exception as e:
            msg = _('Failed to update EPG %(name)s: %(reason)s' %
                    {'name': name_or_id, 'reason': e})
            LOG.error(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)

class CreateVM(forms.SelfHandlingForm):
    availability_zone = forms.ChoiceField(label=_("Availability Zone"), required=False)
    name = forms.CharField(label=_("Instance Name"), max_length=255)
    flavor = forms.ChoiceField(label=_("Flavor"), help_text=_("Size of image to launch."))
    count = forms.IntegerField(label=_("Instance Count"), min_value=1, initial=1, help_text=_("Number of instances to launch."))
    source_type = forms.ChoiceField(label=_("Instance Boot Source"),
                                           widget=forms.Select(attrs={ 'class': 'switchable', 'data-slug': 'source'}),
                                           help_text=_("Choose Your Boot Source Type."))
    #instance_snapshot_id = forms.ChoiceField(label=_("Instance Snapshot"), required=False)
    
    def __init__(self, request, *args, **kwargs):
        super(CreateVM, self).__init__(request, *args, **kwargs)
        tenant_id = request.user.tenant_id
        source_type_choices = [
            ('', _("Select source")),
            ("image_id", _("Boot from image")),
            ("instance_snapshot_id", _("Boot from snapshot")),
        ]
        source_type_choices.append(("volume_id", _("Boot from volume")))
        try:
            if api.nova.extension_supported("BlockDeviceMappingV2Boot", request):
                source_type_choices.append(("volume_image_id", _("Boot from image (creates a new volume)")))
        except Exception:
            exceptions.handle(request, _('Unable to retrieve extensions information.'))
            source_type_choices.append(("volume_snapshot_id", _("Boot from volume snapshot (creates a new volume)")))
        self.fields['source_type'].choices = source_type_choices
        self.fields['availability_zone'].choices = self._availability_zone_choices(request)
        self.fields['flavor'].choices = self._flavor_choices(request)


    def _flavor_choices(self, request):
        flavors = utils.flavor_list(request)
        if flavors:
            return utils.sort_flavor_list(request, flavors)
        return []

    def _availability_zone_choices(self, request):
        try:
            zones = api.nova.availability_zone_list(request)
        except Exception:
            zones = []
            exceptions.handle(request, _('Unable to retrieve availability zones.'))
        zone_list = [(zone.zoneName, zone.zoneName) for zone in zones if zone.zoneState['available']]
        zone_list.sort()
        if not zone_list:
            zone_list.insert(0, ("", _("No availability zones found")))
        elif len(zone_list) > 1:
            zone_list.insert(0, ("", _("Any Availability Zone")))
        return zone_list
    
    def handle(self, request, context):
        print context
        epg_id = self.request.path.split("/")[-2]
        try:
            print "====== port id =========="
            msg = _('Instance was successfully launched.')
            ep = api.group_policy.ep_create(request,endpoint_group_id=epg_id)
            """========== create the VM here ============"""
            api.nova.server_create(request, 
                    context['name'], 
                    context['flavor'],
                    instance_count=context['count'],
                    nics=[{'port-id':ep.port_id}])
            LOG.debug(msg)
            messages.success(request, msg)
        except Exception as e:
            #msg = _('Failed to update EPG %(name)s: %(reason)s' % {'name': name_or_id, 'reason': e})
            msg = _('Failed to launch VM')
            LOG.error(msg)
            redirect = reverse("horizon:project:endpoint_groups:epgdetails", kwargs={'epg_id': epg_id})
            exceptions.handle(request, msg, redirect=redirect) 

class DeleteVM(forms.SelfHandlingForm):
    def handle(self,request,context):
        pass

