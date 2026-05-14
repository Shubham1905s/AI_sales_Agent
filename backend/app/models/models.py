import enum


class LeadStatus(str, enum.Enum):
    new = "new"
    scored = "scored"
    outreach_ready = "outreach_ready"
    contacted = "contacted"
    replied = "replied"
    converted = "converted"
    disqualified = "disqualified"
