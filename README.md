# Recite Coach 背诵教练

Recite Coach 是一个用于“生成背诵卡片 + 本地手卡背诵”的工具包。

它由两部分组成：

1. **Skill 工作流**：指导 Codex/Claude 等 agent 将 PDF、讲义、笔记压缩为“踩分点背诵清单”，再生成 `cards.json` 卡片。
2. **本地网页应用**：读取 `cards.json`，在浏览器中进行学习、背默、对照答案、自评和 Leitner 间隔复习。

## 有什么用

- 把完整学习材料整理成可背诵的踩分点。
- 把踩分点转成统一格式的 `cards.json`。
- 在本地浏览器中用手卡方式复习。
- 根据自评结果安排复习顺序：记不住的卡片更快回来，熟练的卡片逐步延后。

适合期末复习、面试准备、概念记忆、语言学习和需要反复背诵的材料。

## 项目组成

### 1. Skill 工作流

- [`recite-coach/SKILL.md`](recite-coach/SKILL.md)：总控 Skill，说明什么时候使用背诵教练，以及如何把生成好的卡片交给播放器。
- [`recite-coach/card-generator/SKILL.md`](recite-coach/card-generator/SKILL.md)：卡片生成 Skill，负责两阶段流程：
  - Phase 1：从 PDF、讲义、笔记中提取踩分点背诵清单。
  - Phase 2：将踩分点拆成 Q&A 手卡，生成 `cards.json`。

### 2. 本地网页应用

- `serve.py`：本地服务器启动器，只监听 `127.0.0.1`。
- `start.bat` / `start.vbs`：Windows 启动入口。
- `start.sh`：macOS / Linux 启动入口。
- [`cards.json`](cards.json)：默认示例卡片。
- [`cards.template.json`](cards.template.json)：示例卡片模板副本，方便恢复。

## 怎么用

### 路径 A：已经有 `cards.json`

1. 把 `cards.json` 放到项目根目录，和 `serve.py` 在同一层。
2. 启动本地播放器：

   Windows：

   ```bat
   start.bat
   ```

   或双击 `start.vbs`，避免命令行窗口闪现。

   macOS / Linux：

   ```bash
   ./start.sh
   ```

   通用方式：

   ```bash
   python serve.py
   ```

3. 浏览器会自动打开背诵页面。
4. 按页面提示学习、默背、对照答案，并用 `1-4` 自评。

> 不推荐直接双击 `recite-player.html`。直接打开 HTML 时浏览器会使用 `file://`，可能无法稳定读取同目录下最新的 `cards.json`，也不利于保存文件形式的学习进度。

### 路径 B：只有 PDF、讲义或笔记

1. 在 Codex/Claude 中使用 `recite-coach` Skill。
2. 让 agent 先将完整材料压缩为踩分点背诵清单。（可以直接提交简洁的背诵清单然后跳过这一步）
3. 再让 agent 将踩分点转成 `cards.json`。
4. 把生成的 `cards.json` 放到项目根目录。
5. 按“路径 A”启动本地播放器。

## 卡片格式

`cards.json` 的最小结构如下：

```json
{
  "title": "Python 基础知识点",
  "newItemsPerSession": 3,
  "items": [
    {
      "id": 1,
      "title": "列表和元组的区别？",
      "importance": 1,
      "content_full": "(1) 列表可变，元组不可变\n(2) 列表用 []，元组用 ()\n(3) 元组可作为 dict 的 key",
      "mnemonic": "列表可变方括号，元组固定圆括号",
      "hints": ["哪个可以作为 dict 的 key？", "可变的是 list"]
    }
  ]
}
```

字段说明：

| 字段 | 说明 |
|------|------|
| `title` | 卡片集名称 |
| `newItemsPerSession` | 每轮引入的新卡片数 |
| `items[].id` | 卡片编号，建议从 1 开始连续 |
| `items[].title` | 问题或知识点标题 |
| `items[].importance` | 重要性：1=核心，2=重要，3=补充 |
| `items[].content_full` | 标准答案 |
| `items[].mnemonic` | 背诵口诀，可为空字符串 |
| `items[].hints` | 提示列表，可为空数组 |

更多示例见 `example-cards/`。

## 背诵方式

播放器的基本流程是：

1. **学习手卡**：先看标准答案和口诀。
2. **默背测试**：按 `Enter` 后自己默背答案。
3. **对照答案**：再次按 `Enter` 查看标准答案。
4. **自评**：按 `1-4` 评价本次背诵。（直接键入键盘上的数字1-4）

评分含义：

| 按键 | 含义 |
|------|------|
| `1` | 重来，完全忘记 |
| `2` | 困难，回忆不完整 |
| `3` | 记住，基本正确 |
| `4` | 熟练，可以延后复习 |

播放器使用 Leitner 间隔复习思想：答错或困难的卡片会更快出现，熟练的卡片会逐步延后。

## 安全信息

- `cards.json` 可能包含你的私人学习资料。公开、上传或分享前请检查内容。
- `.recite-progress.json` 是本地学习进度文件，不建议提交到 Git 或分享给别人。
- `serve.py` 只监听 `127.0.0.1`，用于本机访问，不会主动开放公网服务。
- 不要把版权教材大段原文、考试原题、个人隐私材料直接公开到仓库。
- 如果你要开源自己的卡片集，建议先确认内容来源和授权。

## 示例文件

| 文件 | 内容 |
|------|------|
| `cards.json` | 默认 Python 基础示例卡片 |
| `cards.template.json` | 默认示例模板副本 |
| `example-cards/demo-programming.json` | 编程示例卡片 |
| `example-cards/demo-english.json` | 英语示例卡片 |

## 开发与打包

本地服务器只使用 Python 标准库。

手动运行：

```bash
python serve.py
```

构建 Windows EXE：

```bash
pip install pyinstaller
pyinstaller ReciteCoach.spec
```

构建产物建议放到 GitHub Releases，不直接提交到源码仓库。

## License

MIT
