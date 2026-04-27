"""
Loan Approval Workflow - Agentic Workflow Example
Demonstrates deterministic multi-step loan processing with branching logic
"""

from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import (
    Flow, flow, START, END, Branch
)


# Input/Output Schemas
class LoanApplicationInput(BaseModel):
    """Input for loan approval workflow"""
    customer_id: str = Field(description="Customer identifier (e.g., CUST-001)")
    loan_amount: float = Field(description="Requested loan amount in GBP")
    loan_purpose: str = Field(description="Purpose of the loan (e.g., 'Home Improvements', 'Vehicle Purchase')")


class LoanApprovalOutput(BaseModel):
    """Output from loan approval workflow"""
    status: str = Field(description="Workflow status: 'approved', 'rejected', 'manual_review'")
    customer_id: str = Field(description="Customer identifier")
    loan_amount: float = Field(description="Requested loan amount")
    decision: str = Field(description="Detailed decision explanation")
    offers: list = Field(default=[], description="List of loan offers if approved")
    next_steps: str = Field(description="What the customer should do next")


@flow(
    name="loan_approval_workflow",
    description="Automated loan approval workflow with credit checks, eligibility assessment, and offer generation",
    input_schema=LoanApplicationInput,
    output_schema=LoanApprovalOutput
)
def build_loan_approval_workflow(aflow: Flow) -> Flow:
    """
    Deterministic loan approval workflow that:
    1. Checks customer credit score
    2. Calculates debt-to-income ratio
    3. Assesses loan eligibility
    4. Branches based on eligibility:
       - If eligible: Generate loan offers
       - If not eligible: Return rejection with reasons
    5. Returns structured decision
    
    This workflow demonstrates:
    - Sequential tool execution
    - Conditional branching based on business rules
    - Integration with existing MCP tools
    - Structured output for downstream processing
    """
    
    # Step 1: Check Credit Score
    # Use tool name as string (the tool must be imported first)
    check_credit_node = aflow.tool("loan-processing:check_credit_score")
    check_credit_node.map_input(input_variable="customer_id", expression="flow.input.customer_id")
    
    # Step 2: Calculate Debt-to-Income Ratio
    calculate_dti_node = aflow.tool("loan-processing:calculate_debt_to_income")
    calculate_dti_node.map_input(input_variable="customer_id", expression="flow.input.customer_id")
    
    # Step 3: Assess Eligibility
    assess_eligibility_node = aflow.tool("loan-processing:calculate_loan_eligibility")
    assess_eligibility_node.map_input(input_variable="customer_id", expression="flow.input.customer_id")
    assess_eligibility_node.map_input(input_variable="loan_amount", expression="flow.input.loan_amount")
    assess_eligibility_node.map_input(input_variable="loan_purpose", expression="flow.input.loan_purpose")
    
    # Step 4: Branch based on eligibility
    # The evaluator checks the output from the assess_eligibility_node
    # Note: The node variable name is used in the evaluator expression
    eligibility_branch: Branch = aflow.branch(
        evaluator="assess_eligibility_node.output.eligible == True"
    )
    
    # Path A: Customer is eligible - Generate loan offers
    generate_offers_node = aflow.tool("loan-processing:generate_loan_offers")
    generate_offers_node.map_input(input_variable="customer_id", expression="flow.input.customer_id")
    generate_offers_node.map_input(input_variable="loan_amount", expression="flow.input.loan_amount")
    generate_offers_node.map_input(input_variable="loan_purpose", expression="flow.input.loan_purpose")
    
    # Build the workflow graph
    # Sequential steps: START -> Credit Check -> DTI -> Eligibility
    aflow.edge(START, check_credit_node)
    aflow.edge(check_credit_node, calculate_dti_node)
    aflow.edge(calculate_dti_node, assess_eligibility_node)
    
    # Connect eligibility assessment to branch
    aflow.edge(assess_eligibility_node, eligibility_branch)
    
    # Branch outcomes:
    # True (eligible) -> Generate offers -> END
    eligibility_branch.case(True, generate_offers_node)
    aflow.edge(generate_offers_node, END)
    
    # False (not eligible) -> END (rejection)
    eligibility_branch.case(False, END)
    
    return aflow


# Made with Bob