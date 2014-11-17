import logging
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from gbp_ui import client

LOG = logging.getLogger(__name__)


def list_column_filter(items):
	if len(items) == 0:
		return ""
	return items

def update_pruleset_attributes(request,prset):
	rules = prset.policy_rules
	url = "horizon:project:application_policy:policyruledetails"
	value = ["<ul>"]
	li = lambda x: "<li><a href='"+reverse(url,kwargs={'policyrule_id':x.id})+"'>"+x.name+"</a></li>"
	for rule in rules:
		r = client.policyrule_get(request,rule)
		value.append(li(r))
	value.append("</ul>")
	value = "".join(value)
	setattr(prset,'policy_rules',mark_safe(value))
	return prset

def update_epg_attributes(request,epg):
 	url = "horizon:project:application_policy:policy_rule_set_details"
	provided = epg.provided_contracts
	consumed = epg.consumed_contracts
	provided = [client.contract_get(request,item) for item in provided]
	consumed = [client.contract_get(request,item) for item in consumed]
	p = ["<ul>"]
	li = lambda x: "<li><a href='"+reverse(url,kwargs={'contract_id':x.id})+"'>"+x.name+"</a></li>"
	for item in provided:
		p.append(li(item))
	p.append("</ul>")
	p = "".join(p)
	c = ["<ul>"]
	for item in consumed:
		c.append(li(item))
	c.append("</ul>")
	c = "".join(c)
	consumed = [item.name for item in consumed]
	setattr(epg,'provided_contracts',mark_safe(p))
	setattr(epg,'consumed_contracts',mark_safe(c))
	l2url = "horizon:project:network_policy:l2policy_details"
	if epg.l2_policy_id is not None:
		policy = client.l2policy_get(request,epg.l2_policy_id)
		atag  = mark_safe("<a href='"+reverse(l2url,kwargs={'l2policy_id':policy.id})+"'>"+policy.name+"</a>")
		setattr(epg,'l2_policy_id',atag)
	return epg

def update_policyrule_attributes(request,prule):
	url = "horizon:project:application_policy:policyclassifierdetails"
	classifier_id = prule.policy_classifier_id
	classifier = client. policyclassifier_get(request,classifier_id)
	tag = mark_safe("<a href='"+reverse(url,kwargs={'policyclassifier_id':classifier.id})+"'>"+classifier.name+"</a>")
	setattr(prule,'policy_classifier_id',tag)
	return prule

def update_sc_spec_attributes(request,scspec):
	nodes = scspec.nodes
	nodes = [client.get_servicechain_node(request,item) for item in nodes]
	value = ["<table class='table table-condensed'><tr><td><span class='glyphicon glyphicon-remove-circle'></span></td>"]
	for n in nodes:
		value.append("<td><span class='glyphicon glyphicon-arrow-right'></span></td>")
		value.append("<td>"+n.name+"("+n.service_type+")</td>")
	value.append("</tr></table>")
	setattr(scspec,'nodes',mark_safe("".join(value)))
	return scspec                                                
