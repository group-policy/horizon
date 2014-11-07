import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from django import http
from django.shortcuts import redirect
from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard import api
import json

from gbp_ui import client
LOG = logging.getLogger(__name__)

SERVICE_TYPES = [('LOADBALANCER','Load Balancer'),
				('FIREWALL','Firewall')]

class CreateServiceChainNodeForm(forms.SelfHandlingForm):
	name = forms.CharField(max_length=80, label=_("Name"))
	description = forms.CharField(max_length=80, label=_("Description"), required=False)
	service_type = forms.ChoiceField(label=_("Service Type"),
						choices=SERVICE_TYPES)
	template_file = forms.FileField(label=_('Template File'),
			help_text=_('A local template file to upload.'),required=False)
	template_string = forms.CharField(label=_("Template String"),
			widget=forms.Textarea,required=False)

	def clean(self):
		cleaned_data = super(CreateServiceChainNodeForm, self).clean()
		files = self.request.FILES
		template_str = None
		if files.has_key('template_file'):
			temp = files['template_file'].read()
			try:
				template_str = json.loads(temp)
			except Exception as e:
				msg = _('Invalid file format.')
				raise forms.ValidationError(msg)
		else:
			try:
				tstr = cleaned_data["template_string"]
				if bool(tstr):
					template_str = json.loads(tstr)
			except Exception as e:
				msg = _("Invalid template string.")
				raise forms.ValidationError(msg)
		if template_str is not None:
			cleaned_data['config'] = template_str
		else:
			msg = _("Please choose a template file or enter template string.")
			raise forms.ValidationError(msg)
		return cleaned_data


	def handle(self,request,context):
		url = reverse("horizon:project:network_services:index")
		try:
			try:
				del context['template_string']
				del context['template_file']
			except KeyError:
				pass
			context['config'] = json.dumps(context['config'])
			scnode = client.create_servicechain_node(request,**context)
			msg = _("Service Chain Node Created Successfully!")
			LOG.debug(msg)
			return http.HttpResponseRedirect(url)
		except Exception as e:
			msg = _("Failed to create Service Chain Node.  %s" % str(e))
			LOG.error(msg)
			exceptions.handle(request, msg, redirect=redirect)

class CreateServiceChainSpecForm(forms.SelfHandlingForm):
  	name = forms.CharField(max_length=80, label=_("Name"))
	description = forms.CharField(max_length=80, label=_("Description"), required=False)
	nodes = forms.MultipleChoiceField(label=_("Nodes"))

	def __init__(self,request,*args,**kwargs):
		super(CreateServiceChainSpecForm,self).__init__(request,*args,**kwargs)
		try:
			nodes = client.servicechainnode_list(request)
			nodes = [(item.id,item.name+":"+str(item.id)) for item in nodes]
			self.fields['nodes'].choices = nodes
		except Exception as e:
			msg = _("Failed to retrive service chain nodes.")
			LOG.error(msg)
			exceptions.handle(request, msg, redirect=redirect)

	def handle(self,request,context):
		url = reverse("horizon:project:network_services:index")
 		try:
			sc_spec = client.create_servicechain_spec(request,**context)
			msg = _("Service Chain Spec Created Successfully!")
			LOG.debug(msg)
			return http.HttpResponseRedirect(url)
		except Exception as e:
			msg = _("Failed to create Service Chain Spec.  %s" % str(e))
			LOG.error(msg)
			exceptions.handle(request, msg, redirect=redirect)

class CreateServiceChainInstanceForm(forms.SelfHandlingForm):
  	name = forms.CharField(max_length=80, label=_("Name"))
	description = forms.CharField(max_length=80, label=_("Description"), required=False)
	servicechain_spec = forms.ChoiceField(label=_("ServiceChain Spec"))
	provider_epg = forms.ChoiceField(label=_("Provider EPG"))
	consumer_epg = forms.ChoiceField(label=_("Consumer EPG"))
	classifier = forms.ChoiceField(label=_("Classifier"))

	def __init__(self,request,*args,**kwargs):
		super(CreateServiceChainInstanceForm,self).__init__(request,*args,**kwargs)
		try:
			sc_specs = client.list_servicechain_specs(request)
			epgs = client.epg_list(request)
 			epgs = [(item.id,item.name) for item in epgs]
			classifiers = client.policyclassifier_list(request)
			self.fields['servicechain_spec'].choices = [(item.id,item.name) for item in sc_specs]
			self.fields['provider_epg'].choices = epgs
			self.fields['consumer_epg'].choices = epgs
			self.fields['classifier'].choices = [(item.id,item.name) for item in classifiers] 
		except Exception as e:
			pass

	def handle(self,request,context):
		url = reverse("horizon:project:network_services:index")
 		try:
			sc_spec = client.create_servicechain_spec(request,**context)
			msg = _("Service Chain Instance Created Successfully!")
			LOG.debug(msg)
			return http.HttpResponseRedirect(url)
		except Exception as e:
			msg = _("Failed to create Service Chain Instance.  %s" % str(e))
			LOG.error(msg)
			exceptions.handle(request, msg, redirect=redirect) 
