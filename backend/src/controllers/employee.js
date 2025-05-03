const { Employee } = require('../models');
const { logger } = require('../utils/logger');

class EmployeeController {
  // 获取所有员工
  static async getEmployees(req, res, next) {
    try {
      const employees = await Employee.findAll();
      res.json(employees);
    } catch (error) {
      logger.error('获取员工列表失败:', error);
      next(error);
    }
  }

  // 获取单个员工
  static async getEmployee(req, res, next) {
    try {
      const employee = await Employee.findByPk(req.params.id);
      if (!employee) {
        return res.status(404).json({ error: '员工不存在' });
      }
      res.json(employee);
    } catch (error) {
      logger.error('获取员工信息失败:', error);
      next(error);
    }
  }

  // 创建员工
  static async createEmployee(req, res, next) {
    try {
      const employee = await Employee.create(req.body);
      res.status(201).json(employee);
    } catch (error) {
      logger.error('创建员工失败:', error);
      next(error);
    }
  }

  // 更新员工信息
  static async updateEmployee(req, res, next) {
    try {
      const employee = await Employee.findByPk(req.params.id);
      if (!employee) {
        return res.status(404).json({ error: '员工不存在' });
      }
      await employee.update(req.body);
      res.json(employee);
    } catch (error) {
      logger.error('更新员工信息失败:', error);
      next(error);
    }
  }

  // 删除员工
  static async deleteEmployee(req, res, next) {
    try {
      const employee = await Employee.findByPk(req.params.id);
      if (!employee) {
        return res.status(404).json({ error: '员工不存在' });
      }
      await employee.destroy();
      res.status(204).send();
    } catch (error) {
      logger.error('删除员工失败:', error);
      next(error);
    }
  }

  // 批量导入员工数据
  static async importEmployees(req, res, next) {
    try {
      const employees = req.body;
      const result = await Employee.bulkCreate(employees);
      res.status(201).json(result);
    } catch (error) {
      logger.error('导入员工数据失败:', error);
      next(error);
    }
  }
}

module.exports = EmployeeController; 