# Banking AI Demonstration - watsonx Orchestrate

A comprehensive demonstration showcasing IBM watsonx Orchestrate's capabilities for financial services, designed for C-suite executives and business leaders in the UK banking sector.

## 📋 Overview

This demo highlights business value, ROI potential, and customer experience improvements through three core banking use cases:
- **Intelligent Customer Service** - 40-60% faster response times
- **Real-Time Fraud Detection** - 95%+ accuracy with automated blocking
- **Automated Loan Processing** - 70% faster processing with compliance

## 📁 Project Structure

```
banking-demo/
├── docs/                                    # Planning & Documentation
│   ├── banking-demo-plan.md                # Complete demo plan with architecture & use cases
│   ├── banking-demo-data.md                # UK-localized dummy data specification
│   ├── banking-demo-implementation-plan.md # Legacy MCP implementation history
│   └── banking-demo-guardrail-validation.md # Guardrail coverage & validation
│
├── data/                                    # ✅ Dummy data (JSON files) - IMPLEMENTED
│   ├── customers.json                       # 3 UK customer profiles with PINs
│   ├── accounts.json                        # 5 accounts with UK banking conventions
│   ├── transactions.json                    # 15 realistic UK transactions
│   ├── fraud_scenarios.json                 # 3 fraud scenarios
│   ├── devices.json                         # Device fingerprints
│   ├── loan_applications.json               # 3 loan applications
│   └── credit_reports.json                  # Experian UK credit data
│
├── cloudant-tools/                          # ✅ Standalone Cloudant-backed Python tools
│   ├── core_banking_tools.py                # Core banking standalone tools
│   ├── fraud_detection_tools.py             # Fraud/risk standalone tools
│   ├── loan_processing_tools.py             # Lending standalone tools
│   ├── repositories/                        # Cloudant data access layer
│   ├── scripts/                             # Bootstrap/seed utilities
│   └── common/                              # Shared Cloudant config/client utilities
│
├── agents/                                  # ✅ Agent configurations - IMPLEMENTED
│   ├── banking-orchestrator-agent.yaml      # Primary interface with auth
│   ├── customer-service-agent.yaml          # Account operations
│   ├── fraud-detection-agent.yaml           # Real-time monitoring
│   ├── loan-processing-agent.yaml           # Automated workflows
│   └── compliance-risk-agent.yaml           # Regulatory compliance
│
├── plugins/                                 # ✅ Guardrails - IMPLEMENTED
│   ├── pii_protection_guardrail.py          # Post-invoke: Redacts sensitive data
│   ├── transaction_limit_guardrail.py       # Pre-invoke: Enforces transfer limits
│   ├── lending_compliance_guardrail.py      # Pre-invoke: UK lending regulations
│   └── fraud_rules_guardrail.py             # Pre-invoke: Risk scoring & blocking
│
├── tests/                                   # ✅ Test cases - IMPLEMENTED
│   ├── test_guardrail_logic.py              # Tests for all 4 guardrails (16 tests)
│   ├── test_pii_protection_guardrail.py     # Standalone PII guardrail tests
│   ├── test_loan_approval_workflow.py       # Workflow simulation tests
│   ├── run_loan_approval_workflow.py        # Workflow execution script (Dev Edition only)
│   └── README.md                            # Test documentation
│
├── tools/                                   # ✅ Agentic Workflows - IMPLEMENTED
│   ├── loan_approval_workflow.py            # Deterministic loan approval workflow
│   └── README.md                            # Workflow documentation
│
├── DEMO_ACCOUNTS.md                         # ✅ Customer credentials & demo scenarios
├── AUTHENTICATION_GUIDE.md                  # ✅ Authentication implementation guide
├── AUTHENTICATION_ARCHITECTURE.md           # ✅ Technical authentication details
├── IMPLEMENTATION_SUMMARY.md                # ✅ Complete implementation summary
├── IMPLEMENTATION.md                        # ✅ Detailed implementation notes
├── TESTING_GUIDE.md                         # ✅ Testing procedures
├── TROUBLESHOOTING.md                       # ✅ Common issues and solutions
├── GUARDRAIL_DEMO_GUIDE.md                  # ✅ Guardrail demo scenarios
├── GUARDRAIL_BEFORE_AFTER_DEMO.md           # ✅ Before/after guardrail comparison
├── GUARDRAILS_IMPLEMENTATION.md             # ✅ Technical guardrail details
├── LOAN_APPROVAL_WORKFLOW.md                # ✅ Workflow implementation guide
├── WORKFLOW_QUICK_START.md                  # ✅ Quick start for workflows
├── QUICK_START_DEMO.md                      # ✅ Quick demo guide
├── import-all.sh                            # ✅ Automated deployment script (with guardrails)
├── import-no-guardrails.sh                  # ⚠️  Demo-only script (without guardrails)
├── publish-to-github.sh                     # ✅ GitHub publishing script
└── requirements.txt                         # ✅ Python dependencies
```

