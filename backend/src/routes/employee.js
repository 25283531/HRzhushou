const express = require('express');
const router = express.Router();
const { authMiddleware, roleMiddleware } = require('../middleware/auth');
const EmployeeController = require('../controllers/employee');

// 获取所有员工
router.get('/', authMiddleware, roleMiddleware(['admin', 'hr']), EmployeeController.getEmployees);

// 获取单个员工
router.get('/:id', authMiddleware, roleMiddleware(['admin', 'hr']), EmployeeController.getEmployee);

// 创建员工
router.post('/', authMiddleware, roleMiddleware(['admin', 'hr']), EmployeeController.createEmployee);

// 更新员工信息
router.put('/:id', authMiddleware, roleMiddleware(['admin', 'hr']), EmployeeController.updateEmployee);

// 删除员工
router.delete('/:id', authMiddleware, roleMiddleware(['admin']), EmployeeController.deleteEmployee);

// 批量导入员工数据
router.post('/import', authMiddleware, roleMiddleware(['admin', 'hr']), EmployeeController.importEmployees);

router.get('/list', async (req, res) => {
  res.json({
    success: true,
    data: {
      items: [],
      total: 0
    }
  });
});

module.exports = router; 