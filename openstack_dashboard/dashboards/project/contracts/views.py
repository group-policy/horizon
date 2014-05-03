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

from horizon import tabs
from horizon import workflows

from openstack_dashboard.dashboards.project.contracts \
    import tabs as contract_tabs
from openstack_dashboard.dashboards.project.contracts \
    import workflows as contract_workflows

ContractTabs = contract_tabs.ContractTabs

AddContract = contract_workflows.AddContract
AddPolicyRule = contract_workflows.AddPolicyRule
AddPolicyClassifier = contract_workflows.AddPolicyClassifier
AddPolicyAction = contract_workflows.AddPolicyAction


class IndexView(tabs.TabView):
    tab_group_class = (ContractTabs)
    template_name = 'project/contracts/details_tabs.html'


class AddContractView(workflows.WorkflowView):
    workflow_class = AddContract
    template_name = "project/contracts/addcontract.html"


class AddPolicyRuleView(workflows.WorkflowView):
    workflow_class = AddPolicyRule
    template_name = "project/contracts/addpolicyrule.html"


class AddPolicyClassifierView(workflows.WorkflowView):
    workflow_class = AddPolicyClassifier
    template_name = "project/contracts/addpolicyclassifier.html"


class AddPolicyActionView(workflows.WorkflowView):
    workflow_class = AddPolicyAction
    template_name = "project/contracts/addpolicyaction.html"


class ContractDetailsView(tabs.TabView):
    #tab_group_class = (EPGDetailsTabs)
    template_name = 'project/contracts/details_tabs.html'


class PolicyRuleDetailsView(tabs.TabView):
    #tab_group_class = (EPGDetailsTabs)
    template_name = 'project/contracts/details_tabs.html'


class PolicyClassifierDetailsView(tabs.TabView):
    #tab_group_class = (EPGDetailsTabs)
    template_name = 'project/contracts/details_tabs.html'


class PolicyActionDetailsView(tabs.TabView):
    #tab_group_class = (EPGDetailsTabs)
    template_name = 'project/contracts/details_tabs.html'
