const express = require('express');
const router = express.Router();

// 导入各个模块的路由
const employeeRoutes = require('./employee');
const attendanceRoutes = require('./attendance');
const salaryRoutes = require('./salary');
const analysisRoutes = require('./analysis');
const salaryGroupRoutes = require('./salary-group');
const positionLevelsRoutes = require('./position-levels');

// 注册路由
router.use('/employee', employeeRoutes);
router.use('/attendance', attendanceRoutes);
router.use('/salary', salaryRoutes);
router.use('/analysis', analysisRoutes);
router.use('/salary-groups', salaryGroupRoutes);
router.use('/position-levels', positionLevelsRoutes);

// 健康检查路由
router.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

router.get('/departments', (req, res) => {
  res.json({
    success: true,
    data: []
  });
});

module.exports = router;