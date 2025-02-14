# Docker 部署指南

## 目录
1. [环境要求](#环境要求)
2. [安装 Docker](#安装-docker)
3. [部署步骤](#部署步骤)
4. [常用命令](#常用命令)
5. [故障排除](#故障排除)
6. [更新应用](#更新应用)

## 环境要求

- Docker Desktop (Windows/macOS) 或 Docker Engine (Linux)
- 至少 2GB 可用内存
- 至少 5GB 可用磁盘空间
- 网络连接（用于拉取镜像）

## 安装 Docker

### Windows
1. 下载并安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. 启动 Docker Desktop
3. 验证安装：打开命令提示符，运行 `docker --version`

### macOS
1. 下载并安装 [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
2. 启动 Docker Desktop
3. 验证安装：打开终端，运行 `docker --version`

### Linux (Ubuntu)
```bash
# 安装必要的系统工具
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates curl gnupg lsb-release

# 添加 Docker 的官方 GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 设置稳定版仓库
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# 验证安装
sudo docker --version
```

## 部署步骤

### 1. 配置 Docker
为了确保更好的下载速度，建议配置国内镜像源：

1. 创建或编辑 Docker 配置文件：
```bash
mkdir -p ~/.docker
```

2. 添加以下配置到 `~/.docker/daemon.json`：
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

### 2. 准备应用文件

1. 克隆或下载应用代码到本地目录
2. 确保目录中包含以下文件：
   - `app.py`（主应用文件）
   - `requirements.txt`（依赖文件）
   - `Dockerfile`（Docker 配置文件）
   - `experiment_analysis.py`（分析模块）

### 3. 构建 Docker 镜像

在应用目录下运行以下命令：
```bash
# 构建镜像
docker build -t aa-analysis-tool .
```

构建过程说明：
- `-t aa-analysis-tool`：指定镜像名称
- `.`：使用当前目录作为构建上下文
- 构建过程可能需要几分钟，具体取决于网络状况和系统性能

### 4. 运行容器

```bash
# 运行容器
docker run -d -p 8501:8501 --name aa-analysis aa-analysis-tool
```

参数说明：
- `-d`：后台运行容器
- `-p 8501:8501`：将容器的 8501 端口映射到主机的 8501 端口
- `--name aa-analysis`：指定容器名称
- `aa-analysis-tool`：使用的镜像名称

### 5. 访问应用

#### 本地访问
- 在部署机器上访问：http://localhost:8501

#### 局域网访问
1. 查看部署机器的IP地址：
   - Windows: 
     ```bash
     # 打开命令提示符，运行：
     ipconfig
     # 查找"IPv4 地址"字段
     ```
   - macOS/Linux: 
     ```bash
     # 打开终端，运行以下命令之一：
     ifconfig | grep "inet " | grep -v 127.0.0.1
     # 或
     ip addr | grep "inet " | grep -v 127.0.0.1
     ```

2. 确认容器运行状态：
   ```bash
   # 查看容器是否正常运行
   docker ps | grep aa-analysis
   
   # 检查端口映射
   docker port aa-analysis
   # 应该看到输出：8501/tcp -> 0.0.0.0:8501
   ```

3. 配置防火墙：
   - macOS:
     ```bash
     # 在系统偏好设置 -> 安全性与隐私 -> 防火墙
     # 添加允许8501端口的入站规则
     ```
   - Windows:
     ```bash
     # 在控制面板 -> Windows Defender 防火墙 -> 高级设置
     # 添加入站规则，允许8501端口
     ```
   - Linux:
     ```bash
     # Ubuntu/Debian
     sudo ufw allow 8501/tcp
     
     # CentOS
     sudo firewall-cmd --permanent --add-port=8501/tcp
     sudo firewall-cmd --reload
     ```

4. 访问地址：
   - 格式：`http://[部署机器IP]:8501`
   - 示例：如果部署机器IP是192.168.1.100，则访问 http://192.168.1.100:8501

5. 访问验证：
   ```bash
   # 在其他设备上验证网络连接
   ping [部署机器IP]
   
   # 检查端口是否开放（需要安装telnet）
   telnet [部署机器IP] 8501
   ```

6. 故障排除：
   如果无法访问，按顺序检查：
   1. 确认容器状态：
      ```bash
      docker ps | grep aa-analysis
      ```
   
   2. 查看应用日志：
      ```bash
      docker logs aa-analysis
      ```
   
   3. 检查网络连接：
      ```bash
      # 查看网络设置
      docker network ls
      
      # 查看容器网络详情
      docker network inspect bridge
      ```
   
   4. 常见问题解决：
      - 确保部署机器和访问设备在同一局域网
      - 检查防火墙设置
      - 确认IP地址是否正确
      - 验证8501端口是否被其他应用占用：
        ```bash
        # macOS/Linux
        lsof -i :8501
        
        # Windows
        netstat -ano | findstr :8501
        ```

7. 安全建议：
   - 限制访问IP范围
   - 设置访问密码
   - 使用反向代理（如Nginx）
   - 配置HTTPS访问

#### 外网访问
如果需要从外网访问，需要进行以下配置：

1. 云服务器配置：
   1. 在云服务器控制台中：
      - 配置安全组，开放8501端口
      - 设置入站规则，允许TCP 8501端口访问
   
   2. 服务器防火墙配置：
      ```bash
      # Ubuntu/Debian
      sudo ufw allow 8501/tcp
      sudo ufw status
      
      # CentOS
      sudo firewall-cmd --permanent --add-port=8501/tcp
      sudo firewall-cmd --reload
      sudo firewall-cmd --list-ports
      ```

2. 运行容器时指定主机绑定：
   ```bash
   # 允许所有IP访问
   docker run -d -p 0.0.0.0:8501:8501 --name aa-analysis aa-analysis-tool
   
   # 或指定特定IP访问
   docker run -d -p [您的服务器IP]:8501:8501 --name aa-analysis aa-analysis-tool
   ```

3. 访问方式：
   - 格式：`http://[服务器公网IP]:8501`
   - 示例：如果服务器公网IP是203.0.113.1，则访问 http://203.0.113.1:8501

4. 安全加固建议：
   1. 配置HTTPS：
      ```bash
      # 使用Nginx作为反向代理
      server {
          listen 443 ssl;
          server_name your-domain.com;
          
          ssl_certificate /path/to/cert.pem;
          ssl_certificate_key /path/to/key.pem;
          
          location / {
              proxy_pass http://localhost:8501;
              proxy_set_header Host $host;
              proxy_set_header X-Real-IP $remote_addr;
          }
      }
      ```
   
   2. 设置访问控制：
      - 配置IP白名单
      - 添加基本认证
      - 使用VPN访问
   
   3. 监控和日志：
      ```bash
      # 查看实时访问日志
      docker logs -f aa-analysis
      
      # 查看容器资源使用情况
      docker stats aa-analysis
      ```

5. 故障排除：
   1. 检查公网IP是否可访问：
      ```bash
      # 在本地电脑上测试
      ping [服务器公网IP]
      ```
   
   2. 验证端口是否开放：
      ```bash
      # 在服务器上检查
      netstat -tulpn | grep 8501
      
      # 或使用nmap工具（需要安装）
      nmap -p 8501 [服务器公网IP]
      ```
   
   3. 检查服务器防火墙：
      ```bash
      # Ubuntu/Debian
      sudo ufw status
      
      # CentOS
      sudo firewall-cmd --list-all
      ```
   
   4. 查看错误日志：
      ```bash
      # 容器日志
      docker logs aa-analysis
      
      # 系统日志
      sudo tail -f /var/log/syslog | grep docker
      ```

6. 性能优化：
   - 配置CDN加速
   - 启用Gzip压缩
   - 优化网络设置
   - 监控资源使用

## 常用命令

```bash
# 查看运行中的容器
docker ps

# 查看所有容器（包括已停止的）
docker ps -a

# 查看容器日志
docker logs aa-analysis

# 查看实时日志
docker logs -f aa-analysis

# 停止容器
docker stop aa-analysis

# 启动容器
docker start aa-analysis

# 重启容器
docker restart aa-analysis

# 删除容器
docker rm aa-analysis

# 删除镜像
docker rmi aa-analysis-tool
```

## 管理已有容器

### 1. 查看现有容器
首先查看系统中的所有容器（包括已停止的）：
```bash
# 查看所有容器
docker ps -a

# 或者使用过滤查找特定容器
docker ps -a | grep aa-analysis
```

### 2. 启动已有容器
如果容器已经存在但已停止，可以直接启动：
```bash
# 启动容器
docker start aa-analysis

# 查看启动状态
docker ps | grep aa-analysis

# 查看启动日志
docker logs aa-analysis
```

### 3. 停止运行中的容器
```bash
# 优雅停止（推荐）
docker stop aa-analysis

# 强制停止（不推荐）
docker kill aa-analysis
```

### 4. 重启容器
```bash
# 重启容器
docker restart aa-analysis

# 查看重启后状态
docker ps | grep aa-analysis
```

### 5. 查看容器信息
```bash
# 查看容器详细信息
docker inspect aa-analysis

# 查看容器资源使用情况
docker stats aa-analysis

# 查看容器日志
docker logs aa-analysis
```

### 6. 进入容器内部
如果需要在容器内执行命令：
```bash
# 进入容器shell
docker exec -it aa-analysis /bin/bash

# 或者使用sh
docker exec -it aa-analysis /bin/sh
```

### 7. 容器管理建议
1. 定期维护：
   - 检查容器状态
   - 查看资源使用情况
   - 备份重要数据

2. 性能监控：
   ```bash
   # 查看容器资源使用
   docker stats aa-analysis
   
   # 查看容器进程
   docker top aa-analysis
   ```

3. 故障恢复：
   ```bash
   # 如果容器无法正常启动，可以尝试强制重启
   docker restart -t 0 aa-analysis
   
   # 如果仍然有问题，可以尝试重新创建容器
   docker rm -f aa-analysis
   docker run -d -p 8501:8501 --name aa-analysis aa-analysis-tool
   ```

4. 数据备份：
   ```bash
   # 从容器复制数据到主机
   docker cp aa-analysis:/app/data ./backup/
   
   # 从主机复制数据到容器
   docker cp ./backup/ aa-analysis:/app/data/
   ```

## 故障排除

### 1. 构建失败
如果遇到构建超时或网络问题：
```bash
# 使用更长的超时时间重新构建
DOCKER_CLIENT_TIMEOUT=120 COMPOSE_HTTP_TIMEOUT=120 docker build --no-cache -t aa-analysis-tool .
```

### 2. 端口冲突
如果 8501 端口被占用：
```bash
# 使用其他端口（例如 8502）
docker run -d -p 8502:8501 --name aa-analysis aa-analysis-tool
```

### 3. 容器无法启动
检查日志查找错误原因：
```bash
docker logs aa-analysis
```

### 4. 内存不足
调整容器内存限制：
```bash
docker run -d -p 8501:8501 --memory=2g --name aa-analysis aa-analysis-tool
```

### 5. 容器名称冲突
如果遇到容器名称已被使用的错误：
```bash
# 错误信息示例：
# Error response from daemon: Conflict. The container name "/aa-analysis" is already in use...
```

解决方法（三选一）：

1. 删除旧容器后重新运行：
```bash
# 停止旧容器
docker stop aa-analysis
# 删除旧容器
docker rm aa-analysis
# 重新运行新容器
docker run -d -p 8501:8501 --name aa-analysis aa-analysis-tool
```

2. 使用不同的容器名称：
```bash
# 使用新的名称运行容器
docker run -d -p 8501:8501 --name aa-analysis-new aa-analysis-tool
```

3. 如果旧容器还需要保留，可以重命名旧容器：
```bash
# 重命名旧容器
docker rename aa-analysis aa-analysis-old
# 运行新容器
docker run -d -p 8501:8501 --name aa-analysis aa-analysis-tool
```

注意事项：
- 在删除容器前，确保已备份重要数据
- 如果旧容器仍在运行，需要先停止才能删除
- 可以使用 `docker ps -a` 查看所有容器（包括已停止的）的状态

## 更新应用

### 方法一：完全重建（推荐）

当应用代码发生更新时，建议按以下步骤操作：

1. 备份数据（如果需要）：
```bash
# 如果有需要保留的数据，先备份
docker cp aa-analysis:/app/data ./backup/
```

2. 停止并删除旧容器：
```bash
# 停止旧容器
docker stop aa-analysis
# 删除旧容器
docker rm aa-analysis
```

3. 更新代码：
   - 如果是从代码仓库部署：
     ```bash
     # 拉取最新代码
     git pull origin main
     ```
   - 如果是直接修改文件：
     确保所有更新的文件（如 `app.py`, `experiment_analysis.py` 等）都已保存

4. 重新构建镜像：
```bash
# 删除旧镜像（可选）
docker rmi aa-analysis-tool
# 构建新镜像
docker build -t aa-analysis-tool .
```

5. 运行新容器：
```bash
# 运行新容器
docker run -d -p 8501:8501 --name aa-analysis aa-analysis-tool
```

6. 验证更新：
```bash
# 查看容器状态
docker ps | grep aa-analysis
# 查看应用日志
docker logs aa-analysis
```

### 方法二：热更新（仅适用于小改动）

对于小的代码修改，可以直接更新容器中的文件：

1. 将更新的文件复制到容器：
```bash
# 复制单个文件
docker cp app.py aa-analysis:/app/
# 或复制整个目录
docker cp ./ aa-analysis:/app/
```

2. 重启容器：
```bash
# 重启容器使更改生效
docker restart aa-analysis
```

3. 验证更新：
```bash
# 检查文件是否更新
docker exec aa-analysis ls -l /app/
# 查看应用日志
docker logs aa-analysis
```

### 方法三：使用卷挂载（开发模式）

在开发过程中，可以使用卷挂载实现实时更新：

1. 首次启动时使用卷挂载：
```bash
# 使用卷挂载启动容器
docker run -d -p 8501:8501 \
  -v $(pwd):/app \
  --name aa-analysis aa-analysis-tool
```

2. 直接修改本地文件，变更会自动反映到容器中

3. 如果需要重新加载应用：
```bash
# 重启容器
docker restart aa-analysis
```

### 更新注意事项

1. 数据持久化：
   - 确保重要数据已备份
   - 使用卷挂载保存数据：
     ```bash
     docker run -d -p 8501:8501 \
       -v /host/data:/app/data \
       --name aa-analysis aa-analysis-tool
     ```

2. 版本控制：
   - 建议使用版本标签：
     ```bash
     # 构建时指定版本
     docker build -t aa-analysis-tool:v1.1 .
     
     # 运行特定版本
     docker run -d -p 8501:8501 --name aa-analysis aa-analysis-tool:v1.1
     ```

3. 回滚策略：
   ```bash
   # 停止当前版本
   docker stop aa-analysis
   docker rm aa-analysis
   
   # 运行旧版本
   docker run -d -p 8501:8501 --name aa-analysis aa-analysis-tool:v1.0
   ```

4. 监控更新：
   ```bash
   # 查看容器日志
   docker logs -f aa-analysis
   
   # 检查应用状态
   docker exec aa-analysis ps aux
   ```

5. 更新失败处理：
   ```bash
   # 如果更新后应用无法正常运行
   # 1. 查看错误日志
   docker logs aa-analysis
   
   # 2. 回滚到上一个工作版本
   docker stop aa-analysis
   docker rm aa-analysis
   docker run -d -p 8501:8501 --name aa-analysis aa-analysis-tool:previous
   ```

## 注意事项

1. 数据持久化：
   - 容器重启后数据会丢失
   - 如需保存数据，建议使用卷挂载
   - 示例：`docker run -d -p 8501:8501 -v /host/data:/app/data --name aa-analysis aa-analysis-tool`

2. 安全性：
   - 确保防火墙配置正确
   - 建议使用 HTTPS 进行外网访问
   - 定期更新 Docker 和依赖包

3. 性能优化：
   - 定期清理未使用的镜像和容器
   - 监控容器资源使用情况
   - 根据需要调整容器资源限制 