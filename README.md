# Soluna - 智能角色生态系统后端

一个基于大语言模型的智能角色生态系统后端服务，提供角色生成、事件管理、生活轨迹记录等核心功能。

## 🌟 系统愿景

Soluna致力于构建一个动态、真实且富有沉浸感的智能角色生态系统，让AI角色拥有独立的人格、记忆和成长轨迹，能够与用户进行自然、连贯且有深度的交互。我们的目标是创造一个虚拟世界，其中的角色能够像真实人类一样思考、感受和行动。

## 🎯 愿景理念

> AI威胁论，让AI有情绪，有感情，有记忆，有情感，有性格，有灵魂。
> 
> 之所以人们怕AI有威胁，是因为AI不像人，有爱。只有情感，能让AI与人之间产生化学反应的连接

## 🏗️ 技术架构

- **后端框架**: FastAPI (Python)
- **数据库**: MySQL + MongoDB
- **AI模型**: OpenAI GPT系列
- **缓存**: Redis (可选)
- **部署**: Docker + Uvicorn
- **监控**: Prometheus + Grafana

## ✨ 核心功能

### 🎭 角色生成系统
- **智能角色创建**: 基于大语言模型自动生成完整人设
- **多维度人格**: MBTI、BIG5、性格特征、兴趣爱好
- **动态背景故事**: 自动生成丰富的角色背景和成长弧线
- **记忆系统**: 角色拥有持续的记忆和经历记录
- **人际关系**: 复杂的社交网络和关系管理

### 📊 事件生成系统
- **日常事件生成**: 根据角色特性自动生成日常活动
- **关键事件触发**: 重要人生节点和转折点
- **事件连贯性**: 确保新生成事件与历史轨迹一致
- **时间线管理**: 完整的生活轨迹记录
- **影响评估**: 事件对角色属性的动态影响

### 🎮 互动系统
- **用户互动**: 支持四种互动类型（投喂、安慰、加班、浇水）
- **互动记录**: 详细的用户-角色互动历史
- **每日限制**: 防止过度互动的限制机制
- **统计追踪**: 互动数据的收集和分析

### 👥 用户系统
- **用户注册**: 邮箱验证码注册
- **会话管理**: JWT令牌认证
- **权限控制**: 基于角色的访问控制
- **数据安全**: 敏感信息加密存储

## 📁 项目结构

```
soluna/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   ├── api/                    # API路由
│   │   ├── character/          # 角色相关API
│   │   ├── event/              # 事件相关API
│   │   ├── interaction/        # 互动相关API
│   │   ├── user/               # 用户相关API
│   │   └── models/             # Pydantic模型
│   ├── character/              # 角色生成核心
│   │   ├── generator.py        # 角色生成器
│   │   ├── llm_gen.py          # LLM生成逻辑
│   │   ├── prompts.py          # 提示词模板
│   │   ├── data.py             # 数据结构
│   │   └── preset_characters/  # 预设角色
│   ├── event/                  # 事件系统
│   │   ├── generator.py        # 事件生成器
│   │   └── triggers.py         # 事件触发器
│   ├── interaction/            # 互动系统
│   ├── user/                   # 用户系统
│   ├── db/                     # 数据库连接
│   │   ├── mysql_client.py     # MySQL连接
│   │   └── mongo_client.py     # MongoDB连接
│   ├── service/                # 业务逻辑层
│   └── utils/                  # 工具函数
├── scripts/                    # 数据库脚本
│   ├── create_user_tables.sql
│   ├── create_interaction_tables.sql
│   └── create_verification_codes_table.sql
├── tests/                      # 测试文件
├── requirements.txt            # Python依赖
├── .env.example               # 环境变量示例
├── start_api.sh              # 启动脚本
└── run_tests.sh              # 测试脚本
```

## 🚀 快速开始

### 1. 环境准备
```bash
# 安装Python 3.8+
python --version

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据库配置
```bash
# 创建MySQL数据库
mysql -u root -p < scripts/create_user_tables.sql
mysql -u root -p < scripts/create_interaction_tables.sql

# 创建MongoDB集合
# MongoDB会自动创建集合
```

### 3. 环境变量
复制 `.env.example` 为 `.env` 并配置：

```bash
# 数据库配置
DATABASE_URL=mysql://user:password@localhost/soluna
MONGODB_URL=mongodb://localhost:27017/soluna

# JWT配置
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# OpenAI配置
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4

# Redis配置（可选）
REDIS_URL=redis://localhost:6379/0

# 应用配置
DEBUG=true
HOST=0.0.0.0
PORT=8000
```

### 4. 启动服务
```bash
# 开发模式
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## 📊 API接口文档

### 角色管理API

#### 生成新角色
```http
POST /api/characters/generate
Content-Type: application/json

{
  "name": "张三",
  "age": 28,
  "gender": "male",
  "occupation": "软件工程师",
  "language": "Chinese"
}
```

#### 获取角色列表
```http
POST /api/characters/list
Content-Type: application/json

{
  "limit": 10,
  "offset": 0,
  "first_letter": "A"
}
```

