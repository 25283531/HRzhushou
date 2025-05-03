const { Employee, Attendance } = require('../models');
const { logger } = require('../utils/logger');

const seed = async () => {
  try {
    // 创建测试员工数据
    const employees = [
      {
        name: '张三',
        department: '技术部',
        position: '工程师',
        baseSalary: 10000,
        joinDate: new Date('2023-01-01'),
        status: '在职',
        contact: '13800138000',
        email: 'zhangsan@example.com'
      },
      {
        name: '李四',
        department: '市场部',
        position: '经理',
        baseSalary: 15000,
        joinDate: new Date('2023-02-01'),
        status: '在职',
        contact: '13900139000',
        email: 'lisi@example.com'
      },
      {
        name: '王五',
        department: '人事部',
        position: '主管',
        baseSalary: 12000,
        joinDate: new Date('2023-03-01'),
        status: '在职',
        contact: '13700137000',
        email: 'wangwu@example.com'
      }
    ];

    // 批量创建员工
    await Employee.bulkCreate(employees);
    logger.info('数据库种子数据创建成功');
  } catch (error) {
    logger.error('数据库种子数据创建失败:', error);
    process.exit(1);
  }
};

seed(); 