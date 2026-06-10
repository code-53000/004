# 农村自备水井管理系统

## 一、系统概述

本系统用于解决农村自备水井巡检记录不规范、问题追溯难的问题，实现水井信息管理、巡检记录、整改跟踪、水质检测全流程数字化管理。

### 核心功能

- **水井信息管理**：记录每口井的位置、供水户数、设备状态（井盖、抽水泵、周边排水）、巡检照片地址、问题隐患、整改负责人
- **巡检管理**：记录每次巡检情况，支持照片上传，自动计算下次巡检日期
- **整改管理**：对巡检发现的问题进行整改跟踪，记录整改措施和结果
- **水质检测**：按批次录入水质检测指标，后端自动判定是否合格并记录判定依据
- **逾期提醒**：逾期未巡检的井在列表中红色背景突出显示
- **权限分层**：巡检员、整改员、送检员、监管员四层角色，各自页面和功能分离

## 二、技术栈

### 后端
- FastAPI 0.95.2
- SQLAlchemy 1.4.47
- PostgreSQL 15
- Pydantic 1.10.7
- JWT + BCrypt 认证授权

### 前端
- Vue 3.2.47
- Vue Router 4.1.6
- Pinia 2.0.35
- Element Plus 2.3.4
- Axios 1.4.0

### 部署
- Docker + docker-compose
- Nginx 反向代理

## 三、项目结构

```
.
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/v1/            # API 路由
│   │   │   ├── auth.py        # 认证接口
│   │   │   ├── wells.py       # 水井管理
│   │   │   ├── inspections.py # 巡检记录
│   │   │   ├── rectifications.py # 整改记录
│   │   │   ├── water_tests.py # 水质检测
│   │   │   └── master_data.py # 基础数据
│   │   ├── core/              # 核心逻辑
│   │   │   ├── config.py      # 配置
│   │   │   ├── security.py    # 安全相关
│   │   │   └── water_quality_judge.py # 水质判定算法
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # 数据校验
│   │   ├── database.py        # 数据库连接
│   │   └── main.py            # 入口文件
│   ├── init_data.py           # 初始化数据脚本
│   ├── requirements.txt
│   ├── Dockerfile
│   └── start.sh
├── frontend/                   # 前端项目
│   ├── src/
│   │   ├── api/               # API 封装
│   │   ├── views/             # 页面组件
│   │   ├── store/             # Pinia 状态管理
│   │   ├── router/            # 路由配置
│   │   └── utils/             # 工具函数
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
└── docker-compose.yml          # 一键部署配置
```

## 四、快速部署

### 环境要求
- Docker 20.10+
- docker-compose 1.29+

### 一键启动

```bash
docker-compose up -d --build
```

启动后访问：
- 前端页面：http://localhost:8080
- 后端 API 文档：http://localhost:8000/docs

### 停止服务

```bash
docker-compose down
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend
```

## 五、数据库设计

### 核心表结构

1. **village** - 村组表
2. **well_type** - 井类型表（含巡检周期）
3. **water_quality_standard** - 水质指标标准表（含比较方式、限值）
4. **user** - 用户表（含角色）
5. **well** - 水井表
6. **inspection_record** - 巡检记录表
7. **rectification_record** - 整改记录表
8. **water_test_batch** - 水质检测批次表
9. **water_test_item** - 水质检测项表（含后端判定结果）

### 数据持久化

PostgreSQL 数据目录通过 Docker named volume 挂载：
- Volume 名称：`well-management-postgres-data`
- 挂载路径：`/var/lib/postgresql/data`

## 六、初始化数据

系统首次启动时自动导入以下数据：

### 村组（5个）
- 东村、西村、南村、北村、中村

### 井类型（4种）
- 集中供水井（巡检周期：30天）
- 散户自备井（巡检周期：60天）
- 灌溉用井（巡检周期：90天）
- 备用应急井（巡检周期：180天）

### 水质指标（35项）
依据《生活饮用水卫生标准》GB5749-2006，包含：
- 微生物指标（总大肠菌群、菌落总数等4项）
- 毒理指标（砷、镉、铬、铅、汞等15项）
- 感官性状和一般化学指标（色度、浑浊度、余氯等15项）
- 放射性指标（总α放射性、总β放射性2项）

### 测试账号（7个）

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | admin123 | supervisor | 监管员（最高权限） |
| inspector1 | 123456 | inspector | 巡检员1 |
| inspector2 | 123456 | inspector | 巡检员2 |
| rectifier1 | 123456 | rectifier | 整改员1 |
| rectifier2 | 123456 | rectifier | 整改员2 |
| tester1 | 123456 | tester | 送检员1 |
| tester2 | 123456 | tester | 送检员2 |

## 七、权限分层设计

### 角色说明

