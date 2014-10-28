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
from django.template.defaultfilters import filesizeformat  # noqa
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import workflows

from openstack_dashboard import api
from gbp_ui import client
from openstack_dashboard.dashboards.project.instances import utils
from openstack_dashboard.dashboards.project.images import utils as imageutils

LOG = logging.getLogger(__name__)

class SelectPolicyRuleSetAction(workflows.Action):
    provided_contract = forms.MultipleChoiceField(
        label=_("Provided Policy Rule Set"),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text=_("Choose a policy rule set for an Group.")) 
    consumed_contract = forms.MultipleChoiceField(
        label=_("Consumed Policy Rule Set"),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text=_("Select consumed policy rule set for Group."))
 

    class Meta:
        name = _("Policy Rule Set")
        help_text = _("Select Policy Rule Set for Group.")

    def _contract_list(self,request,tenant_id):
        contracts = client.contract_list(request,
                tenant_id=tenant_id)
        for c in contracts:
                c.set_id_as_name_if_empty()
        contracts = sorted(contracts,
                           key=lambda rule: rule.name)
        return [(c.id, c.name) for c in contracts]

    def populate_provided_contract_choices(self, request, context):
        try:
            tenant_id = self.request.user.tenant_id
            contract_list = self._contract_list(request,tenant_id)
        except Exception as e:
            contract_list = []
            exceptions.handle(request,
                              _('Unable to retrieve policy rule set (%(error)s).')
                              % {'error': str(e)})
        return contract_list
    
    def populate_consumed_contract_choices(self, request, context):
        try:
            tenant_id = self.request.user.tenant_id
            contract_list = self._contract_list(request,tenant_id)
        except Exception as e:
            contract_list = []
            exceptions.handle(request,
                              _('Unable to retrieve policy rule set (%(error)s).')
                              % {'error': str(e)})
        return contract_list 


class SelectL2policyAction(workflows.Action):
    l2policy_id = forms.ChoiceField(
        label=_("Network Policy"),
        required=False,
        help_text=_("Select network policy for Group."))
    network_services_policy_id = forms.ChoiceField(
        label=_("Network Services Policy"),
        required=False,
        help_text=_("Select network services policy for Group.")) 


    class Meta:
        name = _("Network Policy")
        help_text = _("Select network policy for Group. Selecting default will create an Network Policy implicitly.")

    def populate_l2policy_id_choices(self,request,context):
        policies = []
        try:
            policies = client.l2policy_list(request)
            for p in policies:
                p.set_id_as_name_if_empty()
            policies = sorted(policies, key=lambda rule: rule.name)
            policies = [(p.id, p.name+":"+p.id) for p in policies] 
            policies.insert(0,('default','default'))
        except Exception as e:
            exceptions.handle(request,
                              _("Unable to retrieve policies (%(error)s).")
                              % {'error': str(e)})
        return policies
    
    def populate_network_services_policy_id_choices(self,request,context):
        return []

class SelectL2policyStep(workflows.Step):
    action_class = SelectL2policyAction
    name = _("L2 Policy")
    contributes = ("l2policy_id",)

    def contribute(self,data,context):
        if data['l2policy_id'] != 'default':
            context['l2_policy_id'] = data['l2policy_id']
        return context



class SelectPolicyRuleSetStep(workflows.Step):
    action_class = SelectPolicyRuleSetAction
    name = _("Provided Policy Rule Set")
    contributes = ("provided_contracts","consumed_contracts",)

    def contribute(self, data, context):
        if data:
            contracts = self.workflow.request.POST.getlist(
                "provided_contract")
            if contracts:
                contract_dict = {}
                for contract in contracts:
                    if contract != '':
                        contract_dict[contract] = None
                context['provided_contracts'] = contract_dict
            return context



class AddEPGAction(workflows.Action):
    name = forms.CharField(max_length=80,
                           label=_("Name"),
                           required=False)
    description = forms.CharField(max_length=80,
                                  label=_("Description"),
                                  required=False)

    def __init__(self, request, *args, **kwargs):
        super(AddEPGAction, self).__init__(request, *args, **kwargs)

    class Meta:
        name = _("Create Group")
        help_text = _("Create a new Group")


