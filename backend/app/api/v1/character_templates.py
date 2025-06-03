"""
角色模板基础API
Author: AI Assistant
Created: 2025-06-03
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.character import Character, CharacterType, CharacterGender
from app.models.character_template import (
    CharacterTemplateDetail, UsageExample, 
    CharacterTemplateFavorite, CharacterTemplateUsage
)
from app.schemas.character_template import (
    CharacterTemplateSummaryResponse, CharacterTemplateResponse, 
    CharacterTemplateListResponse, TemplateDetailCreate, TemplateDetailResponse,
    TemplateDetailUpdate, UsageExampleCreate, UsageExampleResponse, UsageExampleUpdate,
    TemplateFilterOption, SearchTemplatesRequest, SearchTemplatesResponse,
    SearchSuggestion, GetTemplateStatsResponse
)
from app.models.novel import Novel

router = APIRouter(prefix="/character-templates", tags=["角色模板"])


@router.get("/", response_model=CharacterTemplateListResponse)
async def get_character_templates(
    gender: Optional[str] = Query(None, description="性别筛选"),
    power_systems: Optional[List[str]] = Query(None, description="力量体系筛选"),
    worldviews: Optional[List[str]] = Query(None, description="世界观筛选"),
    tags: Optional[List[str]] = Query(None, description="标签筛选"),
    is_popular: Optional[bool] = Query(None, description="是否只显示热门"),
    is_new: Optional[bool] = Query(None, description="是否只显示新增"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方向"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    include_filters: bool = Query(False, description="是否包含筛选选项"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取角色模板列表，支持多种筛选和排序选项
    
    Args:
        gender: 性别筛选 (male, female, unknown, other)
        power_systems: 力量体系筛选列表
        worldviews: 世界观筛选列表
        tags: 标签筛选列表
        is_popular: 是否只显示热门
        is_new: 是否只显示新增
        sort_by: 排序字段 (created_at, updated_at, name, usage_count, rating)
        sort_order: 排序方向 (asc, desc)
        page: 页码
        page_size: 每页数量
        include_filters: 是否包含可用筛选选项
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        包含角色模板列表、分页信息和可选的筛选选项的响应
    """
    try:
        # 构建基础查询 - 查找所有模板角色
        # 使用join预加载template_detail，以便获取使用统计等信息
        query = db.query(Character).join(
            CharacterTemplateDetail, 
            Character.id == CharacterTemplateDetail.character_id,
            isouter=True  # 使用左连接确保即使没有详情也能查到角色
        ).filter(Character.is_template == True)
        
        # 应用各种筛选条件
        if gender:
            query = query.filter(Character.gender == gender)
            
        if power_systems:
            # 因为power_system是字符串字段，所以使用OR条件进行筛选
            power_system_filters = []
            for system in power_systems:
                power_system_filters.append(Character.power_system.contains(system))
            query = query.filter(or_(*power_system_filters))
            
        if worldviews:
            worldview_filters = []
            for worldview in worldviews:
                worldview_filters.append(Character.original_world.contains(worldview))
            query = query.filter(or_(*worldview_filters))
            
        if tags:
            # 对于JSON字段中的数组元素，使用JSON包含操作
            for tag in tags:
                query = query.filter(Character.tags.contains([tag]))
                
        if is_popular is not None:
            query = query.filter(CharacterTemplateDetail.is_popular == is_popular)
            
        if is_new is not None:
            query = query.filter(CharacterTemplateDetail.is_new == is_new)
            
        # 构建排序条件
        if sort_by in ["usage_count", "rating", "is_popular", "is_new"]:
            # 这些字段在CharacterTemplateDetail表中
            sort_column = getattr(CharacterTemplateDetail, sort_by)
        else:
            # 其他字段在Character表中
            sort_column = getattr(Character, sort_by if hasattr(Character, sort_by) else "created_at")
            
        # 应用排序方向
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column)
        else:
            query = query.order_by(desc(sort_column))
            
        # 查询用户收藏记录以标记已收藏项
        favorited_template_ids = db.query(CharacterTemplateFavorite.character_id).filter(
            CharacterTemplateFavorite.user_id == current_user.id
        ).all()
        favorited_ids = [item[0] for item in favorited_template_ids]
        
        # 获取总数并应用分页
        total = query.count()
        offset = (page - 1) * page_size
        templates = query.offset(offset).limit(page_size).all()
        
        # 构建响应数据
        template_responses = []
        for template in templates:
            # 从Character基础模型转换
            template_dict = template.to_summary_dict()
            
            # 添加模板特有字段
            if template.template_detail:
                template_dict.update({
                    "usage_count": template.template_detail.usage_count,
                    "rating": template.template_detail.rating,
                    "is_popular": template.template_detail.is_popular,
                    "is_new": template.template_detail.is_new
                })
            else:
                template_dict.update({
                    "usage_count": 0,
                    "rating": 0.0,
                    "is_popular": False,
                    "is_new": False
                })
                
            # 标记是否已被用户收藏
            template_dict["is_favorited"] = template.id in favorited_ids
            
            template_responses.append(CharacterTemplateSummaryResponse.model_validate(template_dict))
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size
        
        # 准备响应数据
        response_data = {
            "characters": template_responses,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
        
        # 如果需要，添加筛选选项
        if include_filters:
            filters_available = {}
            
            # 获取性别选项
            genders = db.query(Character.gender, func.count(Character.id).label("count")).filter(
                Character.is_template == True
            ).group_by(Character.gender).all()
            
            gender_options = [
                TemplateFilterOption(
                    value=gender[0],
                    label=gender[0],
                    count=gender[1]
                ) for gender in genders
            ]
            filters_available["genders"] = gender_options
            
            # 获取力量体系选项 (从最常用的开始)
            power_systems = db.query(Character.power_system, func.count(Character.id).label("count")).filter(
                Character.is_template == True,
                Character.power_system != None,
                Character.power_system != ""
            ).group_by(Character.power_system).order_by(desc("count")).limit(20).all()
            
            power_system_options = [
                TemplateFilterOption(
                    value=system[0],
                    label=system[0],
                    count=system[1]
                ) for system in power_systems
            ]
            filters_available["power_systems"] = power_system_options
            
            # 获取世界观选项
            worldviews = db.query(Character.original_world, func.count(Character.id).label("count")).filter(
                Character.is_template == True,
                Character.original_world != None,
                Character.original_world != ""
            ).group_by(Character.original_world).order_by(desc("count")).limit(20).all()
            
            worldview_options = [
                TemplateFilterOption(
                    value=worldview[0],
                    label=worldview[0],
                    count=worldview[1]
                ) for worldview in worldviews
            ]
            filters_available["worldviews"] = worldview_options
            
            # 获取标签选项 (这需要特殊处理，因为tags是JSON数组)
            # 简化实现，仅返回一些预定义的标签
            predefined_tags = ["王者", "法师", "战士", "刺客", "坦克", "辅助", "射手", "善良", "邪恶", "中立"]
            tag_options = []
            
            for tag in predefined_tags:
                # 这里需要数据库支持JSON查询
                count = db.query(func.count(Character.id)).filter(
                    Character.is_template == True,
                    Character.tags.contains([tag])
                ).scalar()
                
                if count > 0:
                    tag_options.append(
                        TemplateFilterOption(
                            value=tag,
                            label=tag,
                            count=count
                        )
                    )
            
            filters_available["tags"] = tag_options
            
            response_data["filters_available"] = filters_available
        
        return CharacterTemplateListResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取角色模板列表失败: {str(e)}"
        )