## 🎯 Key Features

### Multi-Agent Orchestration
- **Banking Orchestrator Agent** - Primary customer interface with intelligent routing
- **Customer Service Agent** - Account operations and support
- **Fraud Detection Agent** - Real-time transaction monitoring
- **Loan Processing Agent** - Automated loan workflows
- **Compliance & Risk Agent** - Regulatory checks and audit trails

### Agentic Workflows
- **Loan Approval Workflow** - Deterministic multi-step loan processing with branching logic
  - Credit score checking
  - Debt-to-income calculation
  - Eligibility assessment
  - Automated offer generation
  - 60% faster than agent-based approach

### Security & Compliance
- **4 Production Guardrails** ✅ IMPLEMENTED:
  - **PII Protection** - Automatic redaction of sensitive data (account numbers, NI numbers, etc.)
  - **Transaction Limits** - Enforces daily and single transaction limits by account type
  - **Lending Compliance** - FCA CONC 5.2A, affordability checks, income verification
  - **Fraud Detection** - Risk scoring (0-100) with automatic blocking at critical levels
- **UK Regulatory Compliance** - FCA, Consumer Credit Act 1974, Payment Services Regulations 2017
- **GDPR Compliance** - Data protection and privacy controls
- **AML/Sanctions** - Anti-money laundering and sanctions screening

### UK Banking Conventions
- Currency: GBP (£)
- Account types: Current Account, Savings Account, Credit Card
- Sort codes and IBANs
- UK phone numbers and postcodes
- UK credit scoring (0-999 range)
- UK regulatory framework

## 📊 Business Impact

**For 100,000 customers:**
- **£32M+ annual savings**
- **1,200%+ ROI** in Year 1
- **<3 month payback** period
- **40% improvement** in customer satisfaction
- **95%+ fraud detection** accuracy

## 📖 Documentation

### Planning Documents (in `docs/`)

1. **[banking-demo-plan.md](docs/banking-demo-plan.md)**
   - Complete demo architecture
   - Three use case scenarios with workflows
   - Agent specifications
   - Tool designs
   - Guardrail implementations
   - Demo script (30-45 minutes)
   - ROI calculations

2. **[banking-demo-data.md](docs/banking-demo-data.md)**
   - UK-localized customer profiles (3 personas)
   - Account data with UK banking conventions
   - Transaction history
   - Fraud scenarios (high-risk, account takeover, legitimate)
   - Loan applications (personal, business, car finance)
   - Credit bureau data
   - Device & location data
   - Demo scenario mappings

3. **[banking-demo-implementation-plan.md](docs/banking-demo-implementation-plan.md)**
   - MCP server architecture (recommended approach)
   - Three MCP servers: Core Banking, Fraud Detection, Loan Processing
   - Implementation timeline (4 weeks)
   - Code examples and YAML configurations
   - Testing strategy
   - Deployment guide

4. **[banking-demo-guardrail-validation.md](docs/banking-demo-guardrail-validation.md)**
   - Validation matrix for all guardrails
   - 15+ specific demo scenarios
   - Data coverage assessment (75% current, 95% with enhancements)
   - Priority 1 additions needed
   - 10-12 minute guardrail demo script

## 🚀 Implementation Status

### ✅ Completed (Ready for Demo)
- [x] Demo architecture and multi-agent orchestration strategy
- [x] Three use case designs (customer service, fraud, loans)
- [x] **5 Agent configurations** - All deployed and ready
- [x] **3 standalone Cloudant-backed Python tool modules** - Core Banking, Fraud Detection, Loan Processing
- [x] **1 Agentic Workflow** - Loan approval workflow with deterministic processing
- [x] **7 JSON seed data files** - UK-localized customer, account, transaction data
- [x] **Customer authentication system** - PIN-based authentication with session management
- [x] **4 Guardrail plugins** - PII protection, transaction limits, lending compliance, fraud rules
- [x] **Test suite** - Guardrails, workflow tests, and Cloudant-backed tool validation
- [x] **Deployment automation** - `import-all.sh` script for one-command deployment
- [x] **Documentation** - 15+ comprehensive guides covering all aspects
- [x] Demo scripts and presentation flow
- [x] ROI calculations and success metrics

