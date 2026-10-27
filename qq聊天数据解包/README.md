# QQ 聊天数据解包 —— 脚本与逻辑说明

> 本目录汇总了"与app的聊天记录.bak → 人设分析（app.md / 猫猫.md）"全流程中实际使用的脚本与逻辑。
> 数据（解密库、conv.json）与密钥材料不在此目录，见文末"敏感信息与中间产物"。
> 配套交接记录：`..\readme.md`（含 11 节完整执行日志）。
> **动手操作请看 [`使用说明.md`](使用说明.md)**（按阶段复现的逐步手册）。

---

## 一、数据流总览

```
与app的聊天记录.bak（479.5MB ZIP 容器）
   │ ① 解包（PowerShell Expand-Archive）
   ▼
qqbak\db\ 4 个加密库（MSG0 头，SQLCipher 变体）  ── 离线直接解密未成功（密钥不在内存）
   │
   ├──► 确认 bak 已导入本机 QQ（msgbackup\temp\3523605313_3.db + 导入时间戳）
   ▼
本机 nt_msg.db（QQ_NT DB 头，SQLCipher）
   │ ② qqdec.py 修复版解密（密钥来自内存扫描 keys.txt）
   ▼
nt_msg_plain3.db（明文 SQLite，quick_check 通过）
   │ ③ export_conv2.py 导出 + element.proto 解析 40800
   ▼
conv.json（41,085 条结构化消息）
   │ ④ 身份识别（猫猫=本机账号 / app=对方3523605313）
   │ ⑤ stats*.py 语言统计 + 场景抽样
   ▼
app.md、猫猫.md（人设卡）
```

## 二、环境与依赖

- Windows + PowerShell；Python 3.14（miniconda3 环境，路径 `C:\Users\20535\miniconda3\python.exe`）
- Python 包：`cryptography`、`protobuf`（QQNT_Export 的 `element_pb2.py` 依赖）
- 参考代码：`QQNT_Export`（Tealina28/QQNT_Export，含 `element.proto` / `element_pb2.py` / `db\models.py`）
- 关键路径（脚本内为历史绝对路径，运行时按需调整）：
  - 本机库：`C:\Users\20535\Documents\Tencent Files\2053554689\nt_qq\nt_db\nt_msg.db`
  - 解包目录：`C:\Users\20535\AppData\Local\Temp\opencode\qqbak`
  - 输出目录：`C:\Users\20535\AppData\Local\Temp\opencode\dec_out`
  - 密钥材料：`C:\Users\20535\AppData\Local\Temp\opencode\keys.txt`（**敏感，勿外传**）

## 三、SQLCipher 解密参数（已实测验证）

| 参数 | 值 |
| --- | --- |
| 自定义文件头 | 1024 字节（本机库为 `QQ_NT DB`，bak 库为 `SQLite header 3\0` + `MSG0`） |
| 页长 | 4096 |
| 首页 salt | 16 字节 |
| 算法 | AES-256-CBC |
| 页尾保留区 | 48 字节 = IV(16) + HMAC-SHA1(20) + 12 空余 |
| HMAC 派生 | salt 每字节异或 `0x3a` → PBKDF2-HMAC-SHA512，迭代 2，输出 32 字节 |
| HMAC 计算 | hmac(hmac_key, 密文 + IV + 小端页号) |
| 密钥来源 | 内存扫描进程内 `x'<64hex_key><32hex_salt>'` 字符串，key 为已派生 AES key |

**两个关键修复（原解密失败的根因，见 `..\readme.md` 第 11.1 节）：**
1. 非首页解密后须把每页补齐到 4096 字节（原只输出 4048，页不对齐）。
2. 明文 SQLite header 的"每页保留字节"（offset 20）必须写 **48**（匹配实际数据区 4048），不能写 0（会致 cell 指针数组错位），也不要写 header 原始值 0x50(80)。

## 四、脚本分组与用途

