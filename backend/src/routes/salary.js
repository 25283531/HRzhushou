const express = require('express');
const router = express.Router();
const { authMiddleware, roleMiddleware } = require('../middleware/auth');
const SalaryController = require('../controllers/salary');

// 获取薪资记录
router.get('/', authMiddleware, roleMiddleware(['admin', 'hr']), SalaryController.getSalaries);

// 获取单个员工薪资记录
router.get('/:id', authMiddleware, roleMiddleware(['admin', 'hr']), SalaryController.getSalary);

// 创建薪资记录
router.post('/', authMiddleware, roleMiddleware(['admin', 'hr']), SalaryController.createSalary);

// 更新薪资记录
router.put('/:id', authMiddleware, roleMiddleware(['admin', 'hr']), SalaryController.updateSalary);

// 计算薪资
router.post('/calculate', authMiddleware, roleMiddleware(['admin', 'hr']), SalaryController.calculateSalary);

// 批量导入薪资数据
router.post('/import', authMiddleware, roleMiddleware(['admin', 'hr']), SalaryController.importSalaries);

// 获取薪资组列表
router.get('/salary-groups', async (req, res) => {
  res.json({
    success: true,
    data: []
  });
});

// 获取薪资历史
router.get('/history', async (req, res) => {
  res.json({
    success: true,
    data: {
      items: [],
      total: 0
    }
  });
});

module.exports = router; 