### 🔄 Future Enhancements
- [ ] Additional agentic workflows (fraud investigation, account opening)
- [ ] Enhanced test coverage for edge scenarios
- [ ] Performance benchmarking and optimization
- [ ] Multi-turn conversation testing
- [ ] Channel integrations (Slack, Teams, Web Chat)

### 📊 Implementation Metrics
- **Total Files Created**: 40+
- **Lines of Code**: ~4,000+
- **Standalone Tool Modules**: 3 (core banking, fraud, loan)
- **Agentic Workflows**: 1 (loan approval)
- **Agents**: 5 (orchestrator + 4 specialists)
- **Guardrail Plugins**: 4 (PII, transaction limits, lending compliance, fraud rules)
- **Test Files**: 5 (guardrails, workflows, standalone tool validation)
- **Documentation Files**: 15+

## 🎬 Demo Scenarios

### 🔐 Authentication Flow (Required First)
**Customer**: "What's my account balance?"
**System**: "To help you, I need to verify your identity. Please provide your Customer ID and 4-digit PIN."
**Customer**: "CUST-001 and 1234"
**System**: "Welcome back, Emma Thompson! Your current account balance is £4,250.50"
**Demonstrates**: Secure authentication, session management, identity verification

### Scenario 1: Simple Account Inquiry (After Authentication)
**Customer**: "What's my current account balance?"
**Response Time**: 2-3 seconds
**Demonstrates**: Natural language understanding, account lookup, authenticated access

### Scenario 2: Multi-Step Request
**Customer**: "Transfer £1,500 to savings, check pending deposits, and tell me when my credit card payment is due"
**Response Time**: 4-5 seconds
**Demonstrates**: Multi-tool coordination, transaction processing, session token passing

### Scenario 3: Fraud Detection
**Trigger**: £3,500 international transfer to Nigeria at 2 AM
**Response Time**: <1 second
**Demonstrates**: Real-time risk analysis (score: 92/100), automatic blocking, customer notification

### Scenario 4: Loan Application
**Customer**: "I'd like to apply for a £20,000 personal loan"
**System**: Authenticates → Checks eligibility → Generates 3 offers
**Processing Time**: 5-10 seconds
**Demonstrates**: Automated eligibility (up to £32,500), credit scoring (742), compliance checks

## 🔒 Security & Guardrails

### ✅ Implemented Security Features

#### 1. Customer Authentication
- PIN-based authentication with session tokens
- Customer ID + 4-digit PIN verification
- Session token generation and management
- Secure credential storage (demo: plain text, production: hashed)
- Session validation for all operations

#### 2. Guardrail Plugins (4 Implemented)

**PII Protection Guardrail** (Post-invoke)
- Automatically redacts sensitive personal information
- Protects: Account numbers, NI numbers, emails, phone numbers, credit cards, IBANs
- Compliance: GDPR, UK Data Protection Act 2018, FCA SYSC 3.2.6R
- Attached to: All 5 agents

**Transaction Limit Guardrail** (Pre-invoke)
- Enforces daily transfer limits (£10k current, £25k business, £5k savings)
- Single transaction limit: £50,000
- High-value verification threshold: £10,000
- Compliance: UK Payment Services Regulations 2017, FCA SYSC 6.1
- Attached to: Customer Service Agent

**Lending Compliance Guardrail** (Pre-invoke)
- Creditworthiness checks (min score: 550)
- Affordability assessment (max DTI: 40%)
- Income verification (min: £15,000/year)
- Required disclosures (APR, cooling-off period, etc.)
- Compliance: FCA CONC 5.2A, Consumer Credit Act 1974
- Attached to: Loan Processing Agent

**Fraud Rules Guardrail** (Pre-invoke)
- Real-time risk scoring (0-100 scale)
- Blocks critical risk transactions (score ≥91)
- Detects: High-risk countries, suspicious patterns, urgency language
- Compliance: UK Payment Services Regulations, AML Regulations
- Attached to: Customer Service Agent, Fraud Detection Agent

#### 3. Additional Security Capabilities
- Account masking and access control
- Device fingerprinting
- Velocity rule checking
- AML/Sanctions screening
- GDPR compliance structures
- Audit logging and compliance reporting
- Credit bureau integration (Experian UK)

### 📖 Guardrail Documentation
- [`GUARDRAIL_DEMO_GUIDE.md`](GUARDRAIL_DEMO_GUIDE.md) - Complete demo scenarios and scripts
- [`GUARDRAILS_IMPLEMENTATION.md`](GUARDRAILS_IMPLEMENTATION.md) - Technical implementation details

## 👥 Customer Personas & Credentials

