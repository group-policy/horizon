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

class CreateServiceChainNodeForm(forms.SelfHandlingForm):
	name = forms.CharField(max_length=80, label=_("Name"))
	description = forms.CharField(max_length=80, label=_("Description"), required=False)
	service_type = forms.CharField(max_length=80, label=_("Service Type"))
	template_file = forms.FileField(label=_('Template File'),
			help_text=_('A local template to upload.'),required=False)
	template_string = forms.CharField(label=_("Template String"),
			widget=forms.Textarea,required=False)

	def clean(self):
		cleaned_data = super(CreateServiceChainNodeForm, self).clean()
		files = self.request.FILES
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
				temp = json.loads(tstr)
			except Exception as e:
				msg = _("Invalid json format")
				raise forms.ValidationError(msg)
		return cleaned_data


	def handle(self,request,context):
		url = reverse("horizon:project:network_services:index")
		try:
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
	nodes = forms.CharField(max_length=80, label=_("Nodes"))

	def __init__(self,request,*args,**kwargs):
		super(CreateServiceChainSpecForm,self).__init__(request,*args,**kwargs)

	def handle(self,request,context):
		url = reverse("horizon:project:network_services:index")
 		try:
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
	nodes = forms.CharField(max_length=80, label=_("Nodes"))

	def __init__(self,request,*args,**kwargs):
		super(CreateServiceChainInstanceForm,self).__init__(request,*args,**kwargs)

	def handle(self,request,context):
		url = reverse("horizon:project:network_services:index")
 		try:
			msg = _("Service Chain Instance Created Successfully!")
			LOG.debug(msg)
			return http.HttpResponseRedirect(url)
		except Exception as e:
			msg = _("Failed to create Service Chain Instance.  %s" % str(e))
			LOG.error(msg)
			exceptions.handle(request, msg, redirect=redirect) 
