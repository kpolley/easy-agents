# Easy Agents

![Easy Agents](https://static.kpolley.com/easyagents.png)

A novel approach to automation that replaces traditional scripting with simple natural language instructions. Powered by Claude Code and MCP tool-calling.

## Overview

Easy Agents is a framework designed to make it as easy as possible for teams to build intelligent automation agents. Instead of writing complex scripts, you define your automation logic using natural language instructions. 

Use this as a template to build agentic workflows tailored to your specific environment and use case.

### How it Works

Define your agent's behavior with simple natural language:

```
You are an expert security agent that is responsible for investigating security alerts.

High level steps to accomplish your task:
1. Look up the alert with the given id
2. Perform an extremely in-depth analysis of the alert
3. Generate a detailed report of your findings
4. If the alert is a valid alert, send the report to the slack channel #security-alerts
```

That's it! Your agent is ready to handle this complex and ambiguous security workflow automatically.

## Real-World Examples

This repository includes four working examples that demonstrate the framework's capabilities. It utilizes multiple 3rd party MCP servers including [Panther Security Monitoring](https://github.com/panther-labs/mcp-panther), [VirusTotal](https://github.com/BurtTheCoder/mcp-virustotal), [Github](https://github.com/github/github-mcp-server), [Linear](https://linear.app/changelog/2025-05-01-mcp), [Slack](https://github.com/modelcontextprotocol/servers-archived/tree/main/src/slack), and custom Jira MCP servers.

While these examples are cybersecurity focused, this framework can be used to build agents for any team such as those in product engineering or customer support.

### [Security Alert Investigator Agent](main.py#L28-L53)
This agent triages incoming security alerts by correlating events across multiple sources, assessing risk levels, and routing to appropriate teams. The agent reads the alert context, investigates related events, and makes intelligent decisions about severity and response.

### [Application Security Agent](main.py#L56-L85)
This agent reviews GitHub Advanced Security code-scanning alerts and automatically creates fix PRs for valid issues. It even runs tests and linters to ensure all tests pass, and assigns the right reviewers to the PR. 

### [Supply Chain Security Agent](main.py#L88-L118)
This agent triages Github Dependabot alerts by evaluating vulnerability impact, updating packages to secure versions, ensuring tests pass, and managing the entire pull request workflow.

### [Weekly Summary Agent](main.py#L121-L140)
Every Sunday, this agent reviews Linear tickets and projects for their team. It writes a report on current projects, what got done that week and by whom.  

### [Jira Ticket Agent](main.py#L143-L170)
This agent creates and manages Jira tickets based on natural language instructions. It can create tickets with appropriate fields, set priorities, assignees, and labels, and send confirmations to Slack channels.

## Why This Approach Works

**Claude Code excels at intelligent task orchestration.** It transforms high-level goals into detailed action plans, adapts when obstacles arise, and thinks critically through complex problems. With the right tools and clear instructions, it can automate workflows that would typically require hundreds of lines of custom code—making it the ideal MCP client for both technical and operational tasks.

**MCP makes tool integration effortless.** The Model Context Protocol creates a standardized way for AI to interact with external tools, making integrations as simple as configuration changes ([example](https://github.com/kpolley/easy-agents/pull/1))

**Natural language is maintainable.** Your operational playbooks become your automation logic. Team members can easily understand, modify, and extend workflows without wrestling with complex code and 3rd party APIs.

## Getting Started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) for dependency management
- [Claude Code](https://claude.ai/code) for agent execution

### Installation

1. Clone this repository or [create a template](https://github.com/new?template_name=easy-agents&template_owner=kpolley):
```bash
git clone https://github.com/kpolley/easy-agents.git
cd easy_agents
```

2. Install dependencies:
```bash
uv sync
```

3. Start the development server:
```bash
uv run fastapi dev main.py
```

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# GitHub Integration
GITHUB_TOKEN=your-github-token

# Slack Integration
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_TEAM_ID=your-slack-team-id
SLACK_CHANNEL_IDS=channel1,channel2

# Panther Security Monitoring
PANTHER_INSTANCE_URL=https://your-instance.runpanther.io
PANTHER_API_TOKEN=your-panther-api-token

# VirusTotal
VIRUSTOTAL_API_KEY=your-virustotal-api-key

# Jira Integration
JIRA_HOST=https://your-instance.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-jira-api-token
```

**Note**: The Jira integration requires:
1. A Jira Cloud instance
2. An API token generated from your Atlassian account
3. Appropriate permissions to create and manage issues in the target project

### Creating Custom Agents

Creating a new agent is as simple as:

1. Define your agent's behavior in natural language
2. Specify the MCP servers it needs access to
3. Deploy via the provided FastAPI endpoints or cronjob triggers

### Creating Custom MCP Servers

Extend your agent's capabilities by creating custom MCP servers with [FastMCP](https://github.com/jlowin/fastmcp). See [mcps/github_extended.py](mcps/github_extended.py) as an example.

## Production Deployment
See [DEPLOYMENT.md](./DEPLOYMENT.md) for guidance.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

Some ideas we have in mind:
* More examples and use cases (perhaps from other operational areas such as customer support)
* Human-in-the-loop interactions (e.g., Slack message an admin with interactive buttons and wait for their response)

