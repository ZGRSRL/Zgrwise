"""Add priority and is_read fields

Revision ID: 002_add_priority_isread
Revises: 001_fix_rss_models
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_priority_isread'
down_revision = '001_fix_rss_models'
branch_labels = None
depends_on = None


def upgrade():
    # Add priority and is_read fields to articles table
    op.add_column('articles', sa.Column('priority', sa.SmallInteger(), server_default='50', nullable=False))
    op.add_column('articles', sa.Column('is_read', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('articles', sa.Column('source_domain', sa.Text(), nullable=True))
    op.add_column('articles', sa.Column('guid', sa.String(64), nullable=True))
    
    # Add weight field to rss_feeds table
    op.add_column('rss_feeds', sa.Column('weight', sa.SmallInteger(), server_default='50', nullable=False))
    
    # Create indexes for better performance
    op.execute("CREATE INDEX IF NOT EXISTS idx_articles_priority ON articles(priority DESC)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_articles_unread ON articles(is_read) WHERE is_read = FALSE")
    op.execute("CREATE INDEX IF NOT EXISTS idx_articles_guid ON articles(guid)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_articles_domain ON articles(source_domain)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_rss_feeds_weight ON rss_feeds(weight DESC)")


def downgrade():
    # Drop indexes
    op.execute("DROP INDEX IF EXISTS idx_articles_priority")
    op.execute("DROP INDEX IF EXISTS idx_articles_unread")
    op.execute("DROP INDEX IF EXISTS idx_articles_guid")
    op.execute("DROP INDEX IF EXISTS idx_articles_domain")
    op.execute("DROP INDEX IF EXISTS idx_rss_feeds_weight")
    
    # Drop columns
    op.drop_column('articles', 'source_domain')
    op.drop_column('articles', 'guid')
    op.drop_column('articles', 'is_read')
    op.drop_column('articles', 'priority')
    op.drop_column('rss_feeds', 'weight')