# 大富翁游戏项目Git使用指南

## 1. 环境配置

### 1.1 基础配置
```bash
# 配置用户信息
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"

# 配置默认编辑器
git config --global core.editor "code --wait"

# 配置换行符
git config --global core.autocrlf true  # Windows
git config --global core.autocrlf input # Linux/Mac

# 配置默认分支
git config --global init.defaultBranch main
```

### 1.2 别名配置
```bash
# 配置常用命令别名
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual '!gitk'
```

### 1.3 SSH配置
```bash
# 生成SSH密钥
ssh-keygen -t rsa -b 4096 -C "你的邮箱"

# 查看公钥
cat ~/.ssh/id_rsa.pub

# 测试连接
ssh -T git@github.com
```

## 2. 分支管理

### 2.1 分支类型
1. **主分支**
   - `main`：主分支，用于发布
   - `develop`：开发分支，用于集成功能

2. **功能分支**
   - `feature/*`：功能分支，用于开发新功能
   - `bugfix/*`：修复分支，用于修复bug
   - `hotfix/*`：热修复分支，用于紧急修复

3. **发布分支**
   - `release/*`：发布分支，用于版本发布
   - `tag/*`：标签，用于标记版本

### 2.2 分支命名
1. **功能分支**
   ```
   feature/功能名称-开发者
   例如：feature/player-system-zhangsan
   ```

2. **修复分支**
   ```
   bugfix/问题描述-开发者
   例如：bugfix/login-error-zhangsan
   ```

3. **热修复分支**
   ```
   hotfix/问题描述-开发者
   例如：hotfix/server-crash-zhangsan
   ```

4. **发布分支**
   ```
   release/版本号
   例如：release/v1.0.0
   ```

### 2.3 分支操作
```bash
# 创建分支
git branch feature/new-feature

# 切换分支
git checkout feature/new-feature

# 创建并切换分支
git checkout -b feature/new-feature

# 删除分支
git branch -d feature/new-feature

# 强制删除分支
git branch -D feature/new-feature

# 合并分支
git merge feature/new-feature

# 变基分支
git rebase develop
```

## 3. 提交规范

### 3.1 提交信息格式
<类型>(<范围>): <描述>
[可选的正文]
[可选的脚注]

### 3.2 提交类型
1. **feat**：新功能
2. **fix**：修复bug
3. **docs**：文档更新
4. **style**：代码格式（不影响代码运行的变动）
5. **refactor**：重构（既不是新增功能，也不是修改bug的代码变动）
6. **perf**：性能优化
7. **test**：增加测试
8. **chore**：构建过程或辅助工具的变动

### 3.3 提交示例
feat(player): 添加玩家移动功能
实现玩家在地图上的移动
添加移动动画效果
处理移动碰撞检测
Closes #123

### 3.4 提交操作
```bash
# 查看状态
git status

# 添加文件
git add .

# 提交更改
git commit -m "feat(player): 添加玩家移动功能"

# 修改提交信息
git commit --amend

# 合并提交
git rebase -i HEAD~3
```

## 4. 协作流程

### 4.1 功能开发流程
1. **创建功能分支**
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/new-feature
   ```

2. **开发功能**
   ```bash
   # 开发代码
   git add .
   git commit -m "feat: 实现新功能"
   ```

3. **同步主分支**
   ```bash
   git checkout develop
   git pull
   git checkout feature/new-feature
   git rebase develop
   ```

4. **提交合并请求**
   ```bash
   git push origin feature/new-feature
   # 在GitHub上创建Pull Request
   ```

### 4.2 代码审查流程
1. **审查代码**
   - 检查代码规范
   - 检查功能实现
   - 检查测试覆盖
   - 检查文档更新

2. **修改代码**
   ```bash
   # 根据反馈修改代码
   git add .
   git commit -m "fix: 根据反馈修改代码"
   git push origin feature/new-feature
   ```

3. **合并代码**
   ```bash
   # 在GitHub上合并Pull Request
   git checkout develop
   git pull
   ```

### 4.3 发布流程
1. **创建发布分支**
   ```bash
   git checkout develop
   git pull
   git checkout -b release/v1.0.0
   ```

2. **准备发布**
   ```bash
   # 更新版本号
   # 更新文档
   # 运行测试
   git add .
   git commit -m "chore: 准备发布v1.0.0"
   ```

3. **合并到主分支**
   ```bash
   git checkout main
   git merge release/v1.0.0
   git tag -a v1.0.0 -m "发布v1.0.0"
   git push origin main --tags
   ```

4. **合并回开发分支**
   ```bash
   git checkout develop
   git merge release/v1.0.0
   git push origin develop
   ```

## 5. 常见问题

### 5.1 撤销操作
```bash
# 撤销工作区修改
git checkout -- file

# 撤销暂存区修改
git reset HEAD file

# 撤销提交
git reset --soft HEAD^
git reset --mixed HEAD^
git reset --hard HEAD^

