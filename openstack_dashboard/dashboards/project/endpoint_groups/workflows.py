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

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import workflows

from openstack_dashboard import api


class SelectProvidedContractAction(workflows.Action):
    provided_contract = forms.MultipleChoiceField(
        label=_("Provided Contract"),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text=_("Choose a contract for an EPG."))

    class Meta:
        name = _("Provided Contracts")
        help_text = _("Select provided contract for EPG.")

    def populate_provided_contract_choices(self, request, context):
        try:
            tenant_id = self.request.user.tenant_id
            contracts = api.group_policy.contract_list(request,
                tenant_id=tenant_id)
            for c in contracts:
                c.set_id_as_name_if_empty()
            contracts = sorted(contracts,
                           key=lambda rule: rule.name)
            contract_list = [(c.id, c.name) for c in contracts]
        except Exception as e:
            contract_list = []
            exceptions.handle(request,
                              _('Unable to retrieve contracts (%(error)s).')
                              % {'error': str(e)})
        return contract_list


class SelectConsumedContractAction(workflows.Action):
    consumed_contract = forms.MultipleChoiceField(
        label=_("Consumed Contract"),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text=_("Select consumed contract for EPG."))

    class Meta:
        name = _("Consumed Contracts")
        help_text = _("Select consumed contract for EPG.")

    def populate_consumed_contract_choices(self, request, context):
        try:
            tenant_id = self.request.user.tenant_id
            contracts = api.group_policy.contract_list(request,
                tenant_id=tenant_id)
            for c in contracts:
                c.set_id_as_name_if_empty()
            contracts = sorted(contracts,
                           key=lambda rule: rule.name)
            contract_list = [(c.id, c.name) for c in contracts]
        except Exception as e:
            contract_list = []
            exceptions.handle(request,
                              _('Unable to retrieve contracts (%(error)s).')
                              % {'error': str(e)})
        return contract_list


class SelectProvidedContractStep(workflows.Step):
    action_class = SelectProvidedContractAction
    name = _("Provided Contract")
    contributes = ("provided_contracts",)

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


class SelectConsumedContractStep(workflows.Step):
    action_class = SelectConsumedContractAction
    name = _("Consumed Contract")
    contributes = ("consumed_contracts",)

    def contribute(self, data, context):
        if data:
            contracts = self.workflow.request.POST.getlist(
                "consumed_contract")
            if contracts:
                contract_dict = {}
                for contract in contracts:
                    if contract != '':
                        contract_dict[contract] = None
                context['consumed_contracts'] = contract_dict
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
                     SelectProvidedContractStep,
                     SelectConsumedContractStep)
    wizard = True

    def format_status_message(self, message):
        return message % self.context.get('name')

    def handle(self, request, context):
        try:
            api.group_policy.epg_create(request, **context)
            return True
        except Exception as e:
            msg = self.format_status_message(self.failure_message) + str(e)
            exceptions.handle(request, msg)
            return False

class LaunchVM(workflows.Workflow):
    slug = "launch VM"
    name = _("Create Member")
