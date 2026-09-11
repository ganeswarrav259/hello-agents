# Git：保存自己的学习记录，保留上游教程

[准备指南](README.md) · [协作规则](../WORKFLOW.md)

## 三个位置不要混淆

本地文件夹是电脑上的工作副本；`origin` 应指向自己的 `ganeswarrav259/hello-agents`；`upstream` 通常指向原作者 `datawhalechina/hello-agents`。
远程名只是约定，先用 `git remote -v` 检查，不假定现有配置；输出若包含令牌先脱敏。

## 获取助手已经提交的笔记

在本地仓库根目录先检查：

```bash
git status
git branch --show-current
```

只有当前在 main、工作区没有未保存到 Git 的改动时，才执行：

```bash
git pull --ff-only origin main
```

出现拒绝快进或本地修改提示时停止，把脱敏后的提示用于排查。不要用强制推送、硬重置或“丢弃更改”绕过问题。

## 自己修改笔记后上传

在 main 已与远程同步、只准备提交自己的学习记录时：

```bash
git status
git diff -- learning_notes/
git add learning_notes/ LEARNING.md
git diff --cached --stat
git diff --cached
git commit -m "docs(ch01): record first learning question"
git push origin main
```

提交信息根据实际章节更改；先检查暂存内容，不提交所有本地文件。Git 身份配置或推送认证失败时按真实错误处理，不把令牌写进命令或文件。
`.gitignore` 不会保护已经被追踪的秘密，也不是安全扫描器；不要使用 `git add -f` 强行加入配置。

## 上游教程更新时怎么处理

本学习区与 docs/code 分开，是为了减少冲突，不保证永不冲突。
有更新需求时先保存工作、更新 origin/main，再检查 upstream 配置；没有 upstream 才添加：

```bash
git remote add upstream https://github.com/datawhalechina/hello-agents.git
git fetch upstream
```

已经有 upstream 时只 fetch，不重复 add。不要现在为了“准备”就盲目合并。
实际同步建议在干净的 main 上新建未占用的同步分支，合并 upstream/main，检查冲突与学习区，再向自己的 main 开 PR。
示意命令中的分支名需要与当次同步对应，存在同名分支时换名而非覆盖：

```bash
git switch -c sync/upstream-review
git merge upstream/main
```

如果有冲突，不继续自动推送，不选全量覆盖；逐文件核对。同步后重新核对章节链接和引用快照，个人笔记的历史结论保留更正记录。
本次初始化没有执行上游合并，没有改变仓库设置。

参考：[GitHub 同步 fork](https://docs.github.com/en/pull-requests/how-tos/work-with-forks/syncing-a-fork)、[Git 忽略规则](https://git-scm.com/docs/gitignore)。
