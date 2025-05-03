const { Attendance, Employee } = require('../models');
const { logger } = require('../utils/logger');
const moment = require('moment');

class AttendanceController {
  // 获取考勤记录
  static async getAttendance(req, res, next) {
    try {
      const { employeeId, startDate, endDate } = req.query;
      const where = {};

      if (employeeId) {
        where.employeeId = employeeId;
      }

      if (startDate && endDate) {
        where.date = {
          [Op.between]: [startDate, endDate]
        };
      }

      const attendance = await Attendance.findAll({
        where,
        include: [{
          model: Employee,
          attributes: ['name', 'department']
        }]
      });

      res.json(attendance);
    } catch (error) {
      logger.error('获取考勤记录失败:', error);
      next(error);
    }
  }

  // 记录考勤
  static async recordAttendance(req, res, next) {
    try {
      const { employeeId, date, checkIn, checkOut, status, remark } = req.body;

      // 检查员工是否存在
      const employee = await Employee.findByPk(employeeId);
      if (!employee) {
        return res.status(404).json({ error: '员工不存在' });
      }

      // 检查是否已存在当天的考勤记录
      const existingRecord = await Attendance.findOne({
        where: {
          employeeId,
          date
        }
      });

      if (existingRecord) {
        return res.status(400).json({ error: '该日期已有考勤记录' });
      }

      const attendance = await Attendance.create({
        employeeId,
        date,
        checkIn,
        checkOut,
        status,
        remark
      });

      res.status(201).json(attendance);
    } catch (error) {
      logger.error('记录考勤失败:', error);
      next(error);
    }
  }

  // 更新考勤记录
  static async updateAttendance(req, res, next) {
    try {
      const { id } = req.params;
      const { checkIn, checkOut, status, remark } = req.body;

      const attendance = await Attendance.findByPk(id);
      if (!attendance) {
        return res.status(404).json({ error: '考勤记录不存在' });
      }

      await attendance.update({
        checkIn,
        checkOut,
        status,
        remark
      });

      res.json(attendance);
    } catch (error) {
      logger.error('更新考勤记录失败:', error);
      next(error);
    }
  }

  // 批量导入考勤数据
  static async importAttendance(req, res, next) {
    try {
      const { data } = req.body;
      const results = [];

      for (const record of data) {
        const { employeeId, date, checkIn, checkOut, status, remark } = record;

        // 检查员工是否存在
        const employee = await Employee.findByPk(employeeId);
        if (!employee) {
          results.push({
            employeeId,
            date,
            status: '失败',
            error: '员工不存在'
          });
          continue;
        }

        try {
          const attendance = await Attendance.create({
            employeeId,
            date,
            checkIn,
            checkOut,
            status,
            remark
          });
          results.push({
            employeeId,
            date,
            status: '成功'
          });
        } catch (error) {
          results.push({
            employeeId,
            date,
            status: '失败',
            error: error.message
          });
        }
      }

      res.json({ results });
    } catch (error) {
      logger.error('导入考勤数据失败:', error);
      next(error);
    }
  }
}

module.exports = AttendanceController; 