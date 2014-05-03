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

