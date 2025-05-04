const express = require('express');
const router = express.Router();

// 职级类型API
router.get('/types', (req, res) => {
  res.json({
    success: true,
    data: [
      { id: 1, name: '技术类', description: '技术研发相关职位' },
      { id: 2, name: '管理类', description: '管理岗位' },
      { id: 3, name: '销售类', description: '销售相关职位' }
    ]
  });
});

router.post('/types', (req, res) => {
  // 这里应该有创建职级类型的逻辑
  res.json({
    success: true,
    data: { id: 4, ...req.body }
  });
});

router.put('/types/:id', (req, res) => {
  // 这里应该有更新职级类型的逻辑
  res.json({
    success: true,
    data: { id: parseInt(req.params.id), ...req.body }
  });
});

router.delete('/types/:id', (req, res) => {
  // 这里应该有删除职级类型的逻辑
  res.json({
    success: true,
    message: '删除成功'
  });
});

// 职级API
router.get('/levels', (req, res) => {
  const typeId = req.query.type_id;
  // 这里应该根据typeId筛选职级
  res.json({
    success: true,
    data: [
      { id: 1, name: 'P1', type_id: 1, salary_range: '8k-12k', description: '初级工程师' },
      { id: 2, name: 'P2', type_id: 1, salary_range: '12k-18k', description: '中级工程师' },
      { id: 3, name: 'P3', type_id: 1, salary_range: '18k-25k', description: '高级工程师' },
      { id: 4, name: 'M1', type_id: 2, salary_range: '20k-30k', description: '初级经理' },
      { id: 5, name: 'M2', type_id: 2, salary_range: '30k-45k', description: '中级经理' }
    ].filter(item => !typeId || item.type_id === parseInt(typeId))
  });
});

router.post('/levels', (req, res) => {
  // 这里应该有创建职级的逻辑
  res.json({
    success: true,
    data: { id: 6, ...req.body }
  });
});

router.put('/levels/:id', (req, res) => {
  // 这里应该有更新职级的逻辑
  res.json({
    success: true,
    data: { id: parseInt(req.params.id), ...req.body }
  });
});

router.delete('/levels/:id', (req, res) => {
  // 这里应该有删除职级的逻辑
  res.json({
    success: true,
    message: '删除成功'
  });
});

module.exports = router;