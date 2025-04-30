/**
 * 薪资计算Web Worker
 * 用于在后台线程中执行薪资计算、社保计算等耗时操作
 * 避免阻塞主线程导致UI卡顿
 */

// Web Worker上下文中没有window对象，使用self引用Worker全局作用域
const ctx = self;

// 监听主线程发送的消息
ctx.addEventListener('message', (event) => {
  const { type, data, taskId } = event.data;
  
  try {
    let result;
    
    // 根据任务类型执行不同的计算
    switch (type) {
      case 'calculateSalary':
        result = calculateSalary(data);
        break;
      case 'calculateSocialInsurance':
        result = calculateSocialInsurance(data);
        break;
      case 'calculateIncomeTax':
        result = calculateIncomeTax(data);
        break;
      case 'processAttendanceData':
        result = processAttendanceData(data);
        break;
      default:
        throw new Error(`未知的任务类型: ${type}`);
    }
    
    // 将计算结果发送回主线程
    ctx.postMessage({
      type: 'success',
      taskId,
      result
    });
  } catch (error) {
    // 发送错误信息回主线程
    ctx.postMessage({
      type: 'error',
      taskId,
      error: error.message
    });
  }
});

/**
 * 计算薪资
 * 支持员工在同一个月内有职位变动的情况
 * @param {Object} data - 薪资计算所需数据
 * @returns {Object} - 计算结果
 */
function calculateSalary(data) {
  const { employee, month, salaryGroup, attendanceData, positionChanges } = data;
  
  // 检查是否有职位变动
  if (positionChanges && positionChanges.length > 0) {
    // 按职位变动分段计算薪资
    return calculateSalaryWithPositionChanges(data);
  }
  
  // 常规薪资计算
  const baseSalary = parseFloat(employee.base_salary) || 0;
  const attendanceDeductions = calculateAttendanceDeductions(attendanceData, salaryGroup.rules);
  const bonuses = (data.bonuses || []).reduce((sum, bonus) => sum + parseFloat(bonus.amount), 0);
  
  // 计算薪资项
  const salaryItems = {};
  (salaryGroup.items || []).forEach(item => {
    if (item.type === '收入') {
      salaryItems[item.name] = parseFloat(item.amount) || 0;
    } else if (item.type === '扣除') {
      salaryItems[item.name] = -(parseFloat(item.amount) || 0);
    }
  });
  
  // 计算总薪资
  const totalSalary = baseSalary - attendanceDeductions + bonuses + 
    Object.values(salaryItems).reduce((sum, amount) => sum + amount, 0);
  
  return {
    baseSalary,
    attendanceDeductions,
    bonuses,
    salaryItems,
    totalSalary,
    details: {
      employee,
      month,
      salaryGroup
    }
  };
}

/**
 * 处理员工在同一个月内有职位变动的薪资计算
 * @param {Object} data - 薪资计算所需数据
 * @returns {Object} - 计算结果
 */
