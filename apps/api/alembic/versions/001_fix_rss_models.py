"""Fix RSS models and add missing indexes

Revision ID: 001_fix_rss_models
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_fix_rss_models'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create rss_feeds table
    op.create_table('rss_feeds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('url', sa.String(length=1024), nullable=False),
        sa.Column('site', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rss_feeds_id'), 'rss_feeds', ['id'], unique=False)
    op.create_index(op.f('ix_rss_feeds_url'), 'rss_feeds', ['url'], unique=True)

    # Create rss_items table
    op.create_table('rss_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('feed_id', sa.Integer(), nullable=False),
        sa.Column('guid', sa.String(length=1024), nullable=False),
        sa.Column('link', sa.String(length=2048), nullable=True),
        sa.Column('title', sa.String(length=1024), nullable=True),
        sa.Column('content_text', sa.Text(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('fetched_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['feed_id'], ['rss_feeds.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('feed_id', 'guid', name='uq_rssitem_feed_guid')
    )
    op.create_index(op.f('ix_rss_items_feed_published'), 'rss_items', ['feed_id', 'published_at'], unique=False)
    op.create_index(op.f('ix_rss_items_id'), 'rss_items', ['id'], unique=False)
    op.create_index(op.f('ix_rss_items_title_gin'), 'rss_items', ['title'], unique=False, postgresql_using='gin')

    # Add missing indexes for performance
    op.create_index('idx_highlights_source_id', 'highlights', ['source_id'], unique=False)
    op.create_index('idx_embeddings_object_id', 'embeddings', ['object_id'], unique=False)
    op.create_index('idx_reviews_highlight_id', 'reviews', ['highlight_id'], unique=False)

    # Enable pg_trgm extension if not exists
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')


def downgrade():
    # Drop indexes
    op.drop_index('idx_reviews_highlight_id', table_name='reviews')
    op.drop_index('idx_embeddings_object_id', table_name='embeddings')
    op.drop_index('idx_highlights_source_id', table_name='highlights')
    
    # Drop tables
    op.drop_table('rss_items')
    op.drop_table('rss_feeds')