### A 组：解密与密钥验证
| 脚本 | 用途 |
| --- | --- |
| `qqdec.py` | **核心库**：`verify_key_hmac`（首页 HMAC 验证）、`decrypt_page`（单页解密）、`decrypt_db`（整库解密，含修复）、`pagescan_keys` / `scan_pid_for_salts`（进程内存扫描） |
| `qkey.py` | 内存候选密钥扫描（早期修补版） |
| `verify_all.py` | 用 `keys.txt` 候选密钥验证本机 3 库 + 对 bak 4 库 salt 定向内存扫描（**需导入 `scan_pid_for_salts`**，缺导入会导致扫描假失败） |
| `test_header_key.py` | 验证 bak header 内 128-hex（即 key_meta）是否为直接密钥（结论：不是，仅为元数据） |
| `check_header.py` | 解密首页并检查明文 header 原始值（page_size / reserved 等）——**确认了 reserved 真实布局** |
| `test_decrypt_local.py` / `test_decrypt2.py` | 用本机密钥解密 nt_msg.db 并 `quick_check` 验证（**含密钥占位符，需填入 keys.txt 中的密钥**） |
| `integrity_check.py` | 完整 `PRAGMA integrity_check` 检查解密输出 |

### B 组：数据库探查
| 脚本 | 用途 |
| --- | --- |
| `probe_temp.py` / `probe_temp2.py` | 探查备份临时库 `3523605313_3.db` 的表结构、chatUin 分布、消息类型（判定其为"备份导入中间产物"） |
| `probe_bak.py` | 查看 bak 库页 1 头部结构（`MSG0`、key_meta、salt 位置）与 files 资源目录 |
| `probe_blob.py` / `probe_blob2.py` / `probe_blob3.py` | 定位解密库中因 freelist 页碎片导致的少量坏行（约 222 行，缺失率 0.5%） |

### C 组：消息导出与解析
| 脚本 | 用途 |
| --- | --- |
| `test_parse.py` | 用 `element_pb2.Elements` 解析 40800 字段的 protobuf 消息体（验证文本段 45101 可提取） |
| `export_conv2.py` | **导出主脚本**：按主键分块读取目标会话、自动跳过坏行，解析消息体输出 `conv.json`（字段：id / self / sender_num / type / sub / time / els） |

### D 组：会话与身份识别
| 脚本 | 用途 |
| --- | --- |
| `identify_sessions.py` / `identify_sessions2.py` | 统计 c2c_msg_table 会话分布（按对端 UID 40021），定位目标会话 `u_VjGLU3TISJx5yA4_aT7mSQ`（41307 条） |
| `identify_target.py` | 查询目标会话的昵称/备注（40093/40094）：app 昵称 `vec灬菓菓~~喵`、备注 `冷月葬花魂` |
| `identify_names.py` | 从 recent_contact_v3_table 列出全部会话名称（识别"猫猫"字样会话） |
| `search_names.py` | 搜索"app/猫猫/佩佩/鱼鱼/哥哥"全部出现语境——**核实身份对应**（结论见下） |
| `read_conv.py` | 抽样阅读聊天内容（最早消息、随机样本） |

**身份结论（依据聊天内容核实，非猜测）**：
- **猫猫 = 本机账号（2053554689）**：证据"我女朋友是鱼鱼，我是猫猫""叫我猫猫就行"，对方大量称其"猫猫"。
- **app = 对方（3523605313）**：证据用户反复称其"app"（"app好亲人""不是app我不喜欢"）、"佩佩"；备注"冷月葬花魂"。

### E 组：语言统计与人设证据
| 脚本 | 用途 |
| --- | --- |
| `stats1.py` | 基础统计：消息数/字数/长度分布/活跃时段/高频词/语气词/标点（**初版含通知干扰**） |
| `stats2.py` | 长消息样本、每日首尾句、回复间隔、话题关键词 |
| `stats3.py` | 颜文字、emoji 元素、戳一戳动作分布、负面场景抽样、深夜活跃 |
| `stats4.py` | 游戏/撒娇/关心/随机对话流场景抽样 |
| `stats5.py` | 敷衍单字、早晚问候频率、短句样本、游戏求带配对 |
| `recount_nudge.py` | **戳一戳归属修正**：按通知文本 `<qq uin>` 判定发起者（替代不可靠的 40020 归属字段） |
| `parse_nudge_text.py` | 解析双方戳一戳的固定说辞（猫猫"亲亲+爱你哦/你是我的了"、app"捏捏+喵喵喵"） |
| `recount_app_text.py` | 重算 app **纯文本**特征（剔除戳一戳系统通知，修正语气词/口头禅/标点数字） |
| `verify_claims.py` | 核验人设卡红线断言（粗口/我爱你/笑声串的真实计数，防止断言与语料矛盾） |