1. **巡检员 (inspector)**
   - 查看水井列表（含逾期提醒）
   - 新增、编辑、删除自己的巡检记录
   - 查看整改结果和水质检测结果

2. **整改员 (rectifier)**
   - 查看待整改的问题列表
   - 新增、编辑、删除自己的整改记录
   - 查看水井信息和巡检记录

3. **送检员 (tester)**
   - 管理水质检测批次
   - 录入检测数据（自动判定合格）
   - 查看水井信息和检测历史

4. **监管员 (supervisor)**
   - 所有功能的完整权限
   - 管理村组、井类型、水质指标等基础数据
   - 管理所有用户的记录（包括删除）
   - 查看统计数据和报表

### 权限控制机制

- **后端**：使用 `require_roles()` 装饰器控制 API 访问权限
- **前端**：
  - 路由配置 `roles` 元信息进行访问控制
  - 布局组件根据角色动态过滤菜单项
  - 按钮级权限根据用户角色控制显示

## 八、核心业务逻辑

### 1. 水质判定算法

水质判定完全在后端实现，结果存储在数据库中，前端仅展示。

**判定流程**：
1. 录入检测值时，系统自动从 `water_quality_standard` 表获取标准限值和比较方式
2. 根据比较方式（<=、>=、<、>、==）动态判定
3. 将判定结果（is_qualified）和判定依据（judgment_basis）存入 `water_test_item` 表
4. 批次整体结果根据所有检测项综合计算

**特殊处理**：余氯指标支持余氯和游离余氯两种判定标准。

### 2. 逾期巡检计算

每次查询水井列表时自动计算逾期状态：
```
下次巡检日期 = 上次巡检日期 + 井类型巡检周期
如果 下次巡检日期 < 当前日期，则标记为逾期
```

逾期水井在列表中以红色背景突出显示。

### 3. 数据隔离

- 巡检员只能查看和编辑自己创建的巡检记录
- 整改员只能查看和编辑自己负责的整改记录
- 送检员只能查看和编辑自己创建的检测批次
- 监管员可以查看和操作所有数据

## 九、API 接口

### 认证接口
- `POST /api/v1/auth/login` - 用户登录获取 Token

### 水井管理
- `GET /api/v1/wells` - 获取水井列表（自动计算逾期状态）
- `GET /api/v1/wells/{id}` - 获取水井详情
- `POST /api/v1/wells` - 新增水井
- `PUT /api/v1/wells/{id}` - 更新水井
- `DELETE /api/v1/wells/{id}` - 删除水井

### 巡检记录
- `GET /api/v1/inspections` - 获取巡检记录列表
- `POST /api/v1/inspections` - 新增巡检记录
- `PUT /api/v1/inspections/{id}` - 更新巡检记录
- `DELETE /api/v1/inspections/{id}` - 删除巡检记录

### 整改记录
- `GET /api/v1/rectifications` - 获取整改记录列表
- `POST /api/v1/rectifications` - 新增整改记录
- `PUT /api/v1/rectifications/{id}` - 更新整改记录
- `DELETE /api/v1/rectifications/{id}` - 删除整改记录

### 水质检测
- `GET /api/v1/water-tests/batches` - 获取检测批次列表
- `GET /api/v1/water-tests/batches/{id}` - 获取批次详情
- `POST /api/v1/water-tests/batches` - 新增检测批次
- `POST /api/v1/water-tests/batches/{id}/items` - 添加检测项（自动判定）
- `GET /api/v1/water-tests/items` - 获取检测项列表
- `DELETE /api/v1/water-tests/batches/{id}` - 删除批次
- `DELETE /api/v1/water-tests/items/{id}` - 删除检测项

### 基础数据（仅监管员）
- `GET /api/v1/master-data/villages` - 获取村组列表
- `GET /api/v1/master-data/well-types` - 获取井类型列表
- `GET /api/v1/master-data/standards` - 获取水质指标列表
- 完整的 CRUD 接口

## 十、常见问题

### 1. 如何修改数据库密码？

编辑 `docker-compose.yml` 中的环境变量：
```yaml
services:
  db:
    environment:
      POSTGRES_PASSWORD: 你的新密码
  backend:
    environment:
      DATABASE_URL: postgresql+psycopg2://well_admin:你的新密码@db:5432/well_management
```

### 2. 如何修改 JWT 密钥？

编辑 `docker-compose.yml` 中 backend 服务的 `SECRET_KEY` 环境变量。

### 3. 如何备份数据库？

```bash
docker exec well-management-db pg_dump -U well_admin well_management > backup.sql
```

### 4. 如何恢复数据库？

```bash
docker exec -i well-management-db psql -U well_admin well_management < backup.sql
```

### 5. 如何重新导入初始化数据？

删除数据卷后重新启动：
```bash
docker-compose down -v
docker-compose up -d --build
```

## 十一、许可证

内部使用，请勿扩散。
