import re
import validators

from typing import AsyncGenerator
from google.adk.apps.app import App
from google.genai import types
from google.adk.agents import BaseAgent, LlmAgent, LoopAgent, SequentialAgent, ParallelAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.models.lite_llm import LiteLlm
from google.adk.events import Event, EventActions

from .utils import load_config, process_website_data
from .schemas import UrlAnalystOutput, HtmlAnalystOutput, ContentAnalystOutput, BrandAnalystOutput, ModeratorOutput

config = load_config()

# -------------------------------- Judge Agent ------------------------------- #
judgement_agent = LlmAgent(
    model=LiteLlm(model=config["judgement_agent"]["model"]),
    name=config["judgement_agent"]["name"],
    description=config["judgement_agent"]["description"],
    instruction=config["judgement_agent"]["instruction"],
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
                # moderator_output["final_verdict"] = "UNCERTAIN"
                raise ValueError("Final verdict is Finalized")

            yield Event(
                author=self.name,
                content=types.Content(
                    role=self.name,
                    parts=[types.Part(text="Debate should continue because of uncertainity in verdict.")],
                )
            )
        except Exception as e:
            yield Event(
                author=self.name,
                content=types.Content(
                    role=self.name,
                    parts=[types.Part(text="Verdict is finalized.")],
                ),
                actions=EventActions(escalate=True)
            )

# -------------------------- Debate Agent: Moderator ------------------------- #
moderator_agent = LlmAgent(
    model=LiteLlm(model=config["moderator_agent"]["model"]),
    name=config["moderator_agent"]["name"],
    description=config["moderator_agent"]["description"],
    instruction=config["moderator_agent"]["instruction"],
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
            last_event = ctx.session.events[-1].content
            valid_url = None
            if last_event and last_event.role == 'user':
                valid_url = last_event.parts[0].text
            
            if not valid_url:
                raise ValueError("No user input found")

            url_pattern = r"https?://[\w./?=-]+"
            match = re.search(url_pattern, valid_url)
            if not match:
                raise ValueError("No URL found in user query")

            fetch_url = match.group(0)  
            if not validators.url(fetch_url):
                raise ValueError("Invalid URL")

            url, cleaned_html, visible_text = process_website_data(valid_url)

            ctx.session.state["target_url"] = url
            ctx.session.state["html_content"] = cleaned_html
            ctx.session.state["visible_text"] = visible_text

            yield Event(
                author=self.name,
                content=types.Content(
                    role=self.name,
                    parts=[types.Part(text="URL processed successfully.")],
                ),
            )
        except Exception as e:
            ctx.session.state["is_valid_url"] = False
            yield Event(
                author=self.name,
                content=types.Content(
                    role=self.name,
                    parts=[types.Part(text="Invalid URL.")],
                ),
                actions=EventActions(escalate=True)
            )

# ------------------------------- Main Pipeline ------------------------------ #
class CrossCheckPipeline(SequentialAgent):
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        for agent in self.sub_agents:
            if ctx.session.state.get("is_valid_url") is False:
                return
            async for event in agent.run_async(ctx):
                    yield event

cross_check_pipeline = CrossCheckPipeline(
    name="cross_check_pipeline",
    sub_agents=[
        UrlPreProcessor(name="url_preprocessing_agent"),
        debate_loop,
        judgement_agent
    ]
)

root_agent = cross_check_pipeline
app = App(root_agent=root_agent, name="engine")