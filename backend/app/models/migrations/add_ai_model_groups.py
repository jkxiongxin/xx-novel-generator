"""
添加AI模型分组支持
Author: AI Writer Team
Created: 2025-06-02
"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    """添加AI模型分组相关字段"""
    # 添加分组相关字段到ai_model_config表
    op.add_column('ai_model_configs', sa.Column('group_name', sa.String(100), nullable=True, comment='配置分组名称'))
    op.add_column('ai_model_configs', sa.Column('group_description', sa.Text, nullable=True, comment='分组描述'))
    op.add_column('ai_model_configs', sa.Column('is_group_default', sa.Boolean, default=False, nullable=False, comment='是否为分组内默认模型'))
    
    # 创建索引以提高查询性能
    op.create_index('idx_ai_model_configs_group_name', 'ai_model_configs', ['group_name'])
    op.create_index('idx_ai_model_configs_group_default', 'ai_model_configs', ['group_name', 'is_group_default'])


def downgrade():
    """移除AI模型分组相关字段"""
    # 删除索引
    op.drop_index('idx_ai_model_configs_group_default', 'ai_model_configs')
    op.drop_index('idx_ai_model_configs_group_name', 'ai_model_configs')
    
    # 删除字段
    op.drop_column('ai_model_configs', 'is_group_default')
    op.drop_column('ai_model_configs', 'group_description')
    op.drop_column('ai_model_configs', 'group_name')