function calculateSalaryWithPositionChanges(data) {
  const { employee, month, positionChanges, attendanceData } = data;
  
  // 获取月份的天数
  const daysInMonth = new Date(parseInt(month.split('-')[0]), parseInt(month.split('-')[1]), 0).getDate();
  
  // 按职位变动分段计算
  let totalBaseSalary = 0;
  let totalAttendanceDeductions = 0;
  let segments = [];
  
  // 按时间顺序排序职位变动记录
  const sortedChanges = [...positionChanges].sort((a, b) => 
    new Date(a.effective_date) - new Date(b.effective_date)
  );
  
  // 添加月初和月末边界
  const monthStart = new Date(parseInt(month.split('-')[0]), parseInt(month.split('-')[1]) - 1, 1);
  const monthEnd = new Date(parseInt(month.split('-')[0]), parseInt(month.split('-')[1]), 0);
  
  // 计算每个时间段的薪资
  let prevDate = monthStart;
  let prevPosition = employee.position;
  let prevSalary = employee.base_salary;
  
  for (const change of sortedChanges) {
    const changeDate = new Date(change.effective_date);
    
    // 只处理当月的变动
    if (changeDate < monthStart || changeDate > monthEnd) continue;
    
    // 计算这一段的天数
    const days = Math.floor((changeDate - prevDate) / (24 * 60 * 60 * 1000));
    const ratio = days / daysInMonth;
    
    // 这一段的基本工资
    const segmentBaseSalary = prevSalary * ratio;
    totalBaseSalary += segmentBaseSalary;
    
    // 这一段的考勤数据
    const segmentAttendance = attendanceData.filter(record => {
      const recordDate = new Date(record.date);
      return recordDate >= prevDate && recordDate < changeDate;
    });
    
    // 这一段的考勤扣款
    const segmentDeductions = calculateAttendanceDeductions(segmentAttendance, data.salaryGroup.rules);
    totalAttendanceDeductions += segmentDeductions;
    
    // 记录这一段的信息
    segments.push({
      startDate: prevDate,
      endDate: changeDate,
      position: prevPosition,
      baseSalary: segmentBaseSalary,
      attendanceDeductions: segmentDeductions,
      days,
      ratio
    });
    
    // 更新下一段的起始信息
    prevDate = changeDate;
    prevPosition = change.new_position;
    prevSalary = change.new_salary;
  }
  
  // 处理最后一段（最后一次变动到月末）
  if (prevDate < monthEnd) {
    const days = Math.floor((monthEnd - prevDate) / (24 * 60 * 60 * 1000)) + 1; // 包含最后一天
    const ratio = days / daysInMonth;
    
    // 这一段的基本工资
    const segmentBaseSalary = prevSalary * ratio;
    totalBaseSalary += segmentBaseSalary;
    
    // 这一段的考勤数据
    const segmentAttendance = attendanceData.filter(record => {
      const recordDate = new Date(record.date);
      return recordDate >= prevDate && recordDate <= monthEnd;
    });
    
    // 这一段的考勤扣款
    const segmentDeductions = calculateAttendanceDeductions(segmentAttendance, data.salaryGroup.rules);
    totalAttendanceDeductions += segmentDeductions;
    
    // 记录这一段的信息
    segments.push({
      startDate: prevDate,
      endDate: monthEnd,
      position: prevPosition,
      baseSalary: segmentBaseSalary,
      attendanceDeductions: segmentDeductions,
      days,
      ratio
    });
  }
  
  // 计算其他薪资项和总薪资
  const bonuses = (data.bonuses || []).reduce((sum, bonus) => sum + parseFloat(bonus.amount), 0);
  
  // 计算薪资项
  const salaryItems = {};
  (data.salaryGroup.items || []).forEach(item => {
    if (item.type === '收入') {
      salaryItems[item.name] = parseFloat(item.amount) || 0;
    } else if (item.type === '扣除') {
      salaryItems[item.name] = -(parseFloat(item.amount) || 0);
    }
  });
  
  // 计算总薪资
  const totalSalary = totalBaseSalary - totalAttendanceDeductions + bonuses + 
    Object.values(salaryItems).reduce((sum, amount) => sum + amount, 0);
  
  return {
    baseSalary: totalBaseSalary,
    attendanceDeductions: totalAttendanceDeductions,
    bonuses,
    salaryItems,
    totalSalary,
    segments,
    details: {
      employee,
      month,
      salaryGroup: data.salaryGroup
    }
  };
}

/**
 * 计算考勤扣款
 * @param {Array} attendanceData - 考勤数据
 * @param {Object} rules - 考勤规则
 * @returns {number} - 扣款金额
 */
