"""
Prompt生成服务模块
负责处理JSON解析和Prompt模板生成的业务逻辑
"""

import json
import os
from typing import List, Dict
from datetime import datetime

from app.models import PromptRequest, FieldInfo, ApiInfo


class PromptService:
    """Prompt生成服务类"""
    
    @staticmethod
    def get_ai_request_template() -> str:
        """
        获取AI调用的请求报文模板
        
        Returns:
            Markdown格式的请求报文模板字符串
        """
        return """# 核心任务

你是一名Java Web应用开发领域的资深的【需求分析师兼任技术架构师】，请你根据我在下面提供给你的（以一级标题的形式给出）：【接口名称与描述】、【相关表及表模型设计信息】、【接口响应报文格式表】（以markDown格式的表格给出），按要求进行综合分析，得出接口响应报文中的各个字段与数据库表字段的可能关联关系，并将其填入我提供的接口响应报文结构表中，最终将且仅将填充完毕的接口响应报文结构表返回给我（禁止用```markDown的markDown代码块包裹），除表格外，不附带任何多余描述。

# 要求

1. 发挥你在Java Web应用开发领域的丰富经验，综合【包括但不限于】以下两个标准进行综合评估，逐行分析接口响应报文结构表，填充每个响应报文字段的对应关系：
   1. 能够从数据库表中的"_"连接符字段，简单转译成Java应用中驼峰结构参数名的数据，一定是相关的，例如user_id和userId一定是同一个字段；
   2. 面对不能通过上一条规则匹配数据源的数据，你需要综合分析接口描述和响应报文字段名和数据库表字段含义进行评估，匹配有可能存在隐形关联的响应报文字段和数据库表字段。
2. 主数据库源列的数据，应该以 数据库表名.数据库表字段名 的格式填充，例如：database.code;
3. **只返回markDown格式的接口响应报文结构表。**

# 接口名称与描述



# 相关表及表模型设计信息



# 接口响应报文格式表



"""
    
    @staticmethod
    def get_business_logic_ai_request_template() -> str:
        """
        获取业务逻辑分析的AI调用请求模板
        
        Returns:
            用于分析业务逻辑的Markdown格式模板字符串
        """
        return """# 核心任务

你是一名Java Web应用开发领域的资深的【需求分析师兼任技术架构师】，我会提供给你：接口名称、请求报文样例、响应报文样例，你会根据我提供的信息和要求进行综合分析，返回一份接口业务逻辑描述给我。

# 要求

1. 发挥你在Java Web应用开发领域的丰富经验，根据接口名称、请求报文、响应报文进行综合分析，推测同类接口在行业内主流的业务逻辑；
2. 只返回纯净的业务逻辑描述，不返回任何多余描述。


# 接口名称



# 请求报文样例



# 响应报文样例



"""
    
    @staticmethod
    def parse_json_fields(json_string: str) -> List[FieldInfo]:
        """
        解析JSON字符串并提取字段信息
        
        Args:
            json_string: JSON格式的字符串
            
        Returns:
            字段信息列表
        """
        try:
            data = json.loads(json_string)
            fields = []
            
            def extract_fields(obj, prefix=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        field_name = f"{prefix}.{key}" if prefix else key
                        field_type = type(value).__name__
                        
                        if isinstance(value, dict):
                            fields.append(FieldInfo(
                                name=field_name,
                                type="object",
                                required="是",
                                description="对象类型"
                            ))
                            extract_fields(value, field_name)
                        elif isinstance(value, list):
                            fields.append(FieldInfo(
                                name=field_name,
                                type="array",
                                required="是",
                                description="数组类型"
                            ))
                            if value and isinstance(value[0], dict):
                                extract_fields(value[0], f"{field_name}[0]")
                        else:
                            fields.append(FieldInfo(
                                name=field_name,
                                type=field_type,
                                required="是",
                                description=f"{field_type}类型字段"
                            ))
                elif isinstance(obj, list) and obj:
                    extract_fields(obj[0], prefix)
            
            extract_fields(data)
            return fields
        except json.JSONDecodeError:
            return [FieldInfo(
                name="解析错误",
                type="unknown",
                required="未知",
                description="JSON格式不正确"
            )]
    
    @staticmethod
    def generate_request_table(fields: List[FieldInfo]) -> str:
        """
        生成请求参数表格
        
        Args:
            fields: 字段信息列表
            
        Returns:
            Markdown格式的表格字符串
        """
        if not fields:
            return """| 参数 | 类型 | 必填 | 说明 |
| ---- | ---- | ---- | ---- |
| 无参数 | - | - | - |"""
        
        table = "| 参数 | 类型 | 必填 | 说明 |\n| ---- | ---- | ---- | ---- |\n"
        for field in fields:
            table += f"| {field.name} | {field.type} | {field.required} | {field.description} |\n"
        return table
    
    @staticmethod
    def generate_response_table(fields: List[FieldInfo]) -> str:
        """
        生成响应参数表格
        
        Args:
            fields: 字段信息列表
            
        Returns:
            Markdown格式的表格字符串
        """
        if not fields:
            return """| 响应报文字段 | 主数据库源 | 关联数据源 | 逻辑描述 |
| ------------ | ---------- | ---------- | -------- |
| 无字段 | - | - | - |"""
        
        table = "| 响应报文字段 | 主数据库源 | 关联数据源 | 逻辑描述 |\n| ------------ | ---------- | ---------- | -------- |\n"
        for field in fields:
            table += f"| {field.name} | 待填写 | 待填写 | {field.description} |\n"
        return table
    
    @staticmethod
    def format_database_tables(database_tables: List[str]) -> str:
        """
        格式化数据库表DDL
        
        Args:
            database_tables: 数据库表DDL列表
            
        Returns:
            格式化后的数据库表字符串
        """
        if not database_tables:
            return "暂无关联数据库表"
        
        formatted_tables = []
        for i, table_ddl in enumerate(database_tables, 1):
            if table_ddl.strip():
                # 为每个表添加清晰的标题和分隔
                formatted_tables.append(f"## 表{i}：数据库表结构\n\n```sql\n{table_ddl.strip()}\n```")
        
        # 使用更明显的分隔符连接多个表
        return "\n\n---\n\n".join(formatted_tables)
    
    @classmethod
    def generate_api_section(cls, api: ApiInfo) -> str:
        """
        生成单个接口的模板部分
        
        Args:
            api: 单个接口信息
            
        Returns:
            单个接口的模板字符串
        """
        # 解析请求和响应JSON
        request_fields = cls.parse_json_fields(api.request_example)
        response_fields = cls.parse_json_fields(api.response_example)
        
        # 生成表格
        request_table = cls.generate_request_table(request_fields)
        response_table = cls.generate_response_table(response_fields)
        
        # 格式化数据库表
        database_tables_text = cls.format_database_tables_for_api(api.database_tables)
        
        api_template = f"""# 接口API

**接口名称：{api.name}**

```http
{api.route}
```

**请求体：**

```json
{api.request_example}
```

**请求参数：**

{request_table}

**响应结构：**

```json
{api.response_example}
```

**响应参数：**

{response_table}

**关联数据库表：**

{database_tables_text}"""
        
        return api_template

    @staticmethod
    def format_database_tables_for_api(database_tables: List[str]) -> str:
        """
        为单个接口格式化数据库表DDL
        
        Args:
            database_tables: 数据库表DDL列表
            
        Returns:
            格式化后的数据库表字符串
        """
        if not database_tables:
            return "暂无关联数据库表"
        
        formatted_tables = []
        for i, table_ddl in enumerate(database_tables, 1):
            if table_ddl.strip():
                formatted_tables.append(f"表{i}：\n```sql\n{table_ddl.strip()}\n```")
        
        return "\n".join(formatted_tables)

    @classmethod
    def generate_prompt_template(cls, data: PromptRequest, developer: str) -> str:
        """
        生成完整的prompt模板
        
        Args:
            data: Prompt请求数据
            developer: 开发者姓名
            
        Returns:
            生成的prompt模板字符串
        """
        current_date = datetime.now().strftime("%Y/%m/%d")
        
        # 收集所有接口名称
        api_names = [api.name for api in data.apis]
        if len(api_names) == 1:
            core_task = f"请你按要求完成【{api_names[0]}】。"
        else:
            api_names_str = "】、【".join(api_names)
            core_task = f"请你按要求完成【{api_names_str}】。"
        
        # 生成模板头部
        template = f"""- since: {current_date}
- author: {developer}

# 核心任务

{core_task}

# 业务逻辑

# 开发规范
- 接口采用简单的Controller-IService-ServiceImpl-Mapper.java-Mapper.xml的层级设计，具体存放位置参照【待填写】接口；
- 请你在开发时，格外注意**所有使用的方法必须要在项目中有过已使用案例**以确保可用性和规范性；
- 项目使用JDK8+SpringBoot2.7，请你在开发时注意代码的适配性；
- 生成SQL时，请不要使用高级的SQL方法或机制，非必要禁用嵌套SQL，使用JOIN进行联表查询替代嵌套SQL，SQL只返回需要使用到的字段；
- 有可能导致你开发出现错误的不明确的问题或信息，请你先向我询问答案，再进行开发。



"""
        
        # 为每个接口生成对应的部分
        api_sections = []
        for api in data.apis:
            api_section = cls.generate_api_section(api)
            api_sections.append(api_section)
        
        # 合并所有接口部分
        template += "\n\n".join(api_sections)
        
        return template
    
    @staticmethod
    def extract_prompt_info_for_ai(prompt_data: 'PromptRequest') -> Dict[str, str]:
        """
        从PromptRequest数据中提取接口信息用于AI调用
        
        Args:
            prompt_data: PromptRequest数据对象
            
        Returns:
            包含接口名称、数据库表和响应参数表的字典
        """
        if not prompt_data.apis or len(prompt_data.apis) == 0:
            return {
                "interface_name": "",
                "database_tables": "",
                "response_table": ""
            }
        
        # 处理多个接口的情况
        interface_names = []
        all_database_tables = []
        all_response_tables = []
        
        for api in prompt_data.apis:
            # 收集接口名称
            if api.name:
                interface_names.append(api.name)
            
            # 收集数据库表信息
            if api.database_tables:
                for table_ddl in api.database_tables:
                    if table_ddl.strip():
                        all_database_tables.append(table_ddl.strip())
            
            # 收集响应参数表
            if api.response_example:
                response_fields = PromptService.parse_json_fields(api.response_example)
                response_table = PromptService.generate_response_table(response_fields)
                if response_table.strip():
                    all_response_tables.append(response_table.strip())
        
        # 格式化接口名称
        if len(interface_names) == 1:
            interface_name = interface_names[0]
        else:
            interface_name = "、".join(interface_names)
        
        # 格式化数据库表信息
        if all_database_tables:
            formatted_tables = []
            for i, table_ddl in enumerate(all_database_tables, 1):
                formatted_tables.append(f"表{i}：\n```sql\n{table_ddl}\n```")
            database_tables = "\n".join(formatted_tables)
        else:
            database_tables = "暂无关联数据库表"
        
        # 格式化响应参数表
        if all_response_tables:
            response_table = "\n\n".join(all_response_tables)
        else:
            response_table = "暂无响应参数表"
        
        return {
            "interface_name": interface_name,
            "database_tables": database_tables,
            "response_table": response_table
        }
    
    @staticmethod
    def extract_business_logic_info_for_ai(base_prompt: str) -> Dict[str, str]:
        """
        从基础prompt中提取业务逻辑分析所需的信息
        
        Args:
            base_prompt: 基础prompt模板字符串
            
        Returns:
            包含接口名称、请求体、响应结构的字典
        """
        lines = base_prompt.split('\n')
        
        interface_name = ""
        request_example = ""
        response_example = ""
        
        # 查找接口名称
        for i, line in enumerate(lines):
            if line.startswith('**接口名称：'):
                interface_name = line.replace('**接口名称：', '').replace('**', '').strip()
                break
        
        # 查找请求体部分
        in_request_section = False
        request_lines = []
        for i, line in enumerate(lines):
            if line.startswith('**请求体：**'):
                in_request_section = True
                continue
            elif in_request_section:
                if line.startswith('```json'):
                    continue
                elif line.startswith('```') and request_lines:
                    break
                elif line.startswith('**'):
                    break
                elif in_request_section and not line.startswith('```'):
                    request_lines.append(line)
        
        request_example = '\n'.join(request_lines).strip()
        
        # 查找响应结构部分
        in_response_section = False
        response_lines = []
        for i, line in enumerate(lines):
            if line.startswith('**响应结构：**'):
                in_response_section = True
                continue
            elif in_response_section:
                if line.startswith('```json'):
                    continue
                elif line.startswith('```') and response_lines:
                    break
                elif line.startswith('**'):
                    break
                elif in_response_section and not line.startswith('```'):
                    response_lines.append(line)
        
        response_example = '\n'.join(response_lines).strip()
        
        return {
            "interface_name": interface_name,
            "request_example": request_example,
            "response_example": response_example
        }
    
    @staticmethod
    def fill_ai_request_template(prompt_info: Dict[str, str]) -> str:
        """
        将prompt信息填入AI请求模板
        
        Args:
            prompt_info: 包含接口信息的字典
            
        Returns:
            填充完成的AI请求内容
        """
        template = PromptService.get_ai_request_template()
        
        # 替换模板中的占位符
        filled_template = template.replace(
            "# 接口名称与描述\n\n\n",
            f"# 接口名称与描述\n\n{prompt_info['interface_name']}\n"
        ).replace(
            "# 相关表及表模型设计信息\n\n\n",
            f"# 相关表及表模型设计信息\n\n{prompt_info['database_tables']}\n"
        ).replace(
            "# 接口响应报文格式表\n\n\n",
            f"# 接口响应报文格式表\n\n{prompt_info['response_table']}\n"
        )
        
        return filled_template
    
    @staticmethod
    def fill_business_logic_ai_request_template(business_info: Dict[str, str]) -> str:
        """
        将业务逻辑分析信息填入AI请求模板
        
        Args:
            business_info: 包含接口名称、请求体、响应结构的字典
            
        Returns:
            填充完成的业务逻辑分析AI请求内容
        """
        template = PromptService.get_business_logic_ai_request_template()
        
        # 替换模板中的占位符
        filled_template = template.replace(
            "# 接口名称\n\n\n",
            f"# 接口名称\n\n{business_info['interface_name']}\n"
        ).replace(
            "# 请求报文样例\n\n\n",
            f"# 请求报文样例\n\n{business_info['request_example']}\n"
        ).replace(
            "# 响应报文样例\n\n\n",
            f"# 响应报文样例\n\n{business_info['response_example']}\n"
        )
        
        return filled_template
    
    @staticmethod
    def inject_business_logic_into_prompt(original_prompt: str, business_logic: str) -> str:
        """
        将AI返回的业务逻辑注入到原始prompt中的业务逻辑一级标题下
        
        Args:
            original_prompt: 原始prompt内容
            business_logic: AI返回的业务逻辑描述
            
        Returns:
            注入业务逻辑后的prompt内容
        """
        lines = original_prompt.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            result_lines.append(line)
            
            # 在找到"# 业务逻辑"这一行后，添加业务逻辑内容
            if line.strip() == "# 业务逻辑":
                result_lines.append("")
                result_lines.append(business_logic.strip())
                result_lines.append("")
                
                # 跳过原来业务逻辑部分的空行，找到下一个一级标题
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    if next_line.startswith("# "):
                        # 遇到下一个一级标题，停止跳过，不要将这行加入结果
                        break
                    elif next_line.strip() != "":
                        # 遇到非空行且不是一级标题，停止跳过，不要将这行加入结果
                        break
                    # 跳过空行
                    i += 1
                
                # 跳出当前处理，继续外层循环处理剩余行
                continue
            
            i += 1
        
        return '\n'.join(result_lines)
    
    @staticmethod
    def replace_response_table_in_prompt(original_prompt: str, new_response_table: str) -> str:
        """
        将AI返回的响应参数表替换到原始prompt中
        
        Args:
            original_prompt: 原始prompt内容
            new_response_table: AI返回的新响应参数表
            
        Returns:
            替换后的prompt内容
        """
        lines = original_prompt.split('\n')
        result_lines = []
        in_response_table = False
        
        for line in lines:
            if line.startswith('**响应参数：**'):
                result_lines.append(line)
                result_lines.append('')
                result_lines.append(new_response_table.strip())
                in_response_table = True
                continue
            elif in_response_table and line.startswith('**'):
                in_response_table = False
                result_lines.append('')
                result_lines.append(line)
            elif not in_response_table:
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    @staticmethod
    def log_chat_interaction(request_content: str, response_content: str, user_id: int = None):
        """
        记录AI聊天交互到chat.log文件
        
        Args:
            request_content: AI请求内容
            response_content: AI响应内容
            user_id: 用户ID（可选）
        """
        try:
            # 确保logs目录存在
            logs_dir = "logs"
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            
            log_file = os.path.join(logs_dir, "chat.log")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_entry = f"""
==================== AI Chat Log ====================
时间: {timestamp}
用户ID: {user_id if user_id else 'Unknown'}

--- AI 请求内容 ---
{request_content}

--- AI 响应内容 ---
{response_content}

================================================

"""
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"记录chat.log时出错: {str(e)}")
