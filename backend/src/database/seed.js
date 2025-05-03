const { sequelize } = require('../config/database');
const Employee = require('../models/employee');
const SalaryGroup = require('../models/salary-group');
const { logger } = require('../utils/logger');

async function seed() {
  try {
    // 薪资组测试数据
    const salaryGroups = [
      {
        name: '普通员工薪资组',
        description: '适用于普通员工的标准薪资组',
        base_salary: 5000,
        bonus_rate: 10,
        allowance: 500,
        overtime_rate: 1.5,
        late_deduction: 50,
        absence_deduction: 200,
        status: '启用'
      },
      {
        name: '管理层薪资组',
        description: '适用于管理层的薪资组',
        base_salary: 10000,
        bonus_rate: 20,
        allowance: 1000,
        overtime_rate: 2,
        late_deduction: 100,
        absence_deduction: 400,
        status: '启用'
      },
      {
        name: '技术专家薪资组',
        description: '适用于技术专家的薪资组',
        base_salary: 15000,
        bonus_rate: 15,
        allowance: 800,
        overtime_rate: 1.8,
        late_deduction: 80,
        absence_deduction: 300,
        status: '启用'
      }
    ];

    // 创建薪资组测试数据
    await SalaryGroup.bulkCreate(salaryGroups);

    // 员工测试数据
    const employees = [
      {
        name: '张三',
        employee_number: 'EMP001',
        id_card_number: '110101199001011234',
        department_level1: '技术部',
        department_level2: '开发组',
        position: '高级工程师',
        entry_date: '2020-01-01',
        status: '在职',
        salary_group: '1',
        social_security_group: '1',
        phone: '13800138000'
      },
      {
        name: '李四',
        employee_number: 'EMP002',
        id_card_number: '110101199001021234',
        department_level1: '人事部',
        department_level2: '招聘组',
        position: 'HR主管',
        entry_date: '2020-02-01',
        status: '在职',
        salary_group: '2',
        social_security_group: '1',
        phone: '13800138001'
      },
      {
        name: '王五',
        employee_number: 'EMP003',
        id_card_number: '110101199001031234',
        department_level1: '财务部',
        position: '财务经理',
        entry_date: '2020-03-01',
        status: '在职',
        salary_group: '2',
        social_security_group: '1',
        phone: '13800138002'
      }
    ];

    // 创建员工测试数据
    await Employee.bulkCreate(employees);
    
    console.log('测试数据添加成功。');
    process.exit(0);
  } catch (error) {
    console.error('添加测试数据失败:', error);
    process.exit(1);
  }
}

seed(); 