## 五、关键统计结论（写入人设卡的证据）

| 指标 | 猫猫（本机） | app（对方） |
| --- | --- | --- |
| 消息数 | 23,165 | 17,920 |
| 纯文本 / 总字数 | 14,310 / 78,088 | 14,100 / 558,973 |
| 单条中位数 | 4 字（70% ≤5 字） | 4 字（含 1,537 条 50+ 字长文） |
| 口头禅 | 宝宝425 / 佩佩165 / 晚安57 / 在干嘛55 | 哥哥729 / 早290 / 我在168 / 晚安163 / 怎么了138 |
| 戳一戳（按 `<qq uin>` 判定） | **亲了亲 787 + 揉了揉 33 = 820 次**，说"爱你哦652 / 你是我的了91 / 软软的33" | **捏了捏 689 次**，说"喵喵喵！" |
| 早晚安 | 晚安类167 / 早安类53 | 晚安类323 / 早安类225 |
| 标志行为 | 短句轰炸、求带游戏、亲亲宣告占有、怕冷落 | 秒回、清晨先问早、傲娇宠溺、自责型道歉 |

## 六、运行顺序（复现流程）

1. `qkey.py` / `verify_all.py` → 从 QQ 进程内存取得本机库密钥（写入 keys.txt，含 bak 定向扫描）
2. `test_decrypt2.py`（填入密钥）→ 解密 nt_msg.db → `nt_msg_plain3.db`；`integrity_check.py` 验证
3. `probe_blob*.py` → 确认坏行范围（约 222 行可跳过）
4. `export_conv2.py` → 导出 `conv.json`
5. `identify_*.py` + `search_names.py` → 确认目标会话与身份
6. `stats*.py` + `recount_*.py` → 产出统计证据
7. `verify_claims.py` → 校验红线断言 → 据此撰写 `..\app.md`、`..\猫猫.md`

## 七、敏感信息与中间产物

- **密钥明文**（keys.txt、旧 decrypt_all.py）：仅存于 `C:\Users\20535\AppData\Local\Temp\opencode`，**勿复制到本项目目录、勿外传**；本目录脚本已脱敏（密钥占位符）。
- 解密明文库（约 480MB）：`C:\Users\20535\AppData\Local\Temp\opencode\dec_out\nt_msg_plain3.db`
- 结构化消息（7MB）：`C:\Users\20535\AppData\Local\Temp\opencode\qqtask\conv.json`（含完整聊天文本，属用户个人数据）
- 原始 bak 未修改；本机 QQ 库未原地改写。

## 八、已知限制与未完成项

- bak 4 库离线直接解密未实现（密钥不在当前内存；OIDB `0xcde` 协议路线未实现）——当前以"bak 已导入本机"的数据完成分析。
- 解密库存在约 222 条坏行（freelist 页碎片导致，缺失率 0.5%），已跳过。
- 图片（7,232）、语音（30）未识别/转写。
- 年龄、地域、职业等敏感身份未写入人设卡（样本不足，不推断）。

---

# 补充说明（追加章节）

## 九、执行时间线与关键决策记录

以下按实际执行顺序记录每一步做什么、结果如何、为何转向，供复核与复现。

