# User Guide: Getting Started with RRL AI Orchestrator

This guide walks you through using the Rinse Repeat Labs AI Orchestrator to manage your software development business with a team of 12 AI agents.

## Table of Contents

1. [Who Is This For?](#who-is-this-for)
2. [Quick Start Walkthrough](#quick-start-walkthrough)
3. [Use Case Scenarios](#use-case-scenarios)
4. [Dashboard Deep Dive](#dashboard-deep-dive)
5. [Working with AI Agents](#working-with-ai-agents)
6. [Common Workflows](#common-workflows)

---

## Who Is This For?

The RRL AI Orchestrator is designed for anyone building software products who wants AI-powered assistance across business functions. It's particularly valuable if you:

- **Are a solo founder** who needs to wear many hats but lacks expertise in some areas
- **Have a small team** but can't afford specialists in legal, finance, QA, or marketing
- **Run an agency** and need consistent processes for evaluating and managing projects
- **Want to prototype** what having a full team would look like before hiring
- **Need a sounding board** for strategic decisions with multiple perspectives

### The 12 AI Agents Replace or Augment:

| Agent | Replaces/Augments | Cost Savings |
|-------|-------------------|--------------|
| CEO | Strategic advisor, business coach | $200-500/hr consulting |
| CFO | Bookkeeper, financial advisor | $50-150/hr |
| CITO | Technical architect, CTO consultant | $150-300/hr |
| Sales | Sales development rep | $50-80k/yr salary |
| Legal | Contract review attorney | $200-500/hr |
| Dev Lead | Senior developer, tech lead | $120-180k/yr salary |
| Design Lead | UI/UX designer | $80-120k/yr salary |
| QA Lead | QA manager, test engineer | $70-100k/yr salary |
| PM | Project manager | $80-120k/yr salary |
| Customer Success | Account manager | $60-90k/yr salary |
| Marketing | Marketing manager | $70-100k/yr salary |
| Support | Support manager | $50-70k/yr salary |

---

## Quick Start Walkthrough

### Step 1: Initial Setup (5 minutes)

```bash
# Clone the repository
git clone https://github.com/imcmurray/RRL.git
cd RRL

# Run the setup wizard
python orchestrator.py setup --launch-web
```

The setup wizard will:
1. Create necessary directories
2. Check and install dependencies
3. Configure your API key
4. Initialize data stores
5. Launch the web dashboard

### Step 2: Explore the Dashboard

Once the dashboard opens at `http://localhost:5000`, you'll see:

- **Stats Cards** - Overview of ideas, testers, projects, and finances
- **Quick Actions** - One-click access to common tasks
- **Recent Activity** - Latest ideas, projects, and testers
- **AI Agent Team** - Quick access to all 12 agent portals

### Step 3: Meet Your Team

Click **"All Portals"** in the AI Agent Team section to see all 12 agents organized by department:

- **Executive Team** - CEO, CFO, CITO, Sales, Legal
- **Product & Engineering** - Dev Lead, Design Lead, QA Lead
- **Operations** - PM, Customer Success, Marketing, Support

### Step 4: Have Your First Meeting

```bash
# Strategic sync with CEO
python orchestrator.py ceo-sync --topic "Business goals for this quarter"

# Or use interactive mode for guided options
python orchestrator.py interactive
```

---

## Use Case Scenarios

### Scenario 1: Solo Founder Building a SaaS Product

**Situation:** Sarah is a developer building a project management SaaS. She's great at coding but struggles with pricing, legal contracts, and marketing.

**How RRL Helps:**

1. **Pricing Strategy** - Talk to the CFO
   ```bash
   python orchestrator.py 1on1 --agent cfo --topic "How should I price my SaaS? Freemium vs paid?"
   ```

2. **Terms of Service Review** - Consult Legal
   ```bash
   python orchestrator.py 1on1 --agent legal --topic "What do I need in my terms of service?"
   ```

3. **Go-to-Market Strategy** - Work with Marketing
   ```bash
   python orchestrator.py 1on1 --agent marketing --topic "How do I launch my product with no budget?"
   ```

4. **Track Beta Testers** - Use the web dashboard
   - Navigate to **Testers > Add Tester**
   - Track their devices, feedback, and payment info
   - Monitor tester activity and engagement

**Daily Workflow:**
```bash
# Morning check-in
python orchestrator.py standup

# Evening review
python orchestrator.py ceo-sync --topic "What did I accomplish today?"
```

---

### Scenario 2: Small Agency with 3 Developers

**Situation:** Mike runs a small development agency with 2 other developers. They get client inquiries but struggle with sales, project scoping, and client management.

**How RRL Helps:**

1. **Evaluate New Client Inquiries** - Use the Ideas pipeline
   - Add client ideas via **Ideas > Submit New Idea**
   - Run an idea review meeting:
   ```bash
   python orchestrator.py idea-review --idea context/pending_ideas/client-app.md
   ```

2. **Scope and Estimate Projects** - Technical + Business review
   ```bash
   python orchestrator.py meeting --topic "Scope estimation for e-commerce app" \
     --agents cito,dev_lead,cfo,pm
   ```

3. **Manage Client Relationships** - Use Clients section
   - Track all clients in **Clients > All Clients**
   - Link clients to projects
   - Monitor outstanding invoices in **Finances**

4. **Handle Support Requests** - Support agent + dashboard
   ```bash
   python orchestrator.py 1on1 --agent support --topic "Client reporting a bug in production"
   ```

**Weekly Workflow:**
```bash
# Monday planning
python orchestrator.py exec-meeting --topic "Week priorities"

# Friday retrospective
python orchestrator.py all-hands --topic "What went well this week?"
```

---

### Scenario 3: Startup Founder Validating Ideas

**Situation:** Alex has 5 app ideas and needs to figure out which one to build first. They have limited time and money.

**How RRL Helps:**

1. **Add All Ideas to the Pipeline**
   - Via dashboard: **Ideas > Submit New Idea** (repeat for each)
   - Or via CLI:
   ```bash
   python orchestrator.py ideas add --name "FitTrack" --description "Fitness tracking app" \
     --submitter-name "Alex" --submitter-email "alex@example.com"
   ```

2. **Get Multi-Perspective Evaluation**
   ```bash
   # Review each idea with the full team
   python orchestrator.py idea-review --idea context/pending_ideas/fittrack.md
   ```

   The review includes perspectives from:
   - **CITO** - Technical feasibility
   - **CFO** - Revenue potential
   - **Marketing** - Market opportunity
   - **Legal** - Risk assessment
   - **Dev Lead** - Build complexity
   - **Design Lead** - UX considerations

3. **Compare Ideas Side by Side**
   ```bash
   python orchestrator.py strategy --topic "Which of my 5 ideas should I build first?"
   ```

4. **Deep Dive on Winner**
   ```bash
   python orchestrator.py tech-meeting --topic "Architecture for FitTrack app"
   ```

---

### Scenario 4: Non-Technical Founder with an App Idea

**Situation:** Jordan has a great app idea but doesn't know how to code. They need to understand what building an app involves before hiring developers.

**How RRL Helps:**

1. **Understand Technical Requirements**
   ```bash
   python orchestrator.py 1on1 --agent cito --topic "I want to build a food delivery app. What technology do I need?"
   ```

2. **Get Cost Estimates**
   ```bash
   python orchestrator.py meeting --topic "How much will my app cost to build?" \
     --agents cfo,cito,dev_lead,design_lead
   ```

3. **Understand the Process**
   ```bash
   python orchestrator.py 1on1 --agent pm --topic "What are the phases of building an app?"
   ```

4. **Prepare for Developer Conversations**
   ```bash
   python orchestrator.py 1on1 --agent dev_lead --topic "What questions should I ask when hiring a developer?"
   ```

---

### Scenario 5: Growing Team Needs Process

**Situation:** A 10-person startup is growing fast but lacks formal processes. They need structure without hiring a COO.

**How RRL Helps:**

1. **Establish Meeting Cadence**
   ```bash
   # Daily standups
   python orchestrator.py standup

   # Weekly executive sync
   python orchestrator.py exec-meeting

   # Bi-weekly all-hands
   python orchestrator.py all-hands
   ```

2. **Create Decision-Making Framework**
   - All decisions logged automatically to `decisions/decisions.json`
   - Review past decisions:
   ```bash
   python orchestrator.py decisions --last 20
   ```

3. **Standardize Project Intake**
   - Use Ideas pipeline for all new work
   - Run idea-review for consistent evaluation
   - Track in Projects once approved

4. **Document Processes**
   ```bash
   python orchestrator.py 1on1 --agent pm --topic "Help me document our development process"
   ```

---

## Dashboard Deep Dive

### Home Dashboard (`/`)

The main dashboard shows:

| Section | What It Shows | How to Use |
|---------|---------------|------------|
| **Stats Cards** | Ideas, Testers, Projects, Revenue | Quick health check |
| **Quick Actions** | Common tasks | One-click to add items |
| **Recent Ideas** | Latest submissions | Click to review |
| **Active Projects** | Current work | Click for details |
| **Recent Testers** | New beta testers | Manage signups |
| **AI Agent Team** | All 12 agents | Access portals |

### Ideas (`/ideas`)

**Purpose:** Track app ideas from submission through approval to development.

**Workflow:**
1. **Submit** - Add new ideas via form
2. **Review** - Click idea to see details
3. **Decide** - Approve, decline, or request changes
4. **Convert** - Approved ideas become projects

**Statuses:** Submitted → Under Review → Approved/Declined → In Development → Completed

### Testers (`/testers`)

**Purpose:** Manage your beta tester community.

**Key Features:**
- Track devices and platforms each tester has
- Store payment preferences (PayPal, Venmo, Crypto)
- Monitor tester activity and reliability
- Assign testers to projects

**Payment Methods Supported:**
- PayPal, Venmo
- Bitcoin, Ethereum, USDC, Dogecoin, XRP, Stellar, Dash

### Clients (`/clients`)

**Purpose:** CRM for client relationships.

**Track:**
- Contact information
- Company details
- Associated projects
- Communication history

### Projects (`/projects`)

**Purpose:** Manage active development work.

**Track:**
- Project status (Planning → Design → Development → Testing → Launched)
- Assigned team members
- Client association
- Milestones and progress

### Finances (`/finances`)

**Purpose:** Invoice and payment tracking.

**Features:**
- Create invoices linked to clients/projects
- Track payment status
- View revenue reports
- Monitor outstanding amounts

### Agent Portals (`/agents`)

**Purpose:** Individual workspaces for each AI agent.

**Each Portal Shows:**
- Agent role and responsibilities
- Key metrics for their domain
- Recent activity
- Feature requests they've submitted

### Reports (`/reports`)

**Purpose:** Generate business reports.

**Report Types:**
- Ideas Pipeline - Submission and approval metrics
- Tester Program - Beta tester statistics
- Projects Status - Active work overview
- Financial Summary - Revenue and expenses

---

## Working with AI Agents

### Two Ways to Interact

You can interact with AI agents through:

1. **CLI Meetings** — Multi-agent discussions via command line
2. **Web Chat** — Real-time conversations through the dashboard

### Web-Based Agent Chat

The web dashboard provides a chat interface for each agent:

1. Navigate to an agent's portal (`/agents/<agent_id>`)
2. Click **"Start Chat"** in Quick Actions
3. Have a real-time conversation with the AI agent

**Benefits of Web Chat:**
- Visual interface with message history
- Conversation persistence (resume later)
- Agent context automatically loaded
- CEO can take actions on your behalf

### CEO as Your AI Manager

The CEO agent has special powers through web chat. You can have a conversation with the CEO and ask them to make changes across the entire system:

```
You: "I want all agents to focus on enterprise clients instead of startups"

CEO: "I'll update the custom instructions for all agents to emphasize
enterprise client focus. Here's what I'll do:

[ACTION: broadcast_to_agents]
{"agent_ids": "all", "instruction": "Focus on enterprise clients. Emphasize scalability, security, and compliance in all recommendations.", "append": true}
[/ACTION]"

→ Review the proposed action
→ Click "Confirm" to execute
→ All agents receive updated instructions
```

**What the CEO can do:**
- Update any agent's settings, instructions, or responsibilities
- Change company-wide settings (name, tagline, industry)
- Create, approve, or reject feature requests
- Update idea statuses in the pipeline
- Broadcast instructions to all agents or specific groups
- Modify reporting structures

This makes the CEO your strategic AI partner who can manage the entire agent team on your behalf.

### Web-Based Group Meetings

Hold meetings with multiple AI agents through the web dashboard:

1. Navigate to **Agent Portals** > **Start Group Meeting** (or go to `/group-meetings/new`)
2. Choose a meeting type or select custom agents
3. Enter your meeting topic
4. Click **Start Meeting**

**Meeting Presets:**

| Preset | Participants | Best For |
|--------|--------------|----------|
| **Executive Meeting** | CEO, CFO, CITO, Sales, Legal | Strategic decisions |
| **Technical Meeting** | CITO, Dev Lead, Design Lead, QA Lead | Architecture, quality |
| **Product Meeting** | PM, Dev Lead, Design Lead, QA Lead | Sprint coordination |
| **Operations Meeting** | PM, Customer Success, Marketing, Support | Day-to-day operations |
| **All-Hands Meeting** | All 12 agents | Company-wide alignment |
| **Idea Review** | CEO, CITO, CFO, Dev Lead, Design Lead, Marketing | Evaluate new ideas |
| **Custom** | Your selection | Any combination |

**How It Works:**
1. You type a message to the team
2. Each agent responds in turn based on their role
3. Quick prompts help guide the conversation (summarize, identify risks, next steps)
4. End the meeting when done - transcript is saved

**Example:**
```
You: "Should we build a mobile app version of our product?"

CEO: "From a strategic standpoint, mobile could expand our market reach..."
CFO: "The budget implications we need to consider include..."
CITO: "Technically, we have several options for mobile development..."
Dev Lead: "Our current architecture would support mobile through..."
```

### CLI Meeting Types

| Type | Best For | Participants |
|------|----------|--------------|
| **1:1** | Deep dive on specific topic | You + 1 agent |
| **CEO Sync** | Strategic alignment | You + CEO |
| **Exec Meeting** | Business decisions | 5 executives |
| **Tech Meeting** | Architecture, quality | 4 tech leads |
| **Project Meeting** | Sprint coordination | PM + dev team |
| **All-Hands** | Company alignment | All 12 agents |
| **Idea Review** | Evaluate submissions | 6 key agents |
| **Strategy** | Big decisions | Custom selection |

### Getting Good Results

**Be Specific:**
```bash
# Too vague
python orchestrator.py 1on1 --agent cfo --topic "Help with money"

# Better
python orchestrator.py 1on1 --agent cfo --topic "Should I offer annual billing at 20% discount?"
```

**Provide Context:**
```bash
# Add context files to context/ directory
# Reference them in meetings
python orchestrator.py 1on1 --agent cito --topic "Review the architecture in context/tech-spec.md"
```

**Use the Right Agent:**

| Question Type | Best Agent |
|---------------|------------|
| Should we build this? | CEO, CITO |
| How much will it cost? | CFO, Dev Lead |
| Is this legal? | Legal |
| How do we market this? | Marketing |
| What's the technical approach? | CITO, Dev Lead |
| How should the UI work? | Design Lead |
| How do we test this? | QA Lead |
| How do we manage the project? | PM |
| How do we keep clients happy? | Customer Success |
| How do we support users? | Support |

---

## Common Workflows

### New Project from Idea to Launch

```bash
# 1. Submit idea
python orchestrator.py ideas add --name "TaskMaster" --description "Task management app" \
  --submitter-name "You" --submitter-email "you@example.com"

# 2. Review idea
python orchestrator.py idea-review --idea context/pending_ideas/taskmaster.md

# 3. Technical planning
python orchestrator.py tech-meeting --topic "TaskMaster architecture"

# 4. Create project (via dashboard)
# Projects > New Project

# 5. Weekly check-ins
python orchestrator.py project-meeting --project "TaskMaster"

# 6. Launch review
python orchestrator.py exec-meeting --topic "TaskMaster launch readiness"

# 7. Post-launch retro
python orchestrator.py retro --project "TaskMaster"
```

### Handling a Client Inquiry

```bash
# 1. Add client
python orchestrator.py clients add --name "John Smith" --company "Acme Corp" \
  --email "john@acme.com"

# 2. Review their idea
python orchestrator.py idea-review --idea context/pending_ideas/acme-request.md

# 3. Scope and estimate
python orchestrator.py meeting --topic "Acme Corp project scope" \
  --agents cfo,cito,dev_lead,pm

# 4. Prepare proposal
python orchestrator.py 1on1 --agent sales --topic "Draft proposal for Acme Corp"
```

### Monthly Business Review

```bash
# 1. Generate reports
python orchestrator.py report all

# 2. Executive review
python orchestrator.py exec-meeting --topic "Monthly business review"

# 3. Technical review
python orchestrator.py tech-meeting --topic "Technical debt and improvements"

# 4. Strategic planning
python orchestrator.py ceo-sync --topic "Next month priorities"
```

### Pivoting Your Business Focus (Using CEO Chat)

When you need to change strategic direction across the entire team:

1. **Start a CEO Chat** - Go to `/agents/ceo/chat`
2. **Explain Your New Direction**
   ```
   You: "We're pivoting from B2C to B2B enterprise. All agents need to
   adjust their thinking and recommendations accordingly."
   ```
3. **CEO Proposes Actions** - The CEO will suggest updates to agents
4. **Confirm Each Action** - Review and approve the changes
5. **Verify Updates** - Check agent portals to see new instructions

Example conversation:
```
You: "Update all agents to focus on B2B enterprise instead of B2C"

CEO: "I'll broadcast new instructions to all agents emphasizing B2B enterprise focus.

[ACTION: broadcast_to_agents]
{"agent_ids": "all", "instruction": "Our focus is now B2B enterprise clients. Prioritize scalability, security, compliance, and enterprise sales cycles in all recommendations.", "append": true}
[/ACTION]"

→ Click "Confirm"
→ All 12 agents receive updated instructions
```

---

## Customizing Your Company

The RRL AI Orchestrator can be customized to match any business type, not just software development.

### Changing Company Settings

Access settings via the **Settings** menu (gear icon) > **Company Settings**, or navigate to `/settings`.

You can customize:

| Setting | Description |
|---------|-------------|
| **Company Name** | Appears in the navigation bar and throughout the dashboard |
| **Company Tagline** | Shows in the footer, describing your business |
| **Industry Focus** | Adapts agent roles and suggestions to your business type |

### Industry Presets

Choose from pre-configured industry presets:

| Industry | Best For |
|----------|----------|
| **Software Development** | App studios, dev agencies, tech startups |
| **Marketing Agency** | Digital marketing, advertising, brand agencies |
| **Consulting Firm** | Business, management, and strategy consulting |
| **E-commerce Business** | Online retail, marketplaces, D2C brands |
| **Creative Agency** | Design studios, media production, creative services |
| **Professional Services** | Accounting, law firms, architecture firms |
| **Custom** | Build your own configuration from scratch |

Each preset adjusts agent roles to match your industry. For example:
- In a **Marketing Agency**, the CFO focuses on campaign ROI and client billing
- In a **Consulting Firm**, the PM emphasizes engagement management
- In an **E-commerce Business**, the Sales agent handles vendor and supplier relations

### Advanced Customization

For deeper customization:

1. **Edit agent prompts** - Modify files in `agents/` folder to change how agents think and respond
2. **Update AGENT_INFO** - Edit `webapp/app.py` to change agent descriptions in portals
3. **Create custom presets** - Add new industry configurations in `src/data_store.py`

---

## Tips for Success

1. **Start with 1:1s** - Get comfortable talking to individual agents before running group meetings

2. **Use the Dashboard Daily** - Check stats, review recent activity, stay organized

3. **Document Decisions** - All meeting decisions are saved; reference them later

4. **Iterate on Topics** - If an answer isn't helpful, rephrase or provide more context

5. **Mix CLI and Web** - Both CLI and web support group meetings; web is more visual, CLI is faster

6. **Review Transcripts** - Meeting transcripts in `meetings/` folder contain valuable insights

7. **Customize Your Company** - Use Settings to rebrand and adapt to your industry

8. **Use CEO Chat for System Changes** - Let the CEO manage agent updates and settings through conversation

9. **Customize Agent Instructions** - Add custom instructions via Settings to tailor each agent to your business

10. **Use Web Group Meetings** - For visual discussions with multiple agents, use the web-based group meeting feature at `/group-meetings/new`

---

## Getting Help

- **In-app:** Check the Settings menu for quick links
- **Documentation:** See `docs/` folder for detailed guides
- **Issues:** Report bugs at https://github.com/imcmurray/RRL/issues

---

## What's Next?

Once you're comfortable with the basics:

1. **Rebrand for your business** - Go to Settings and customize company name, tagline, and industry
2. **Customize agent prompts** - Edit files in `agents/` to refine agent personalities
3. **Set up recurring meetings** - Establish consistent check-ins with your AI team
4. **Integrate with your tools** - Use the JSON data stores in `data/*.json`
5. **Build custom reports** - Extend the reporting system for your specific needs

The AI Orchestrator grows with you - start simple and add complexity as needed.