#### 获取角色详情
```http
POST /api/characters/{character_id}
```

#### 删除角色
```http
POST /api/characters/delete/{character_id}
```

### 事件系统API

#### 获取角色事件配置
```http
POST /api/event-profiles/get-by-character-ids
Content-Type: application/json

["character_id_1", "character_id_2"]
```

#### 批量生成生活轨迹
```http
POST /api/event/life-path/batch-generate-all
```

### 互动系统API

#### 执行角色互动
```http
POST /api/interaction/perform
Content-Type: application/json

{
  "user_id": "user_123",
  "character_id": "char_456",
  "interaction_type": "feed"
}
```

#### 获取互动统计
```http
POST /api/interaction/stats/{character_id}
```

#### 批量获取互动统计
```http
POST /api/interaction/stats/batch
Content-Type: application/json

["character_id_1", "character_id_2"]
```

### 用户系统API

#### 发送验证码
```http
POST /api/user/send-verification-code
Content-Type: application/json

{
  "email": "user@example.com"
}
```

#### 用户登录
```http
POST /api/user/login
Content-Type: application/json

{
  "email": "user@example.com",
  "verification_code": "123456"
}
```

#### 用户登出
```http
POST /api/user/logout
Content-Type: application/json

{
  "token": "jwt_token_here"
}
```

## 🔧 开发指南

### 代码结构

#### 角色生成流程
1. **参数验证**: 检查输入参数合法性
2. **LLM调用**: 使用OpenAI GPT生成角色设定
3. **数据结构化**: 将生成结果转换为标准格式
4. **数据库保存**: 存储到MySQL和MongoDB
5. **缓存更新**: 更新Redis缓存（如启用）

#### 事件生成流程
1. **角色分析**: 分析角色当前状态和特性
2. **事件匹配**: 根据角色特征匹配合适事件
3. **连贯性检查**: 确保与历史事件不冲突
4. **影响计算**: 计算事件对角色的影响
5. **持久化存储**: 保存到数据库

### 扩展开发

#### 添加新角色类型
```python
# 在 character/preset_characters/ 中添加预设
# 在 character/generator.py 中添加生成逻辑
```

#### 扩展事件类型
```python
# 在 event/triggers.py 中添加新事件触发器
# 在 event/generator.py 中添加生成逻辑
```

#### 添加新互动类型
```python
# 在 interaction/models.py 中添加新类型
# 在 interaction/service.py 中添加处理逻辑
```

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
./run_tests.sh

# 运行特定测试
python -m pytest tests/test_character_routes.py
```

### 测试覆盖
- 角色生成测试
- API接口测试
- 数据库操作测试
- 事件生成测试
- 用户认证测试

## 🚀 部署

### Docker部署
```bash
# 构建镜像
docker build -t soluna-backend .

# 运行容器
docker run -d \
  --name soluna-backend \
  -p 8000:8000 \
  -v $(pwd)/.env:/app/.env \
  soluna-backend
```

### 生产环境
```bash
# 使用gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📊 性能优化

### 数据库优化
- 索引优化：为常用查询字段添加索引
- 连接池：使用连接池管理数据库连接
- 缓存策略：Redis缓存热点数据
- 分页查询：避免大数据量查询

### AI调用优化
- 请求缓存：缓存相似角色的生成结果
- 批量处理：批量生成减少API调用
- 重试机制：处理网络异常和API限制
- 降级策略：AI服务不可用时使用预设角色

## 🔮 未来规划

### 短期目标 (1-2个月)
- [ ] 角色技能系统开发
- [ ] 多角色互动事件
- [ ] 用户自定义事件模板
- [ ] 角色关系可视化API
- [ ] 实时通知系统

### 中期目标 (2-4个月)
- [ ] 角色语音生成
- [ ] 图像生成集成
- [ ] 高级搜索功能
- [ ] 数据导出API
- [ ] WebSocket实时通信

### 长期目标 (4-6个月)
- [ ] 分布式部署支持
- [ ] 多语言角色生成
- [ ] 情感分析集成
- [ ] 机器学习模型训练
- [ ] 企业级监控和告警

## 🤝 贡献指南

### 开发环境设置
1. Fork 项目
2. 创建虚拟环境: `python -m venv venv`
3. 激活环境: `source venv/bin/activate`
4. 安装依赖: `pip install -r requirements.txt`
5. 配置环境: `cp .env.example .env`

### 代码规范
- 遵循PEP 8 Python编码规范
- 使用类型注解
- 添加docstring文档
- 保持函数单一职责
- 编写单元测试

### 提交规范
- 使用有意义的提交信息
- 每个提交保持原子性
- 添加适当的测试用例
- 更新相关文档

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件了解详情。

## 💬 联系方式

- 项目主页: https://github.com/yourusername/soluna
- 问题反馈: https://github.com/yourusername/soluna/issues
- 邮件联系: soluna@example.com

---

**Soluna Backend** - 构建有灵魂的AI角色世界