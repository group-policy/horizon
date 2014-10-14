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

from django import http
from django.shortcuts import redirect
from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard import api

LOG = logging.getLogger(__name__)


class UpdateEPGForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=80, label=_("Name"), required=False)
    description = forms.CharField(max_length=80, label=_("Description"), required=False)
    provided_contracts = forms.MultipleChoiceField(label=_("Provided Contracts"),required=False)
    consumed_contracts = forms.MultipleChoiceField(label=_("Consumed Contracts"),required=False)
    failure_url = 'horizon:project:endpoint_groups:index'

    def __init__(self, request, *args, **kwargs):
        super(UpdateEPGForm, self).__init__(request, *args, **kwargs)
        try:
            epg_id = self.initial['epg_id']
            epg = api.group_policy.epg_get(request, epg_id)
            self.fields['name'].initial = epg.name
            self.fields['description'].initial = epg.description
            provided = [api.group_policy.contract_get(request,item) for item in epg.provided_contracts]
            consumed = [api.group_policy.contract_get(request,item) for item in epg.consumed_contracts]
            self.fields['provided_contracts'].initial = provided
            self.fields['consumed_contracts'].initial = consumed
            tenant_id = self.request.user.tenant_id
            contracts = api.group_policy.contract_list(request, tenant_id=tenant_id)
            for c in contracts:
                c.set_id_as_name_if_empty()
            contracts = sorted(contracts, key=lambda rule: rule.name)
            contract_list = [(c.id, c.name) for c in contracts] 
            self.fields['provided_contracts'].choices = contract_list
            self.fields['consumed_contracts'].choices = contract_list
        except Exception as e:
            exceptions.handle(request, _('Unable to retrieve contract details.'))
            pass

    def handle(self, request, context):
        epg_id = self.initial['epg_id']
        name_or_id = context.get('name') or epg_id
        try:
            context['provided_contracts'] = dict([(i,'string') for i in context['provided_contracts']])
            context['consumed_contracts'] = dict([(i,'string') for i in context['consumed_contracts']])
            epg = api.group_policy.epg_update(request, epg_id, **context)
            msg = _('EPG %s was successfully updated.') % name_or_id
            LOG.debug(msg)
            messages.success(request, msg)
            return epg
        except Exception as e:
            msg = _('Failed to update EPG %(name)s: %(reason)s' % {'name': name_or_id, 'reason': e})
            LOG.error(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)

class CreateContractForm(forms.SelfHandlingForm):
    #This function does Add Provided contracts to EPG
    contract = forms.MultipleChoiceField(label=_("Provided Contracts"),)
    
    def __init__(self, request, *args, **kwargs):
        super(CreateContractForm, self).__init__(request, *args, **kwargs)
        contracts = []
        try:
            tenant_id = self.request.user.tenant_id
            epg_id = kwargs['initial']['epg_id']
            epg = api.group_policy.epg_get(request, epg_id)
            providedcontracts = epg.get("provided_contracts") 
            items = api.group_policy.contract_list(request, tenant_id=tenant_id)
            contracts = [(p.id,p.name) for p in items if p.id not in providedcontracts]
        except Exception as e:
            pass
        self.fields['contract'].choices = contracts
    
    def handle(self,request,context):
        epg_id = self.initial['epg_id']
        epg = api.group_policy.epg_get(request, epg_id)
        url = reverse("horizon:project:endpoint_groups:epgdetails", kwargs={'epg_id': epg_id})
        try:
            for contract in epg.get("provided_contracts"):
                context['contract'].append(contract)
            contracts = dict([(item,'string') for item in context['contract']])
            api.group_policy.epg_update(request,epg_id,provided_contracts=contracts)
            msg = _('Contract added successfully!')
            messages.success(request, msg)
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception:
            msg = _('Failed to add contract!')
            redirect = reverse("horizon:project:endpoint_groups:epgdetails", kwargs={'epg_id': epg_id})
            LOG.error(msg)
            exceptions.handle(request, msg, redirect=redirect)

