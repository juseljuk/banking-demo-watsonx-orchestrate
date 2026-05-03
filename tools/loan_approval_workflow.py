"""
Loan Approval Workflow using standalone Cloudant-backed Python tools.

Flow:
1. Check credit score
2. Calculate debt-to-income ratio
3. Assess eligibility with explicit mapped inputs
4. Branch:
   - Eligible -> generate loan offers -> approved result
   - Not eligible -> rejected result
"""

from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import (
    Flow, flow, START, END, Branch
)


class LoanApplicationInput(BaseModel):
    """Input for the loan approval workflow."""

    customer_id: str = Field(description="Customer identifier (e.g., CUST-001)")
    loan_amount: float = Field(description="Requested loan amount in GBP")
    loan_purpose: str = Field(
        description="Purpose of the loan (e.g., 'Home Improvements', 'Vehicle Purchase')"
    )


class LoanApprovalOutput(BaseModel):
    """Output from the loan approval workflow."""

    status: str = Field(description="Workflow status: 'approved' or 'rejected'")
    customer_id: str = Field(description="Customer identifier")
    loan_amount: float = Field(description="Requested loan amount")
    decision: str = Field(description="Decision explanation")
    offers: list = Field(default=[], description="Loan offers if approved")
    next_steps: str = Field(description="What the customer should do next")


@flow(
    name="loan_approval_workflow",
    description="Deterministic loan approval workflow using standalone Cloudant-backed Python tools",
    input_schema=LoanApplicationInput,
    output_schema=LoanApprovalOutput,
)
def build_loan_approval_workflow(aflow: Flow) -> Flow:
    """
    Deterministic workflow for loan approval using standalone imported tools.

    Flow:
    1. Check credit score
    2. Calculate debt-to-income ratio
    3. Assess eligibility using explicit values from prior steps
    4. If eligible, generate offers and return approval
    5. If not eligible, return rejection with reasons
    """

    check_credit_score_node = aflow.tool("check_credit_score")
    check_credit_score_node.map_input(
        input_variable="customer_id",
        expression="flow.input.customer_id",
    )

    calculate_dti_node = aflow.tool("calculate_debt_to_income")
    calculate_dti_node.map_input(
        input_variable="customer_id",
        expression="flow.input.customer_id",
    )

    assess_eligibility_node = aflow.tool("calculate_loan_eligibility")
    assess_eligibility_node.map_input(
        input_variable="customer_id",
        expression="flow.input.customer_id",
    )
    assess_eligibility_node.map_input(
        input_variable="loan_amount",
        expression="flow.input.loan_amount",
    )
    assess_eligibility_node.map_input(
        input_variable="loan_purpose",
        expression="flow.input.loan_purpose",
    )
    assess_eligibility_node.map_input(
        input_variable="credit_score",
        expression="parent.check_credit_score_node.output.credit_score",
    )
    assess_eligibility_node.map_input(
        input_variable="debt_to_income_ratio",
        expression="parent.calculate_dti_node.output.debt_to_income_ratio",
    )

    eligibility_branch: Branch = aflow.branch(
        evaluator='flow["calculate_loan_eligibility"].output.eligible == True'  # pyright: ignore[reportArgumentType]
    )

    generate_offers_node = aflow.tool("generate_loan_offers")
    generate_offers_node.map_input(
        input_variable="customer_id",
        expression="flow.input.customer_id",
    )
    generate_offers_node.map_input(
        input_variable="loan_amount",
        expression="flow.input.loan_amount",
    )
    generate_offers_node.map_input(
        input_variable="credit_score",
        expression="parent.check_credit_score_node.output.credit_score",
    )

    approved_result_node = aflow.script(
        name="approved_result_node",
        script="""
try:
    offers = parent.generate_offers_node.output.offers
except:
    offers = []

try:
    decision = parent.assess_eligibility_node.output.reason
except:
    decision = "Application meets eligibility criteria. Loan offers generated successfully."

result = {
    "status": "approved",
    "customer_id": parent.input.customer_id,
    "loan_amount": parent.input.loan_amount,
    "decision": decision,
    "offers": offers,
    "next_steps": "Review the available loan offers and select the preferred option."
}
""",
    )

    rejected_result_node = aflow.script(
        name="rejected_result_node",
        script="""
try:
    decision = parent.assess_eligibility_node.output.reason
except:
    decision = "Application does not meet eligibility criteria."

result = {
    "status": "rejected",
    "customer_id": parent.input.customer_id,
    "loan_amount": parent.input.loan_amount,
    "decision": decision,
    "offers": [],
    "next_steps": "Explain the rejection reason to the customer and discuss alternative options."
}
""",
    )

    aflow.edge(START, check_credit_score_node)
    aflow.edge(check_credit_score_node, calculate_dti_node)
    aflow.edge(calculate_dti_node, assess_eligibility_node)
    aflow.edge(assess_eligibility_node, eligibility_branch)

    eligibility_branch.case(True, generate_offers_node)
    aflow.edge(generate_offers_node, approved_result_node)
    aflow.edge(approved_result_node, END)

    eligibility_branch.case(False, rejected_result_node)
    aflow.edge(rejected_result_node, END)

    return aflow


# Made with Bob