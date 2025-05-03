const express = require('express');
const router = express.Router();
const SalaryGroup = require('../models/salary-group');
const { Op } = require('sequelize');

// 获取薪资组列表
router.get('/', async (req, res) => {
  try {
    const { page = 1, page_size = 10, name = '', status = '' } = req.query;
    
    // 构建查询条件
    const where = {};
    if (name) where.name = { [Op.like]: `%${name}%` };
    if (status) where.status = status;
    
    // 查询数据
    const { count, rows } = await SalaryGroup.findAndCountAll({
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
    console.error('获取薪资组列表失败:', error);
    res.status(500).json({
      success: false,
      error: '获取薪资组列表失败'
    });
  }
});

// 获取单个薪资组
router.get('/:id', async (req, res) => {
  try {
    const salaryGroup = await SalaryGroup.findByPk(req.params.id);
    if (!salaryGroup) {
      return res.status(404).json({
        success: false,
        error: '薪资组不存在'
      });
    }
    res.json({
      success: true,
      data: salaryGroup
    });
  } catch (error) {
    console.error('获取薪资组详情失败:', error);
    res.status(500).json({
      success: false,
      error: '获取薪资组详情失败'
    });
  }
});

// 创建薪资组
router.post('/', async (req, res) => {
  try {
    const salaryGroup = await SalaryGroup.create(req.body);
    res.json({
      success: true,
      data: salaryGroup
    });
  } catch (error) {
    console.error('创建薪资组失败:', error);
    res.status(500).json({
      success: false,
      error: '创建薪资组失败'
    });
  }
});

// 更新薪资组
router.put('/:id', async (req, res) => {
  try {
    const salaryGroup = await SalaryGroup.findByPk(req.params.id);
    if (!salaryGroup) {
      return res.status(404).json({
        success: false,
        error: '薪资组不存在'
      });
    }
    await salaryGroup.update(req.body);
    res.json({
      success: true,
      data: salaryGroup
    });
  } catch (error) {
    console.error('更新薪资组失败:', error);
    res.status(500).json({
      success: false,
      error: '更新薪资组失败'
    });
  }
});

// 删除薪资组
router.delete('/:id', async (req, res) => {
  try {
    const salaryGroup = await SalaryGroup.findByPk(req.params.id);
    if (!salaryGroup) {
      return res.status(404).json({
        success: false,
        error: '薪资组不存在'
      });
    }
    await salaryGroup.destroy();
    res.json({
      success: true,
      message: '薪资组删除成功'
    });
  } catch (error) {
    console.error('删除薪资组失败:', error);
    res.status(500).json({
      success: false,
      error: '删除薪资组失败'
    });
  }
});

module.exports = router; 