import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from experiment_analysis import ExperimentAnalysis
import seaborn as sns
import io
import base64

# Set page configuration
st.set_page_config(
    page_title="AA回溯分析工具",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🔬"
)

# Custom CSS for styling
st.markdown("""
    <style>
    /* Main font and colors */
    .main {
        font-family: Arial, sans-serif;
        color: #2C3E50;
    }
    
    /* Headers styling */
    h1 {
        color: #1E88E5;
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 2rem;
    }
    h2 {
        color: #2196F3;
        font-size: 1.8rem;
        font-weight: 500;
        margin-top: 1.5rem;
    }
    h3 {
        color: #42A5F5;
        font-size: 1.3rem;
        font-weight: 500;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        width: 100%;
        margin: 0.5rem 0;
    }
    .stButton>button:hover {
        background-color: #1976D2;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transform: translateY(-1px);
    }
    
    /* Action button styling */
    .action-button {
        background-color: #4CAF50 !important;
    }
    .action-button:hover {
        background-color: #388E3C !important;
    }
    
    /* Input fields styling */
    .stTextInput>div>div>input {
        font-family: Arial, sans-serif;
        border-radius: 6px;
        border: 1px solid #E0E0E0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        padding: 2rem 1rem;
    }
    
    /* DataFrame styling */
    .dataframe {
        border: 1px solid #E0E0E0;
        border-radius: 6px;
        padding: 1rem;
        width: 100%;
    }
    
    /* Success/Warning/Error messages */
    .stSuccess {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
    .stWarning {
        background-color: #FFF3E0;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #FF9800;
        margin: 1rem 0;
    }
    .stError {
        background-color: #FFEBEE;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #F44336;
        margin: 1rem 0;
    }
    
    /* Card-like containers */
    div.stDataFrame, div.stPlotlyChart {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        margin: 1rem 0;
    }
    
    /* Progress indicators */
    .stProgress {
        margin: 1rem 0;
    }
    .stProgress > div > div > div {
        background-color: #1E88E5;
        height: 8px;
        border-radius: 4px;
    }
    
    /* Section connectors */
    .section-connector {
        width: 2px;
        height: 30px;
        background-color: #E0E0E0;
        margin: 0 auto;
    }
    
    /* Step indicators */
    .step-complete {
        color: #4CAF50;
        font-weight: bold;
    }
    .step-current {
        color: #1E88E5;
        font-weight: bold;
    }
    .step-pending {
        color: #9E9E9E;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-size: 1.2rem;
        font-weight: 500;
        background-color: #F5F5F5;
        border-radius: 6px;
    }
    
    /* Step indicator badges */
    .step-badge {
        display: inline-block;
        width: 24px;
        height: 24px;
        line-height: 24px;
        text-align: center;
        border-radius: 50%;
        margin-right: 8px;
        font-weight: bold;
        font-size: 14px;
    }
    .step-badge-current {
        background-color: #1E88E5;
        color: white;
    }
    .step-badge-complete {
        background-color: #4CAF50;
        color: white;
    }
    .step-badge-pending {
        background-color: #E0E0E0;
        color: #9E9E9E;
    }
    
    /* Help tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    .tooltip:hover::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        padding: 8px;
        background-color: #333;
        color: white;
        border-radius: 4px;
        font-size: 12px;
        white-space: nowrap;
        z-index: 1000;
    }
    
    /* Section status indicator */
    .section-status {
        float: right;
        font-size: 0.9rem;
        padding: 4px 8px;
        border-radius: 4px;
        margin-left: 8px;
    }
    .status-complete {
        background-color: #E8F5E9;
        color: #4CAF50;
    }
    .status-current {
        background-color: #E3F2FD;
        color: #1E88E5;
    }
    .status-pending {
        background-color: #F5F5F5;
        color: #9E9E9E;
    }
    
    /* Step title styling */
    .step-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1E88E5;
        margin: 1rem 0;
        padding: 0.5rem;
        border-radius: 8px;
        background: #E3F2FD;
    }
    
    .step-title.active {
        background: #1E88E5;
        color: white;
    }
    
    .step-title.completed {
        background: #E8F5E9;
        color: #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'groups_configured' not in st.session_state:
    st.session_state.groups_configured = False
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = ExperimentAnalysis()
if 'proportions' not in st.session_state:
    st.session_state.proportions = None
if 'show_group_config' not in st.session_state:
    st.session_state.show_group_config = False
if 'show_metric_analysis' not in st.session_state:
    st.session_state.show_metric_analysis = False
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'metrics' not in st.session_state:
    st.session_state.metrics = None
if 'metric_types' not in st.session_state:
    st.session_state.metric_types = None
if 'results' not in st.session_state:
    st.session_state.results = None
if 'unit_id_col' not in st.session_state:
    st.session_state.unit_id_col = None
if 'has_preexisting_groups' not in st.session_state:
    st.session_state.has_preexisting_groups = False
if 'group_column' not in st.session_state:
    st.session_state.group_column = None

def reset_analysis():
    """Reset all session state variables to restart analysis"""
    # Clear all session state variables completely
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Force reinitialization of all variables to their default states
    st.session_state.data = None
    st.session_state.groups_configured = False
    st.session_state.analyzer = ExperimentAnalysis()
    st.session_state.proportions = None
    st.session_state.show_group_config = False
    st.session_state.show_metric_analysis = False
    st.session_state.show_results = False
    st.session_state.uploaded_file = None
    st.session_state.metrics = None
    st.session_state.metric_types = None
    st.session_state.results = None
    st.session_state.unit_id_col = None
    st.session_state.has_preexisting_groups = False
    st.session_state.group_column = None
    
    # Clear any widget states
    if 'seed_input' in st.session_state:
        del st.session_state.seed_input
    if 'groups_input' in st.session_state:
        del st.session_state.groups_input
    
    # Force the UI to show only the data upload section
    st.session_state.show_group_config = False
    st.session_state.show_metric_analysis = False
    st.session_state.show_results = False

def get_download_link(df, filename, text):
    """Generate a download link for a DataFrame"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">{text}</a>'
    return href

def plot_group_distribution(data, group_column):
    """Create a bar plot for group distribution"""
    group_counts = data[group_column].value_counts()
    fig = px.bar(
        x=group_counts.index,
        y=group_counts.values,
        title="Group Distribution",
        labels={'x': 'Group', 'y': 'Count'},
        color=group_counts.index
    )
    return fig

def plot_metric_boxplot(data, metric, group_column):
    """Create a box plot for metric distribution by group"""
    fig = px.box(
        data,
        x=group_column,
        y=metric,
        title=f"{metric} Distribution by Group",
        color=group_column
    )
    return fig

# Calculate progress
progress = 0
if st.session_state.data is not None:
    progress += 25
if st.session_state.groups_configured:
    progress += 25
if st.session_state.show_metric_analysis:
    progress += 25
if st.session_state.show_results:
    progress += 25

# Page title and reset button
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 0;">
    <div>
        <h1 style="margin: 0;">🔬 AA回溯分析工具</h1>
        <p style="font-size: 1.2rem; color: #666; margin: 0;">一个全面的在线实验分析工具</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Show progress bar
st.progress(progress/100)
st.markdown(f"<p style='text-align: center; color: #666;'>分析进度: {progress}%</p>", unsafe_allow_html=True)

# Sidebar with information
with st.sidebar:
    st.image("https://raw.githubusercontent.com/streamlit/streamlit/develop/examples/streamlit_app_logo.png", width=200)
    st.markdown("---")
    
    # Add statistical test direction selection
    st.markdown("### 📊 统计检验设置")
    test_direction = st.radio(
        "选择检验方向",
        options=[
            "双边检验 (Two-sided)",
            "单边检验-上升 (One-sided, Greater)",
            "单边检验-下降 (One-sided, Less)"
        ],
        help="""
        - 双边检验：检验实验组与对照组是否有显著差异（上升或下降）
        - 单边检验-上升：检验实验组是否显著高于对照组
        - 单边检验-下降：检验实验组是否显著低于对照组
        """
    )
    
    # Convert selection to parameters for statistical test
    is_two_sided = test_direction == "双边检验 (Two-sided)"
    alternative = "two-sided"
    if not is_two_sided:
        alternative = "greater" if "上升" in test_direction else "less"
    
    st.markdown("---")
    
    # Add experiment information section
    st.markdown("### 📊 实验信息")
    if st.session_state.data is not None:
        st.info(f"""
        - 数据集大小: {st.session_state.data.shape[0]} 行
        - 实验单元: {st.session_state.unit_id_col}
        - 指标数量: {len(st.session_state.data.select_dtypes(include=[np.number]).columns)}
        """)
    else:
        st.info("请上传数据集开始分析")
    
    st.markdown("---")
    
    # Add progress tracking
    st.markdown("### 🎯 分析进度")
    progress_status = []
    if st.session_state.data is not None:
        progress_status.append("✅ 数据上传完成")
    if st.session_state.groups_configured:
        progress_status.append("✅ 分组配置完成")
    if st.session_state.show_metric_analysis:
        progress_status.append("✅ 指标分析完成")
    
    if progress_status:
        for status in progress_status:
            st.write(status)
    else:
        st.write("⏳ 等待开始分析...")
    
    st.markdown("---")
    
    # Add help information
    st.markdown("### ℹ️ 帮助信息")
    with st.expander("使用说明"):
        st.markdown("""
        1. **数据上传**
           - 支持CSV和Excel格式
           - 需要包含唯一标识列
        
        2. **分组配置**
           - 设置对照组比例
           - 配置实验组数量
        
        3. **指标分析**
           - 支持均值、比例、比率分析
           - 自动计算统计显著性
        """)
    
    with st.expander("关于"):
        st.markdown("""
        实验分析工具 v1.0
        
        - 支持多种统计检验方法
        - 自动生成分析报告
        - 数据可视化展示
        """)

# Main content area
st.markdown("---")

# Helper function for step badges
def get_step_badge(step_number, status):
    return f"""
    <span class="step-badge step-badge-{status}">{step_number}</span>
    """

# Helper function for section status
def get_section_status(status, text):
    return f"""
    <span class="section-status status-{status}">{text}</span>
    """

# Section 1: Data Upload
with st.expander("第一步：数据上传", expanded=not st.session_state.show_group_config):
    status = "completed" if st.session_state.data is not None else "active"
    st.markdown(f"""
    <div class='step-title {status}'>
    📤 第一步：数据上传
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("上传数据集（支持CSV或Excel格式）", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            # Read the file
            if uploaded_file.name.endswith('.csv'):
                data = pd.read_csv(uploaded_file)
            else:
                data = pd.read_excel(uploaded_file)
            
            unit_id_col = st.selectbox(
                "选择包含实验单元ID的列：",
                options=data.columns.tolist(),
                help="选择包含实验单元唯一标识符的列"
            )

            # 检查是否存在预分组
            potential_group_columns = []
            
            # 1. 检查列名中包含'group'的列
            columns_with_group_name = [col for col in data.columns if 'group' in col.lower()]
            potential_group_columns.extend(columns_with_group_name)
            
            # 2. 检查字符串类型列的内容是否包含'group'
            string_columns = data.select_dtypes(include=['object']).columns
            for col in string_columns:
                if col not in potential_group_columns:  # 避免重复检查
                    # 检查前100行数据
                    sample_values = data[col].head(100).astype(str).str.lower()
                    if any(sample_values.str.contains('group')):
                        potential_group_columns.append(col)
            
            # 去重
            potential_group_columns = list(set(potential_group_columns))
            
            if potential_group_columns:
                st.info(f"检测到以下可能的分组列：\n" + 
                       "\n".join([f"- {col}" for col in potential_group_columns]) +
                       "\n您可以选择使用已有的分组或重新分组。")
                
                use_existing_groups = st.checkbox("使用已有分组", value=True)
                
                if use_existing_groups:
                    # 显示每个潜在分组列的唯一值示例
                    st.write("各分组列的唯一值示例：")
                    for col in potential_group_columns:
                        unique_values = data[col].unique()
                        st.write(f"**{col}**: {', '.join(map(str, unique_values[:5]))}" + 
                               ("..." if len(unique_values) > 5 else ""))
                    
                    group_column = st.selectbox(
                        "选择分组列：",
                        options=potential_group_columns,
                        help="选择包含实验组信息的列"
                    )
                    st.session_state.has_preexisting_groups = True
                    st.session_state.group_column = group_column
            else:
                st.session_state.has_preexisting_groups = False
                st.session_state.group_column = None
            
            if st.button("处理数据集"):
                try:
                    # Process unit IDs
                    data[unit_id_col] = data[unit_id_col].apply(
                        lambda x: '{:.0f}'.format(float(x)) if pd.notnull(x) else '')
                    
                    if unit_id_col != 'apollo_key':
                        data['apollo_key'] = data[unit_id_col]
                    
                    # 如果使用预分组，重命名分组列并跳过分组配置
                    if st.session_state.has_preexisting_groups:
                        data['group_name'] = data[st.session_state.group_column]
                        st.session_state.groups_configured = True
                        st.session_state.show_metric_analysis = True
                        
                        # 显示现有分组的分布情况
                        group_counts = data['group_name'].value_counts()
                        total_samples = len(data)
                        actual_proportions = (group_counts / total_samples * 100).round(2)
                        
                        st.success("✅ 使用已有分组进行分析！")
                        st.write("现有分组分布：")
                        
                        # 创建比较DataFrame
                        distribution_df = pd.DataFrame({
                            '样本数': group_counts,
                            '比例(%)': actual_proportions
                        }).round(2)
                        st.dataframe(distribution_df)
                        
                        # 显示分组分布图表
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("样本数量分布")
                            fig_counts = px.bar(
                                distribution_df,
                                y='样本数',
                                title='各组样本数量',
                                color=distribution_df.index,
                                text='样本数'
                            )
                            fig_counts.update_traces(textposition='outside')
                            fig_counts.update_layout(
                                showlegend=False,
                                height=400,
                                yaxis_title="样本数量",
                                xaxis_title="实验组"
                            )
                            st.plotly_chart(fig_counts, use_container_width=True)
                        
                        with col2:
                            st.subheader("分组比例分布")
                            fig_props = px.bar(
                                distribution_df,
                                y='比例(%)',
                                title='各组比例分布',
                                color=distribution_df.index,
                                text='比例(%)'
                            )
                            fig_props.update_traces(textposition='outside')
                            fig_props.update_layout(
                                showlegend=False,
                                height=400,
                                yaxis_title="比例 (%)",
                                xaxis_title="实验组",
                                yaxis=dict(range=[0, 100])
                            )
                            st.plotly_chart(fig_props, use_container_width=True)
                    else:
                        st.session_state.show_group_config = True
                    
                    st.session_state.data = data
                    st.session_state.unit_id_col = unit_id_col
                    
                    # Show complete processed dataframe
                    st.subheader("📋 处理后的数据集")
                    st.dataframe(data)
                    
                    # Show detailed information in tabs
                    st.subheader("📊 数据集详情")
                    summary_tab, stats_tab = st.tabs(["数据概览", "统计信息"])
                    
                    with summary_tab:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("数据集信息：")
                            st.write(f"- 行数：{data.shape[0]}")
                            st.write(f"- 列数：{data.shape[1]}")
                            st.write("实验单元ID示例：", data['apollo_key'].head().tolist())
                        
                        with col2:
                            st.write("数据类型：")
                            st.write(data.dtypes)
                    
                    with stats_tab:
                        numeric_cols = data.select_dtypes(include=[np.number]).columns
                        if not numeric_cols.empty:
                            st.write("数值列统计信息：")
                            st.dataframe(data[numeric_cols].describe())
                    
                except Exception as e:
                    st.error(f"处理实验单元ID时出错：{str(e)}")
                    st.error("如果遇到问题，请点击右上角的'🔄 重新开始'按钮重置应用。")
            
        except Exception as e:
            st.error(f"读取文件时出错：{str(e)}")
            st.error("如果遇到问题，请点击右上角的'🔄 重新开始'按钮重置应用。")

# Visual connector
if st.session_state.show_group_config:
    st.markdown("<div class='section-connector'></div>", unsafe_allow_html=True)

# Section 2: Group Configuration
if st.session_state.show_group_config:
    with st.expander("第二步：分组配置", expanded=True):
        status = "completed" if st.session_state.groups_configured else "active"
        st.markdown(f"""
        <div class='step-title {status}'>
        ⚙️ 第二步：分组配置
        </div>
        """, unsafe_allow_html=True)
        
        # Add tooltips to inputs
        st.markdown("""
        <div class="tooltip" data-tooltip="为您的实验设置一个唯一标识符">
        随机种子
        </div>
        """, unsafe_allow_html=True)
        random_seed = st.text_input("", value="experiment_1", key="seed_input")
        
        st.markdown("""
        <div class="tooltip" data-tooltip="设置需要测试的不同处理组数量">
        处理组数量
        </div>
        """, unsafe_allow_html=True)
        n_groups = st.number_input("", min_value=1, max_value=5, value=1, key="groups_input")
        
        # Group proportion inputs
        proportions = {}
        col1, col2 = st.columns(2)
        
        with col1:
            control_prop = st.slider("对照组占比 %", 1, 100, 50)
            proportions["control_group"] = control_prop
        
        remaining_prop = 100 - control_prop
        
        with col2:
            if n_groups == 1:
                proportions["treatment_group_1"] = remaining_prop
                st.write(f"处理组占比：{remaining_prop}%")
            else:
                default_treatment_prop = remaining_prop // n_groups
                remaining_for_treatments = remaining_prop
                for i in range(n_groups):
                    if i < n_groups - 1:
                        prop = st.slider(f"处理组 {i+1} 占比 %", 1, remaining_for_treatments, default_treatment_prop)
                        proportions[f"treatment_group_{i+1}"] = prop
                        remaining_for_treatments -= prop
                    else:
                        proportions[f"treatment_group_{i+1}"] = remaining_for_treatments
                        st.write(f"处理组 {i+1} 占比：{remaining_for_treatments}%")
        
        # 验证总比例是否为100%
        total_proportion = sum(proportions.values())
        if total_proportion != 100:
            st.error(f"所有组的总占比必须等于100%，当前总占比为{total_proportion}%")
        else:
            if st.button("生成分组"):
                try:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("初始化分组编号...")
                    st.session_state.data['bucket_number'] = st.session_state.data['apollo_key'].apply(
                        lambda x: st.session_state.analyzer.apollo_bucket(random_seed, x))
                    progress_bar.progress(25)
                    
                    status_text.text("分配实验组...")
                    proportions_with_percent = {k: f"{v}%" for k, v in proportions.items()}
                    st.session_state.data['group_name'] = st.session_state.data['bucket_number'].apply(
                        lambda x: st.session_state.analyzer.assign_groups(x, proportions_with_percent))
                    progress_bar.progress(50)
                    
                    status_text.text("验证分组结果...")
                    group_counts = st.session_state.data['group_name'].value_counts()
                    total_samples = len(st.session_state.data)
                    
                    # 计算实际比例
                    actual_proportions = (group_counts / total_samples * 100).round(2)
                    
                    # 创建比较DataFrame
                    comparison_df = pd.DataFrame({
                        '目标比例': proportions,
                        '实际比例': actual_proportions,
                        '样本数': group_counts
                    }).round(2)
                    
                    progress_bar.progress(75)
                    
                    status_text.text("完成分组配置...")
                    st.session_state.groups_configured = True
                    st.session_state.proportions = proportions_with_percent
                    progress_bar.progress(100)
                    status_text.text("分组生成完成！")
                    
                    st.success("✅ 分组生成成功！")
                    
                    # 显示分组分布比较
                    st.write("分组分布比较：")
                    st.dataframe(comparison_df)
                    
                    # 创建两个列来放置图表
                    col1, col2 = st.columns(2)
                    
                    # 样本数量柱状图
                    with col1:
                        st.subheader("样本数量分布")
                        fig_counts = px.bar(
                            comparison_df,
                            y='样本数',
                            title='各组样本数量',
                            labels={'index': '组别', 'value': '样本数'},
                            color=comparison_df.index,
                            text='样本数'  # 显示具体数值
                        )
                        fig_counts.update_traces(textposition='outside')  # 将数值显示在柱子上方
                        fig_counts.update_layout(
                            showlegend=False,
                            height=400,
                            yaxis_title="样本数量",
                            xaxis_title="实验组"
                        )
                        st.plotly_chart(fig_counts, use_container_width=True)
                    
                    # 比例对比柱状图
                    with col2:
                        st.subheader("分组比例对比")
                        fig_props = go.Figure()
                        
                        # 添加目标比例柱状图
                        fig_props.add_trace(go.Bar(
                            name='目标比例',
                            x=comparison_df.index,
                            y=comparison_df['目标比例'],
                            text=comparison_df['目标比例'].apply(lambda x: f'{x:.1f}%'),
                            textposition='outside'
                        ))
                        
                        # 添加实际比例柱状图
                        fig_props.add_trace(go.Bar(
                            name='实际比例',
                            x=comparison_df.index,
                            y=comparison_df['实际比例'],
                            text=comparison_df['实际比例'].apply(lambda x: f'{x:.1f}%'),
                            textposition='outside'
                        ))
                        
                        # 更新布局
                        fig_props.update_layout(
                            title='目标比例 vs 实际比例',
                            height=400,
                            yaxis_title="比例 (%)",
                            xaxis_title="实验组",
                            barmode='group',
                            yaxis=dict(range=[0, 100])  # 固定y轴范围为0-100%
                        )
                        st.plotly_chart(fig_props, use_container_width=True)
                    
                    st.markdown("### 📥 下载处理后的数据集")
                    st.markdown("下载包含分组信息的数据集：")
                    st.markdown(get_download_link(
                        st.session_state.data,
                        "processed_dataset_with_groups.xlsx",
                        "📥 下载分组后的数据集"
                    ), unsafe_allow_html=True)
                    
                    st.session_state.show_metric_analysis = True
                    
                except Exception as e:
                    st.error(f"分组配置出错：{str(e)}")

# Visual connector
if st.session_state.show_metric_analysis:
    st.markdown("<div class='section-connector'></div>", unsafe_allow_html=True)

# Section 3: Metric Analysis
if st.session_state.show_metric_analysis:
    with st.expander("第三步：指标分析", expanded=st.session_state.show_metric_analysis and not st.session_state.show_results):
        status = "completed" if st.session_state.show_results else "active"
        st.markdown(f"""
        <div class='step-title {status}'>
        📊 第三步：指标分析
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin-bottom: 1rem;">
        <b>指标类型说明：</b>
        <ul>
        <li><b>均值</b>：比较平均值（如：收入、使用时长）</li>
        <li><b>比例</b>：比较比率或百分比（如：转化率）</li>
        <li><b>比值</b>：比较两个指标的比值（如：人均收入）</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        numeric_cols = st.session_state.data.select_dtypes(include=[np.number]).columns.tolist()
        if 'bucket_number' in numeric_cols:
            numeric_cols.remove('bucket_number')
        
        metrics = st.multiselect("选择需要分析的指标：", numeric_cols)
        
        if metrics:
            metric_types = []
            cols = st.columns(len(metrics))
            for i, metric in enumerate(metrics):
                with cols[i]:
                    metric_type = st.selectbox(
                        f"{metric} 的指标类型",
                        ["均值", "比例", "比值"],
                        key=f"metric_type_{i}"
                    )
                    metric_types.append(metric_type.replace("均值", "mean").replace("比例", "proportion").replace("比值", "ratio"))
            
            if st.button("运行分析"):
                try:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("准备数据分析...")
                    
                    # 处理预分组数据的情况
                    if st.session_state.has_preexisting_groups:
                        # 获取所有非对照组的组名
                        all_groups = st.session_state.data['group_name'].unique()
                        control_group = [g for g in all_groups if 'control' in g.lower()]
                        if not control_group:  # 如果没有找到包含'control'的组名，使用第一个组作为对照组
                            control_group = [all_groups[0]]
                        treatment_groups = [g for g in all_groups if g not in control_group]
                        control_label = control_group[0]
                        treated_labels = treatment_groups
                    else:
                        # 使用原有的分组逻辑
                        n_treatment_groups = len(st.session_state.proportions) - 1
                        control_label = "control_group"
                        treated_labels = [f"treatment_group_{i+1}" for i in range(n_treatment_groups)]
                    
                    progress_bar.progress(25)
                    
                    status_text.text("执行统计检验...")
                    results = st.session_state.analyzer.run_statistical_tests(
                        data=st.session_state.data,
                        metrics=metrics,
                        metric_types=metric_types,
                        groupname="group_name",
                        treated_labels=treated_labels,
                        control_label=control_label,
                        is_two_sided=is_two_sided,
                        alternative=alternative
                    )
                    progress_bar.progress(75)
                    
                    status_text.text("生成分析结果...")
                    st.session_state.results = results
                    progress_bar.progress(100)
                    status_text.text("分析完成！")
                    
                    st.success("✅ 分析完成！")
                    
                    st.write("分析结果：")
                    st.dataframe(results)
                    
                    st.markdown("### 📥 下载分析结果")
                    st.markdown(get_download_link(
                        results,
                        "experiment_results.xlsx",
                        "📥 下载分析结果报告"
                    ), unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"分析过程出错：{str(e)}")
                    st.error("错误详细信息：")
                    st.write("现有分组：", st.session_state.data['group_name'].unique())
                    st.write("指标：", metrics)
                    st.write("指标类型：", metric_types)

# Remove the entire Section 4: Results Summary section and its related code
if st.session_state.show_results:
    st.markdown("<div class='section-connector'></div>", unsafe_allow_html=True) 