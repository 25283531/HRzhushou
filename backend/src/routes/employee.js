const express = require('express');
const router = express.Router();
const { authMiddleware, roleMiddleware } = require('../middleware/auth');
const EmployeeController = require('../controllers/employee');
const Employee = require('../models/employee');
const { Op } = require('sequelize');

// 获取员工列表（带分页和搜索）
router.get('/list', async (req, res) => {
  try {
    const { page = 1, page_size = 10, name = '', employee_number = '', department = '' } = req.query;
    
    // 构建查询条件
    const where = {};
    if (name) where.name = { [Op.like]: `%${name}%` };
    if (employee_number) where.employee_number = { [Op.like]: `%${employee_number}%` };
    if (department) where.department_level1 = { [Op.like]: `%${department}%` };
    
    // 查询数据
    const { count, rows } = await Employee.findAndCountAll({
      where,
      limit: parseInt(page_size),
      offset: (parseInt(page) - 1) * parseInt(page_size),
      order: [['id', 'DESC']]
    });
    
    res.json({
      success: true,
      data: {
        items: rows,
        total: count
      }
    });
  } catch (error) {
    console.error('获取员工列表失败:', error);
    res.status(500).json({
      success: false,
      error: '获取员工列表失败'
    });
  }
});

// 获取所有员工
router.get('/', EmployeeController.getEmployees);

// 获取单个员工
router.get('/:id', EmployeeController.getEmployee);

// 创建员工
router.post('/', EmployeeController.createEmployee);

// 更新员工信息
router.put('/:id', EmployeeController.updateEmployee);

// 删除员工
router.delete('/:id', EmployeeController.deleteEmployee);

// 批量导入员工数据
router.post('/import', EmployeeController.importEmployees);

module.exports = router; 