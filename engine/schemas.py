from pydantic import BaseModel, Field
from typing import Literal

class UrlAnalystOutput(BaseModel):
    Claim: Literal["PHISHING", "LEGITIMATE"] = Field(description="Your phishing/non-phishing assessment of the URL")
    confidence: str = Field(pattern=r"^(0(\.\d+)?|1(\.0+)?)$", description="A score between 0 and 1")
    reasoning: str = Field(description="Key suspicious or benign patterns you found")

class HtmlAnalystOutput(BaseModel):
    Claim: Literal["PHISHING", "LEGITIMATE"] = Field(description="Your assessment about the HTML structure indicating phishing or not")
    confidence: str = Field(pattern=r"^(0(\.\d+)?|1(\.0+)?)$", description="A score between 0 and 1")
    reasoning: str = Field(description="Relevant structural elements or tag patterns you found")

class ContentAnalystOutput(BaseModel):
    Claim: Literal["PHISHING", "LEGITIMATE"] = Field(description="Whether the page language seems phishing-related")
    confidence: str = Field(pattern=r"^(0(\.\d+)?|1(\.0+)?)$", description="A score between 0 and 1")
    reasoning: str = Field(description="Specific words, phrases, or sentence patterns that support your claim")

class BrandAnalystOutput(BaseModel):
    Claim: Literal["PHISHING", "LEGITIMATE"] = Field(description="Does the content attempt to impersonate a known brand?")
    confidence: str = Field(pattern=r"^(0(\.\d+)?|1(\.0+)?)$", description="A score between 0 and 1")
    reasoning: str = Field(description="Name(s) of impersonated brands and supporting context")
