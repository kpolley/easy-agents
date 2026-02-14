from claude_agent_sdk import query, ClaudeAgentOptions, Message
from typing import Optional
import os
from dotenv import load_dotenv

# If .env exists, load it
if os.path.exists(".env"):
    load_dotenv()

# Typical MCP config
# https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line-mcp-understanding-config.html
mcp_config = {
    "mcpServers": {
        "panther": {
            "command": "docker",
            "args": [
                "run",
                "-i",
                "-e",
                "PANTHER_INSTANCE_URL",
                "-e",
                "PANTHER_API_TOKEN",
                "--rm",
                "ghcr.io/panther-labs/mcp-panther",
            ],
            "env": {
                "PANTHER_INSTANCE_URL": os.getenv("PANTHER_INSTANCE_URL"),
                "PANTHER_API_TOKEN": os.getenv("PANTHER_API_TOKEN"),
            },
        },
        "github": {
            "type": "http",
            "url": "https://api.githubcopilot.com/mcp/",
            "headers": {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"},
        },
        "github_extended": {
            "command": "uv",
            "args": ["run", "mcps/github_extended.py"],
            "env": {"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")},
        },
        "slack": {
            "command": "docker",
            "args": [
                "run",
                "-i",
                "--rm",
                "-e",
                "SLACK_BOT_TOKEN",
                "-e",
                "SLACK_TEAM_ID",
                "-e",
                "SLACK_CHANNEL_IDS",
                "mcp/slack",
            ],
            "env": {
                "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN"),
                "SLACK_TEAM_ID": os.getenv("SLACK_TEAM_ID"),
                "SLACK_CHANNEL_IDS": os.getenv("SLACK_CHANNEL_IDS"),
            },
        },
        "linear": {
            "command": "npx",
            "args": ["-y", "mcp-remote", "https://mcp.linear.app/sse"],
        },
        "virustotal": {
            "command": "npx",
            "args": ["@burtthecoder/mcp-virustotal"],
            "env": {
                "VIRUSTOTAL_API_KEY": os.getenv("VIRUSTOTAL_API_KEY"),
            },
        },
        "jira": {
            "command": "uv",
            "args": ["run", "mcps/jira.py"],
            "env": {
                "JIRA_HOST": os.getenv("JIRA_HOST"),
                "JIRA_USERNAME": os.getenv("JIRA_USERNAME"),
                "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN"),
            },
        },
    }
}


class Agent:
    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str,
        prompt: str,
        mcp_servers: list[str],
        allowed_tools: Optional[list[str]] = None,
    ):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.prompt = prompt
        self.mcp_servers: dict[str, dict] = {
            server: mcp_config["mcpServers"][server]
            for server in mcp_servers
            if server in mcp_config["mcpServers"]
        }
        self.allowed_tools: Optional[list[str]] = allowed_tools
        self._claude_agent_options = ClaudeAgentOptions(
            permission_mode="bypassPermissions",
            mcp_servers=self.mcp_servers,
            mcp_tools=self.allowed_tools,
            system_prompt=self.system_prompt,
        )

    async def run(self) -> list[Message]:
        messages = []
        async for message in query(
            prompt=self.prompt, options=self._claude_agent_options
        ):
            print(message)
            messages.append(message)
        return messages
