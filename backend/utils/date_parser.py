from datetime import datetime
import re

def parse_date(date_str):
    """解析多种格式的日期字符串
    
    支持的格式包括：
    - YYYY-MM-DD
    - YYYY/MM/DD
    - DD-MM-YYYY
    - DD/MM/YYYY
    - MM-DD-YYYY
    - MM/DD/YYYY
    - 以及Excel日期序列号
    
    Args:
        date_str: 日期字符串或Excel日期序列号
        
    Returns:
        格式化为YYYY-MM-DD的日期字符串，解析失败则返回None
    """
    # 如果已经是datetime对象，直接格式化返回
    if isinstance(date_str, datetime):
        return date_str.strftime('%Y-%m-%d')
    
    # 转换为字符串
    date_str = str(date_str).strip()
    
    # 尝试解析常见日期格式
    date_formats = [
        '%Y-%m-%d',  # 2023-01-01
        '%Y/%m/%d',  # 2023/01/01
        '%d-%m-%Y',  # 01-01-2023
        '%d/%m/%Y',  # 01/01/2023
        '%m-%d-%Y',  # 01-01-2023
        '%m/%d/%Y',  # 01/01/2023
        '%Y年%m月%d日',  # 2023年01月01日
        '%Y.%m.%d',  # 2023.01.01
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    # 尝试解析Excel日期序列号
    # Excel日期序列号从1900-01-01开始，该日期的序列号为1
    try:
        if date_str.isdigit() or (date_str.replace('.', '', 1).isdigit() and date_str.count('.') == 1):
            excel_date = float(date_str)
            # Excel的bug：将1900年2月29日错误地视为闰年
            if excel_date > 60:
                excel_date -= 1
            
            # 从1899-12-30开始计算（Excel中的日期0）
            date = datetime(1899, 12, 30) + timedelta(days=excel_date)
            return date.strftime('%Y-%m-%d')
    except (ValueError, OverflowError):
        pass
    
    # 尝试从字符串中提取日期
    # 匹配常见的日期模式
    patterns = [
        r'(\d{4})[-/年\.](\d{1,2})[-/月\.](\d{1,2})',  # YYYY-MM-DD
        r'(\d{1,2})[-/\.](\d{1,2})[-/\.](\d{4})',  # DD-MM-YYYY 或 MM-DD-YYYY
    ]
    
    for pattern in patterns:
        match = re.search(pattern, date_str)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                if len(groups[0]) == 4:  # YYYY-MM-DD
                    year, month, day = groups
                else:  # DD-MM-YYYY 或 MM-DD-YYYY
                    # 这里简单假设第一个数字是日，第二个是月
                    # 实际应用中可能需要更复杂的逻辑来区分
                    day, month, year = groups
                
                try:
                    return datetime(int(year), int(month), int(day)).strftime('%Y-%m-%d')
                except ValueError:
                    # 如果日期无效（如月份>12或日>31），尝试交换月和日
                    try:
                        return datetime(int(year), int(day), int(month)).strftime('%Y-%m-%d')
                    except ValueError:
                        pass
    
    # 所有尝试都失败，返回None
    return None

def get_month_from_date(date_str):
    """从日期字符串中提取年月
    
    Args:
        date_str: 日期字符串，格式为YYYY-MM-DD
        
    Returns:
        格式化为YYYY-MM的年月字符串，解析失败则返回None
    """
    parsed_date = parse_date(date_str)
    if parsed_date:
        return parsed_date[:7]  # 取YYYY-MM部分
    return None

def get_days_in_month(year, month):
    """获取指定年月的天数
    
    Args:
        year: 年份
        month: 月份
        
    Returns:
        该月的天数
    """
    import calendar
    return calendar.monthrange(year, month)[1]

def calculate_work_days_ratio(start_date, end_date, month):
    """计算指定日期范围在某月中的工作天数比例
    
    Args:
        start_date: 开始日期，格式为YYYY-MM-DD
        end_date: 结束日期，格式为YYYY-MM-DD
        month: 月份，格式为YYYY-MM
        
    Returns:
        工作天数比例（0-1之间的小数）
    """
    # 解析日期
    start_date = parse_date(start_date)
    end_date = parse_date(end_date)
    
    if not start_date or not end_date or not month:
        return 1.0
    
    # 解析年月
    year, month_num = map(int, month.split('-'))
    
    # 获取该月的天数
    total_days = get_days_in_month(year, month_num)
    
    # 计算该月的开始和结束日期
    month_start = f"{month}-01"
    month_end = f"{month}-{total_days}"
    
    # 确定实际的开始和结束日期
    actual_start = max(start_date, month_start)
    actual_end = min(end_date, month_end)
    
    # 如果实际开始日期晚于实际结束日期，则不在该月内
    if actual_start > actual_end:
        return 0.0
    
    # 计算实际工作天数
    start_day = int(actual_start.split('-')[2])
    end_day = int(actual_end.split('-')[2])
    work_days = end_day - start_day + 1
    
    # 计算比例
    return work_days / total_days