| 步骤 | 动作 | 结果 / 决策 |
| --- | --- | --- |
| 1 | 解包 `与app的聊天记录.bak`（ZIP 容器） | 得到 `qqbak\db\` 4 个加密库（160AA5/428214/742BB4/DCD02E），页 1 为 `MSG0` 自定义头 |
| 2 | 进程内存扫描候选密钥 | 扫描到 19-20 对 `x'<key><salt>'` 字符串，写为 keys.txt |
| 3 | 用候选密钥验证本机 3 个库 | 本机 `nt_msg.db`（QQ_NT DB 头）密钥命中且 HMAC 通过 |
| 4 | 用同一批密钥定向扫描 bak 4 库 salt | **全部不匹配** → bak 离线直接解密死路；`test_header_key.py` 也证明 header 内 128-hex（key_meta）不是密钥 |
| 5 | **决策**：改走"bak 已导入本机"路线 | 发现 `msgbackup\temp\3523605313_3.db`（41,279 条）与 `msg_backup_storage_table` 导入时间戳（≈2026-10-26 10:03），锁定"目标会话已在本机库中" |
| 6 | 修复 `qqdec.py` 两个 bug | ① 非首页页长补齐 4096；② 明文 header reserved 字段写 48 → 解密成功（nt_msg_plain3.db 480MB，quick_check 通过） |
| 7 | 导出目标会话 | 分块 + 跳过坏行 → `conv.json` 41,085 条（缺失 222 条 / 0.5%） |
| 8 | 身份核实 | 依聊天内容：猫猫=本机账号（自称"我是猫猫"）、app=对方 3523605313（昵称 vec灬菓菓~~喵 / 备注 冷月葬花魂 / 用户称其"app""佩佩"） |
| 9 | 统计 + 人设卡 | stats1-5 + 场景抽样 → `app.md` / `猫猫.md`（初版完成） |
| 10 | **戳一戳归属修正** | 用户指出"猫猫发起的戳一戳也挺多的" → 用通知文本 `<qq uin>` 重判：猫猫 820 次（亲亲 787 + 揉揉 33）、app 689 次（捏捏）；同时剔除通知后重算 app 纯文本特征 |
| 11 | 红线断言核验 | verify_claims.py 复核"0 粗口/我爱你/哈哈哈"等断言并修正 |
| 12 | 脚本归档 | 复制 31 脚本 + 脱敏 + 撰写本 README |

## 十、数据库字段映射与消息解析细节

### c2c_msg_table 关键字段（本机 nt_msg.db）
| 字段号 | 含义 | 说明 |
| --- | --- | --- |
| 40001 | 消息自增 id | 主键 |
| 40020 | 发送者 UID | **戳一戳系统通知不可靠**（多归为接收方），发起者以通知文本 `<qq uin>` 为准 |
| 40021 | 会话对端 UID | 目标会话 `u_VjGLU3TISJx5yA4_aT7mSQ` = 3523605313 |
| 40011 | 消息类型 | 1=文本、2=图片、3=语音、4=视频、5=系统通知（戳一戳/撤回等）、6=文件、7=表情…（按实际统计） |
| 40012 | 子类型 | 如通知类细分 |
| 40050 | 时间 | Unix 秒 |
| 40800 | 消息体 | protobuf，用 `element.proto` 的 `Elements` 解析 |
| 40093/40094 | 昵称/备注 | 对方昵称 `vec灬菓菓~~喵`、备注 `冷月葬花魂` |

### protobuf 解析路径（QQNT_Export / element.proto）
```
Elements { repeated Element elements = 40800; }
Element { optional ElementType type = 3; (其余字段略) }
  type=1  → TextElement { string content = 45101; }      # 纯文本
  type=7  → FaceElement / image (其余略)                  # 表情/图片（未转写）
  type=8  → NoticeElement (其余略)                        # 系统通知（含戳一戳文本 48214）
