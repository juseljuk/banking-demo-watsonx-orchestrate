"""
Core Banking MCP Server
Simulates core banking system APIs for demo purposes
"""

import asyncio
import json
from datetime import datetime
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
app = Server("core-banking")

# Session store file path (file-based for persistence across tool calls)
# In production, this would be a secure session management system (Redis, database, etc.)
SESSION_FILE = DATA_DIR / "sessions.json"


def load_sessions() -> dict:
    """Load sessions from file."""
    if SESSION_FILE.exists():
        try:
            with open(SESSION_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_sessions(sessions: dict) -> None:
    """Save sessions to file."""
    try:
        with open(SESSION_FILE, 'w') as f:
            json.dump(sessions, f, indent=2)
    except IOError as e:
        print(f"Warning: Could not save sessions: {e}")


def load_json_file(filename: str) -> dict:
    """Load JSON data from file."""
    file_path = DATA_DIR / filename
    with open(file_path, 'r') as f:
        return json.load(f)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available banking tools."""
    return [
        Tool(
            name="authenticate_customer",
            description="Authenticate a customer using their customer ID and PIN code. This must be called first before any other banking operations. Returns authentication token on success.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "The customer identifier (e.g., CUST-001)"
                    },
                    "pin": {
                        "type": "string",
                        "description": "The customer's 4-digit PIN code"
                    }
                },
                "required": ["customer_id", "pin"]
            }
        ),
        Tool(
            name="get_current_customer",
            description="Get the currently authenticated customer's information and their accounts. Must be called after authenticate_customer. Returns error if no customer is authenticated.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_token": {
                        "type": "string",
                        "description": "The session token from authenticate_customer"
                    }
                },
                "required": ["session_token"]
            }
        ),
        Tool(
            name="check_account_balance",
            description="Check the current balance of a customer account",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "The account identifier (e.g., CUR-001-1234)"
                    }
                },
                "required": ["account_id"]
            }
        ),
        Tool(
            name="get_recent_transactions",
            description="Retrieve recent transactions for an account",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "The account identifier"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of transactions to retrieve (default: 10, max: 50)",
                        "default": 10
                    }
                },
                "required": ["account_id"]
            }
        ),
        Tool(
            name="transfer_funds",
            description="Transfer funds between customer accounts",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_account": {
                        "type": "string",
                        "description": "Source account identifier"
                    },
                    "to_account": {
                        "type": "string",
                        "description": "Destination account identifier"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Transfer amount (must be positive)"
                    },
                    "memo": {
                        "type": "string",
                        "description": "Optional transfer memo",
                        "default": ""
                    }
                },
                "required": ["from_account", "to_account", "amount"]
            }
        ),
        Tool(
            name="check_pending_deposits",
            description="Check pending deposits for an account",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "The account identifier"
                    }
                },
                "required": ["account_id"]
            }
        ),
        Tool(
            name="get_payment_due_date",
            description="Get the payment due date for a credit card account",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string",
                        "description": "The credit card account identifier"
                    }
                },
                "required": ["account_id"]
            }
        ),
        Tool(
            name="get_customer_accounts",
            description="Get all accounts for a customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "The customer identifier (e.g., CUST-001)"
                    }
                },
                "required": ["customer_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    
    try:
        if name == "authenticate_customer":
            customer_id = arguments["customer_id"]
            pin = arguments["pin"]
            
            customers = load_json_file("customers.json")
            
            # Check if customer exists
            if customer_id not in customers:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": "Invalid customer ID or PIN"
                    })
                )]
            
            customer = customers[customer_id]
            
            # Verify PIN
            if customer.get("pin") != pin:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": "Invalid customer ID or PIN"
                    })
                )]
            
            # Generate session token (simple demo implementation)
            session_token = f"SESSION-{customer_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Load existing sessions, add new one, and save
            sessions = load_sessions()
            sessions[session_token] = {
                "customer_id": customer_id,
                "authenticated_at": datetime.now().isoformat()
            }
            save_sessions(sessions)
            
            await asyncio.sleep(0.1)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "message": f"Welcome back, {customer['first_name']} {customer['last_name']}!",
                    "session_token": session_token,
                    "customer_id": customer_id,
                    "customer_name": f"{customer['first_name']} {customer['last_name']}"
                })
            )]
        
        elif name == "get_current_customer":
            session_token = arguments.get("session_token")
            
            # Load sessions from file
            sessions = load_sessions()
            
            # Check if session exists
            if not session_token or session_token not in sessions:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": "Not authenticated. Please authenticate first using authenticate_customer."
                    })
                )]
            
            # Get customer from session
            session = sessions[session_token]
            customer_id = session["customer_id"]
            
            customers = load_json_file("customers.json")
            accounts = load_json_file("accounts.json")
            
            customer = customers[customer_id]
            
            # Get all accounts for this customer
            customer_accounts = {
                acc_id: acc for acc_id, acc in accounts.items()
                if acc["customer_id"] == customer_id
            }
            
            await asyncio.sleep(0.1)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "customer_id": customer_id,
                    "customer_name": f"{customer['first_name']} {customer['last_name']}",
                    "email": customer["email"],
                    "phone": customer["phone"],
                    "accounts": [
                        {
                            "account_id": acc["account_id"],
                            "account_type": acc["account_type"],
                            "account_name": acc["account_name"],
                            "account_number_masked": acc["account_number_masked"],
                            "current_balance": acc["current_balance"],
                            "currency": acc["currency"]
                        }
                        for acc in customer_accounts.values()
                    ]
                })
            )]
        
        elif name == "check_account_balance":
            account_id = arguments["account_id"]
            accounts = load_json_file("accounts.json")
            
            account = accounts.get(account_id)
            if not account:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": f"Account {account_id} not found"
                    })
                )]
            
            # Simulate API delay
            await asyncio.sleep(0.1)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "account_id": account["account_id"],
                    "account_type": account["account_type"],
                    "account_name": account["account_name"],
                    "account_number_masked": account["account_number_masked"],
                    "current_balance": account["current_balance"],
                    "available_balance": account["available_balance"],
                    "currency": account["currency"]
                })
            )]
        
        elif name == "get_recent_transactions":
            account_id = arguments["account_id"]
            limit = arguments.get("limit", 10)
            
            transactions = load_json_file("transactions.json")
            account_txns = [t for t in transactions if t.get("account_id") == account_id and t.get("status") == "Posted"]
            
            # Sort by date descending and limit
            account_txns.sort(key=lambda x: (x["date"], x["time"]), reverse=True)
            account_txns = account_txns[:limit]
            
            await asyncio.sleep(0.1)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "account_id": account_id,
                    "transactions": account_txns,
                    "count": len(account_txns)
                })
            )]
        
        elif name == "transfer_funds":
            from_account = arguments["from_account"]
            to_account = arguments["to_account"]
            amount = arguments["amount"]
            memo = arguments.get("memo", "")
            
            accounts = load_json_file("accounts.json")
            
            # Validate accounts exist
            if from_account not in accounts:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": f"Source account {from_account} not found"
                    })
                )]
            
            if to_account not in accounts:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": f"Destination account {to_account} not found"
                    })
                )]
            
            # Check sufficient balance
            if accounts[from_account]["current_balance"] < amount:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": "Insufficient funds"
                    })
                )]
            
            # Simulate transfer (in real system, this would update database)
            await asyncio.sleep(0.2)
            
            new_from_balance = accounts[from_account]["current_balance"] - amount
            new_to_balance = accounts[to_account]["current_balance"] + amount
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "transaction_id": f"TXN-{int(datetime.now().timestamp())}",
                    "from_account": from_account,
                    "to_account": to_account,
                    "amount": amount,
                    "memo": memo,
                    "timestamp": datetime.now().isoformat(),
                    "new_from_balance": new_from_balance,
                    "new_to_balance": new_to_balance
                })
            )]
        
        elif name == "check_pending_deposits":
            account_id = arguments["account_id"]
            
            transactions = load_json_file("transactions.json")
            pending_txns = [t for t in transactions if t.get("account_id") == account_id and t.get("status") == "Pending"]
            
            await asyncio.sleep(0.1)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "account_id": account_id,
                    "pending_deposits": pending_txns,
                    "count": len(pending_txns),
                    "total_amount": sum(t.get("amount", 0) for t in pending_txns)
                })
            )]
        
        elif name == "get_payment_due_date":
            account_id = arguments["account_id"]
            
            accounts = load_json_file("accounts.json")
            account = accounts.get(account_id)
            
            if not account:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": f"Account {account_id} not found"
                    })
                )]
            
            if account.get("account_type") != "Credit Card":
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": "This is not a credit card account"
                    })
                )]
            
            await asyncio.sleep(0.1)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "account_id": account_id,
                    "payment_due_date": account.get("payment_due_date"),
                    "minimum_payment": account.get("minimum_payment"),
                    "current_balance": account.get("current_balance"),
                    "last_payment_date": account.get("last_payment_date"),
                    "last_payment_amount": account.get("last_payment_amount")
                })
            )]
        
        elif name == "get_customer_accounts":
            customer_id = arguments["customer_id"]
            
            accounts = load_json_file("accounts.json")
            customer_accounts = [acc for acc in accounts.values() if acc.get("customer_id") == customer_id]
            
            await asyncio.sleep(0.1)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "customer_id": customer_id,
                    "accounts": customer_accounts,
                    "count": len(customer_accounts)
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
