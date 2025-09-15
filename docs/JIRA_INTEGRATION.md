# Jira Integration Guide

This guide covers how to set up and use the Jira MCP server integration in easy-agents for automated ticket creation and management.

## Overview

The Jira integration provides a comprehensive set of tools for interacting with Jira Cloud instances through the Model Context Protocol (MCP). It enables AI agents to create, update, search, and manage Jira issues automatically based on natural language instructions.

## Features

- **Create Issues**: Create new Jira tickets with customizable fields
- **Read Issues**: Retrieve existing issues by key
- **Update Issues**: Modify issue fields and properties
- **Search Issues**: Query issues using JQL (Jira Query Language)
- **Add Comments**: Add comments to existing issues
- **Transition Issues**: Move issues between different statuses
- **Slack Integration**: Send notifications to Slack channels

## Prerequisites

Before setting up the Jira integration, ensure you have:

1. **Jira Cloud Instance**: Access to a Jira Cloud instance (not Jira Server/Data Center)
2. **Admin Permissions**: Ability to create API tokens and manage project permissions
3. **Project Access**: Appropriate permissions to create and manage issues in target projects

## Setup Instructions

### Step 1: Generate Jira API Token

1. Log in to your Jira Cloud instance
2. Navigate to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
3. Click "Create API token"
4. Give your token a descriptive name (e.g., "easy-agents-integration")
5. Copy the generated token and store it securely

### Step 2: Configure Environment Variables

Add the following variables to your `.env` file:

```bash
# Jira Integration
JIRA_HOST=https://your-instance.atlassian.net
JIRA_USERNAME=your-email@company.com
JIRA_API_TOKEN=your-api-token-here
```

**Important Notes:**
- `JIRA_HOST`: Your Jira Cloud instance URL (without trailing slash)
- `JIRA_USERNAME`: Your Atlassian account email address
- `JIRA_API_TOKEN`: The API token generated in Step 1

### Step 3: Verify Configuration

Test your configuration by running:

```bash
uv run python -c "import mcps.jira; print('Jira MCP server configured successfully')"
```

## Available Tools

### create_jira_issue

Creates a new Jira issue with specified fields.

**Parameters:**
- `project_key` (str): The project key (e.g., "PROJ", "DEV")
- `summary` (str): Issue summary/title
- `description` (str): Detailed issue description
- `issue_type` (str, optional): Issue type (default: "Task")
- `priority` (str, optional): Priority level (default: "Medium")
- `assignee` (str, optional): Username of assignee
- `labels` (list, optional): List of labels to apply

**Example:**
```python
await create_jira_issue(
    project_key="PROJ",
    summary="Fix login authentication bug",
    description="Users are unable to log in with valid credentials",
    issue_type="Bug",
    priority="High",
    assignee="john.doe",
    labels=["authentication", "critical"]
)
```

### get_jira_issue

Retrieves an existing Jira issue by its key.

**Parameters:**
- `issue_key` (str): The issue key (e.g., "PROJ-123")

**Example:**
```python
await get_jira_issue("PROJ-123")
```

### update_jira_issue

Updates fields of an existing Jira issue.

**Parameters:**
- `issue_key` (str): The issue key
- `fields` (dict): Dictionary of fields to update

**Example:**
```python
await update_jira_issue("PROJ-123", {
    "summary": "Updated issue title",
    "priority": {"name": "Critical"},
    "assignee": {"name": "jane.smith"}
})
```

### search_jira_issues

Searches for Jira issues using JQL.

**Parameters:**
- `jql` (str): JQL query string
- `max_results` (int, optional): Maximum number of results (default: 50)

**Example:**
```python
await search_jira_issues(
    jql="project = PROJ AND status = 'In Progress'",
    max_results=25
)
```

### add_jira_comment

Adds a comment to an existing Jira issue.

**Parameters:**
- `issue_key` (str): The issue key
- `comment_body` (str): The comment text

**Example:**
```python
await add_jira_comment("PROJ-123", "This issue has been resolved in the latest release.")
```

### transition_jira_issue

Transitions a Jira issue to a different status.

**Parameters:**
- `issue_key` (str): The issue key
- `transition_id` (str): The transition ID (numeric)
- `comment` (str, optional): Optional comment for the transition

**Example:**
```python
await transition_jira_issue("PROJ-123", "31", "Moving to Done - testing completed")
```

## Using the Jira Agent

The Jira integration includes a pre-built agent endpoint for automated ticket creation:

### Endpoint

```
GET /jira-ticket-agent/{project_key}
```

### Usage

