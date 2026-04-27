"""
Loan Processing MCP Server
Simulates loan origination and processing system for demo purposes
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Initialize data directory path
# When running locally for tests, data is in parent/data
# When deployed in watsonx Orchestrate, data is in ./data (same directory as server)
DATA_DIR = Path(__file__).parent / "data"
if not DATA_DIR.exists():
    # Fallback for local testing
    DATA_DIR = Path(__file__).parent.parent / "data"

# Create MCP server
app = Server("loan-processing")


def load_json_file(filename: str) -> dict:
    """Load JSON data from file."""
    file_path = DATA_DIR / filename
    with open(file_path, 'r') as f:
        return json.load(f)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available loan processing tools."""
    return [
        Tool(
            name="calculate_loan_eligibility",
            description="Calculate loan eligibility for a customer based on income, credit score, and debt",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "The customer identifier"
                    },
                    "loan_amount": {
                        "type": "number",
                        "description": "Requested loan amount"
                    },
                    "loan_purpose": {
                        "type": "string",
                        "description": "Purpose of the loan (e.g., 'Home Improvements', 'Vehicle Purchase')"
                    }
                },
                "required": ["customer_id", "loan_amount", "loan_purpose"]
            }
        ),
        Tool(
            name="check_credit_score",
            description="Check customer credit score from credit bureau",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "The customer identifier"
                    }
                },
                "required": ["customer_id"]
            }
        ),
        Tool(
            name="calculate_debt_to_income",
            description="Calculate debt-to-income ratio for a customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "The customer identifier"
                    }
                },
                "required": ["customer_id"]
            }
        ),
        Tool(
            name="generate_loan_offers",
            description="Generate personalized loan offers based on eligibility",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "The customer identifier"
                    },
                    "loan_amount": {
                        "type": "number",
                        "description": "Requested loan amount"
                    },
                    "credit_score": {
                        "type": "integer",
                        "description": "Customer credit score"
                    }
                },
                "required": ["customer_id", "loan_amount", "credit_score"]
            }
        ),
        Tool(
            name="initiate_loan_approval",
            description="Initiate loan approval workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "The customer identifier"
                    },
                    "loan_amount": {
                        "type": "number",
                        "description": "Loan amount"
                    },
                    "loan_purpose": {
                        "type": "string",
                        "description": "Purpose of the loan"
                    },
                    "selected_offer_id": {
                        "type": "string",
                        "description": "Selected loan offer identifier"
                    }
                },
                "required": ["customer_id", "loan_amount", "loan_purpose"]
            }
        ),
        Tool(
            name="generate_loan_documents",
            description="Generate loan agreement documents",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "Loan application identifier"
                    }
                },
                "required": ["application_id"]
            }
        ),
        Tool(
            name="send_for_esignature",
            description="Send loan documents for electronic signature",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "Document identifier"
                    },
                    "customer_id": {
                        "type": "string",
                        "description": "Customer identifier"
                    }
                },
                "required": ["document_id", "customer_id"]
            }
        ),
        Tool(
            name="disburse_funds",
            description="Disburse approved loan funds to customer account",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "Loan application identifier"
                    },
                    "account_id": {
                        "type": "string",
                        "description": "Destination account identifier"
                    }
                },
                "required": ["application_id", "account_id"]
            }
        ),
        Tool(
            name="get_loan_application",
            description="Get details of a loan application",
            inputSchema={
                "type": "object",
                "properties": {
                    "application_id": {
                        "type": "string",
                        "description": "Loan application identifier (e.g., LOAN-APP-001)"
                    }
                },
                "required": ["application_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    
    try:
        if name == "calculate_loan_eligibility":
            customer_id = arguments["customer_id"]
            loan_amount = arguments["loan_amount"]
            loan_purpose = arguments["loan_purpose"]
            
            # Load customer and credit data
            customers = load_json_file("customers.json")
            credit_reports = load_json_file("credit_reports.json")
            
            customer = customers.get(customer_id)
            credit_report = credit_reports.get(customer_id)
            
            if not customer:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": f"Customer {customer_id} not found"
                    })
                )]
            
            # Calculate eligibility
            credit_score = customer.get("credit_score", 0)
            annual_income = customer.get("employment", {}).get("annual_income", 0)
            
            # Simple eligibility logic
            eligible = True
            max_loan_amount = annual_income * 0.5  # 50% of annual income
            
            if credit_score < 600:
                eligible = False
                reason = "Credit score too low"
            elif loan_amount > max_loan_amount:
                eligible = False
                reason = f"Requested amount exceeds maximum (£{max_loan_amount:.2f})"
            else:
                reason = "Meets eligibility criteria"
            
            # Determine risk rating
            if credit_score >= 750:
                risk_rating = "A+ (Excellent)"
            elif credit_score >= 700:
                risk_rating = "A (Very Good)"
            elif credit_score >= 650:
                risk_rating = "B+ (Good)"
            else:
                risk_rating = "B (Acceptable)"
            
            await asyncio.sleep(0.2)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "customer_id": customer_id,
                    "eligible": eligible,
                    "reason": reason,
                    "credit_score": credit_score,
                    "annual_income": annual_income,
                    "requested_amount": loan_amount,
                    "max_approved_amount": max_loan_amount,
                    "risk_rating": risk_rating,
                    "loan_purpose": loan_purpose
                })
            )]
        
        elif name == "check_credit_score":
            customer_id = arguments["customer_id"]
            
            credit_reports = load_json_file("credit_reports.json")
            credit_report = credit_reports.get(customer_id)
            
            if not credit_report:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": f"Credit report not found for customer {customer_id}"
                    })
                )]
            
            await asyncio.sleep(0.1)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "customer_id": customer_id,
                    "credit_score": credit_report["credit_score"]["score"],
                    "rating": credit_report["credit_score"]["rating"],
                    "bureau": credit_report["bureau"],
                    "report_date": credit_report["report_date"]
                })
            )]
        
        elif name == "calculate_debt_to_income":
            customer_id = arguments["customer_id"]
            
            customers = load_json_file("customers.json")
            credit_reports = load_json_file("credit_reports.json")
            
            customer = customers.get(customer_id)
            credit_report = credit_reports.get(customer_id)
            
            if not customer:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": f"Customer {customer_id} not found"
                    })
                )]
            
            annual_income = customer.get("employment", {}).get("annual_income", 0)
            monthly_income = annual_income / 12
            
            # Calculate total debt from credit report
            total_debt = 0
            monthly_debt_payments = 0
            
            if credit_report:
                for account in credit_report.get("credit_accounts", []):
                    if account.get("status") == "Open":
                        total_debt += account.get("current_balance", 0)
                        # Estimate monthly payment (simplified)
                        monthly_debt_payments += account.get("current_balance", 0) * 0.03
            
            dti_ratio = monthly_debt_payments / monthly_income if monthly_income > 0 else 0
            
            await asyncio.sleep(0.1)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "customer_id": customer_id,
                    "monthly_income": monthly_income,
                    "monthly_debt_payments": monthly_debt_payments,
                    "total_debt": total_debt,
                    "debt_to_income_ratio": round(dti_ratio, 3),
                    "debt_to_income_percentage": f"{round(dti_ratio * 100, 1)}%"
                })
            )]
        
        elif name == "generate_loan_offers":
            customer_id = arguments["customer_id"]
            loan_amount = arguments["loan_amount"]
            credit_score = arguments["credit_score"]
            
            # Generate APR based on credit score
            if credit_score >= 750:
                base_apr = 6.5
            elif credit_score >= 700:
                base_apr = 7.5
            elif credit_score >= 650:
                base_apr = 8.5
            else:
                base_apr = 9.5
            
            # Generate 3 offers with different terms
            offers = []
            for i, (term, apr_adjustment) in enumerate([(36, -0.5), (60, 0), (84, 0.5)]):
                apr = base_apr + apr_adjustment
                monthly_payment = (loan_amount * (apr/100/12)) / (1 - (1 + apr/100/12)**(-term))
                total_interest = (monthly_payment * term) - loan_amount
                total_repayment = loan_amount + total_interest
                
                offers.append({
                    "offer_id": f"OFFER-{customer_id[-3:]}-{chr(65+i)}",
                    "loan_amount": loan_amount,
                    "term_months": term,
                    "apr": round(apr, 1),
                    "monthly_payment": round(monthly_payment, 2),
                    "total_interest": round(total_interest, 2),
                    "total_repayment": round(total_repayment, 2),
                    "recommended": i == 1  # Middle option recommended
                })
            
            await asyncio.sleep(0.2)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "customer_id": customer_id,
                    "offers": offers,
                    "count": len(offers)
                })
            )]
        
        elif name == "initiate_loan_approval":
            customer_id = arguments["customer_id"]
            loan_amount = arguments["loan_amount"]
            loan_purpose = arguments["loan_purpose"]
            selected_offer_id = arguments.get("selected_offer_id", "")
            
            application_id = f"LOAN-APP-{int(datetime.now().timestamp())}"
            
            await asyncio.sleep(0.3)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "application_id": application_id,
                    "customer_id": customer_id,
                    "loan_amount": loan_amount,
                    "loan_purpose": loan_purpose,
                    "selected_offer_id": selected_offer_id,
                    "application_status": "Approved",
                    "approval_date": datetime.now().isoformat(),
                    "processing_time_minutes": 15,
                    "automated_approval": True,
                    "next_steps": [
                        "Review and sign loan agreement",
                        "E-signature via DocuSign",
                        "Funds disbursement within 24 hours"
                    ]
                })
            )]
        
        elif name == "generate_loan_documents":
            application_id = arguments["application_id"]
            
            document_id = f"DOC-{int(datetime.now().timestamp())}"
            
            await asyncio.sleep(0.2)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "application_id": application_id,
                    "document_id": document_id,
                    "documents": [
                        {
                            "type": "Loan Agreement",
                            "status": "Generated",
                            "pages": 12
                        },
                        {
                            "type": "Truth in Lending Disclosure",
                            "status": "Generated",
                            "pages": 3
                        },
                        {
                            "type": "Direct Debit Mandate",
                            "status": "Generated",
                            "pages": 2
                        }
                    ],
                    "generated_at": datetime.now().isoformat()
                })
            )]
        
        elif name == "send_for_esignature":
            document_id = arguments["document_id"]
            customer_id = arguments["customer_id"]
            
            customers = load_json_file("customers.json")
            customer = customers.get(customer_id)
            
            if not customer:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": f"Customer {customer_id} not found"
                    })
                )]
            
            await asyncio.sleep(0.1)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "document_id": document_id,
                    "customer_id": customer_id,
                    "email_sent_to": customer.get("email"),
                    "esignature_link": f"https://docusign.example.com/sign/{document_id}",
                    "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
                })
            )]
        
        elif name == "disburse_funds":
            application_id = arguments["application_id"]
            account_id = arguments["account_id"]
            
            await asyncio.sleep(0.3)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "application_id": application_id,
                    "account_id": account_id,
                    "disbursement_status": "Completed",
                    "disbursement_date": datetime.now().isoformat(),
                    "transaction_id": f"TXN-{int(datetime.now().timestamp())}",
                    "message": "Funds have been deposited to your account"
                })
            )]
        
        elif name == "get_loan_application":
            application_id = arguments["application_id"]
            
            loan_applications = load_json_file("loan_applications.json")
            application = loan_applications.get(application_id)
            
            if not application:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": f"Loan application {application_id} not found"
                    })
                )]
            
            await asyncio.sleep(0.1)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "application": application
                })
            )]
        
        # Unknown tool
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "error",
                "message": f"Unknown tool: {name}"
            })
        )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "error",
                "message": f"Error executing tool: {str(e)}"
            })
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
