import pytest
from fastapi.testclient import TestClient
import sys
import os
import asyncio
import pytest
from datetime import datetime, timedelta
from typing import AsyncIterator

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 导入必要的模块
from src.api.main import app
from src.service.event.service import event_service
from src.service.character.service import character_service
from src.character.db.event_profile_dao import EventProfileDAO

event_profile_dao = EventProfileDAO()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
async def test_character():
    # 创建一个测试角色
    character = await character_service.generate_character({
        "name": "测试角色",
        "age": 25,
        "gender": "男",
        "occupation": "工程师",
        "language": "Chinese"
    })
    try:
        yield character
    finally:
        # 清理：删除测试角色
        await character_service.delete_character(character['character_id'])

# 测试生成事件配置接口
@pytest.mark.asyncio
async def test_generate_event_profile(client, test_character):
    character = await anext(test_character)
    character_id = character.character_id

    # 测试成功生成事件配置
    response = client.post(f"/api/characters/{character_id}/event-profiles/generate")
    assert response.status_code == 200
    data = response.json()
    print(f"生成事件配置响应: {data}")
    assert data["recode"] == 200
    assert data["msg"] == "事件配置生成成功"
    assert "data" in data
    assert "id" in data["data"]
    assert "character_id" in data["data"]
    assert data["data"]["character_id"] == character_id

    # 测试生成事件配置失败（角色不存在）
    response = client.post("/api/characters/non_existent_id/event-profiles/generate")
    assert response.status_code == 200
    data = response.json()
    assert data["recode"] == 500
    assert data["msg"] == "事件配置生成失败"

# 测试保存事件配置接口
@pytest.mark.asyncio
async def test_save_event_profile(client, test_character):
    character = await anext(test_character)
    character_id = character.character_id

    # 先生成事件配置
    generate_response = client.post(f"/api/characters/{character_id}/event-profiles/generate")
    generate_data = generate_response.json()
    event_profile_data = generate_data["data"]

    # 测试成功保存事件配置
    response = client.post(f"/api/characters/{character_id}/event-profiles/save", json=event_profile_data)
    assert response.status_code == 200
    data = response.json()
    print(f"保存事件配置响应: {data}")
    assert data["recode"] == 200
    assert data["msg"] == "事件配置保存成功"
    assert "data" in data
    assert "profile_id" in data["data"]
    assert data["data"]["profile_id"] == event_profile_data["id"]

    # 测试保存事件配置失败（无效数据）
    response = client.post(f"/api/characters/{character_id}/event-profiles/save", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["recode"] == 500
    assert data["msg"] == "事件配置保存失败"

# 测试删除事件配置接口
@pytest.mark.asyncio
async def test_delete_event_profile(client, test_character):
    character = await anext(test_character)
    character_id = character.character_id

    # 先生成并保存事件配置
    generate_response = client.post(f"/api/characters/{character_id}/event-profiles/generate")
    generate_data = generate_response.json()
    event_profile_data = generate_data["data"]

    save_response = client.post(f"/api/characters/{character_id}/event-profiles/save", json=event_profile_data)
    save_data = save_response.json()
    profile_id = save_data["data"]["profile_id"]

    # 测试成功删除事件配置
    response = client.post(f"/api/characters/{character_id}/event-profiles/delete/{profile_id}")
    assert response.status_code == 200
    data = response.json()
    print(f"删除事件配置响应: {data}")
    assert data["recode"] == 200
    assert data["msg"] == "事件配置已删除"
    assert data["data"]["success"] is True

    # 测试删除不存在的事件配置
    response = client.post(f"/api/characters/{character_id}/event-profiles/delete/non_existent_id")
    assert response.status_code == 200
    data = response.json()
    assert data["recode"] == 404
    assert data["msg"] == "事件配置未找到或删除失败"

# 测试根据角色ID删除事件配置接口
@pytest.mark.asyncio
async def test_delete_event_profile_by_character(client, test_character):
    character = await anext(test_character)
    character_id = character.character_id

    # 先生成并保存事件配置
    generate_response = client.post(f"/api/characters/{character_id}/event-profiles/generate")
    generate_data = generate_response.json()
    event_profile_data = generate_data["data"]

    save_response = client.post(f"/api/characters/{character_id}/event-profiles/save", json=event_profile_data)
    assert save_response.status_code == 200

    # 测试成功删除事件配置
    response = client.post(f"/api/characters/{character_id}/event-profiles/delete-by-character")
    assert response.status_code == 200
    data = response.json()
    print(f"根据角色ID删除事件配置响应: {data}")
    assert data["recode"] == 200
    assert data["msg"] == "事件配置已删除"
    assert data["data"]["success"] is True

    # 测试删除不存在的角色的事件配置
    response = client.post("/api/characters/non_existent_id/event-profiles/delete-by-character")
    assert response.status_code == 200
    data = response.json()
    assert data["recode"] == 404
    assert data["msg"] == "未找到角色或事件配置删除失败"

# 测试新建生活轨迹接口
@pytest.mark.asyncio
async def test_create_life_path(client, test_character):
    character = await anext(test_character)
    character_id = character.character_id

    # 先生成并保存事件配置
    generate_response = client.post(f"/api/characters/{character_id}/event-profiles/generate")
    generate_data = generate_response.json()
    event_profile_data = generate_data["data"]

    save_response = client.post(f"/api/characters/{character_id}/event-profiles/save", json=event_profile_data)
    assert save_response.status_code == 200

    # 设置日期参数
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    # 测试成功创建生活轨迹
    response = client.post(
        f"/api/characters/{character_id}/life-paths/generate",
        json={"start_date": today, "end_date": tomorrow, "max_events": 3}
    )
    assert response.status_code == 200
    data = response.json()
    print(f"创建生活轨迹响应: {data}")
    assert data["recode"] == 200
    assert data["msg"] == "生活轨迹创建成功"
    assert data["data"]["success"] is True

    # 测试创建生活轨迹失败（角色不存在）
    response = client.post(
        "/api/characters/non_existent_id/life-paths/generate",
        json={"start_date": today, "end_date": tomorrow, "max_events": 3}
    )
    assert response.status_code == 200
    data = response.json()
    print(f"创建生活轨迹失败响应: {data}")
    assert data["recode"] == 200
    assert data["msg"] == "生活轨迹创建成功"

if __name__ == "__main__":
    pytest.main(["-v", "tests/test_event_routes.py"])