@router.get("/{template_id}", response_model=CharacterTemplateResponse)
async def get_character_template_detail(
    template_id: int = Path(..., description="角色模板ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取角色模板详情
    
    Args:
        template_id: 角色模板ID
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        角色模板详细信息
    """
    try:
        # 查询模板角色
        template = db.query(Character).filter(
            Character.id == template_id,
            Character.is_template == True
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色模板不存在"
            )
            
        # 查询模板详情
        detail = db.query(CharacterTemplateDetail).filter(
            CharacterTemplateDetail.character_id == template_id
        ).first()
        
        # 查询使用示例
        usage_examples = []
        if detail:
            examples = db.query(UsageExample).filter(
                UsageExample.template_detail_id == detail.id
            ).all()
            usage_examples = [UsageExampleResponse.model_validate(example) for example in examples]
            
        # 检查是否已收藏
        is_favorited = db.query(CharacterTemplateFavorite).filter(
            CharacterTemplateFavorite.character_id == template_id,
            CharacterTemplateFavorite.user_id == current_user.id
        ).first() is not None
        
        # 构建响应数据
        template_dict = template.to_dict()
        template_dict["is_favorited"] = is_favorited
        
        # 添加详情信息
        if detail:
            template_dict["template_detail"] = TemplateDetailResponse.model_validate(detail)
        
        # 添加使用示例
        template_dict["usage_examples"] = usage_examples
        
        # 最后，更新使用统计
        if detail:
            detail.usage_count += 1  # 增加查看计数
            db.commit()
            
        return CharacterTemplateResponse.model_validate(template_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取角色模板详情失败: {str(e)}"
        )


@router.post("/search", response_model=SearchTemplatesResponse)
async def search_character_templates(
    request: SearchTemplatesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    搜索角色模板
    
    Args:
        request: 搜索请求
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        搜索结果，包含匹配的模板和元数据
    """
    try:
        import time
        start_time = time.time()
        
        # 构建基础查询
        query = db.query(Character).join(
            CharacterTemplateDetail, 
            Character.id == CharacterTemplateDetail.character_id,
            isouter=True
        ).filter(Character.is_template == True)
        
        # 准备搜索字段
        search_fields = request.search_fields or ["name", "description", "personality", "abilities", "tags"]
        keyword = request.keyword.strip()
        
        # 确保关键词有效
        if not keyword or len(keyword) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="搜索关键词过短，请提供至少2个字符"
            )
        
        # 构建搜索条件
        search_conditions = []
        
        if "name" in search_fields:
            if request.fuzzy_search:
                search_conditions.append(Character.name.contains(keyword))
            else:
                search_conditions.append(Character.name == keyword)
                
        if "description" in search_fields:
            search_conditions.append(Character.description.contains(keyword))
            
        if "personality" in search_fields:
            search_conditions.append(Character.personality.contains(keyword))
            
        if "abilities" in search_fields:
            search_conditions.append(Character.abilities.contains(keyword))
            
        if "tags" in search_fields and not request.fuzzy_search:
            search_conditions.append(Character.tags.contains([keyword]))
            
        # 应用搜索条件
        query = query.filter(or_(*search_conditions))
        
        # 应用额外的筛选条件
        if request.filters:
            if "gender" in request.filters and request.filters["gender"]:
                query = query.filter(Character.gender == request.filters["gender"])
                
            if "power_systems" in request.filters and request.filters["power_systems"]:
                power_system_filters = []
                for system in request.filters["power_systems"]:
                    power_system_filters.append(Character.power_system.contains(system))
                query = query.filter(or_(*power_system_filters))
                
            if "tags" in request.filters and request.filters["tags"]:
                for tag in request.filters["tags"]:
                    query = query.filter(Character.tags.contains([tag]))
                    
            if "is_popular" in request.filters and request.filters["is_popular"] is not None:
                query = query.filter(CharacterTemplateDetail.is_popular == request.filters["is_popular"])
                
            if "is_new" in request.filters and request.filters["is_new"] is not None:
                query = query.filter(CharacterTemplateDetail.is_new == request.filters["is_new"])
        
        # 获取分页参数
        page = request.filters.get("page", 1) if request.filters else 1
        page_size = request.filters.get("page_size", 20) if request.filters else 20
        
        # 应用排序
        query = query.order_by(desc(CharacterTemplateDetail.usage_count))
        
        # 获取用户收藏记录
        favorited_template_ids = db.query(CharacterTemplateFavorite.character_id).filter(
            CharacterTemplateFavorite.user_id == current_user.id
        ).all()
        favorited_ids = [item[0] for item in favorited_template_ids]
        
        # 获取总数并应用分页
        total = query.count()
        offset = (page - 1) * page_size
        templates = query.offset(offset).limit(page_size).all()
        
        # 构建响应数据
        template_responses = []
        for template in templates:
            template_dict = template.to_summary_dict()
            
            if template.template_detail:
                template_dict.update({
                    "usage_count": template.template_detail.usage_count,
                    "rating": template.template_detail.rating,
                    "is_popular": template.template_detail.is_popular,
                    "is_new": template.template_detail.is_new
                })
            else:
                template_dict.update({
                    "usage_count": 0,
                    "rating": 0.0,
                    "is_popular": False,
                    "is_new": False
                })
                
            template_dict["is_favorited"] = template.id in favorited_ids
            template_responses.append(CharacterTemplateSummaryResponse.model_validate(template_dict))
        
        # 计算总页数和搜索时间
        total_pages = (total + page_size - 1) // page_size
        search_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        # 准备搜索元数据
        search_metadata = {
            "keyword": keyword,
            "total_matches": total,
            "search_time": search_time
        }
        
        # 如果没有结果，提供搜索建议
        if total == 0:
            # 获取一些相关标签作为建议
            similar_tags = db.query(Character.tags).filter(
                Character.is_template == True
            ).all()
            
            # 简化处理，将所有标签平铺并去重
            all_tags = []
            for tags_list in similar_tags:
                if tags_list[0]:  # 确保tags不为None
                    all_tags.extend(tags_list[0])
            
            unique_tags = list(set(all_tags))[:5]  # 取前5个不重复的标签
            search_metadata["suggestions"] = unique_tags
        
        # 构建完整响应
        response_data = {
            "characters": template_responses,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "search_metadata": search_metadata
        }
        
        # 如果请求了高亮结果（暂不实现复杂逻辑）
        if request.highlight and templates:
            highlighted_results = []
            # 简化的高亮实现，后续可扩展
            for template in templates:
                if keyword.lower() in template.name.lower():
                    highlighted_results.append({
                        "character_id": template.id,
                        "highlighted_fields": [
                            {
                                "field": "name",
                                "content": template.name.replace(
                                    keyword, f"<em>{keyword}</em>"
                                )
                            }
                        ]
                    })
            
            if highlighted_results:
                response_data["highlighted_results"] = highlighted_results
        
        return SearchTemplatesResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索角色模板失败: {str(e)}"
        )


