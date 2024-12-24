from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ad3569f77f64"
down_revision = "5fb1a2a9a098"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("forum_categories")
    op.drop_table("forum_polls")
    op.drop_table("forum_poll_choices")
    op.drop_table("forum_post_votes")

    op.create_table(
        "forum_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "forum_polls",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("question", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["topic_id"], ["forum_topics.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "forum_poll_choices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("poll_id", sa.Integer(), nullable=False),
        sa.Column("choice_text", sa.String(length=255), nullable=False),
        sa.Column("votes", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["poll_id"], ["forum_polls.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "forum_post_votes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("vote_type", sa.String(length=10), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["forum_posts.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("forum_topics", schema=None) as batch_op:
        batch_op.add_column(sa.Column("category_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_forum_topics_category_id", "forum_categories", ["category_id"], ["id"])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("forum_topics", schema=None) as batch_op:
        batch_op.drop_constraint("fk_forum_topics_category_id", type_="foreignkey")
        batch_op.drop_column("category_id")

    op.drop_table("forum_post_votes")
    op.drop_table("forum_poll_choices")
    op.drop_table("forum_polls")
    op.drop_table("forum_categories")
    # ### end Alembic commands ###
