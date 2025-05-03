const { Salary, Employee } = require('../models');
const { logger } = require('../utils/logger');

class SalaryController {
  // 获取所有薪资记录
  static async getSalaries(req, res) {
    try {
      const salaries = await Salary.findAll({
        include: [Employee]
      });
      res.json(salaries);
    } catch (error) {
      logger.error('获取薪资记录失败:', error);
      res.status(500).json({ error: '获取薪资记录失败' });
    }
  }

  // 获取单个员工薪资记录
  static async getSalary(req, res) {
    try {
      const salary = await Salary.findByPk(req.params.id, {
        include: [Employee]
      });
      if (!salary) {
        return res.status(404).json({ error: '薪资记录不存在' });
      }
      res.json(salary);
    } catch (error) {
      logger.error('获取薪资记录失败:', error);
      res.status(500).json({ error: '获取薪资记录失败' });
    }
  }

  // 创建薪资记录
  static async createSalary(req, res) {
    try {
      const salary = await Salary.create(req.body);
      res.status(201).json(salary);
    } catch (error) {
      logger.error('创建薪资记录失败:', error);
      res.status(500).json({ error: '创建薪资记录失败' });
    }
  }

  // 更新薪资记录
  static async updateSalary(req, res) {
    try {
      const salary = await Salary.findByPk(req.params.id);
      if (!salary) {
        return res.status(404).json({ error: '薪资记录不存在' });
      }
      await salary.update(req.body);
      res.json(salary);
    } catch (error) {
      logger.error('更新薪资记录失败:', error);
      res.status(500).json({ error: '更新薪资记录失败' });
    }
  }

  // 计算薪资
  static async calculateSalary(req, res) {
    try {
      const { employeeId, month } = req.body;
      const employee = await Employee.findByPk(employeeId);
      if (!employee) {
        return res.status(404).json({ error: '员工不存在' });
      }

      // 计算基本工资
      const baseSalary = employee.baseSalary;

      // 计算奖金（示例：根据考勤情况计算）
      const bonus = 0; // 这里需要根据实际业务逻辑计算

      // 计算扣款（示例：根据考勤情况计算）
      const deduction = 0; // 这里需要根据实际业务逻辑计算

      // 计算个税（示例：简化计算）
      const taxableIncome = baseSalary + bonus - deduction;
      const tax = Math.max(0, (taxableIncome - 5000) * 0.1);

      // 计算实发工资
      const netSalary = baseSalary + bonus - deduction - tax;

      const salary = await Salary.create({
        employeeId,
        month,
        baseSalary,
        bonus,
        deduction,
        tax,
        netSalary
      });

      res.status(201).json(salary);
    } catch (error) {
      logger.error('计算薪资失败:', error);
      res.status(500).json({ error: '计算薪资失败' });
    }
  }

  // 批量导入薪资数据
  static async importSalaries(req, res) {
    try {
      const salaries = req.body;
      const result = await Salary.bulkCreate(salaries);
      res.status(201).json(result);
    } catch (error) {
      logger.error('导入薪资数据失败:', error);
      res.status(500).json({ error: '导入薪资数据失败' });
    }
  }
}

module.exports = SalaryController; 