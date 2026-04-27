"""
Fraud Detection MCP Server
Simulates fraud detection and monitoring system for demo purposes
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
app = Server("fraud-detection")


def load_json_file(filename: str) -> dict:
    """Load JSON data from file."""
    file_path = DATA_DIR / filename
    with open(file_path, 'r') as f:
        return json.load(f)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available fraud detection tools."""
    return [
        Tool(
            name="analyze_transaction_risk",
            description="Analyze a transaction for fraud risk and return risk score with detailed analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "string",
                        "description": "The transaction identifier to analyze"
                    },
                    "account_id": {
                        "type": "string",
                        "description": "The account identifier"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Transaction amount"
                    },
                    "merchant": {
                        "type": "string",
                        "description": "Merchant name"
                    },
                    "location": {
                        "type": "string",
                        "description": "Transaction location"
                    },
                    "transaction_type": {
                        "type": "string",
                        "description": "Type of transaction (e.g., 'Debit Card', 'International Transfer')"
                    }
                },
                "required": ["transaction_id", "account_id", "amount"]
            }
        ),
        Tool(
            name="check_customer_profile",
            description="Get customer fraud risk profile and transaction patterns",
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
            name="verify_device_fingerprint",
            description="Verify if a device is known and trusted for a customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "The device identifier"
                    },
                    "customer_id": {
                        "type": "string",
                        "description": "The customer identifier"
                    }
                },
                "required": ["device_id"]
            }
        ),
        Tool(
            name="check_velocity_rules",
            description="Check if customer has exceeded velocity limits (transaction frequency)",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "The customer identifier"
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Timeframe to check (e.g., '15min', '1hour', '24hours')",
                        "default": "24hours"
                    }
                },
                "required": ["customer_id"]
            }
        ),
        Tool(
            name="block_transaction",
            description="Block a suspicious transaction and create fraud case",
            inputSchema={
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "string",
                        "description": "The transaction identifier to block"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for blocking"
                    },
                    "risk_score": {
                        "type": "integer",
                        "description": "Risk score (0-100)"
                    }
                },
                "required": ["transaction_id", "reason"]
            }
        ),
        Tool(
            name="send_fraud_alert",
            description="Send fraud alert to customer via specified channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "The customer identifier"
                    },
                    "channel": {
                        "type": "string",
                        "description": "Alert channel (SMS, Email, Mobile App, Phone Call)",
                        "enum": ["SMS", "Email", "Mobile App", "Phone Call"]
                    },
                    "message": {
                        "type": "string",
                        "description": "Alert message"
                    }
                },
                "required": ["customer_id", "channel", "message"]
            }
        ),
        Tool(
            name="create_fraud_case",
            description="Create a fraud investigation case",
            inputSchema={
                "type": "object",
                "properties": {
                    "transaction_id": {
                        "type": "string",
                        "description": "The transaction identifier"
                    },
                    "customer_id": {
                        "type": "string",
                        "description": "The customer identifier"
                    },
                    "risk_score": {
                        "type": "integer",
                        "description": "Risk score (0-100)"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Case priority",
                        "enum": ["Low", "Medium", "High", "Critical"],
                        "default": "Medium"
                    }
                },
                "required": ["transaction_id", "customer_id", "risk_score"]
            }
        ),
        Tool(
            name="get_fraud_scenario",
            description="Get a pre-defined fraud scenario for demo purposes",
            inputSchema={
                "type": "object",
                "properties": {
                    "scenario_id": {
                        "type": "string",
                        "description": "Scenario identifier (e.g., TXN-FRAUD-001, FRAUD-INC-002, TXN-LEGIT-001)"
                    }
                },
                "required": ["scenario_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    
    try:
        if name == "analyze_transaction_risk":
            transaction_id = arguments["transaction_id"]
            account_id = arguments["account_id"]
            amount = arguments["amount"]
            merchant = arguments.get("merchant", "Unknown")
            location = arguments.get("location", "Unknown")
            transaction_type = arguments.get("transaction_type", "Unknown")
            
            # Load customer data to get typical patterns
            accounts = load_json_file("accounts.json")
            account = accounts.get(account_id, {})
            customer_id = account.get("customer_id")
            
            # Simple risk scoring logic
            risk_score = 10  # Base score
            triggered_rules = []
            
            # Check amount against typical patterns
            if amount > 2000:
                risk_score += 20
                triggered_rules.append("Large transaction amount")
            
            if "International" in transaction_type:
                risk_score += 30
                triggered_rules.append("International transaction")
            
            if location and "Nigeria" in location:
                risk_score += 40
                triggered_rules.append("High-risk country")
            
            # Determine risk level
            if risk_score >= 80:
                risk_level = "HIGH"
                recommended_action = "BLOCK"
            elif risk_score >= 50:
                risk_level = "MEDIUM"
                recommended_action = "REVIEW"
            else:
                risk_level = "LOW"
                recommended_action = "APPROVE"
            
            await asyncio.sleep(0.1)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "transaction_id": transaction_id,
                    "risk_analysis": {
                        "risk_score": risk_score,
                        "risk_level": risk_level,
                        "fraud_probability": risk_score / 100,
                        "triggered_rules": triggered_rules,
                        "recommended_action": recommended_action,
                        "confidence": 0.85
                    }
                })
            )]
        
        elif name == "check_customer_profile":
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
                    "customer_id": customer_id,
                    "risk_profile": customer.get("risk_profile", "Medium"),
                    "customer_since": customer.get("customer_since"),
                    "typical_transaction_amount": 400.00,
                    "typical_locations": ["London, UK"],
                    "international_transfers_last_year": 0
                })
            )]
        
        elif name == "verify_device_fingerprint":
            device_id = arguments["device_id"]
            customer_id = arguments.get("customer_id")
            
            devices = load_json_file("devices.json")
            device = devices.get(device_id)
            
            if not device:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "device_id": device_id,
                        "known_device": False,
                        "trusted": False,
                        "risk_score": 80,
                        "message": "Unknown device"
                    })
                )]
            
            await asyncio.sleep(0.1)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "device_id": device_id,
                    "known_device": True,
                    "trusted": device.get("trusted", False),
                    "device_type": device.get("device_type"),
                    "last_seen": device.get("last_seen"),
                    "risk_score": device.get("risk_score", 10)
                })
            )]
        
        elif name == "check_velocity_rules":
            customer_id = arguments["customer_id"]
            timeframe = arguments.get("timeframe", "24hours")
            
            # Simulate velocity check
            await asyncio.sleep(0.1)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "customer_id": customer_id,
                    "timeframe": timeframe,
                    "transaction_count": 2,
                    "velocity_limit": 10,
                    "within_limits": True,
                    "total_amount": 1200.00,
                    "amount_limit": 10000.00
                })
            )]
        
        elif name == "block_transaction":
            transaction_id = arguments["transaction_id"]
            reason = arguments["reason"]
            risk_score = arguments.get("risk_score", 90)
            
            await asyncio.sleep(0.1)
            
            case_id = f"FRAUD-CASE-{int(datetime.now().timestamp())}"
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "transaction_id": transaction_id,
                    "blocked": True,
                    "reason": reason,
                    "risk_score": risk_score,
                    "case_id": case_id,
                    "timestamp": datetime.now().isoformat()
                })
            )]
        
        elif name == "send_fraud_alert":
            customer_id = arguments["customer_id"]
            channel = arguments["channel"]
            message = arguments["message"]
            
            await asyncio.sleep(0.1)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "customer_id": customer_id,
                    "channel": channel,
                    "message_sent": True,
                    "timestamp": datetime.now().isoformat()
                })
            )]
        
        elif name == "create_fraud_case":
            transaction_id = arguments["transaction_id"]
            customer_id = arguments["customer_id"]
            risk_score = arguments["risk_score"]
            priority = arguments.get("priority", "Medium")
            
            await asyncio.sleep(0.1)
            
            case_id = f"FRAUD-CASE-{int(datetime.now().timestamp())}"
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "case_id": case_id,
                    "transaction_id": transaction_id,
                    "customer_id": customer_id,
                    "risk_score": risk_score,
                    "priority": priority,
                    "assigned_to": "Fraud Investigation Team",
                    "created_at": datetime.now().isoformat()
                })
            )]
        
        elif name == "get_fraud_scenario":
            scenario_id = arguments["scenario_id"]
            
            fraud_scenarios = load_json_file("fraud_scenarios.json")
            scenario = fraud_scenarios.get(scenario_id)
            
            if not scenario:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": f"Scenario {scenario_id} not found"
                    })
                )]
            
            await asyncio.sleep(0.1)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "scenario": scenario
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
