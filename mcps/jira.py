from fastmcp import FastMCP
import requests
import os
import base64

mcp = FastMCP("Jira Tools")


@mcp.tool
async def create_jira_issue(
    project_key: str,
    summary: str,
    description: str,
    issue_type: str = "Task",
    priority: str = "Medium",
    assignee: str = None,
    labels: list = None
):
    """Create a new Jira issue"""
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{os.getenv("JIRA_USERNAME")}:{os.getenv("JIRA_API_TOKEN")}'.encode()).decode()}",
        "Content-Type": "application/json",
    }
    
    data = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type},
            "priority": {"name": priority},
        }
    }
    
    if assignee:
        data["fields"]["assignee"] = {"name": assignee}
    if labels:
        data["fields"]["labels"] = labels
    
    response = requests.post(
        f"{os.getenv('JIRA_HOST')}/rest/api/3/issue",
        headers=headers,
        json=data,
    )
    return response.json()


@mcp.tool
async def get_jira_issue(issue_key: str):
    """Get a Jira issue by key"""
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{os.getenv("JIRA_USERNAME")}:{os.getenv("JIRA_API_TOKEN")}'.encode()).decode()}",
        "Content-Type": "application/json",
    }
    
    response = requests.get(
        f"{os.getenv('JIRA_HOST')}/rest/api/3/issue/{issue_key}",
        headers=headers,
    )
    return response.json()


@mcp.tool
async def update_jira_issue(issue_key: str, fields: dict):
    """Update a Jira issue"""
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{os.getenv("JIRA_USERNAME")}:{os.getenv("JIRA_API_TOKEN")}'.encode()).decode()}",
        "Content-Type": "application/json",
    }
    
    data = {"fields": fields}
    
    response = requests.put(
        f"{os.getenv('JIRA_HOST')}/rest/api/3/issue/{issue_key}",
        headers=headers,
        json=data,
    )
    return response.json()


@mcp.tool
async def search_jira_issues(jql: str, max_results: int = 50):
    """Search Jira issues using JQL"""
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{os.getenv("JIRA_USERNAME")}:{os.getenv("JIRA_API_TOKEN")}'.encode()).decode()}",
        "Content-Type": "application/json",
    }
    
    data = {
        "jql": jql,
        "maxResults": max_results,
        "fields": ["summary", "status", "assignee", "priority", "created", "updated"]
    }
    
    response = requests.post(
        f"{os.getenv('JIRA_HOST')}/rest/api/3/search",
        headers=headers,
        json=data,
    )
    return response.json()


@mcp.tool
async def add_jira_comment(issue_key: str, comment_body: str):
    """Add a comment to a Jira issue"""
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{os.getenv("JIRA_USERNAME")}:{os.getenv("JIRA_API_TOKEN")}'.encode()).decode()}",
        "Content-Type": "application/json",
    }
    
    data = {
        "body": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": comment_body
                        }
                    ]
                }
            ]
        }
    }
    
    response = requests.post(
        f"{os.getenv('JIRA_HOST')}/rest/api/3/issue/{issue_key}/comment",
        headers=headers,
        json=data,
    )
    return response.json()


@mcp.tool
async def transition_jira_issue(issue_key: str, transition_id: str, comment: str = None):
    """Transition a Jira issue to a different status"""
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{os.getenv("JIRA_USERNAME")}:{os.getenv("JIRA_API_TOKEN")}'.encode()).decode()}",
        "Content-Type": "application/json",
    }
    
    data = {
        "transition": {"id": transition_id}
    }
    
    if comment:
        data["update"] = {
            "comment": [
                {
                    "add": {
                        "body": {
                            "type": "doc",
                            "version": 1,
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": comment
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            ]
        }
    
    response = requests.post(
        f"{os.getenv('JIRA_HOST')}/rest/api/3/issue/{issue_key}/transitions",
        headers=headers,
        json=data,
    )
    return response.json()


if __name__ == "__main__":
    mcp.run()
