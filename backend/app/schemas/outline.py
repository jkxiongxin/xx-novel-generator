"""
大纲数据模式
Author: AI Assistant
Created: 2025-06-01
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.outline import OutlineType


class RoughOutlineBase(BaseModel):
    """粗略大纲基础模式"""
    outline_type: OutlineType = Field(..., description="大纲类型")
    title: str = Field(..., description="标题", max_length=200)
    content: str = Field(..., description="内容描述")
    order_index: int = Field(default=0, description="排序索引")
    start_chapter: Optional[int] = Field(None, description="开始章节数")
    end_chapter: Optional[int] = Field(None, description="结束章节数")


class RoughOutlineCreate(RoughOutlineBase):
    """创建粗略大纲请求模式"""
    novel_id: int = Field(..., description="小说ID")


class RoughOutlineUpdate(BaseModel):
    """更新粗略大纲请求模式"""
    title: Optional[str] = Field(None, description="标题", max_length=200)
    content: Optional[str] = Field(None, description="内容描述")
    order_index: Optional[int] = Field(None, description="排序索引")
    start_chapter: Optional[int] = Field(None, description="开始章节数")
    end_chapter: Optional[int] = Field(None, description="结束章节数")


class RoughOutlineResponse(RoughOutlineBase):
    """粗略大纲响应模式"""
    id: int = Field(..., description="大纲ID")
    novel_id: int = Field(..., description="小说ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class DetailedOutlineBase(BaseModel):
    """详细大纲基础模式"""
    chapter_number: int = Field(..., description="章节号")
    chapter_title: Optional[str] = Field(None, description="章节标题", max_length=200)
    plot_points: str = Field(..., description="章节情节点")
    participating_characters: List[int] = Field(default_factory=list, description="参与角色ID列表")
    entering_characters: List[int] = Field(default_factory=list, description="入场角色ID列表")
    exiting_characters: List[int] = Field(default_factory=list, description="离场角色ID列表")
    chapter_summary: Optional[str] = Field(None, description="章节简介")
    is_plot_end: bool = Field(default=False, description="是否剧情结束")
    is_new_plot: bool = Field(default=False, description="是否新剧情开始")
    new_plot_summary: Optional[str] = Field(None, description="新剧情简介")


class DetailedOutlineCreate(DetailedOutlineBase):
    """创建详细大纲请求模式"""
    novel_id: int = Field(..., description="小说ID")


class DetailedOutlineUpdate(BaseModel):
    """更新详细大纲请求模式"""
    chapter_title: Optional[str] = Field(None, description="章节标题", max_length=200)
    plot_points: Optional[str] = Field(None, description="章节情节点")
    participating_characters: Optional[List[int]] = Field(None, description="参与角色ID列表")
    entering_characters: Optional[List[int]] = Field(None, description="入场角色ID列表")
    exiting_characters: Optional[List[int]] = Field(None, description="离场角色ID列表")
    chapter_summary: Optional[str] = Field(None, description="章节简介")
    is_plot_end: Optional[bool] = Field(None, description="是否剧情结束")
    is_new_plot: Optional[bool] = Field(None, description="是否新剧情开始")
    new_plot_summary: Optional[str] = Field(None, description="新剧情简介")


class DetailedOutlineResponse(DetailedOutlineBase):
    """详细大纲响应模式"""
    id: int = Field(..., description="大纲ID")
    novel_id: int = Field(..., description="小说ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class RoughOutlineListResponse(BaseModel):
    """粗略大纲列表响应模式"""
    items: List[RoughOutlineResponse] = Field(..., description="粗略大纲列表")
    total: int = Field(..., description="总数量")


class DetailedOutlineListResponse(BaseModel):
    """详细大纲列表响应模式"""
    items: List[DetailedOutlineResponse] = Field(..., description="详细大纲列表")
    total: int = Field(..., description="总数量")


class RoughOutlineGenerationRequest(BaseModel):
    """粗略大纲生成请求模式"""
    novel_id: int = Field(..., description="小说ID")
    outline_types: List[OutlineType] = Field(default_factory=list, description="要生成的大纲类型")
    target_chapters: Optional[int] = Field(None, description="目标章节数", ge=1, le=1000)
    user_suggestion: Optional[str] = Field(None, description="用户建议")
    include_worldview: bool = Field(default=True, description="是否包含世界观信息")
    include_novel_idea: bool = Field(default=True, description="是否包含小说创意")


class DetailedOutlineGenerationRequest(BaseModel):
    """详细大纲生成请求模式"""
    novel_id: int = Field(..., description="小说ID")
    plot_point_id: Optional[int] = Field(None, description="大情节点ID")
    start_chapter: int = Field(..., description="开始章节数", ge=1)
    end_chapter: int = Field(..., description="结束章节数", ge=1)
    user_suggestion: Optional[str] = Field(None, description="用户建议")
    include_worldview: bool = Field(default=True, description="是否包含世界观信息")
    include_rough_outline: bool = Field(default=True, description="是否包含粗略大纲信息")
    include_characters: bool = Field(default=True, description="是否包含角色信息")


class OutlineGenerationResponse(BaseModel):
    """大纲生成响应模式"""
    success: bool = Field(..., description="生成是否成功")
    message: str = Field(..., description="响应消息")
    rough_outlines: List[RoughOutlineResponse] = Field(default_factory=list, description="生成的粗略大纲列表")
    detailed_outlines: List[DetailedOutlineResponse] = Field(default_factory=list, description="生成的详细大纲列表")
    total_generated: int = Field(default=0, description="成功生成的大纲数量")


class OutlineFilterRequest(BaseModel):
    """大纲筛选请求模式"""
    outline_type: Optional[OutlineType] = Field(None, description="大纲类型筛选")
    chapter_range_start: Optional[int] = Field(None, description="章节范围开始")
    chapter_range_end: Optional[int] = Field(None, description="章节范围结束")
    has_plot_end: Optional[bool] = Field(None, description="是否包含剧情结束")
    has_new_plot: Optional[bool] = Field(None, description="是否包含新剧情开始")


class OutlineSummaryRequest(BaseModel):
    """大纲总结请求模式"""
    outline_id: int = Field(..., description="大纲ID")
    outline_type: str = Field(..., description="大纲类型: rough/detailed")
    summary_length: str = Field(default="detailed", description="总结长度: brief/detailed/complete")
    focus_points: List[str] = Field(default_factory=list, description="关注点")


class OutlineSummaryResponse(BaseModel):
    """大纲总结响应模式"""
    success: bool = Field(..., description="总结是否成功")
    message: str = Field(..., description="响应消息")
    summary: str = Field(..., description="大纲总结内容")
    outline_id: int = Field(..., description="大纲ID")
    outline_type: str = Field(..., description="大纲类型")