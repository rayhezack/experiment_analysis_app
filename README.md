# AA回溯分析工具

一个用于AA实验分析和随机分组的Python工具。

## Application简介

AA回溯分析工具是一个基于Python的Web应用，专门用于实验分组和统计分析。

### 工作流程

1. 数据准备与上传
   ```mermaid
   flowchart TD
       A[准备数据文件] --> B{文件格式检查}
       B -->|CSV/Excel| C[上传文件]
       B -->|其他格式| D[格式转换]
       D --> C
       C --> E[数据预处理]
       E --> F[识别实验单元ID]
       F --> G{预分组检查}
       G -->|有预分组| H[使用已有分组]
       G -->|无预分组| I[进入分组配置]
   ```

2. 分组配置与执行
   ```mermaid
   flowchart TD
       A[分组配置] --> B[设置对照组比例]
       B --> C[配置处理组数量]
       C --> D[设置处理组比例]
       D --> E{总比例验证}
       E -->|=100%| F[执行分组]
       E -->|≠100%| G[调整比例]
       G --> E
       F --> H[生成分组结果]
       H --> I[可视化展示]
   ```

3. 指标分析与结果输出
   ```mermaid
   flowchart TD
       A[选择分析指标] --> B[指定指标类型]
       B --> C[执行统计分析]
       C --> D[计算显著性]
       D --> E[生成分析报告]
       E --> F[可视化结果]
       F --> G[导出Excel报告]
   ```

### 应用流程说明

#### 1. 数据准备与上传阶段
- **数据格式要求**
  - 支持CSV和Excel格式
  - 需包含唯一标识符列
  - 数值型指标列清晰标注

- **数据预处理**
  - 自动检测文件编码
  - 清理异常值和缺失值
  - 标准化列名格式

- **预分组处理**
  - 自动识别分组列
  - 验证分组完整性
  - 分组信息提取

#### 2. 分组配置与执行阶段
- **分组设置**
  - 对照组比例配置
  - 处理组数量选择（1-5个）
  - 各组比例分配

- **分组执行**
  - 随机分组算法
  - 比例平衡控制
  - 结果一致性检验

- **可视化反馈**
  - 分组分布展示
  - 样本量对比
  - 比例偏差分析

#### 3. 指标分析与结果输出阶段
- **指标配置**
  - 选择分析指标
  - 设置指标类型
  - 配置分析参数

- **统计分析**
  - 执行显著性检验
  - 计算效应量
  - 生成置信区间

- **结果展示**
  - 可视化图表展示
  - 统计结果汇总
  - 导出分析报告

### 核心功能
1. 实验分组
   - 支持多组实验设计
   - 随机分组算法
   - 预分组数据处理
   
2. 统计分析
   - 多种指标类型支持（均值、比例、比值）
   - 灵活的检验方向选择（双边/单边）
   - 自动显著性检验
   - 可视化结果展示
   - 智能化的结果解释

3. 数据管理
   - 多格式数据支持
   - 批量数据处理
   - 结果导出功能

### 应用架构
```
aa-analysis/
├── app.py                 # 主应用入口
├── experiment_analysis.py # 核心分析模块
├── requirements.txt       # 依赖管理
├── Dockerfile            # 容器配置
├── deployment_guide.md   # 部署指南
```

## Docker部署工作流程

### 1. 环境准备
```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 验证安装
docker --version
```

### 2. 应用构建
```bash
# 克隆代码仓库
git clone <repository_url>
cd aa-analysis

# 构建Docker镜像
docker build -t aa-analysis-tool .
```

### 3. 部署流程
```bash
# 检查已有容器
docker ps -a | grep aa-analysis

# 停止并删除已有容器（如果存在）
docker stop aa-analysis
docker rm aa-analysis

# 运行新容器
docker run -d -p 8501:8501 --name aa-analysis aa-analysis-tool
```

### 4. 验证部署
```bash
# 检查容器状态
docker ps | grep aa-analysis

# 查看应用日志
docker logs aa-analysis

# 检查端口映射
docker port aa-analysis
```

### 5. 访问应用
- 本地访问：http://localhost:8501
- 局域网访问：http://[服务器IP]:8501

### 6. 维护操作
```bash
# 更新应用
git pull origin main
docker build -t aa-analysis-tool .
docker stop aa-analysis
docker rm aa-analysis
docker run -d -p 8501:8501 --name aa-analysis aa-analysis-tool

# 查看资源使用
docker stats aa-analysis

# 容器管理
docker restart aa-analysis  # 重启容器
docker exec -it aa-analysis /bin/bash  # 进入容器
```

### 7. 故障排除
```bash
# 查看详细日志
docker logs -f aa-analysis

# 检查容器配置
docker inspect aa-analysis

# 验证网络连接
telnet localhost 8501
```

## 本地安装

1. 创建虚拟环境:
```bash
python -m venv venv
```

2. 激活虚拟环境:
- macOS/Linux:
```bash
source venv/bin/activate
```
- Windows:
```bash
.\venv\Scripts\activate
```

3. 安装依赖:
```bash
pip install -r requirements.txt
```

