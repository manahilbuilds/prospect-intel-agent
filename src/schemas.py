"""Pydantic schemas for structured prospect intelligence extraction."""

from pydantic import BaseModel, Field


class PainPoint(BaseModel):
    """A likely operational or growth bottleneck inferred from the prospect's site."""

    title: str = Field(description="Short, specific name of the bottleneck or pain point.")
    evidence: str = Field(
        description="What on the website suggests this pain point or opportunity."
    )
    automation_opportunity: str = Field(
        description="How an AI agent or Python automation workflow could solve this."
    )


class ProspectReport(BaseModel):
    """Structured intelligence brief for a target B2B company."""

    company_name: str = Field(description="Official name of the company.")
    industry: str = Field(description="Primary industry or vertical.")
    target_audience: str = Field(description="Who the company sells to (ICP).")
    core_offer: str = Field(
        description="Concise 1-2 sentence summary of their main product or service."
    )
    likely_pain_points: list[PainPoint] = Field(
        description="2 to 3 specific operational bottlenecks where AI automation helps."
    )
    cold_outreach_hook: str = Field(
        description=(
            "A short, personalized 2-3 sentence outreach opener referencing a real detail "
            "from their website (no generic fluff)."
        )
    )
