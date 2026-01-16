# Bili FindU

B站动态爬虫 + 评论区UID收集器

## 功能

### 动态爬虫 (main.py)
- 批量爬取用户动态内容
- 解析动态类型（图文、视频、转发等）
- 获取带图动态的详细信息（使用 WBI 签名）
- 支持过滤纯转发动态
- 自动保存为 CSV 文件

### 评论收集器 (comment_collector.py)
- 从视频评论区收集用户UID
- 支持多种排序方式（按点赞/按时间）
- 按性别、等级、粉丝数筛选用户
- 自动查询用户粉丝数

### 动态查看器 (view_dynamic.py)
- 快速查看动态详情
- 支持输出 JSON 格式

## 配置说明 (config.json)

```json
{
    "crawl_deepth": 10,
    "crawl_all": true,
    "min_dynamics": 50,
    "request_interval": 10,
    "skip_empty_forward": true,
    "crawl_all_comments": true,
    "comment_pages": 100,
    "comments_per_page": 20,
    "comment_sorts": [1, 0],
    "max_fans": 1000,
    "min_level": 4,
    "sex_filter": ["女"],
    "cookies": { ... }
}
```

### 动态爬虫配置

| 选项 | 类型 | 说明 |
|------|------|------|
| `crawl_deepth` | int | 爬取页数，每页约12条动态 |
| `crawl_all` | bool | `true`: 忽略页数限制，爬取全部动态 |
| `min_dynamics` | int | 最少动态数，低于此数量不保存 |
| `request_interval` | float | 请求间隔（秒），防止风控 |
| `skip_empty_forward` | bool | `true`: 跳过纯转发动态（无评论的转发） |

### 评论收集器配置

| 选项 | 类型 | 说明 |
|------|------|------|
| `crawl_all_comments` | bool | `true`: 爬取全部评论（约5000条上限） |
| `comment_pages` | int | 评论页数（仅 `crawl_all_comments=false` 时生效） |
| `comments_per_page` | int | 每页评论数，最大20 |
| `comment_sorts` | array | 排序方式：`0`=按时间, `1`=按点赞。可多个如 `[1, 0]` |
| `max_fans` | int | 粉丝数上限，超过此数不收集 |
| `min_level` | int | 最低等级要求 |
| `sex_filter` | array | 性别筛选：`"男"`, `"女"`, `"保密"` |

### Cookies 配置

需要从浏览器获取以下 Cookie 字段：

| 字段 | 必须 | 说明 |
|------|------|------|
| `SESSDATA` | ✅ | 登录凭证，最重要的字段 |
| `buvid3` | ✅ | 设备标识，用于 WBI 签名 |
| `buvid4` | ✅ | 设备标识v4，用于 WBI 签名 |
| `b_nut` | ⚠️ | 设备标识，建议填写 |
| `_uuid` | ⚠️ | 设备UUID，建议填写 |

**获取方法：**
1. 登录 [bilibili.com](https://www.bilibili.com)
2. 按 `F12` 打开开发者工具
3. 切换到 `Network` (网络) 标签
4. 刷新页面，点击任意请求
5. 在 `Headers` → `Request Headers` → `Cookie` 中找到对应字段

(也可以直接 edge/chrome 安装cookie editor以获取)

## 使用方法

### 1. 安装依赖

```bash
conda create --name <env> --file requirements.txt
conda activate <env>
```

### 2. 配置文件

```bash
cp config.example.json config.json
```

编辑 `config.json`，填入你的 cookies。

### 3. 动态爬虫

**批量模式** - 从 `collected_uids.csv` 读取UID列表：
```bash
python main.py           # 从头开始
python main.py 100       # 从第100个UID开始（跳过前100个）
```

**单个UID模式**：
```bash
python main.py -u 12345678
```

输出保存在 `saved/xxx的成分表.csv`

### 4. 评论收集器

1. 创建 `target_video.txt`，每行一个BV号：
```
BV1xx411x7xx
BV1yy411y7yy
```

2. 运行：
```bash
python comment_collector.py          # 从头开始
python comment_collector.py 500      # 跳过前500条评论
```

输出 `collected_uids.csv`，可直接作为动态爬虫的输入。

### 5. 动态查看器

```bash
python view_dynamic.py 693542870792011784           # 在浏览器打开
python view_dynamic.py 693542870792011784 --json    # 显示JSON
```

## 注意事项

- 动态保存路径：`./saved/xxx的成分表.csv`
- 日期格式：`YYYY-MM-DD HH:MM:SS`
- B站评论API限制约5000条（250页），使用多种排序可获取更多不同用户
- 遇到风控(-352错误)会自动等待重试(3次, 5s, 10s, 15s)

> ⚠️ **请勿滥用，本项目仅用于学习和测试！**
>
> 尽管已主动降低爬取频率，但**仍无法保证使用本脚本不会导致B站账号被限制**, 本人测试大约10s的request interval不会产生风控问题.

## 致谢

- 感谢原作者的初始代码: https://github.com/GowayLee/bili_dynamic_spy
- 感谢 [SocialSisterYi/bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect) 提供的 B站 API 文档

## License

MIT