# 撤销合并
git reset --hard ORIG_HEAD
```

### 5.2 冲突解决
1. **查看冲突**
   ```bash
   git status
   ```

2. **解决冲突**
   ```bash
   # 编辑冲突文件
   # 解决冲突
   git add .
   git commit -m "fix: 解决冲突"
   ```

3. **继续变基**
   ```bash
   git rebase --continue
   ```

### 5.3 分支管理
1. **清理分支**
   ```bash
   # 删除已合并的分支
   git branch --merged | grep -v "\*" | xargs -n 1 git branch -d

   # 删除远程分支
   git push origin --delete branch-name
   ```

2. **同步远程分支**
   ```bash
   # 更新远程分支信息
   git fetch --prune

   # 同步远程分支
   git pull --rebase
   ```

### 5.4 版本管理
1. **查看版本**
   ```bash
   # 查看标签
   git tag

   # 查看版本历史
   git log --oneline --graph --decorate
   ```

2. **创建版本**
   ```bash
   # 创建标签
   git tag -a v1.0.0 -m "发布v1.0.0"

   # 推送标签
   git push origin v1.0.0
   ```

## 6. 最佳实践

### 6.1 提交规范
1. **提交前检查**
   - 运行测试
   - 检查代码规范
   - 检查文档更新
   - 检查提交信息

2. **提交粒度**
   - 一个功能一个提交
   - 一个bug修复一个提交
   - 一个文档更新一个提交

3. **提交信息**
   - 使用规范的提交类型
   - 简明扼要的描述
   - 必要时添加详细说明

### 6.2 分支管理
1. **分支策略**
   - 主分支保持稳定
   - 功能分支及时合并
   - 定期清理分支
   - 保持分支最新

2. **合并策略**
   - 使用rebase保持提交历史清晰
   - 合并前进行代码审查
   - 合并后及时删除分支
   - 保持提交历史整洁

### 6.3 协作流程
1. **日常开发**
   - 及时同步主分支
   - 定期提交代码
   - 保持代码整洁
   - 及时处理冲突

2. **代码审查**
   - 认真审查代码
   - 及时反馈问题
   - 积极沟通讨论
   - 保持代码质量

3. **版本发布**
   - 严格遵循发布流程
   - 确保代码质量
   - 及时更新文档
   - 做好版本管理

## 7. 工具配置

### 7.1 Git配置
```bash
# 配置Git
git config --global core.autocrlf true
git config --global core.safecrlf true
git config --global core.quotepath false
git config --global gui.encoding utf-8
git config --global i18n.commit.encoding utf-8
git config --global i18n.logoutputencoding utf-8
```

### 7.2 编辑器配置
1. **VSCode配置**
   ```json
   {
     "editor.formatOnSave": true,
     "editor.codeActionsOnSave": {
       "source.fixAll": true
     },
     "git.enableSmartCommit": true,
     "git.confirmSync": false,
     "git.autofetch": true
   }
   ```

2. **PyCharm配置**
   - 启用自动导入
   - 启用代码格式化
   - 启用代码检查
   - 启用Git集成

### 7.3 钩子配置
1. **提交前钩子**
   ```bash
   # pre-commit
   #!/bin/sh
   # 运行测试
   python -m pytest
   # 检查代码规范
   flake8 .
   # 检查类型
   mypy .
   ```

2. **提交信息钩子**
   ```bash
   # commit-msg
   #!/bin/sh
   # 检查提交信息格式
   npx commitlint --edit $1
   ```

## 8. 安全措施

### 8.1 访问控制
1. **SSH密钥**
   - 使用SSH密钥认证
   - 定期更新密钥
   - 妥善保管私钥
   - 及时撤销失效密钥

2. **权限管理**
   - 严格控制仓库权限
   - 定期审查权限
   - 及时撤销权限
   - 记录权限变更

### 8.2 数据安全
1. **备份策略**
   - 定期备份仓库
   - 多地点备份
   - 加密备份数据
   - 测试备份恢复

2. **敏感信息**
   - 不提交敏感信息
   - 使用环境变量
   - 使用配置文件
   - 使用密钥管理

### 8.3 操作安全
1. **提交安全**
   - 验证提交者身份
   - 签名提交
   - 验证提交内容
   - 记录操作日志

2. **合并安全**
   - 强制代码审查
   - 验证合并内容
   - 记录合并历史
   - 保护重要分支

## 9. 故障处理

### 9.1 常见问题
1. **提交问题**
   - 提交信息错误
   - 提交内容错误
   - 提交冲突
   - 提交丢失

2. **分支问题**
   - 分支冲突
   - 分支丢失
   - 分支混乱
   - 分支污染

3. **合并问题**
   - 合并冲突
   - 合并错误
   - 合并丢失
   - 合并污染

### 9.2 解决方案
1. **提交修复**
   ```bash
   # 修改提交信息
   git commit --amend

   # 修改提交内容
   git reset --soft HEAD^
   git add .
   git commit -m "新的提交信息"

   # 恢复提交
   git reflog
   git reset --hard HEAD@{n}
   ```

2. **分支修复**
   ```bash
   # 恢复分支
   git reflog
   git checkout -b branch-name HEAD@{n}

   # 清理分支
   git branch -D branch-name
   git checkout -b branch-name
   ```

3. **合并修复**
   ```bash
   # 取消合并
   git merge --abort

   # 重置合并
   git reset --hard ORIG_HEAD

   # 重新合并
   git merge branch-name
   ```

## 10. 文档维护

### 10.1 文档更新
1. **更新时机**
   - 新增功能时
   - 修改功能时
   - 修复bug时
   - 更新规范时

2. **更新内容**
   - 功能说明
   - 接口文档
   - 使用说明
   - 注意事项

### 10.2 版本管理
1. **文档版本**
   - 跟随代码版本
   - 记录更新历史
   - 保持版本一致
   - 及时更新文档

2. **文档备份**
   - 定期备份
   - 多地点备份
   - 版本控制
   - 及时恢复

### 10.3 文档审查
1. **审查内容**
   - 文档完整性
   - 文档准确性
   - 文档及时性
   - 文档规范性

2. **审查流程**
   - 提交审查
   - 修改完善
   - 确认发布
   - 定期更新