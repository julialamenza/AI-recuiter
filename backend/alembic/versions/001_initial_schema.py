"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-06

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "candidates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("cv_storage_path", sa.Text(), nullable=False),
        sa.Column("cv_mime_type", sa.String(128), nullable=False),
        sa.Column("cv_extracted_text", sa.Text(), nullable=True),
        sa.Column("extracted_profile", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("raw_description", sa.Text(), nullable=False),
        sa.Column("structured_requirements", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "screenings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("reasons", postgresql.JSONB(), nullable=False),
        sa.Column("summary_markdown", sa.Text(), nullable=False),
        sa.Column("model_recommendation", sa.String(32), nullable=False),
        sa.Column("human_decision", sa.String(32), nullable=True),
        sa.Column("human_decision_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_confirmed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_screenings_candidate_id", "screenings", ["candidate_id"])
    op.create_index("ix_screenings_job_id", "screenings", ["job_id"])

    op.create_table(
        "recruiter_availability",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.String(64), nullable=False, unique=True),
        sa.Column("weekly_rules", postgresql.JSONB(), nullable=False),
        sa.Column("timezone", sa.String(64), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "interview_proposals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("screening_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("proposed_slots", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("candidate_selected_slot", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["screening_id"], ["screenings.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_interview_proposals_screening_id", "interview_proposals", ["screening_id"])


def downgrade() -> None:
    op.drop_index("ix_interview_proposals_screening_id", table_name="interview_proposals")
    op.drop_table("interview_proposals")
    op.drop_table("recruiter_availability")
    op.drop_index("ix_screenings_job_id", table_name="screenings")
    op.drop_index("ix_screenings_candidate_id", table_name="screenings")
    op.drop_table("screenings")
    op.drop_table("jobs")
    op.drop_table("candidates")
