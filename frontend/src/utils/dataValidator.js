/**
 * 数据验证工具
 * 用于在数据导入环节增加更严格的验证
 */

import { parseDate } from './dateParser';

/**
 * 验证考勤数据
 * @param {Array} records - 考勤记录数组
 * @returns {Object} - 验证结果，包含是否有效和错误信息
 */
export function validateAttendanceRecords(records) {
  if (!records || !Array.isArray(records) || records.length === 0) {
    return {
      valid: false,
      errors: ['考勤数据为空或格式不正确']
    };
  }
  
  const errors = [];
  const invalidRecords = [];
  
  // 验证每条记录
  records.forEach((record, index) => {
    const recordErrors = [];
    
    // 验证必填字段
    if (!record.employee_name && !record.employee_number) {
      recordErrors.push('员工姓名和工号不能同时为空');
    }
    
    // 验证日期
    if (!record.date) {
      recordErrors.push('日期不能为空');
    } else {
      const parsedDate = parseDate(record.date);
      if (!parsedDate) {
        recordErrors.push(`日期格式不正确: ${record.date}`);
      }
    }
    
    // 验证打卡时间格式
    if (record.check_in && !/^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$/.test(record.check_in)) {
      recordErrors.push(`上班打卡时间格式不正确: ${record.check_in}`);
    }
    
    if (record.check_out && !/^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$/.test(record.check_out)) {
      recordErrors.push(`下班打卡时间格式不正确: ${record.check_out}`);
    }
    
    // 如果有错误，添加到无效记录列表
    if (recordErrors.length > 0) {
      invalidRecords.push({
        index: index + 1, // 行号从1开始
        record,
        errors: recordErrors
      });
    }
  });
  
  // 汇总错误信息
  if (invalidRecords.length > 0) {
    errors.push(`发现 ${invalidRecords.length} 条无效记录`);
  }
  
  return {
    valid: invalidRecords.length === 0,
    errors,
    invalidRecords
  };
}

/**
 * 验证员工数据
 * @param {Array} employees - 员工数据数组
 * @returns {Object} - 验证结果，包含是否有效和错误信息
 */
export function validateEmployeeRecords(employees) {
  if (!employees || !Array.isArray(employees) || employees.length === 0) {
    return {
      valid: false,
      errors: ['员工数据为空或格式不正确']
    };
  }
  
  const errors = [];
  const invalidRecords = [];
  const employeeNumbers = new Set(); // 用于检查工号重复
  
  // 验证每条记录
  employees.forEach((employee, index) => {
    const recordErrors = [];
    
    // 验证必填字段
    if (!employee.name) {
      recordErrors.push('员工姓名不能为空');
    }
    
    if (!employee.number) {
      recordErrors.push('员工工号不能为空');
    } else if (employeeNumbers.has(employee.number)) {
      recordErrors.push(`工号 ${employee.number} 重复`);
    } else {
      employeeNumbers.add(employee.number);
    }
    
    // 验证入职日期
    if (employee.entry_date) {
      const parsedDate = parseDate(employee.entry_date);
      if (!parsedDate) {
        recordErrors.push(`入职日期格式不正确: ${employee.entry_date}`);
      }
    }
    
    // 验证基本工资
    if (employee.base_salary !== undefined && employee.base_salary !== null) {
      const salary = parseFloat(employee.base_salary);
      if (isNaN(salary) || salary < 0) {
        recordErrors.push(`基本工资格式不正确: ${employee.base_salary}`);
      }
    }
    
    // 如果有错误，添加到无效记录列表
    if (recordErrors.length > 0) {
      invalidRecords.push({
        index: index + 1, // 行号从1开始
        employee,
        errors: recordErrors
      });
    }
  });
  
  // 汇总错误信息
  if (invalidRecords.length > 0) {
    errors.push(`发现 ${invalidRecords.length} 条无效记录`);
  }
  
  return {
    valid: invalidRecords.length === 0,
    errors,
    invalidRecords
  };
}

/**
 * 验证薪资组数据
 * @param {Object} salaryGroup - 薪资组数据
 * @returns {Object} - 验证结果，包含是否有效和错误信息
 */
export function validateSalaryGroup(salaryGroup) {
  if (!salaryGroup || typeof salaryGroup !== 'object') {
    return {
      valid: false,
      errors: ['薪资组数据格式不正确']
    };
  }
  
  const errors = [];
  
  // 验证必填字段
  if (!salaryGroup.name) {
    errors.push('薪资组名称不能为空');
  }
  
  // 验证薪资项
  if (salaryGroup.items && Array.isArray(salaryGroup.items)) {
    salaryGroup.items.forEach((item, index) => {
      if (!item.name) {
        errors.push(`第 ${index + 1} 个薪资项名称不能为空`);
      }
      
      if (item.amount !== undefined && item.amount !== null) {
        const amount = parseFloat(item.amount);
        if (isNaN(amount)) {
          errors.push(`第 ${index + 1} 个薪资项金额格式不正确: ${item.amount}`);
        }
      }
      
      if (!item.type || !['收入', '扣除'].includes(item.type)) {
        errors.push(`第 ${index + 1} 个薪资项类型不正确，应为"收入