function calculateAttendanceDeductions(attendanceData, rules) {
  if (!attendanceData || !rules) return 0;
  
  let totalDeduction = 0;
  let lateCount = 0;
  
  attendanceData.forEach(record => {
    switch (record.status) {
      case '迟到':
        lateCount++;
        // 超过免扣次数才扣款
        if (lateCount > (rules.lateFreeCount || 0)) {
          totalDeduction += parseFloat(rules.lateDeduction) || 0;
        }
        break;
      case '严重迟到':
        totalDeduction += parseFloat(rules.seriousLateDeduction) || 0;
        break;
      case '早退':
        totalDeduction += parseFloat(rules.earlyLeaveDeduction) || 0;
        break;
      case '缺卡':
        totalDeduction += parseFloat(rules.missedPunchDeduction) || 0;
        break;
      case '旷工':
        totalDeduction += parseFloat(rules.absentDeduction) || 0;
        break;
    }
  });
  
  return totalDeduction;
}

/**
 * 计算社保
 * 支持按实际工作天数比例计算
 * @param {Object} data - 社保计算所需数据
 * @returns {Object} - 计算结果
 */
function calculateSocialInsurance(data) {
  const { employee, month, socialBase, socialRates, entryExitRecords } = data;
  
  // 获取月份的天数
  const daysInMonth = new Date(parseInt(month.split('-')[0]), parseInt(month.split('-')[1]), 0).getDate();
  
  // 检查是否是中途入职或离职
  let workDays = daysInMonth;
  let workRatio = 1;
  
  if (entryExitRecords && entryExitRecords.length > 0) {
    // 查找当月的入职记录
    const entryRecord = entryExitRecords.find(record => {
      const recordDate = new Date(record.date);
      return record.type === 'entry' && 
             recordDate.getFullYear() === parseInt(month.split('-')[0]) && 
             recordDate.getMonth() + 1 === parseInt(month.split('-')[1]);
    });
    
    // 查找当月的离职记录
    const exitRecord = entryExitRecords.find(record => {
      const recordDate = new Date(record.date);
      return record.type === 'exit' && 
             recordDate.getFullYear() === parseInt(month.split('-')[0]) && 
             recordDate.getMonth() + 1 === parseInt(month.split('-')[1]);
    });
    
    // 计算实际工作天数
    if (entryRecord) {
      const entryDate = new Date(entryRecord.date);
      const dayOfMonth = entryDate.getDate();
      workDays -= (dayOfMonth - 1);
    }
    
    if (exitRecord) {
      const exitDate = new Date(exitRecord.date);
      const dayOfMonth = exitDate.getDate();
      workDays -= (daysInMonth - dayOfMonth);
    }
    
    // 计算工作天数比例
    workRatio = workDays / daysInMonth;
  }
  
  // 社保基数，可能有上下限
  const base = Math.min(
    Math.max(parseFloat(socialBase.min) || 0, parseFloat(employee.social_base) || parseFloat(employee.base_salary) || 0),
    parseFloat(socialBase.max) || Infinity
  );
  
  // 按比例计算各项社保
  const pension = base * parseFloat(socialRates.pension.employee) / 100 * workRatio;
  const medical = base * parseFloat(socialRates.medical.employee) / 100 * workRatio;
  const unemployment = base * parseFloat(socialRates.unemployment.employee) / 100 * workRatio;
  const housing = base * parseFloat(socialRates.housing.employee) / 100 * workRatio;
  
  // 公司缴纳部分
  const companyPension = base * parseFloat(socialRates.pension.company) / 100 * workRatio;
  const companyMedical = base * parseFloat(socialRates.medical.company) / 100 * workRatio;
  const companyUnemployment = base * parseFloat(socialRates.unemployment.company) / 100 * workRatio;
  const companyHousing = base * parseFloat(socialRates.housing.company) / 100 * workRatio;
  
  // 计算总金额
  const totalEmployee = pension + medical + unemployment + housing;
  const totalCompany = companyPension + companyMedical + companyUnemployment + companyHousing;
  
  return {
    base,
    workDays,
    workRatio,
    employee: {
      pension,
      medical,
      unemployment,
      housing,
      total: totalEmployee
    },
    company: {
      pension: companyPension,
      medical: companyMedical,
      unemployment: companyUnemployment,
      housing: companyHousing,
      total: totalCompany
    },
    details: {
      employee: data.employee,
      month,
      socialBase,
      socialRates
    }
  };
}

