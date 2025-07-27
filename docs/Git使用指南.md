# Git使用指南

## 1. Git基础概念

### 1.1 什么是Git
Git是一个分布式版本控制系统，用于跟踪文件的变化，协调多人协作开发。

### 1.2 基本概念
- **仓库（Repository）**：项目的代码存储空间
- **工作区（Working Directory）**：本地编辑文件的地方
- **暂存区（Staging Area）**：临时存储修改的地方
- **本地仓库（Local Repository）**：本地代码版本库
- **远程仓库（Remote Repository）**：服务器上的代码版本库

### 1.3 分支概念
- **主分支（main）**：稳定版本分支
- **开发分支（develop）**：开发版本分支
- **功能分支（feature）**：新功能开发分支
- **修复分支（hotfix）**：紧急bug修复分支

## 2. Git安装和配置

### 2.1 安装Git
1. **Windows系统**
   - 访问 https://git-scm.com/download/win
   - 下载并安装Git for Windows
   - 安装时选择默认选项即可

2. **Mac系统**
   - 使用Homebrew安装：`brew install git`
   - 或访问 https://git-scm.com/download/mac

3. **Linux系统**
   - Ubuntu/Debian：`sudo apt-get install git`
   - CentOS：`sudo yum install git`

### 2.2 基础配置
```bash
# 配置用户名和邮箱
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"

# 配置默认编辑器
git config --global core.editor "notepad"  # Windows
git config --global core.editor "vim"      # Linux/Mac
```

## 3. 基本操作

### 3.1 仓库操作
```bash
# 克隆远程仓库
git clone https://github.com/用户名/仓库名.git

# 初始化本地仓库
git init

# 查看仓库状态
git status

# 查看提交历史
git log
```

### 3.2 文件操作
```bash
# 添加文件到暂存区
git add 文件名
git add .  # 添加所有文件

# 提交更改
git commit -m "提交说明"

# 查看文件差异
git diff
```

### 3.3 分支操作
```bash
# 查看分支
git branch

# 创建分支
git branch 分支名

# 切换分支
git checkout 分支名

# 创建并切换分支
git checkout -b 分支名

# 合并分支
git merge 分支名
```

## 4. 团队协作流程

### 4.1 基本工作流程
1. **获取最新代码**
   ```bash
   git pull origin develop
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/功能名称
   ```

3. **开发功能**
   - 编写代码
   - 添加文件：`git add .`
   - 提交更改：`git commit -m "功能说明"`

4. **推送到远程**
   ```bash
   git push origin feature/功能名称
   ```

5. **创建合并请求**
   - 在GitHub/GitLab上创建Pull Request
   - 等待代码审查
   - 解决冲突（如果有）

### 4.2 解决冲突
1. **查看冲突文件**
   ```bash
   git status
   ```

2. **手动解决冲突**
   - 打开冲突文件
   - 找到并解决冲突标记（<<<<<<< HEAD, =======, >>>>>>>）
   - 保存文件

3. **提交解决后的文件**
   ```bash
   git add .
   git commit -m "解决冲突"
   ```

## 5. 常用命令速查

### 5.1 基础命令
```bash
# 查看帮助
git help 命令名

# 查看配置
git config --list

# 撤销修改
git checkout -- 文件名

# 撤销暂存
git reset HEAD 文件名
```

### 5.2 远程操作
```bash
# 查看远程仓库
git remote -v

# 添加远程仓库
git remote add origin 仓库地址

# 推送到远程
git push origin 分支名

# 拉取远程更新
git pull origin 分支名
```

## 6. 最佳实践

### 6.1 提交规范
- 提交信息格式：`type(scope): message`
- 类型（type）：
  - feat: 新功能
  - fix: 修复bug
  - docs: 文档更新
  - style: 代码格式
  - refactor: 重构
  - test: 测试
  - chore: 构建过程或辅助工具的变动

### 6.2 分支管理
- 主分支（main）：保持稳定
- 开发分支（develop）：日常开发
- 功能分支（feature/*）：新功能开发
- 修复分支（hotfix/*）：紧急bug修复

### 6.3 代码审查
- 提交前自我检查
- 遵循代码规范
- 编写清晰的提交信息
- 及时响应审查意见

## 7. 常见问题

### 7.1 常见错误
1. **提交失败**
   - 检查网络连接
   - 确认有提交权限
   - 检查远程仓库地址

2. **合并冲突**
   - 先拉取最新代码
   - 仔细检查冲突内容
   - 与团队成员沟通

3. **分支问题**
   - 确保在正确的分支上
   - 检查分支名称
   - 确认分支权限

### 7.2 实用技巧
1. **查看历史**
   ```bash
   # 查看提交历史
   git log --oneline
   
   # 查看文件历史
   git log --oneline 文件名
   ```

2. **暂存工作**
   ```bash
   # 暂存当前工作
   git stash
   
   # 恢复暂存的工作
   git stash pop
   ```

3. **撤销操作**
   ```bash
   # 撤销最后一次提交
   git reset --soft HEAD^
   
   # 撤销远程提交
   git revert 提交ID
   ```

## 8. 学习资源

### 8.1 官方资源
- Git官方文档：https://git-scm.com/doc
- Git参考手册：https://git-scm.com/docs

### 8.2 推荐教程
- Git教程：https://www.runoob.com/git/git-tutorial.html
- Git简明指南：https://rogerdudler.github.io/git-guide/index.zh.html

### 8.3 图形化工具
- GitHub Desktop
- SourceTree
- GitKraken
- VS Code的Git插件 