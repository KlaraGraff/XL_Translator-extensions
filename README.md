# Translator 扩展列表

[English](README.en.md)

这里登记在 [Translator](https://github.com/KlaraGraff/XL_Translator)「扩展」页「浏览扩展」里能搜到、能直接安装的扩展。每个扩展一个条目 `extensions/<id>.json`，扩展的代码和安装包在作者自己的仓库里。Translator 读取的是工作流从这些条目生成的 `index.json`。

想自己做一个扩展，请从[扩展模板](https://github.com/KlaraGraff/XL_Translator-extension-template)开始。

## 如何提交

1. 在自己的仓库里按模板的 README 完成自测并发布。推送 `v<version>` 标签后，Release 工作流会打出 zip，并在日志里打印条目。
2. Fork 本仓库，新增 `extensions/<id>.json`，内容就是上一步的条目，文件名与 `id` 一致。`summary` 用中文、英文、法文各写一两句，说明它翻译什么文件、哪些内容不翻译。
3. 提 PR 并按模板填写。自动检查会做三件事：
   - 按 `schema/entry.schema.json` 和 Translator 自己的规则校验条目；
   - 从 `download` 的每个地址下载 zip，核对大小和 SHA-256；
   - 用 Translator 的 `adapter test` 检查扩展包（与用户安装时的检查相同），并在扩展的 `samples/` 上试运行。
4. 发布新版本时，在同一个条目文件里改 `version`、`download`、`sha256`、`size`，再提一个 PR。

## 审核规则

- 自动检查全部通过，并且维护者读过代码、没有发现可疑行为（联网、读取与翻译无关的文件、混淆过的代码、与说明不符的功能），即合并。目前由 Claude 代维护者审读代码并合并，合并后在 Translator 项目里报告。
- 合并时填写 `reviewed_at`、`reviewed_by`，`status` 为 `reviewed`。`official` 只用于 Translator 项目自己维护的扩展。
- 审核针对的是提交时的那个版本。扩展以用户的权限运行，「已审核」不是担保；用户安装前会被提醒只安装信任的来源。

## 下架

扩展有问题时（恶意行为、严重缺陷、许可证问题，或作者要求），删掉它的条目即下架。`index.json` 随后重新生成，「浏览扩展」里不再出现它。已经安装的用户不受影响，可以在「扩展」页卸载。作者也可以提 PR 删除自己的条目。

## 条目字段

| 字段 | 说明 |
| --- | --- |
| `id` | 与扩展 `adapter.json` 的 `id` 相同，文件名是 `<id>.json` |
| `name`、`summary` | 名称和简介，中文、英文、法文 |
| `extensions` | 处理的扩展名，与 `adapter.json` 一致 |
| `author`、`repo`、`license` | 作者、项目主页、许可证 |
| `version`、`adapter_api_version`、`min_app_version` | 版本、协议版本、需要的最低 Translator 版本（可空） |
| `download` | zip 的下载地址，按顺序尝试，每个地址都须是同一个文件 |
| `sha256`、`size` | zip 的 SHA-256 和字节数，不超过 2 MB |
| `tags` | 搜索用的标签，可空 |
| `status`、`reviewed_at`、`reviewed_by` | 由维护者在合并时填写 |

## 文件

- `extensions/`：条目。
- `index.json`：`.github/workflows/index.yml` 在 main 更新后生成，不要手改。
- `packages/`：Translator 项目自己维护的扩展的安装包。
- `schema/entry.schema.json`：条目的格式。
- `scripts/`：生成索引（`build_index.py`，只用标准库）和检查条目（`check_entries.py`，需要 Translator 源码）的脚本。
