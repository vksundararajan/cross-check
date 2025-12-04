import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import re
import validators

from typing import AsyncGenerator
from google.adk.apps.app import App
from google.adk.agents import BaseAgent, LlmAgent, LoopAgent, SequentialAgent, ParallelAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions

from utils import load_config, process_website_data
from schemas import UrlAnalystOutput, HtmlAnalystOutput, ContentAnalystOutput, BrandAnalystOutput, ModeratorOutput

config = load_config()

# -------------------------------- Judge Agent ------------------------------- #
judgement_agent = LlmAgent(
    model=LiteLlm(model=config["judge"]["model"]),
    name=config["judge"]["name"],
    description=config["judge"]["description"],
    instruction=config["judge"]["instruction"],
)

# ---------------------- Custom Agent: Consensus Checker --------------------- #
class ConsensusChecker(BaseAgent):
    def __init__(self, name: str):
        super().__init__(name=name)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        try:
            moderator_output = ctx.session.state.get("moderator_output")
            if moderator_output and moderator_output.get("final_verdict") != "UNCERTAIN":
                raise ValueError("Invalid URL")

            yield Event(author=self.name)
        except Exception as e:
            yield Event(author=self.name, actions=EventActions(escalate=True))

# -------------------------- Debate Agent: Moderator ------------------------- #
moderator_agent = LlmAgent(
    model=LiteLlm(model=config["moderator"]["model"]),
    name=config["moderator"]["name"],
    description=config["moderator"]["description"],
    instruction=config["moderator"]["instruction"],
    output_schema=ModeratorOutput,
    output_key="moderator_output"
)

# ------------------------ Debate Agents: Specialists ------------------------ #
url_analyst_agent = LlmAgent(
    model=LiteLlm(model=config["url_analyst"]["model"]),
    name=config["url_analyst"]["name"],
    description=config["url_analyst"]["description"],
    instruction=config["url_analyst"]["instruction"],
    output_schema=UrlAnalystOutput,
    output_key="url_assessment"
)

html_analyst_agent = LlmAgent(
    model=LiteLlm(model=config["html_analyst"]["model"]),
    name=config["html_analyst"]["name"],
    description=config["html_analyst"]["description"],
    instruction=config["html_analyst"]["instruction"],
    output_schema=HtmlAnalystOutput,
    output_key="html_assessment"
)

content_analyst_agent = LlmAgent(
    model=LiteLlm(model=config["content_analyst"]["model"]),
    name=config["content_analyst"]["name"],
    description=config["content_analyst"]["description"],
    instruction=config["content_analyst"]["instruction"],    
    output_schema=ContentAnalystOutput,
    output_key="content_assessment"
)

brand_analyst_agent = LlmAgent(
    model=LiteLlm(model=config["brand_analyst"]["model"]),
    name=config["brand_analyst"]["name"],
    description=config["brand_analyst"]["description"],
    instruction=config["brand_analyst"]["instruction"],    
    output_schema=BrandAnalystOutput,
    output_key="brand_assessment"
)

# -------------------------------- Debate Loop ------------------------------- #
debate_loop = LoopAgent(
    name="debate_loop_agent",
    sub_agents=[
        ParallelAgent(
            name="specialists_group",
            sub_agents=[
                url_analyst_agent, 
                html_analyst_agent, 
                content_analyst_agent, 
                brand_analyst_agent
            ]
        ),
        moderator_agent,
        ConsensusChecker(name="consensus_checking_agent")
    ],
    max_iterations=3
)

# ---------------------- Custom Agent: URL Preprocessor ---------------------- #
class UrlPreProcessor(BaseAgent):
    def __init__(self, name: str):
        super().__init__(name=name)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        try:
            last_event = ctx.session.history[-1] 
            user_query = last_event.content
            
            url_pattern = r"https?://[\w./?=-]+"
            match = re.search(url_pattern, user_query)
            if not match:
                raise ValueError("No URL found in user query")

            fetch_url = match.group(0)  
            if not validators.url(fetch_url):
                raise ValueError("Invalid URL")
            
            url, cleaned_html, visible_text = process_website_data(valid_url)

            ctx.session.state["target_url"] = url
            ctx.session.state["html_content"] = cleaned_html
            ctx.session.state["visible_text"] = visible_text

            yield Event(author=self.name)
        except Exception as e:
            yield Event(author=self.name, actions=EventActions(escalate=True))

# ------------------------------- Main Pipeline ------------------------------ #
cross_check_pipeline = SequentialAgent(
    name="cross_check_pipeline",
    sub_agents=[
        UrlPreProcessor(name="url_preprocessing_agent"),
        debate_loop,
        judgement_agent
    ]
)

root_agent = cross_check_pipeline
app = App(root_agent=root_agent, name="engine")