1. **Via HTTP Request:**
   ```bash
   curl -X GET "http://localhost:8000/jira-ticket-agent/PROJ"
   ```

2. **Via Webhook:** Configure your monitoring systems to trigger this endpoint when tickets need to be created.

### Agent Behavior

The Jira ticket agent:
1. Analyzes provided ticket information
2. Creates a Jira ticket with appropriate fields
3. Sets priority, assignee, and labels as needed
4. Sends confirmation to Slack channel

## Custom Agent Examples

### Security Incident Ticket Agent

```python
@app.get("/security-incident-agent/{project_key}")
async def security_incident_agent(project_key: str):
    system_prompt = """
    You are a security incident response agent.
    
    Steps:
    1. Analyze the security incident details
    2. Create a high-priority Jira ticket
    3. Assign to security team
    4. Add security-related labels
    5. Notify team via Slack
    """
    
    agent = Agent(
        name="security-incident-agent",
        description="Agent for creating security incident tickets",
        system_prompt=system_prompt,
        prompt=f"Create security incident ticket in project: {project_key}",
        mcp_servers=["jira", "slack"],
    )
    
    asyncio.create_task(agent.run())
    return {"status": "task started"}
```

### Bug Report Agent

```python
@app.get("/bug-report-agent/{project_key}")
async def bug_report_agent(project_key: str):
    system_prompt = """
    You are a bug report processing agent.
    
    Steps:
    1. Analyze bug report details
    2. Create Jira bug ticket
    3. Set appropriate priority based on severity
    4. Assign to development team
    5. Add bug-related labels
    """
    
    agent = Agent(
        name="bug-report-agent",
        description="Agent for processing bug reports",
        system_prompt=system_prompt,
        prompt=f"Process bug report for project: {project_key}",
        mcp_servers=["jira", "slack"],
    )
    
    asyncio.create_task(agent.run())
    return {"status": "task started"}
```

## JQL Query Examples

The `search_jira_issues` tool supports JQL queries. Here are some common examples:

### Basic Queries
```jql
# All issues in a project
project = PROJ

# Issues assigned to a user
assignee = john.doe

# Issues created in the last week
created >= -1w

# High priority issues
priority = High
```

### Complex Queries
```jql
# Open bugs in a specific project
project = PROJ AND issuetype = Bug AND status != Done

# Issues assigned to me that are overdue
assignee = currentUser() AND duedate < now()

# Security-related issues
labels in (security, vulnerability) AND priority in (High, Critical)
```

## Error Handling

The Jira MCP server includes comprehensive error handling:

- **Authentication Errors**: Invalid credentials or expired tokens
- **Permission Errors**: Insufficient permissions for requested operations
- **Validation Errors**: Invalid field values or missing required fields
- **Network Errors**: Connection issues or API timeouts

All errors are returned as structured JSON responses with appropriate error messages.

## Troubleshooting

### Common Issues

1. **"Unauthorized" Error**
   - Verify your API token is correct
   - Check that your username matches your Atlassian account email
   - Ensure the token hasn't expired

2. **"Forbidden" Error**
   - Check project permissions
   - Verify you have access to create issues in the target project
   - Ensure your account has appropriate roles

3. **"Not Found" Error**
   - Verify the Jira host URL is correct
   - Check that the project key exists
   - Ensure issue keys are valid

4. **"Bad Request" Error**
   - Check field values are valid
   - Verify required fields are provided
   - Ensure issue types and priorities exist in your Jira instance

### Debug Mode

Enable debug logging by setting the environment variable:

```bash
export LOG_LEVEL=DEBUG
```

## Security Considerations

- **API Token Security**: Store API tokens securely and rotate them regularly
- **Environment Variables**: Never commit `.env` files to version control
- **Permissions**: Use the principle of least privilege for Jira permissions
- **Network Security**: Ensure secure communication with Jira Cloud APIs

## Limitations

- **Jira Cloud Only**: This integration only supports Jira Cloud instances
- **API Rate Limits**: Jira Cloud has API rate limits that may affect high-volume operations
- **Field Customization**: Some custom fields may require additional configuration
- **Workflow Transitions**: Transition IDs are instance-specific and may need customization

## Support

For issues with the Jira integration:

1. Check the troubleshooting section above
2. Review Jira Cloud API documentation
3. Verify your configuration and permissions
4. Check the easy-agents logs for detailed error messages

## Related Documentation

- [Jira Cloud REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [JQL Reference](https://www.atlassian.com/software/jira/guides/expand-jira/jql)
- [Atlassian API Token Management](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)