class RemoveContractForm(forms.SelfHandlingForm):
    contract = forms.MultipleChoiceField(label=_("Provided Contracts"),)
    
    def __init__(self, request, *args, **kwargs):
        super(RemoveContractForm, self).__init__(request, *args, **kwargs)
        contracts = []
        try:
            tenant_id = self.request.user.tenant_id
            epg_id = kwargs['initial']['epg_id']
            epg = api.group_policy.epg_get(request, epg_id)
            providedcontracts = epg.get("provided_contracts") 
            items = api.group_policy.contract_list(request, tenant_id=tenant_id)
            contracts = [(p.id,p.name) for p in items if p.id in providedcontracts] 
        except Exception as e:
            pass
        self.fields['contract'].choices = contracts
    
    def handle(self,request,context):
        epg_id = self.initial['epg_id']
        url = reverse("horizon:project:endpoint_groups:epgdetails", kwargs={'epg_id': epg_id})
        try:
            epg = api.group_policy.epg_get(request, epg_id)
            old_contracts = epg.get("provided_contracts")
            for contract in context['contract']:
                old_contracts.remove(contract)
            contracts = dict([(item,'string') for item in old_contracts])
            api.group_policy.epg_update(request,epg_id,provided_contracts=contracts)
            msg = _('Contract removed successfully!')
            messages.success(request, msg)
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception:
            msg = _('Failed to remove contract!')
            redirect = reverse("horizon:project:endpoint_groups:epgdetails", kwargs={'epg_id': epg_id})
            LOG.error(msg) 
            exceptions.handle(request, msg, redirect=redirect)

class AddConsumedForm(forms.SelfHandlingForm):
    contract = forms.MultipleChoiceField(label=_("Consumed Contracts"),)
    
    def __init__(self, request, *args, **kwargs):
        super(AddConsumedForm, self).__init__(request, *args, **kwargs)
        contracts = []
        try:
            tenant_id = self.request.user.tenant_id
            epg_id = kwargs['initial']['epg_id']
            epg = api.group_policy.epg_get(request, epg_id)
            consumedcontracts = epg.get("consumed_contracts")             
            items = api.group_policy.contract_list(request, tenant_id=tenant_id)
            contracts = [(p.id,p.name) for p in items if p.id not in consumedcontracts]
        except Exception as e:
            pass
        self.fields['contract'].choices = contracts
    
    def handle(self,request,context):
        epg_id = self.initial['epg_id']
        url = reverse("horizon:project:endpoint_groups:epgdetails", kwargs={'epg_id': epg_id})
        try:
            epg = api.group_policy.epg_get(request, epg_id)
            for contract in epg.get("consumed_contracts"):
                context['contract'].append(contract)
            consumed = dict([(item,'string') for item in context['contract']])
            api.group_policy.epg_update(request,epg_id,consumed_contracts=consumed)
            msg = _('Contract Added successfully!')
            messages.success(request, msg)
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception:
            msg = _('Failed to add contract!')
            redirect = reverse("horizon:project:endpoint_groups:epgdetails", kwargs={'epg_id': epg_id})
            LOG.error(msg)  
            exceptions.handle(request, msg, redirect=redirect)

class RemoveConsumedForm(forms.SelfHandlingForm):
    contract = forms.MultipleChoiceField(label=_("Consumed Contracts"),)
    
    def __init__(self, request, *args, **kwargs):
        super(RemoveConsumedForm, self).__init__(request, *args, **kwargs)
        contracts = []
        try:
            tenant_id = self.request.user.tenant_id
            epg_id = kwargs['initial']['epg_id']
            epg = api.group_policy.epg_get(request, epg_id)
            consumedcontracts = epg.get("consumed_contracts") 
            items = api.group_policy.contract_list(request, tenant_id=tenant_id)
            contracts = [(p.id,p.name) for p in items if p.id in consumedcontracts]
        except Exception as e:
            pass
        self.fields['contract'].choices = contracts
    
    def handle(self,request,context):
        epg_id = self.initial['epg_id']
        url = reverse("horizon:project:endpoint_groups:epgdetails", kwargs={'epg_id': epg_id})
        try:
            epg = api.group_policy.epg_get(request, epg_id)
            old_contracts = epg.get("consumed_contracts")
            for contract in context['contract']:
                old_contracts.remove(contract)
            consumed = dict([(item,'string') for item in old_contracts])
            api.group_policy.epg_update(request,epg_id,consumed_contracts=consumed)
            msg = _('Contract removed successfully!')
            messages.success(request, msg)
            LOG.debug(msg)
            return http.HttpResponseRedirect(url)
        except Exception:
			msg = _('Failed to remove contract!')
			redirect = url
			LOG.error(msg)   
			exceptions.handle(request, msg, redirect=redirect)

