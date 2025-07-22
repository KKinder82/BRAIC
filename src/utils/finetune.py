
import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI


def convert_json_to_langchain_finetune_data(json_file_paths):
    """
    将一个或多个JSON文件转换为LangChain微调数据格式

    Args:
        json_file_paths (str or list): JSON文件路径或路径数组

    Returns:
        list: LangChain微调数据列表
    """
    # 支持单个字符串或路径数组
    if isinstance(json_file_paths, str):
        json_file_paths = [json_file_paths]

    all_finetune_data = []

    for json_file_path in json_file_paths:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 系统提示词
        system_prompt = """# 个人能力  

 - 作为教育技术学家，您具备教育心理学、学习、教学和评估的分类学、系统化教学设计和教育技术学的专业背景，能够结合学生的实际技术需求设计课程。

#技能

 1. 具备教学研究、设计经验：具备教育学、学习心理学、计算机科学与信息技术的交叉学科知识背景，系统掌握学习科学理论（有意义学习和图式理论、情境认知、皮亚杰、布鲁纳、维果茨基、学习的神经生理学、加涅的教学论、建构主义）、教学设计模型（如迪克凯瑞、ADDIE、SAM）、教育数据挖掘、人工智能教育应用、知识图谱搭建等核心领域，熟悉虚拟现实（VR）、增强现实（AR）、MOOCs平台开发等前沿技术。

2. 技能层面，擅长教育软件设计与开发（如Unity、Scratch）、学习分析工具应用（如Tableau、Python）、教育实验设计与量化研究，具备教育政策分析、跨学科课程设计能力，同时精通SCORM标准、xAPI等数字化学习技术规范，能够独立开展智能教育系统研发或教育数字化转型战略研究，部分研究者还兼具教育神经科学或教育机器人等专项领域的技术转化经验。

3. 熟悉学员认知发展，能够将复杂技术概念简化为易于理解的内容。
"""
        finetune_data = []

        def process_task_steps(task_steps, profession, post, project_name, parent_path=""):
            """递归处理任务步骤"""
            for task in task_steps:
                current_path = f"{parent_path}，{task['level']}级任务：{task['content']}" if parent_path else f"{task['level']}级任务：{task['content']}"

                # 如果有陈述性知识和程序性知识，生成微调数据
                if 'declarativeKnowledge' in task and task['declarativeKnowledge']:
                    declarative_input = f"专业：{profession}，岗位：{post}，项目名称：{project_name}，{current_path}"
                    declarative_output = ",".join(task['declarativeKnowledge'])

                    finetune_data.append({
                        "instruction": "请根据输入内容，生成陈述性知识。",
                        "input": declarative_input,
                        "output": declarative_output,
                        "system": system_prompt,
                        "history": []
                    })

                if 'proceduralKnowledge' in task and task['proceduralKnowledge']:
                    procedural_input = f"专业：{profession}，岗位：{post}，项目名称：{project_name}，{current_path}"
                    procedural_output = ",".join(task['proceduralKnowledge'])

                    finetune_data.append({
                        "instruction": "请根据输入内容，生成程序性知识。",
                        "input": procedural_input,
                        "output": procedural_output,
                        "system": system_prompt,
                        "history": []
                    })

                # 递归处理子任务
                if 'children' in task and task['children']:
                    process_task_steps(task['children'], profession, post, project_name, current_path)

        # 处理每个文件
        profession = data.get("profession", "")
        post = data.get("post", "")
        project_name = data.get("projectName", "")
        task_steps = data.get("taskSteps", [])
        process_task_steps(task_steps, profession, post, project_name)
        all_finetune_data.extend(finetune_data)

    return all_finetune_data

    
    finetune_data = []
    
    def process_task_steps(task_steps, profession, post, project_name, parent_path=""):
        """递归处理任务步骤"""
        for task in task_steps:
            current_path = f"{parent_path}，{task['level']}级任务：{task['content']}" if parent_path else f"{task['level']}级任务：{task['content']}"
            
            # 如果有陈述性知识和程序性知识，生成微调数据
            if 'declarativeKnowledge' in task and task['declarativeKnowledge']:
                declarative_input = f"专业：{profession}，岗位：{post}，项目名称：{project_name}，{current_path}"
                declarative_output = ",".join(task['declarativeKnowledge'])
                
                finetune_data.append({
                    "instruction": "请根据输入内容，生成陈述性知识。",
                    "input": declarative_input,
                    "output": declarative_output,
                    "system": system_prompt,
                    "history": []
                })
            
            if 'proceduralKnowledge' in task and task['proceduralKnowledge']:
                procedural_input = f"专业：{profession}，岗位：{post}，项目名称：{project_name}，{current_path}"
                procedural_output = ",".join(task['proceduralKnowledge'])
                
                finetune_data.append({
                    "instruction": "请根据输入内容，生成程序性知识。",
                    "input": procedural_input,
                    "output": procedural_output,
                    "system": system_prompt,
                    "history": []
                })
            
            # 递归处理子任务
            if 'children' in task and task['children']:
                process_task_steps(task['children'], profession, post, project_name, current_path)
    
    # 开始处理
    profession = data.get('profession', '')
    post = data.get('post', '')
    project_name = data.get('projectName', '')
    task_steps = data.get('taskSteps', [])
    
    process_task_steps(task_steps, profession, post, project_name)
    
    return finetune_data

def save_finetune_data_to_json(finetune_data, output_file_path):
    """
    将微调数据保存为JSON文件
    
    Args:
        finetune_data (list): 微调数据列表
        output_file_path (str): 输出文件路径
    """
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(finetune_data, f, ensure_ascii=False, indent=2)

# 使用示例
if __name__ == "__main__":
    # 示例用法
    input_files = [
        "data/低压三相四线标准配置计量装置接线判别与更正作业_final.json",
        "data/低压三相四线标准配置计量装置新装接线作业_final.json",
        "data/低压三相四线电能表运行状态作业_final.json",
        "data/电能表接线测量及六角图绘制作业_0703版本.json",
        "data/三相三线标准配置计量装置接线作业_final.json"
    ]
    output_file = "data/finetune_data.json"
    try:
        finetune_data = convert_json_to_langchain_finetune_data(input_files)
        save_finetune_data_to_json(finetune_data, output_file)
        print(f"成功转换 {len(finetune_data)} 条微调数据")
        print(f"数据已保存到: {output_file}")
    except Exception as e:
        print(f"转换失败: {e}")