class AddEPGStep(workflows.Step):
    action_class = AddEPGAction
    contributes = ("name", "description")

    def contribute(self, data, context):
        context = super(AddEPGStep, self).contribute(data, context)
        return context


class AddEPG(workflows.Workflow):
    slug = "addepg"
    name = _("Create Group")
    finalize_button_name = _("Create")
    success_message = _('Create Group "%s".')
    failure_message = _('Unable to create Group "%s".')
    success_url = "horizon:project:endpoint_groups:index"
    default_steps = (AddEPGStep,
                     SelectPolicyRuleSetStep,
					 SelectL2policyStep,)

    def format_status_message(self, message):
        return message % self.context.get('name')

    def handle(self, request, context):
		try:
			group = client.epg_create(request, **context)
			return group
		except Exception as e:
			msg = self.format_status_message(self.failure_message) + str(e)
			exceptions.handle(request, msg)
			return False


def _image_choice_title(img):
    gb = filesizeformat(img.size)
    return '%s (%s)' % (img.name or img.id, gb)


class LaunchInstance(workflows.Action):
    availability_zone = forms.ChoiceField(label=_("Availability Zone"), required=False)
    name = forms.CharField(label=_("Instance Name"), max_length=255)
    flavor = forms.ChoiceField(label=_("Flavor"), help_text=_("Size of image to launch."))
    count = forms.IntegerField(label=_("Instance Count"), min_value=1, initial=1, help_text=_("Number of instances to launch."))
    image = forms.ChoiceField(label=_("Select Image"),
            widget=forms.SelectWidget(attrs={'class': 'image-selector'},
                                       data_attrs=('size', 'display-name'),
                                       transform=_image_choice_title))
    
    def __init__(self, request, *args, **kwargs):
        super(LaunchInstance, self).__init__(request, *args, **kwargs)
        tenant_id = request.user.tenant_id
        images = imageutils.get_available_images(request, request.user.tenant_id)
        choices = [(image.id, image) for image in images]
        if choices:
            choices.insert(0, ("", _("Select Image")))
        else:
            choices.insert(0, ("", _("No images available")))
        self.fields['image'].choices = choices
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
        epg_id = self.request.path.split("/")[-2]
        try:
            msg = _('Member was successfully created.')
            ep = client.ep_create(request,endpoint_group_id=epg_id)
            api.nova.server_create(request, 
                    context['name'], 
                    context['image'],
                    context['flavor'],
                    key_name=None,
                    user_data=None,
                    security_groups=None,
                    instance_count=context['count'],
                    nics=[{'port-id':ep.port_id}])
            LOG.debug(msg)
            messages.success(request, msg)
        except Exception as e:
            #msg = _('Failed to update Group %(name)s: %(reason)s' % {'name': name_or_id, 'reason': e})
            msg = _('Failed to launch VM')
            LOG.error(msg)
            redirect = reverse("horizon:project:endpoint_groups:epgdetails", kwargs={'epg_id': epg_id})
            exceptions.handle(request, msg, redirect=redirect) 


class LaunchVMStep(workflows.Step):
    action_class = LaunchInstance
    contributes = ("name", "availability_zone", "flavor", "count", "image")

    def contribute(self, data, context):
        context = super(LaunchVMStep, self).contribute(data, context)
        return context


class CreateVM(workflows.Workflow):
    slug = "launch VM"
    name = _("Create Member")
    
    finalize_button_name = _("Launch")
    success_message = _('Create Member "%s".')
    failure_message = _('Unable to create Member "%s".')
    default_steps = (LaunchVMStep,)
    wizard = True

    def format_status_message(self, message):
        return message % self.context.get('name')
    
    def get_success_url(self):
        epgid = self.request.path.split("/")[-2] #TODO need to find a better way of doing this.
        success_url = reverse("horizon:project:endpoint_groups:epgdetails",kwargs={'epg_id':epgid})
        return success_url