```

### 戳一戳通知的文本结构（归属判定依据）
```
<qq uin="发起者UID">昵称</qq> 捏了捏 <qq uin="接收者UID">昵称</qq> 的脸并对我说:喵喵喵！
```
- **第一个 `<qq uin>` 为发起者**；40020 字段对这类通知不可靠。
- 结论：猫猫=亲了亲 787（"爱你哦"652 / "你是我的了"91 / "爱你😘"37）+ 揉了揉 33（"软软的"）= 820 次；app=捏了捏 689（"喵喵喵！"）+ 猫猫另有捏了捏 5 次。

### gtip 通知与纯文本的区分
- 撤回、入群、名片分享等 `gtip` 通知文本会被计入"消息数"，但**不是对方真实发言**——统计纯文本特征时必须剔除（见 `recount_app_text.py`）。
- 初版 stats1 的口头禅（哦 718、感叹号 718 等）即因此失真，修正后：哦 66、感叹号 24、哥哥 729、早 290、我在 168、晚安 163、怎么了 138。

## 十一、踩坑与失败记录（完整清单）

1. **`python` 命令缺 cryptography**：默认解释器没有该包 → 全部解密脚本须用 `C:\Users\20535\miniconda3\python.exe`（cryptography 50.0.0）。
2. **verify_all.py 缺导入**：`scan_pid_for_salts` 未定义会抛异常、表现为"扫描失败"——补 import 后正常。
3. **明文 header 保留字节不能照抄**：header 明文原始值是 0x50(80)，与真实布局不符（数据区实际 4048）；必须写 48（RESERVE）。写 0 会致 cell 指针错位、quick_check 大范围失败。
4. **非首页每页输出长度**：原实现每页只输出 4048 字节（丢尾部 48 字节保留区）→ 页不对齐、全库错位；须补齐 4096。
5. **戳一戳归属字段不可靠**：40020 对戳一戳通知几乎全记为接收方 → 按通知文本 `<qq uin>` 重判（用户指出的问题）。
6. **坏行分散**：约 222 行损坏行分散在 offset 20/200/1000 附近，`40030` 列在坏行上抛 malformed → 用"按主键分块 + skip 策略"绕过，缺失率 0.5%。
7. **bak 离线解密死路**：密钥不在当前内存、OIDB `0xcde` 协议未实现；key_meta 非密钥（HMAC 实测不匹配）。

## 十二、脚本入参/出参速查

> 所有脚本为"硬编码路径 + 直接运行"式（历史调试风格），无命令行参数；改路径需直接编辑脚本内常量。

| 脚本 | 输入（脚本内常量） | 输出 |
| --- | --- | --- |
| `qqdec.py` | 库路径 / 密钥 / salt | 解密后明文库（模块，被调用） |
| `qkey.py` | QQ 进程名（内存扫描） | 候选密钥/盐写入 keys.txt |
| `verify_all.py` | keys.txt + 本机 3 库 + bak 4 库 salt | 各库密钥命中结论 |
| `test_header_key.py` | bak 库路径 + HEXSTR | key_meta 各切法的 HMAC 匹配结论 |
| `check_header.py` | 库路径 + 密钥 | 明文 header 原始值（page_size/reserved） |
| `test_decrypt_local.py` / `test_decrypt2.py` | nt_msg.db + 密钥（占位符） | nt_msg_plain3.db + quick_check 结果 |
| `integrity_check.py` | 明文库路径 | integrity_check 输出 |
| `probe_temp.py` / `probe_temp2.py` | 备份临时库路径 | 表结构 / chatUin 分布 / 消息类型 |
| `probe_bak.py` | bak 库路径 | 页 1 头部结构 / files 目录 |
| `probe_blob*.py` | 明文库路径 | 坏行定位（offset、行数） |
| `test_parse.py` | 40800 字节样本 | 解析字段验证 |
| `export_conv2.py` | 明文库 + 会话 UID | conv.json（41,085 条） |
| `identify_sessions*.py` | 明文库 | 会话分布表（按 40021） |
| `identify_target.py` | 明文库 + 会话 UID | 昵称/备注（40093/40094） |
| `identify_names.py` | recent_contact_v3_table | 全部会话名称 |
| `search_names.py` / `read_conv.py` | conv.json | 称呼语境样本 / 聊天抽样 |
| `stats1-5.py` | conv.json | 各项统计 + 场景样本（打印） |
| `recount_nudge.py` | conv.json（通知消息） | 戳一戳归属统计（按 `<qq uin>`） |
| `parse_nudge_text.py` | conv.json | 双方戳一戳固定说辞分布 |
| `recount_app_text.py` | conv.json | app 纯文本口头禅/语气词/标点（剔除通知） |
| `verify_claims.py` | conv.json | 红线断言真实计数（粗口/我爱你/哈哈哈） |

## 十三、验证与质量保证

1. **解密正确性**：`PRAGMA quick_check`（仅剩无害 freelist 警告）+ `integrity_check.py`；32 张表全部可读。
2. **统计口径**：口头禅/语气词用**子串计数**（含叠词、跨词命中），消息条数为独立口径；统计数字与人设卡并排核对（readme.md 第 11.3 节）。
3. **断言核验**：人设卡红线断言（"几乎不爆粗""我爱你 1 次"等）经 `verify_claims.py` 在真实语料上复算后才写入，防止模型臆断。
4. **交付校验**：app.md / 猫猫.md / 本 README 均通过 verifier-hub 校验（格式 OK、0 占位符）。
5. **身份不臆断**：猫猫=本机、app=对方 的结论均来自聊天原文证据（自称与互称），非猜测。