class AddL2PolicyForm(forms.SelfHandlingForm):
	name = forms.CharField(max_length=80, label=_("Name"), required=False)
	description = forms.CharField(max_length=80, label=_("Description"), required=False)
	l3_policy_id = forms.ChoiceField(label=_("L3 Policy"),required=False)

	def __init__(self,request,*args,**kwargs):
		super(AddL2PolicyForm,self).__init__(request, *args, **kwargs)
		try:
			policies = api.group_policy.l3policy_list(request)
			policies = [(item['id'],item['name']+":"+item['id']) for item in policies]
			self.fields['l3_policy_id'].choices = policies
		except Exception as e:
			msg = _("Failed to get L3 policy list")
			LOG.error(msg)
			exceptions.handle(request, msg, redirect=redirect)


	def handle(self, request, context):
		url = reverse("horizon:project:endpoint_groups:index")
		try:
			l2_policy = api.group_policy.l2policy_create(request,**context)
			msg = _("L2 Policy Created Successfully!")
			LOG.debug(msg)
			return http.HttpResponseRedirect(url)
		except Exception as e:
			print e
			msg = _("Failed to create L2 policy")
			LOG.error(msg)
			exceptions.handle(request, msg, redirect=redirect)

class AddL3PolicyForm(forms.SelfHandlingForm):
 	name = forms.CharField(max_length=80, label=_("Name"))
	description = forms.CharField(max_length=80, label=_("Description"), required=False)
	ip_version = forms.ChoiceField(choices=[(4, 'IPv4'), (6, 'IPv6')],
								widget=forms.Select(attrs={
                                  'class': 'switchable',
                                  'data-slug': 'ipversion',
                                }), label=_("IP Version")) 
	ip_pool = forms.IPField(label=_("IP Pool"),
									initial="",
									help_text=_("IP Pool"),
									version=forms.IPv4 | forms.IPv6,
									mask=True) 
	subnet_prefix_length = forms.CharField(max_length=80,
									label=_("Subnet Prefix Length"),
									help_text=_("Between 2-30 for IP4 and 2-127 for IP6."),)

	def __init__(self,request,*args,**kwargs):
		super(AddL3PolicyForm,self).__init__(request,*args,**kwargs)

	def clean(self):
		cleaned_data = super(AddL3PolicyForm, self).clean()
		if self.is_valid():
			ipversion = int(cleaned_data['ip_version'])
			subnet_prefix_length = int(cleaned_data['subnet_prefix_length'])
			msg = _("Subnet prefix out of range.")
			if ipversion == 4 and subnet_prefix_length not in range(2,31):
				raise forms.ValidationError(msg)
			if ipversion == 6 and subnet_prefix_length not in range(2,128):
				raise forms.ValidationError(msg)
		return cleaned_data
	
	def handle(self,request,context):
		url = reverse("horizon:project:endpoint_groups:index")
 		try:
			l3_policy = api.group_policy.l3policy_create(request,**context)
			msg = _("L3 Policy Created Successfully!")
			LOG.debug(msg)
			return http.HttpResponseRedirect(url)
		except Exception:
			msg = _("Failed to create L3 policy")
			LOG.error(msg)
			exceptions.handle(request, msg, redirect=redirect)
 