
# 运行测试，启用asyncio支持
pytest tests/test_character_routes.py -v -p pytest_asyncio
pytest tests/test_event_routes.py -v -p pytest_asyncio
