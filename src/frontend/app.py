"""智能测试探索架构 - 前端应用"""
import streamlit as st
import asyncio
import json
import pandas as pd
from io import BytesIO

# 导入项目模块
from src.shared.database import get_db_session
from src.services.api_parser.openapi_parser import OpenAPIParser
from src.services.api_parser.api_importer import ApiImporter
from src.services.ai_review.review_service import AIReviewService
from src.services.test_point.generator import TestPointGenerator
from src.services.test_case.generator import TestCaseGenerator
from src.services.test_script.generator import TestScriptGenerator
from src.services.test_execution.executor import TestExecutor
from src.services.test_execution.report_generator import TestReportGenerator

# 设置页面配置
st.set_page_config(
    page_title="智能测试探索",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 页面标题
st.title("🔍 智能测试探索")

# 工作流程状态
workflow_steps = [
    {"id": 1, "name": "API管理", "status": "pending"},
    {"id": 2, "name": "AI评审-API", "status": "pending"},
    {"id": 3, "name": "测试点生成", "status": "pending"},
    {"id": 4, "name": "AI评审-测试点", "status": "pending"},
    {"id": 5, "name": "人工评审-测试点", "status": "pending"},
    {"id": 6, "name": "测试用例生成", "status": "pending"},
    {"id": 7, "name": "AI评审-测试用例", "status": "pending"},
    {"id": 8, "name": "人工评审-测试用例", "status": "pending"},
    {"id": 9, "name": "测试脚本生成", "status": "pending"},
    {"id": 10, "name": "AI评审-测试脚本", "status": "pending"},
    {"id": 11, "name": "人工评审-测试脚本", "status": "pending"},
    {"id": 12, "name": "测试执行", "status": "pending"},
    {"id": 13, "name": "测试报告", "status": "pending"}
]

# 会话状态
if "workflow" not in st.session_state:
    st.session_state.workflow = workflow_steps

if "api_project_id" not in st.session_state:
    st.session_state.api_project_id = None

if "test_points" not in st.session_state:
    st.session_state.test_points = []

if "test_cases" not in st.session_state:
    st.session_state.test_cases = []

if "test_scripts" not in st.session_state:
    st.session_state.test_scripts = []

# 侧边栏菜单
menu = st.sidebar.selectbox(
    "选择功能",
    ["工作流程", "API导入", "测试点管理", "测试用例管理", "测试脚本管理", "测试执行", "测试报告"]
)

# 工作流程视图
if menu == "工作流程":
    st.subheader("工作流程")
    
    # 显示工作流程图
    col1, col2, col3, col4 = st.columns(4)
    
    for i, step in enumerate(st.session_state.workflow):
        if i % 4 == 0:
            col = col1
        elif i % 4 == 1:
            col = col2
        elif i % 4 == 2:
            col = col3
        else:
            col = col4
            
        with col:
            if step["status"] == "completed":
                st.success(f"✅ {i+1}. {step['name']}")
            elif step["status"] == "in_progress":
                st.warning(f"🔄 {i+1}. {step['name']}")
            else:
                st.info(f"⏳ {i+1}. {step['name']}")

# API导入视图
elif menu == "API管理":
    st.subheader("API管理")
    
    # API导入方式
    import_method = st.radio(
        "选择API导入方式",
        ("上传OpenAPI/Swagger文件", "输入API URL")
    )
    
    spec_content = None
    
    if import_method == "上传OpenAPI/Swagger文件":
        uploaded_file = st.file_uploader("选择OpenAPI/Swagger文件", type=["json", "yaml", "yml"])
        if uploaded_file:
            spec_content = uploaded_file.getvalue().decode("utf-8")
    else:
        api_url = st.text_input("输入API URL")
        if api_url:
            # 从URL获取spec
            import requests
            try:
                response = requests.get(api_url)
                spec_content = response.text
                st.success("成功获取API规范")
            except Exception as e:
                st.error(f"获取API规范失败: {str(e)}")
    
    # 解析和导入API
    if spec_content:
        if st.button("解析和导入API"):
            try:
                # 解析API规范
                parser = OpenAPIParser()
                if parser.load_spec(spec_content):
                    st.success("API规范解析成功")
                    
                    # 显示API信息
                    api_info = parser.get_api_info()
                    st.json(api_info)
                    
                    # 导入到数据库
                    async def import_api():
                        async with get_db_session() as db:
                            importer = ApiImporter()
                            result = await importer.import_api(db, api_info)
                            return result
                    
                    result = asyncio.run(import_api())
                    
                    if result["success"]:
                        st.success(f"API成功导入数据库，项目ID: {result['project_id']}")
                        st.session_state.api_project_id = result['project_id']
                        
                        # 更新工作流程状态
                        for step in st.session_state.workflow:
                            if step["name"] == "API导入":
                                step["status"] = "completed"
                            elif step["name"] == "AI评审":
                                step["status"] = "in_progress"
                        st.session_state.workflow = st.session_state.workflow
                    else:
                        st.error(f"API导入失败: {result['message']}")
            except Exception as e:
                st.error(f"API处理失败: {str(e)}")

# 测试点管理视图
elif menu == "测试点管理":
    st.subheader("测试点管理")
    
    if not st.session_state.api_project_id:
        st.warning("请先导入API")
    else:
        # 显示现有测试点
        async def get_test_points():
            async with get_db_session() as db:
                generator = TestPointGenerator()
                return await generator.get_test_points(db, st.session_state.api_project_id)
        
        if st.button("刷新测试点"):
            st.session_state.test_points = asyncio.run(get_test_points())
        
        if st.session_state.test_points:
            st.dataframe(pd.DataFrame(st.session_state.test_points))
        
        # 生成测试点
        if st.button("生成测试点"):
            try:
                async def generate_points():
                    async with get_db_session() as db:
                        generator = TestPointGenerator()
                        return await generator.generate_test_points(db, st.session_state.api_project_id)
                
                result = asyncio.run(generate_points())
                if result["success"]:
                    st.success(f"成功生成{result['generated_count']}个测试点")
                    st.session_state.test_points = result["test_points"]
                    
                    # 更新工作流程状态
                    for step in st.session_state.workflow:
                        if step["name"] == "测试点生成":
                            step["status"] = "completed"
                        elif step["name"] == "测试点AI评审":
                            step["status"] = "in_progress"
                    st.session_state.workflow = st.session_state.workflow
            except Exception as e:
                st.error(f"测试点生成失败: {str(e)}")

# 测试用例管理视图
elif menu == "测试用例管理":
    st.subheader("测试用例管理")
    
    if not st.session_state.api_project_id:
        st.warning("请先导入API")
    else:
        # 显示现有测试用例
        async def get_test_cases():
            async with get_db_session() as db:
                generator = TestCaseGenerator()
                return await generator.get_test_cases(db, st.session_state.api_project_id)
        
        if st.button("刷新测试用例"):
            st.session_state.test_cases = asyncio.run(get_test_cases())
        
        if st.session_state.test_cases:
            df = pd.DataFrame(st.session_state.test_cases)
            st.dataframe(df)
            
            # 导出测试用例
            if st.button("导出为Excel"):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='测试用例')
                output.seek(0)
                st.download_button(
                    label="下载测试用例Excel",
                    data=output,
                    file_name="test_cases.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        # 生成测试用例
        if st.button("生成测试用例"):
            try:
                # 获取测试点ID
                async def get_test_point_ids():
                    async with get_db_session() as db:
                        from src.models.test_point import TestPoint
                        from sqlalchemy import select
                        result = await db.execute(
                            select(TestPoint.id).where(TestPoint.api_project_id == st.session_state.api_project_id)
                        )
                        return [point_id for point_id, in result.all()]
                
                test_point_ids = asyncio.run(get_test_point_ids())
                
                if test_point_ids:
                    async def generate_cases():
                        async with get_db_session() as db:
                            generator = TestCaseGenerator()
                            return await generator.generate_test_cases(db, test_point_ids)
                    
                    result = asyncio.run(generate_cases())
                    if result["success"]:
                        st.success(f"成功生成{result['generated_count']}个测试用例")
                        
                        # 更新测试用例列表
                        st.session_state.test_cases = asyncio.run(get_test_cases())
                        
                        # 更新工作流程状态
                        for step in st.session_state.workflow:
                            if step["name"] == "测试用例生成":
                                step["status"] = "completed"
                            elif step["name"] == "测试用例AI评审":
                                step["status"] = "in_progress"
                        st.session_state.workflow = st.session_state.workflow
                else:
                    st.warning("没有找到测试点")
            except Exception as e:
                st.error(f"测试用例生成失败: {str(e)}")

# 测试脚本管理视图
elif menu == "测试脚本管理":
    st.subheader("测试脚本管理")
    
    if not st.session_state.api_project_id:
        st.warning("请先导入API")
    else:
        # 显示现有测试脚本
        async def get_test_scripts():
            async with get_db_session() as db:
                generator = TestScriptGenerator()
                return await generator.get_test_scripts(db, st.session_state.api_project_id)
        
        if st.button("刷新测试脚本"):
            st.session_state.test_scripts = asyncio.run(get_test_scripts())
        
        if st.session_state.test_scripts:
            for script in st.session_state.test_scripts:
                with st.expander(f"脚本 {script['id']} - {script['script_type']}"):
                    st.text(script['script_content'])
                    
                    # 下载按钮
                    st.download_button(
                        label=f"下载脚本 {script['id']}",
                        data=script['script_content'],
                        file_name=f"test_script_{script['id']}.py",
                        mime="text/plain"
                    )
        
        # 生成测试脚本
        if st.button("生成测试脚本"):
            try:
                # 获取测试用例ID
                async def get_test_case_ids():
                    async with get_db_session() as db:
                        from src.models.test_case import TestCase
                        from src.models.test_point import TestPoint
                        from sqlalchemy import select
                        
                        # 先获取测试点ID
                        test_points_result = await db.execute(
                            select(TestPoint.id).where(TestPoint.api_project_id == st.session_state.api_project_id)
                        )
                        test_point_ids = [point_id for point_id, in test_points_result.all()]
                        
                        # 再获取测试用例ID
                        test_cases_result = await db.execute(
                            select(TestCase.id).where(TestCase.test_point_id.in_(test_point_ids))
                        )
                        return [case_id for case_id, in test_cases_result.all()]
                
                test_case_ids = asyncio.run(get_test_case_ids())
                
                if test_case_ids:
                    async def generate_scripts():
                        async with get_db_session() as db:
                            generator = TestScriptGenerator()
                            return await generator.generate_test_scripts(db, test_case_ids)
                    
                    result = asyncio.run(generate_scripts())
                    if result["success"]:
                        st.success(f"成功生成{result['generated_count']}个测试脚本")
                        
                        # 更新测试脚本列表
                        st.session_state.test_scripts = asyncio.run(get_test_scripts())
                        
                        # 更新工作流程状态
                        for step in st.session_state.workflow:
                            if step["name"] == "测试脚本生成":
                                step["status"] = "completed"
                            elif step["name"] == "测试脚本AI评审":
                                step["status"] = "in_progress"
                        st.session_state.workflow = st.session_state.workflow
                else:
                    st.warning("没有找到测试用例")
            except Exception as e:
                st.error(f"测试脚本生成失败: {str(e)}")

# 测试执行视图
elif menu == "测试执行":
    st.subheader("测试执行")
    
    if not st.session_state.api_project_id:
        st.warning("请先导入API")
    else:
        # 获取测试脚本ID
        async def get_script_ids():
            async with get_db_session() as db:
                generator = TestScriptGenerator()
                scripts = await generator.get_test_scripts(db, st.session_state.api_project_id)
                return [script['id'] for script in scripts]
        
        script_ids = asyncio.run(get_script_ids())
        
        if script_ids:
            # 选择要执行的脚本
            selected_scripts = st.multiselect(
                "选择要执行的测试脚本",
                script_ids
            )
            
            # 执行测试脚本
            if st.button("执行测试脚本"):
                if selected_scripts:
                    try:
                        async def execute_scripts():
                            async with get_db_session() as db:
                                executor = TestExecutor()
                                return await executor.execute_test_scripts(db, selected_scripts)
                        
                        result = asyncio.run(execute_scripts())
                        if result["success"]:
                            st.success("测试脚本执行完成")
                            
                            # 显示执行结果
                            for execution_result in result["execution_results"]:
                                with st.expander(f"脚本 {execution_result['script_id']} 执行结果"):
                                    if execution_result["result"]["success"]:
                                        st.success("执行成功")
                                    else:
                                        st.error("执行失败")
                                    
                                    st.text("输出:")
                                    st.text(execution_result["result"]["output"])
                                    
                                    if execution_result["result"]["error"]:
                                        st.text("错误:")
                                        st.text(execution_result["result"]["error"])
                            
                            # 更新工作流程状态
                            for step in st.session_state.workflow:
                                if step["name"] == "测试执行":
                                    step["status"] = "completed"
                                elif step["name"] == "测试报告":
                                    step["status"] = "in_progress"
                            st.session_state.workflow = st.session_state.workflow
                    except Exception as e:
                        st.error(f"测试执行失败: {str(e)}")
        else:
            st.warning("没有找到测试脚本")

# 测试报告视图
elif menu == "测试报告":
    st.subheader("测试报告")
    
    if not st.session_state.api_project_id:
        st.warning("请先导入API")
    else:
        # 生成测试报告
        if st.button("生成测试报告"):
            try:
                async def generate_report():
                    async with get_db_session() as db:
                        generator = TestReportGenerator()
                        return await generator.generate_detailed_report(db, st.session_state.api_project_id)
                
                result = asyncio.run(generate_report())
                if result["success"]:
                    report = result["report"]
                    
                    # 显示报告摘要
                    st.write("### 报告摘要")
                    st.write(f"项目名称: {report['project_name']}")
                    st.write(f"报告日期: {report['report_date']}")
                    st.write(f"总脚本数: {report['total_scripts']}")
                    st.write(f"通过数: {report['passed_count']}")
                    st.write(f"失败数: {report['failed_count']}")
                    st.write(f"成功率: {report['success_rate']}%")
                    
                    # 显示详细结果
                    with st.expander("详细执行结果"):
                        st.dataframe(pd.DataFrame(report['execution_results']))
                    
                    # 下载报告
                    report_json = json.dumps(report, ensure_ascii=False, indent=2)
                    st.download_button(
                        label="下载JSON格式报告",
                        data=report_json,
                        file_name="test_report.json",
                        mime="application/json"
                    )
                    
                    # 更新工作流程状态
                    for step in st.session_state.workflow:
                        if step["name"] == "测试报告":
                            step["status"] = "completed"
                    st.session_state.workflow = st.session_state.workflow
            except Exception as e:
                st.error(f"测试报告生成失败: {str(e)}")

# 页脚
st.markdown("---")
st.text("智能测试探索架构 - 基于LangChain的智能接口测试自动生成系统")