/**
 * 计算个人所得税
 * @param {Object} data - 个税计算所需数据
 * @returns {Object} - 计算结果
 */
function calculateIncomeTax(data) {
  const { salary, socialInsurance, taxBase, taxRates } = data;
  
  // 计算应纳税所得额
  const taxableIncome = salary - socialInsurance - parseFloat(taxBase.threshold);
  
  // 如果应纳税所得额小于等于0，则不需要缴税
  if (taxableIncome <= 0) {
    return {
      taxableIncome: 0,
      tax: 0,
      afterTax: salary - socialInsurance,
      details: data
    };
  }
  
  // 查找适用税率和速算扣除数
  let rate = 0;
  let quickDeduction = 0;
  
  for (const level of taxRates) {
    if (taxableIncome > level.min && (level.max === null || taxableIncome <= level.max)) {
      rate = parseFloat(level.rate) / 100;
      quickDeduction = parseFloat(level.quickDeduction);
      break;
    }
  }
  
  // 计算个税
  const tax = taxableIncome * rate - quickDeduction;
  
  // 税后收入
  const afterTax = salary - socialInsurance - tax;
  
  return {
    taxableIncome,
    tax,
    afterTax,
    details: {
      ...data,
      appliedRate: rate * 100,
      quickDeduction
    }
  };
}

/**
 * 处理考勤数据
 * @param {Object} data - 考勤数据处理所需数据
 * @returns {Object} - 处理结果
 */
function processAttendanceData(data) {
  const { attendanceRecords, rules } = data;
  
  // 处理考勤记录，计算状态
  const processedRecords = attendanceRecords.map(record => {
    // 深拷贝记录，避免修改原始数据
    const processed = { ...record };
    
    // 解析打卡时间
    const checkInTime = record.check_in ? new Date(`2000-01-01 ${record.check_in}`) : null;
    const checkOutTime = record.check_out ? new Date(`2000-01-01 ${record.check_out}`) : null;
    
    // 标准上下班时间
    const standardCheckIn = new Date(`2000-01-01 ${rules.standardCheckIn || '09:00:00'}`);
    const standardCheckOut = new Date(`2000-01-01 ${rules.standardCheckOut || '18:00:00'}`);
    
    // 判断考勤状态
    if (!checkInTime && !checkOutTime) {
      processed.status = '旷工';
    } else if (!checkInTime || !checkOutTime) {
      processed.status = '缺卡';
    } else if (checkInTime > standardCheckIn) {
      // 计算迟到分钟数
      const lateMinutes = Math.floor((checkInTime - standardCheckIn) / (60 * 1000));
      
      if (lateMinutes > (rules.seriousLateMinutes || 30)) {
        processed.status = '严重迟到';
      } else {
        processed.status = '迟到';
      }
    } else if (checkOutTime < standardCheckOut) {
      processed.status = '早退';
    } else {
      processed.status = '正常';
    }
    
    return processed;
  });
  
  return {
    processedRecords,
    summary: {
      total: processedRecords.length,
      normal: processedRecords.filter(r => r.status === '正常').length,
      late: processedRecords.filter(r => r.status === '迟到').length,
      seriousLate: processedRecords.filter(r => r.status === '严重迟到').length,
      earlyLeave: processedRecords.filter(r => r.status === '早退').length,
      missedPunch: processedRecords.filter(r => r.status === '缺卡').length,
      absent: processedRecords.filter(r => r.status === '旷工').length
    }
  };
}