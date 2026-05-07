import enum


class ModelRecommendation(str, enum.Enum):
    reject = "reject"
    shortlist = "shortlist"
    manual_review = "manual_review"


class HumanDecision(str, enum.Enum):
    reject = "reject"
    shortlist = "shortlist"
    manual_review = "manual_review"


class ProposalStatus(str, enum.Enum):
    draft = "draft"
    sent = "sent"
    candidate_responded = "candidate_responded"
