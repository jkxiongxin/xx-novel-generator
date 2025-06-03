"""
添加脑洞生成器相关数据表
Author: AI Writer Team
Created: 2025-06-03
"""

from sqlalchemy import text
from app.core.database import get_db

def upgrade():
    """创建脑洞生成器相关数据表"""
    
    # 获取数据库连接
    db = next(get_db())
    
    try:
        # 创建脑洞生成历史表
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS brain_storm_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                generation_id VARCHAR(50) NOT NULL UNIQUE,
                topic VARCHAR(200) NOT NULL,
                creativity_level INTEGER DEFAULT 7,
                idea_count INTEGER DEFAULT 10,
                idea_types JSON,
                elements JSON,
                style VARCHAR(100),
                language VARCHAR(20) DEFAULT 'zh-CN',
                avoid_keywords JSON,
                reference_works JSON,
                ideas_generated INTEGER DEFAULT 0,
                generation_time REAL,
                model_used VARCHAR(100),
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                rating INTEGER,
                user_feedback TEXT,
                useful_ideas JSON,
                copied_count INTEGER DEFAULT 0,
                exported_count INTEGER DEFAULT 0,
                applied_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """))
        
        # 创建脑洞创意表
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS brain_storm_ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                history_id INTEGER NOT NULL,
                idea_id VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                idea_type VARCHAR(50),
                summary VARCHAR(500),
                potential_development TEXT,
                creativity_score REAL,
                practical_score REAL,
                tags JSON,
                related_elements JSON,
                copied_times INTEGER DEFAULT 0,
                user_rating INTEGER,
                is_favorite BOOLEAN DEFAULT FALSE,
                user_notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (history_id) REFERENCES brain_storm_history (id)
            )
        """))
        
        # 创建用户偏好表
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS brain_storm_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                default_creativity_level INTEGER DEFAULT 7,
                default_idea_count INTEGER DEFAULT 10,
                preferred_types JSON,
                favorite_elements JSON,
                default_style VARCHAR(100),
                auto_save_history BOOLEAN DEFAULT TRUE,
                enable_notifications BOOLEAN DEFAULT TRUE,
                show_creativity_scores BOOLEAN DEFAULT TRUE,
                enable_auto_suggestions BOOLEAN DEFAULT TRUE,
                preferred_layout VARCHAR(50) DEFAULT 'grid',
                items_per_page INTEGER DEFAULT 20,
                enable_dark_mode BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """))
        
        # 创建要素库表
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS brain_storm_elements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                display_name VARCHAR(100) NOT NULL,
                description TEXT,
                category VARCHAR(50) NOT NULL,
                usage_count INTEGER DEFAULT 0,
                effectiveness_score REAL DEFAULT 0.0,
                success_rate REAL DEFAULT 0.0,
                related_elements JSON,
                compatible_types JSON,
                example_usage TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                is_featured BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # 创建主题建议表
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS brain_storm_topic_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic VARCHAR(200) NOT NULL,
                description TEXT,
                category VARCHAR(50) NOT NULL,
                popularity INTEGER DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                expected_ideas INTEGER DEFAULT 10,
                related_topics JSON,
                sample_ideas JSON,
                recommended_elements JSON,
                is_active BOOLEAN DEFAULT TRUE,
                is_trending BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # 创建索引
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_brain_storm_history_user_id ON brain_storm_history (user_id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_brain_storm_history_generation_id ON brain_storm_history (generation_id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_brain_storm_ideas_history_id ON brain_storm_ideas (history_id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_brain_storm_elements_category ON brain_storm_elements (category)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_brain_storm_topic_suggestions_category ON brain_storm_topic_suggestions (category)"))
        
        # 初始化一些基础数据
        _insert_initial_elements(db)
        _insert_initial_topic_suggestions(db)
        
        db.commit()
        print("脑洞生成器数据表创建成功")
        
    except Exception as e:
        db.rollback()
        print(f"创建脑洞生成器数据表失败: {str(e)}")
        raise
    finally:
        db.close()


def _insert_initial_elements(db):
    """插入初始要素数据"""
    elements_data = [
        # 类型要素
        ('玄幻', '玄幻', '超自然力量和奇幻世界观', 'genre', 0, 8.5, 0.8),
        ('科幻', '科幻', '科学技术和未来世界', 'genre', 0, 8.0, 0.75),
        ('现代', '现代', '当代现实背景', 'genre', 0, 7.0, 0.7),
        ('古代', '古代', '历史古代背景', 'genre', 0, 7.5, 0.65),
        ('都市', '都市', '城市现代生活', 'genre', 0, 6.5, 0.6),
        
        # 主题要素
        ('爱情', '爱情', '情感和恋爱关系', 'theme', 0, 9.0, 0.9),
        ('冒险', '冒险', '探险和挑战', 'theme', 0, 8.5, 0.85),
        ('悬疑', '悬疑', '推理和谜团', 'theme', 0, 8.0, 0.8),
        ('复仇', '复仇', '报复和仇恨', 'theme', 0, 7.5, 0.75),
        ('成长', '成长', '角色发展和成熟', 'theme', 0, 8.5, 0.8),
        
        # 元素要素
        ('魔法', '魔法', '魔法力量和法术', 'element', 0, 9.0, 0.85),
        ('修仙', '修仙', '修炼和仙道', 'element', 0, 8.5, 0.8),
        ('异能', '异能', '超自然能力', 'element', 0, 8.0, 0.75),
        ('武侠', '武侠', '武功和江湖', 'element', 0, 7.5, 0.7),
        ('机甲', '机甲', '机械战甲', 'element', 0, 7.0, 0.65),
        
        # 风格要素
        ('轻松', '轻松', '轻快愉悦的氛围', 'style', 0, 7.0, 0.8),
        ('严肃', '严肃', '深刻严谨的风格', 'style', 0, 6.5, 0.7),
        ('幽默', '幽默', '诙谐有趣的表达', 'style', 0, 8.0, 0.85),
        ('黑暗', '黑暗', '阴暗压抑的氛围', 'style', 0, 7.0, 0.6),
        ('热血', '热血', '激情澎湃的感觉', 'style', 0, 8.5, 0.8),
    ]
    
    for name, display_name, description, category, usage_count, effectiveness_score, success_rate in elements_data:
        db.execute(text("""
            INSERT OR IGNORE INTO brain_storm_elements 
            (name, display_name, description, category, usage_count, effectiveness_score, success_rate, is_featured)
            VALUES (:name, :display_name, :description, :category, :usage_count, :effectiveness_score, :success_rate, :is_featured)
        """), {
            'name': name,
            'display_name': display_name,
            'description': description,
            'category': category,
            'usage_count': usage_count,
            'effectiveness_score': effectiveness_score,
            'success_rate': success_rate,
            'is_featured': effectiveness_score >= 8.0
        })


def _insert_initial_topic_suggestions(db):
    """插入初始主题建议数据"""
    topics_data = [
        ('穿越重生', '主角穿越或重生到另一个世界', 'classic', 95, 0, 0.85, 12),
        ('系统流', '主角获得系统辅助成长', 'classic', 90, 0, 0.8, 10),
        ('修仙成神', '主角修炼成仙或成神', 'classic', 85, 0, 0.75, 15),
        ('都市异能', '现代都市中的超能力者', 'modern', 80, 0, 0.7, 8),
        ('星际征途', '太空探索和星际战争', 'scifi', 75, 0, 0.65, 12),
        ('虚拟现实', '虚拟游戏世界的冒险', 'scifi', 70, 0, 0.6, 10),
        ('末世求生', '末日世界中的生存斗争', 'apocalypse', 85, 0, 0.8, 15),
        ('古代权谋', '古代宫廷政治斗争', 'historical', 65, 0, 0.55, 8),
        ('校园青春', '学校生活和青春恋情', 'youth', 60, 0, 0.7, 6),
        ('商战风云', '商业竞争和企业斗争', 'business', 55, 0, 0.5, 7),
    ]
    
    for topic, description, category, popularity, usage_count, success_rate, expected_ideas in topics_data:
        db.execute(text("""
            INSERT OR IGNORE INTO brain_storm_topic_suggestions 
            (topic, description, category, popularity, usage_count, success_rate, expected_ideas, is_trending)
            VALUES (:topic, :description, :category, :popularity, :usage_count, :success_rate, :expected_ideas, :is_trending)
        """), {
            'topic': topic,
            'description': description,
            'category': category,
            'popularity': popularity,
            'usage_count': usage_count,
            'success_rate': success_rate,
            'expected_ideas': expected_ideas,
            'is_trending': popularity >= 80
        })


def downgrade():
    """删除脑洞生成器相关数据表"""
    db = next(get_db())
    
    try:
        # 删除表（注意顺序，先删除有外键依赖的表）
        db.execute(text("DROP TABLE IF EXISTS brain_storm_ideas"))
        db.execute(text("DROP TABLE IF EXISTS brain_storm_history"))
        db.execute(text("DROP TABLE IF EXISTS brain_storm_preferences"))
        db.execute(text("DROP TABLE IF EXISTS brain_storm_elements"))
        db.execute(text("DROP TABLE IF EXISTS brain_storm_topic_suggestions"))
        
        db.commit()
        print("脑洞生成器数据表删除成功")
        
    except Exception as e:
        db.rollback()
        print(f"删除脑洞生成器数据表失败: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    upgrade()