const express = require('express');
const router = express.Router();
const { authMiddleware, roleMiddleware } = require('../middleware/auth');
const AttendanceController = require('../controllers/attendance');

// 获取考勤记录
router.get('/', authMiddleware, roleMiddleware(['admin', 'hr']), AttendanceController.getAttendance);

// 记录考勤
router.post('/', authMiddleware, roleMiddleware(['admin', 'hr']), AttendanceController.recordAttendance);

// 更新考勤记录
router.put('/:id', authMiddleware, roleMiddleware(['admin', 'hr']), AttendanceController.updateAttendance);

// 批量导入考勤数据
router.post('/import', authMiddleware, roleMiddleware(['admin', 'hr']), AttendanceController.importAttendance);

// 获取考勤数据分页列表
router.get('/list', async (req, res) => {
  // 解析分页参数
  const { month, page = 1, page_size = 10 } = req.query;
  // TODO: 实际应从数据库查询
  // 这里返回空数据结构，前端不会报错
  res.json({
    success: true,
    data: {
      items: [], // 实际数据
      total: 0   // 总数
    }
  });
});

module.exports = router;