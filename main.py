from fastapi import FastAPI
from agent import Agent
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import asynccontextmanager
from utils.cron import cron, cron_jobs


# This is a FastAPI lifecycle manager that starts the cron job scheduler when the app starts
# and stops it when the app stops
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register all decorated cron jobs
    for func, trigger in cron_jobs:
        scheduler.add_job(func, trigger)

    scheduler.start()

    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)  # for webhook triggers
scheduler = AsyncIOScheduler()  # for cron job triggers


@app.get("/security-alert-agent/{alert_id}")
async def security_alert_agent(alert_id: str):
    system_prompt = """
    You are an expert security agent that is responsible for investigating security alerts from our SIEM.
    
    High level steps to accomplish your task:
    1. Look up the alert with the given id
    2. perform an extremely in-depth analysis of the alert. Leave no stone unturned. Consider all possible angles and scenarios and correlate the alert with other alerts and events from other sources. 
    3. Generate a detailed report of your findings 
    4. Send the report to the slack channel #security-alerts (channel ID: CXXXXX).

    Things to remember:
    - Do not assume that just because we received an alert that the alert is valid or of the correct severity. Perform a thorough analysis of the alert to determine if the alert is valid and of the correct severity. You may change the severity if you think it is incorrect.
    - The report should include alert title, severity, event timelime, any notable details, and whether you think the alert is malicious or benign. 
    """

    agent = Agent(
        name="security-alert-agent",
        description="Agent for handling security alerts from our SIEM",
        system_prompt=system_prompt,
        prompt=f"security alert ID: {alert_id}",
        mcp_servers=["panther", "virustotal", "slack"],
    )

    asyncio.create_task(agent.run())
    return {"status": "task started"}


@app.get("/code-scanning-alert-agent/{repo_owner}/{repo_name}/{alert_id}")
async def code_scanning_alert_agent(repo_owner: str, repo_name: str, alert_id: str):
    system_prompt = """
    You are a security agent that is responsible for analyzing and fixing code-scanning security alerts.
    
    High level steps to accomplish your task:
    1. Look up the alert with the given id
    2. Determine if the vulnerability is a false positive, not applicable, or so low risk that it is not worth fixing. Have a thoughtful and valid reason for your decision.
    3. If it is a false positive, not applicable or low risk, do nothing other than explain why
    4. If it is not a false positive, create a fix PR
    5. Find the engineer who introduced the vulnerability via git blame and request a PR review from them. No additional comments on the PR is necessary. 

    Things to remember:
    - Do not assume that just because we received an alert that the alert is valid or of the correct severity. Perform a thorough analysis of the alert to determine if the alert is valid and of the correct severity.
    - If the vulnerability is not part of our core product (ex. internal scripts and tools) then it extremely low risk and should be ignored.
    - Be sure to run `just` commands to ensure all tests pass before creating a PR.
    - Use git worktrees so multiple agents can work on the same repo without conflicts. Create the worktree in the tmp directory ($CWD/tmp). The branch name should include the alert ID.
    - Ensure you pull latest from main branch before making any code changes.
    - Add "Created with Claude Code Security Agent 🤖. Any issues or questions please contact Kyle" to the PR description and any comments.
    """
    agent = Agent(
        name="code-scanning-alert-agent",
        description="Agent for handling code-scanning security alerts and creating fix PRs",
        system_prompt=system_prompt,
        prompt=f"code-scanning alert ID: {alert_id} repo: {repo_owner}/{repo_name}",
        mcp_servers=["github", "github_extended"],
    )

    asyncio.create_task(agent.run())
    return {"status": "task started"}


@app.get("/dependabot-alert-agent/{repo_owner}/{repo_name}/{alert_id}")
async def dependabot_alert_agent(repo_owner: str, repo_name: str, alert_id: str):
    system_prompt = """
    You are a security agent that is responsible for analyzing and fixing dependabot security alerts.
    
    High level steps to accomplish your task:
    1. Look up the alert with the given id
    2. Determine if the vulnerability is a false positive, not applicable, or so low risk that it is not worth fixing. Have a thoughtful and valid reason for your decision.
    3. If it is a false positive, not applicable or low risk, do nothing other than explain why
    4. If it is not a false positive, update the package version to the latest non-vulnerable version. Ensure to update the lockfile as well by running the appropiate package manager command.
    5. Create a PR with the updated package version and tag @kpolley as a reviewer

    Things to remember:
    - Do not assume that just because we received an alert that the alert is valid or of the correct severity. Perform a thorough analysis of the alert to determine if the alert is valid and of the correct severity.
    - If the vulnerability is not part of our core product (ex. internal scripts and tools) then it extremely low risk and should be ignored.
    - Be sure to run `just` commands to ensure all tests pass before creating a PR.
    - Use git worktrees so multiple agents can work on the same repo without conflicts. Create the worktree in the tmp directory ($CWD/tmp). The branch name should include the alert ID.
    - Ensure you pull latest from main branch before making any code changes.
    - Add "Created with Claude Code Security Agent 🤖. Any issues or questions please contact Kyle" to the PR description and any comments.
    """

    agent = Agent(
        name="dependabot-alert-agent",
        description="Agent for handling dependabot security alerts and updating package versions",
        system_prompt=system_prompt,
        prompt=f"dependabot alert ID: {alert_id} repo: {repo_owner}/{repo_name}",
        mcp_servers=["github", "github_extended"],
    )

    asyncio.create_task(agent.run())
    return {"status": "task started"}


@cron(CronTrigger(day_of_week="sun", hour=17, minute=0))
async def weekly_update_agent(team_name: str = "SEC"):
    system_prompt = """
    You are an agent that is responsible for summarizing what the team got done this week.

    High level steps to accomplish your task:
    1. Look up the linear team with the given name
    2. Summarize what projects are in progress and what tasks were completed this week.
    3. Send the summary to the slack channel #updates (channel ID: CXXXXXX)
    
    """
    agent = Agent(
        name=f"weekly-update-agent-{team_name}",
        description="Agent for summarizing what the team got done this week",
        system_prompt=system_prompt,
        prompt=f"team: {team_name}",
        mcp_servers=["linear", "slack"],
    )
    asyncio.create_task(agent.run())
    return {"status": "task started"}


@app.get("/jira-ticket-agent/{project_key}")
async def jira_ticket_agent(project_key: str):
    system_prompt = """
    You are a Jira ticket creation agent responsible for creating and managing tickets.
    
    High level steps:
    1. Analyze the provided ticket information
    2. Create a Jira ticket with appropriate fields
    3. Set priority, assignee, and labels as needed
    4. Send confirmation to Slack channel
    
    Things to remember:
    - Use appropriate issue types (Bug, Story, Task, etc.)
    - Set correct priority levels
    - Include detailed descriptions and acceptance criteria
    - Always confirm ticket creation by sending a message to Slack
    """
    
    agent = Agent(
        name="jira-ticket-agent",
        description="Agent for creating and managing Jira tickets",
        system_prompt=system_prompt,
        prompt=f"Create ticket in project: {project_key}",
        mcp_servers=["jira", "slack"],
    )
    
    asyncio.create_task(agent.run())
    return {"status": "task started"}
