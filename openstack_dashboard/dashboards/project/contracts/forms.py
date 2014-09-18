from django.core.urlresolvers import reverse
from django.template.defaultfilters import filesizeformat  # noqa
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables  # noqa
from django import http

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import validators

from openstack_dashboard import api

class UpdateContractForm(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))
    description = forms.CharField(label=_("Description"),required=False)
    rules = forms.MultipleChoiceField(label=_("Policy Rules"),)

    def __init__(self, request, *args, **kwargs):
        super(UpdateContractForm, self).__init__(request, *args, **kwargs)
        rules = []
        try:
            items = api.group_policy.policyrule_list(request)
            rules = [(p.id,p.name) for p in items]
            contract = api.group_policy.contract_get(request, self.initial['contract_id'])
            if contract:
                self.fields['name'].initial = contract.name
                self.fields['description'].initial = contract.description
                existing = [item for item in contract.policy_rules]
                self.fields['rules'].initial = existing
        except Exception as e:
            exceptions.handle(request, _('Unable to retrieve policy rules'))
        self.fields['rules'].choices = rules
    
    def handle(self,request,context):
        try:
            contract_id = self.initial['contract_id']
            con = api.group_policy.contract_update(request, 
                                                  contract_id,
                                                  name=context['name'],
                                                  description=context['description'],
                                                  policy_rules=context['rules'],
                                                  )
            messages.success(request, _('Contract successfully updated.'))
            url = reverse('horizon:project:contracts:index')
            return http.HttpResponseRedirect(url)
        except Exception as e:
            redirect = reverse('horizon:project:contracts:index')
            exceptions.handle(request, _("Unable to update contract."), redirect=redirect)

class UpdatePolicyActionForm(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))
    description = forms.CharField(label=_("Description"),required=False)
    action_type = forms.ChoiceField(label=_("Action"))
    action_value = forms.CharField(label=_("Action Value"),required=False)

    def __init__(self, request, *args, **kwargs):
        super(UpdatePolicyActionForm, self).__init__(request, *args, **kwargs)

        try:
            policyaction_id = self.initial['policyaction_id']
            pa = api.group_policy.policyaction_get(request, policyaction_id)
            self.fields['name'].initial = pa.name
            self.fields['action_value'].initial = pa.action_value
            self.fields['action_type'].initial = pa.action_type
        except Exception as e:
            pass
        self.fields['action_type'].choices = [('allow', _('ALLOW')), ('redirect', _('REDIRECT'))]
    
    def handle(self,request,context):
        url = reverse('horizon:project:contracts:index')
        try:
            policyaction_id = self.initial['policyaction_id']
            messages.success(request, _('Policy Action successfully updated.'))
            return http.HttpResponseRedirect(url)
        except Exception as e:
            exceptions.handle(request, _("Unable to update policy action."), redirect=url)