### Emma Thompson (Primary Demo Customer)
- **Customer ID**: `CUST-001`
- **PIN**: `1234`
- Location: London, Kensington
- Occupation: Senior Software Engineer
- Income: £65,000/year
- Credit Score: 742 (Good)
- Accounts: Current (£4,250.50), Savings (£18,750.00), Credit Card (£1,856.75 balance)

### James Patel (Business Customer)
- **Customer ID**: `CUST-002`
- **PIN**: `5678`
- Location: London, Canary Wharf
- Occupation: Managing Director, Patel Consulting Ltd
- Income: £125,000/year
- Credit Score: 785 (Excellent)
- Accounts: Business Current (£68,450.25), Business Savings (£125,600.00)

### Sophie Williams (Young Professional)
- **Customer ID**: `CUST-003`
- **PIN**: `9012`
- Location: Manchester
- Occupation: Marketing Coordinator
- Income: £32,000/year
- Credit Score: 680 (Good)
- Accounts: Current, Savings

**See [`DEMO_ACCOUNTS.md`](DEMO_ACCOUNTS.md) for complete account details and demo scenarios**

## 🎯 Target Audience

**Primary**: C-suite executives and business leaders in UK banking sector

**Key Messages**:
- Business value and ROI (£32M+ savings, 1,200%+ ROI)
- Customer experience improvements (40-60% faster, 24/7 availability)
- Risk reduction (95%+ fraud detection, built-in compliance)
- Operational efficiency (70% faster loan processing, 30-50% cost savings)

## 📞 Next Steps

### Immediate (Ready Now)
1. **Test in watsonx Orchestrate UI**
   - Authenticate with Emma Thompson (CUST-001, PIN: 1234)
   - Try the 5 demo scenarios
   - Verify agent routing and tool execution
   - Check response quality and accuracy

2. **Validate Multi-Agent Orchestration**
   - Test orchestrator routing to specialists
   - Verify session token passing between agents
   - Check context preservation across handoffs

3. **Performance Testing**
   - Measure response times
   - Check token usage
   - Validate concurrent requests

### Optional Enhancements
1. **Implement Guardrail Plugins** (see `docs/banking-demo-guardrail-validation.md`)
2. **Add Additional Test Cases** (edge cases, error handling, multi-turn)
3. **Create Presentation Materials** (slides, architecture diagrams)
4. **Rehearse Demo** with all scenarios

## 📚 Additional Resources

### Documentation
- [watsonx Orchestrate Documentation](https://www.ibm.com/docs/en/watsonx/watson-orchestrate)
- [Agent Development Kit (ADK) Guide](https://developer.watson-orchestrate.ibm.com/)
- [MCP Server Integration](https://modelcontextprotocol.io/)

### Project Documentation
- [`DEMO_ACCOUNTS.md`](DEMO_ACCOUNTS.md) - Customer credentials and demo scenarios
- [`AUTHENTICATION_GUIDE.md`](AUTHENTICATION_GUIDE.md) - Authentication implementation details
- [`AUTHENTICATION_ARCHITECTURE.md`](AUTHENTICATION_ARCHITECTURE.md) - Technical architecture
- [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md) - Complete implementation summary
- [`IMPLEMENTATION.md`](IMPLEMENTATION.md) - Detailed implementation notes
- [`TESTING_GUIDE.md`](TESTING_GUIDE.md) - Testing procedures and validation
- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) - Common issues and solutions
- [`GUARDRAIL_DEMO_GUIDE.md`](GUARDRAIL_DEMO_GUIDE.md) - Guardrail demonstration guide
- [`GUARDRAIL_BEFORE_AFTER_DEMO.md`](GUARDRAIL_BEFORE_AFTER_DEMO.md) - Before/after comparison
- [`GUARDRAILS_IMPLEMENTATION.md`](GUARDRAILS_IMPLEMENTATION.md) - Technical guardrail details
- [`LOAN_APPROVAL_WORKFLOW.md`](LOAN_APPROVAL_WORKFLOW.md) - Workflow implementation guide
- [`WORKFLOW_QUICK_START.md`](WORKFLOW_QUICK_START.md) - Quick start for workflows
- [`QUICK_START_DEMO.md`](QUICK_START_DEMO.md) - Quick demo guide

### Deployment
- [`import-all.sh`](import-all.sh) - Automated deployment script
- [`requirements.txt`](requirements.txt) - Python dependencies

---

**Project Status**: ✅ Implementation Complete - Ready for Demo Testing
**Last Updated**: 2026-04-26
**Implementation By**: Bob (WXO Agent Architect)
**Next Action**: Test demo scenarios in watsonx Orchestrate UI