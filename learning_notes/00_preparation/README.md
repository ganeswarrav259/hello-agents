# 学习前准备

[返回总目录](../README.md) · [环境记录](environment.md) · [Git 与同步](git_and_sync.md)

今天只验证“能找到文件、能运行一段不联网的 Python”。不安装全书依赖，不申请或填写 API 密钥。

## 1. 在哪里输入命令

下面的命令写在终端中，不写进 Python 文件，也不在 `>>>` 提示符后执行。
仓库根目录就是能同时看到 `README.md`、`docs/`、`code/`、`learning_notes/` 的那层文件夹。

没有本地副本时，在准备存放项目的父文件夹执行：

```bash
git clone https://github.com/ganeswarrav259/hello-agents.git
cd hello-agents
```

已经克隆过就进入已有文件夹，不重复克隆；同步前看 [Git 指南](git_and_sync.md)，保留未提交改动。
只阅读笔记可以在 GitHub 网页上完成。提示找不到 Git 或 Python 时，把报错发来，不执行不明安装脚本。

## 2. 检查工具版本

Windows 可先运行 `py -3 --version`；macOS / Linux 可先运行 `python3 --version`。再运行 `git --version`。
若某个命令不存在，不代表其他命令也不存在；根据实际报错定位安装或 PATH 问题。
原教程第 4 章建议 Python 3.10+；实际章节的依赖要求仍需逐项核对，不保证任意新版本都兼容全部框架。

## 3. 创建隔离环境并运行离线文件

仅在尚未创建此虚拟环境时执行创建命令；已有项目环境可以继续使用，不覆盖现有环境。
下面直接调用环境中的 Python，不需要激活脚本，也不用修改 PowerShell 执行策略。

Windows PowerShell，在仓库根目录：

```powershell
py -3 -m venv learning_notes/.venv
.\learning_notes\.venv\Scripts\python.exe learning_notes/00_preparation/hello.py
```

macOS / Linux 终端，在仓库根目录：

```bash
python3 -m venv learning_notes/.venv
./learning_notes/.venv/bin/python learning_notes/00_preparation/hello.py
```

这些是供学习者执行的步骤，不表示已在你的电脑运行。已有可用 Python 时，也可以先用它直接运行 hello.py。

预期输出：

```text
Hello, Agents!
我会按章节记录学习。
```

这个示例只调用 print，不联网、不读配置、不安装第三方包。

## 4. 记录，不猜测

在 [environment.md](environment.md) 中记录系统、Python 版本、终端、成功命令和实际输出。初始值保留“待确认”。
把 hello.py 第二行改成自己的学习目标，重新运行；不要填姓名、邮箱等个人信息。

## 5. 以后才做的准备

遇到真实服务调用时，再确认目标服务、依赖版本、数据去向与费用，并为当前案例建立依赖记录。
`.env` 放在哪里由代码的加载方式决定；不要以为存在模板就会自动读取。
阅读 [原教程环境配置](../../Extra-Chapter/Extra07-环境配置.md) 时，涉及服务与安装版本的信息需当场核对。
不要上传真实 .env、令牌或截图中的密钥。

依据：[Python venv 官方文档](https://docs.python.org/3/library/venv.html)，包括无需激活即可调用虚拟环境解释器；
[本 fork 第 4 章](../../docs/chapter4/第四章%20智能体经典范式构建.md) 的 4.1.1。