4. 运行应用:
```bash
streamlit run app.py
```

## Docker部署

我们提供了详细的Docker部署指南，包括：
- 环境要求
- 安装步骤
- 故障排除
- 性能优化建议

详细信息请参考 [Docker部署指南](deployment_guide.md)

## 使用示例

```python
from experiment_analysis import ExperimentAnalysis
import pandas as pd

# 初始化分析器
analyzer = ExperimentAnalysis()

# 随机分组示例
bucket = analyzer.apollo_bucket("experiment_1", "user_123")
group = analyzer.assign_groups(bucket, {
    "control": "50%",
    "treatment_1": "50%"
})

# 统计分析示例
df = pd.DataFrame({
    'group_column': ['treatment', 'control', 'treatment', 'control'],
    'metric1': [10, 8, 11, 9],
    'metric2': [1, 0, 1, 0],
    'revenue': [100, 80, 120, 90],
    'impressions': [1000, 900, 1100, 950]
})

# 双边检验示例
results_two_sided = analyzer.run_statistical_tests(
    data=df,
    metrics=["metric1", "metric2", "revenue/impressions"],
    metric_types=["mean", "proportion", "ratio"],
    groupname="group_column",
    treated_label="treatment",
    control_label="control",
    is_two_sided=True,
    alternative="two-sided"
)

# 单边检验（上升）示例
results_one_sided = analyzer.run_statistical_tests(
    data=df,
    metrics=["metric1", "metric2", "revenue/impressions"],
    metric_types=["mean", "proportion", "ratio"],
    groupname="group_column",
    treated_label="treatment",
    control_label="control",
    is_two_sided=False,
    alternative="greater"
)

print(results_two_sided)
print(results_one_sided)
```

## 注意事项

1. 数据要求:
   - CSV或Excel格式
   - 必须包含唯一标识符列
   - 数值型指标列
   - 支持最大1000MB的文件上传（可通过配置调整）

2. 大文件处理建议:
   - 文件优化：
     * 上传前压缩文件
     * 移除不必要的列
     * 确保数据类型合理（如避免存储冗长的字符串）
   
   - 分批处理：
     * 建议将大文件分批处理
     * 每批建议不超过500MB
     * 使用数据透视表预处理大量数据
   
   - 性能优化：
     * 使用局域网环境上传大文件
     * 保持稳定的网络连接
     * 上传期间避免刷新页面

   - 替代方案：
     * 对于超大文件（>1GB），建议使用数据库导入
     * 考虑使用批处理脚本
     * 可使用数据预处理工具减小文件体积

3. 分组配置:
   - 支持1-5个处理组
   - 总比例必须等于100%

4. 指标分析:
   - 支持均值、比例、比值三种类型
   - 自动计算统计显著性
   - 生成可下载的分析报告

## 最近更新

1. 统计检验增强
   - 新增统计检验方向选择功能：
     * 双边检验 (Two-sided)：检验实验组与对照组是否有显著差异
     * 单边检验-上升 (One-sided, Greater)：检验实验组是否显著高于对照组
     * 单边检验-下降 (One-sided, Less)：检验实验组是否显著低于对照组
   - 根据检验方向自动调整：
     * P值计算方法
     * 置信区间的计算
     * 结果的解释说明

2. 界面优化
   - 优化了实验组分配的可视化展示
   - 将样本数量和比例分布图分开展示，提高可读性
   - 更新了应用标题为"一个全面的在线实验分析工具"

3. 功能增强
   - 新增预分组数据检测和处理功能
   - 支持自动识别和使用已有的分组信息
   - 优化了分析结果的展示方式
   - 增强了容器管理功能，提供更完善的部署指南

4. 数据处理优化
   - 支持CSV和Excel格式数据上传
   - 自动检测和处理预分组数据
   - 智能识别实验单元ID
   - 将导出格式从CSV更改为Excel，解决中文乱码问题
   - 优化了导出文件的格式和可读性

## 功能特性

1. 数据处理
   - 支持CSV和Excel格式数据上传
   - 自动检测和处理预分组数据
   - 智能识别实验单元ID
   - Excel格式导出，支持中文

2. 分组配置
   - 支持1-5个处理组
   - 灵活的比例配置
   - 可视化的分组分布展示
   - 预分组数据自动识别

3. 统计分析
   - 支持多种指标类型（均值/比例/比值）
   - 灵活的检验方向选择
     * 双边检验：适用于探索性分析
     * 单边检验-上升：适用于期望指标提升的场景
     * 单边检验-下降：适用于期望指标下降的场景
   - 智能化的结果解释
   - 自动化的显著性判断

4. 可视化展示
   - 分组分布的双图表展示
   - 样本数量和比例分布独立展示
   - 交互式数据可视化
   - 优化的图表布局

5. 部署与维护
   - 完整的Docker部署方案
   - 详细的容器管理指南
   - 本地和局域网访问支持
   - 性能监控和优化建议

## 技术栈

- Python 3.9+
- Streamlit
- Pandas
- NumPy
- SciPy
- Plotly
- Docker
- OpenPyXL (Excel支持) 
