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
from horizon import tabs

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.contracts import tables

ContractsTable = tables.ContractsTable
PolicyRulesTable = tables.PolicyRulesTable
PolicyClassifiersTable = tables.PolicyClassifiersTable
PolicyActionsTable = tables.PolicyActionsTable


class PolicyActionsTab(tabs.TableTab):
    table_classes = (PolicyActionsTable,)
    name = _("Policy-Actions")
    slug = "policyactions"
    template_name = "horizon/common/_detail_table.html"

    def get_policyactionstable_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            actions = api.group_policy.policyaction_list(
                self.tab_group.request,
                tenant_id=tenant_id)
        except Exception:
            actions = []
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve actions list.'))

        for action in actions:
            action.set_id_as_name_if_empty()

        return actions


class PolicyClassifiersTab(tabs.TableTab):
    table_classes = (PolicyClassifiersTable,)
    name = _("Policy-Classifiers")
    slug = "policyclassifiers"
    template_name = "horizon/common/_detail_table.html"

    def get_policyclassifierstable_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            classifiers = api.group_policy.policyclassifier_list(
                self.tab_group.request,
                tenant_id=tenant_id)
        except Exception:
            classifiers = []
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve classifier list.'))

        for classifier in classifiers:
            classifier.set_id_as_name_if_empty()

        return classifiers


class PolicyRulesTab(tabs.TableTab):
    table_classes = (PolicyRulesTable,)
    name = _("Policy-Rules")
    slug = "policyrules"
    template_name = "horizon/common/_detail_table.html"

    def get_policyrulestable_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            policy_rules = api.group_policy.policyrule_list(
                self.tab_group.request,
                tenant_id=tenant_id)
        except Exception:
            policy_rules = []
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve policy-rule list.'))

        for rule in policy_rules:
            rule.set_id_as_name_if_empty()

        return policy_rules


class ContractsTab(tabs.TableTab):
    table_classes = (ContractsTable,)
    name = _("Contracts")
    slug = "contracts"
    template_name = "horizon/common/_detail_table.html"

    def get_contractstable_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            contracts = api.group_policy.contract_list(self.tab_group.request,
                                                       tenant_id=tenant_id)
        except Exception:
            contracts = []
            exceptions.handle(self.tab_group.request,
                              _('Unable to retrieve contract list.'))

        for contract in contracts:
            contract.set_id_as_name_if_empty()

        return contracts


class ContractTabs(tabs.TabGroup):
    slug = "contracttabs"
    tabs = (ContractsTab,
            PolicyRulesTab,
            PolicyClassifiersTab,
            PolicyActionsTab)
    sticky = True