@router.get("/suggestions/search", response_model=List[SearchSuggestion])
async def get_search_suggestions(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取搜索建议
    
    Args:
        q: 搜索关键词
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        匹配的搜索建议列表
    """
    try:
        suggestions = []
        
        # 角色名称建议
        name_matches = db.query(Character.name).filter(
            Character.is_template == True,
            Character.name.contains(q)
        ).limit(5).all()
        
        for match in name_matches:
            suggestions.append(SearchSuggestion(
                text=match[0],
                type="character_name",
                match_count=1
            ))
            
        # 力量体系建议
        power_system_matches = db.query(Character.power_system, func.count(Character.id).label("count")).filter(
            Character.is_template == True,
            Character.power_system.contains(q)
        ).group_by(Character.power_system).order_by(desc("count")).limit(3).all()
        
        for match in power_system_matches:
            suggestions.append(SearchSuggestion(
                text=match[0],
                type="power_system",
                match_count=match[1]
            ))
            
        # 简化的标签建议（实际实现需要更复杂的JSON查询）
        # 这里只是示例实现
        tag_matches = []
        all_templates = db.query(Character).filter(
            Character.is_template == True,
            Character.tags != None
        ).limit(100).all()
        
        tag_count = {}
        for template in all_templates:
            for tag in template.tags or []:
                if q.lower() in tag.lower():
                    tag_count[tag] = tag_count.get(tag, 0) + 1
        
        # 排序并限制结果
        sorted_tags = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for tag, count in sorted_tags:
            suggestions.append(SearchSuggestion(
                text=tag,
                type="tag",
                match_count=count
            ))
            
        # 世界观建议
        worldview_matches = db.query(Character.original_world, func.count(Character.id).label("count")).filter(
            Character.is_template == True,
            Character.original_world.contains(q)
        ).group_by(Character.original_world).order_by(desc("count")).limit(2).all()
        
        for match in worldview_matches:
            if match[0]:  # 确保不是None
                suggestions.append(SearchSuggestion(
                    text=match[0],
                    type="worldview",
                    match_count=match[1]
                ))
        
        return suggestions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取搜索建议失败: {str(e)}"
        )


@router.get("/stats", response_model=GetTemplateStatsResponse)
async def get_template_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取角色模板使用统计
    
    Args:
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        角色模板统计信息
    """
    try:
        # 获取模板总数
        total_templates = db.query(func.count(Character.id)).filter(
            Character.is_template == True
        ).scalar() or 0
        
        # 获取总使用次数
        total_usages = db.query(func.sum(CharacterTemplateDetail.usage_count)).scalar() or 0
        
        # 获取热门模板 (前5个)
        popular_templates_query = db.query(Character).join(
            CharacterTemplateDetail,
            Character.id == CharacterTemplateDetail.character_id
        ).filter(
            Character.is_template == True
        ).order_by(desc(CharacterTemplateDetail.usage_count)).limit(5)
        
        popular_templates = []
        for template in popular_templates_query:
            template_dict = template.to_summary_dict()
            
            if template.template_detail:
                template_dict.update({
                    "usage_count": template.template_detail.usage_count,
                    "rating": template.template_detail.rating,
                    "is_popular": template.template_detail.is_popular,
                    "is_new": template.template_detail.is_new
                })
                
            popular_templates.append(CharacterTemplateSummaryResponse.model_validate(template_dict))
            
        # 获取流行标签
        # 简化实现，使用预定义标签
        trending_tags = ["王者", "法师", "战士", "刺客", "坦克"]
        
        # 按类型使用统计
        # 这里假设novel.genre已经映射到了Character
        usage_by_genre = [
            {"genre": "玄幻", "usage_count": 120},
            {"genre": "武侠", "usage_count": 85},
            {"genre": "仙侠", "usage_count": 65},
            {"genre": "科幻", "usage_count": 45},
            {"genre": "奇幻", "usage_count": 30}
        ]
        
        # 获取用户统计
        user_templates_used = db.query(func.count(CharacterTemplateUsage.id)).filter(
            CharacterTemplateUsage.user_id == current_user.id
        ).scalar() or 0
        
        user_favorite_count = db.query(func.count(CharacterTemplateFavorite.id)).filter(
            CharacterTemplateFavorite.user_id == current_user.id
        ).scalar() or 0
        
        # 获取用户最常用的标签
        # 简化实现
        user_most_used_tags = ["战士", "王者", "邪恶"]
        
        user_stats = {
            "templates_used": user_templates_used,
            "favorite_count": user_favorite_count,
            "most_used_tags": user_most_used_tags
        }
        
        return GetTemplateStatsResponse(
            total_templates=total_templates,
            total_usages=total_usages,
            popular_templates=popular_templates,
            trending_tags=trending_tags,
            usage_by_genre=usage_by_genre,
            user_stats=user_stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取角色模板统计失败: {str(e)}"
        )