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
      // 打印接收到的数据
      logger.info('Creating employee with data:', JSON.stringify(req.body, null, 2));

      // 数据类型转换和验证
      const employeeData = {
        name: req.body.name?.trim(),
        employee_number: req.body.employee_number?.trim(),
        id_card_number: req.body.id_card_number?.trim(),
        department_level1: req.body.department_level1?.trim(),
        department_level2: req.body.department_level2?.trim() || '',
        position: req.body.position?.trim() || '',
        entry_date: req.body.entry_date ? new Date(req.body.entry_date).toISOString().split('T')[0] : null,
        status: req.body.status || '在职',
        salary_group: req.body.salary_group ? Number(req.body.salary_group) : null,
        social_security_group: req.body.social_security_group ? Number(req.body.social_security_group) : null,
        bank_account: req.body.bank_account?.trim() || '',
        phone: req.body.phone?.trim() || '',
        remarks: req.body.remarks?.trim() || ''
      };

      // 打印转换后的数据
      logger.info('Formatted employee data:', JSON.stringify(employeeData, null, 2));

      // 验证必填字段
      const requiredFields = {
        name: '员工姓名',
        employee_number: '工号',
        id_card_number: '身份证号',
        department_level1: '一级部门',
        entry_date: '入职日期'
      };

      for (const [field, label] of Object.entries(requiredFields)) {
        if (!employeeData[field]) {
          return res.status(400).json({
            success: false,
            error: {
              status: 400,
              message: `${label}不能为空`,
              timestamp: new Date().toISOString()
            }
          });
        }
      }

      // 验证数字类型字段
      if (employeeData.salary_group !== null && !Number.isInteger(employeeData.salary_group)) {
        return res.status(400).json({
          success: false,
          error: {
            status: 400,
            message: '薪资组必须是整数',
            timestamp: new Date().toISOString()
          }
        });
      }

      if (employeeData.social_security_group !== null && !Number.isInteger(employeeData.social_security_group)) {
        return res.status(400).json({
          success: false,
          error: {
            status: 400,
            message: '社保组必须是整数',
            timestamp: new Date().toISOString()
          }
        });
      }

      const employee = await Employee.create(employeeData);
      res.status(201).json({
        success: true,
        data: employee
      });
    } catch (error) {
      logger.error('创建员工失败:', {
        error: error.message,
        stack: error.stack,
        data: req.body
      });

      // 检查是否是验证错误
      if (error.name === 'SequelizeValidationError') {
        return res.status(400).json({
          success: false,
          error: {
            status: 400,
            message: '数据验证失败',
            details: error.errors.map(err => ({
              field: err.path,
              message: err.message
            })),
            timestamp: new Date().toISOString()
          }
        });
      }

      // 检查是否是唯一约束错误
      if (error.name === 'SequelizeUniqueConstraintError') {
        return res.status(400).json({
          success: false,
          error: {
            status: 400,
            message: '数据已存在',
            details: error.errors.map(err => ({
              field: err.path,
              message: `${err.path} 已存在`
            })),
            timestamp: new Date().toISOString()
          }
        });
      }

      // 检查是否是数据类型错误
      if (error.message.includes('SQLITE_MISMATCH')) {
        return res.status(400).json({
          success: false,
          error: {
            status: 400,
            message: '数据类型错误',
            details: '请检查薪资组和社保组的数据类型',
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(500).json({
        success: false,
        error: {
          status: 500,
          message: error.message || '创建员工失败',
          timestamp: new Date().toISOString()
        }
      });
    }
  }

  // 更新员工信息
  static async updateEmployee(req, res, next) {
    try {
      // 打印接收到的数据
      logger.info('Updating employee with data:', JSON.stringify(req.body, null, 2));

      const employee = await Employee.findByPk(req.params.id);
      if (!employee) {
        return res.status(404).json({
          success: false,
          error: {
            status: 404,
            message: '员工不存在',
            timestamp: new Date().toISOString()
          }
        });
      }

      // 数据类型转换和验证
      const employeeData = {
        ...req.body,
        salary_group: req.body.salary_group ? parseInt(req.body.salary_group) : null,
        social_security_group: req.body.social_security_group ? parseInt(req.body.social_security_group) : null,
        entry_date: req.body.entry_date ? new Date(req.body.entry_date).toISOString().split('T')[0] : null
      };

      // 打印转换后的数据
      logger.info('Formatted employee data:', JSON.stringify(employeeData, null, 2));

      await employee.update(employeeData);
      res.json({
        success: true,
        data: employee
      });
    } catch (error) {
      logger.error('更新员工信息失败:', {
        error: error.message,
        stack: error.stack,
        data: req.body
      });

      // 检查是否是验证错误
      if (error.name === 'SequelizeValidationError') {
        return res.status(400).json({
          success: false,
          error: {
            status: 400,
            message: '数据验证失败',
            details: error.errors.map(err => ({
              field: err.path,
              message: err.message
            })),
            timestamp: new Date().toISOString()
          }
        });
      }

      // 检查是否是唯一约束错误
      if (error.name === 'SequelizeUniqueConstraintError') {
        return res.status(400).json({
          success: false,
          error: {
            status: 400,
            message: '数据已存在',
            details: error.errors.map(err => ({
              field: err.path,
              message: `${err.path} 已存在`
            })),
            timestamp: new Date().toISOString()
          }
        });
      }

      res.status(500).json({
        success: false,
        error: {
          status: 500,
          message: error.message || '更新员工信息失败',
          timestamp: new Date().toISOString()
        }
      });
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