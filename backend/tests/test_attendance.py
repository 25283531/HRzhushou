import unittest

class TestAttendance(unittest.TestCase):
    def test_import_attendance_data(self):
        """测试考勤数据导入功能"""
        from backend.models.attendance import import_attendance_data
        
        # 模拟考勤数据
        test_data = [
            {"employee_id": "001", "date": "2023-01-01", "status": "present", "hours": 8},
            {"employee_id": "002", "date": "2023-01-01", "status": "absent", "hours": 0}
        ]
        
        # 导入数据
        result = import_attendance_data(test_data)
        
        # 验证导入结果
        self.assertEqual(len(result["success"]), 2, "应成功导入2条记录")
        self.assertEqual(len(result["failed"]), 0, "不应有失败记录")
        self.assertTrue(result["total"] == 2, "总记录数应为2")

    def test_attendance_filter(self):
        """测试考勤数据筛选功能"""
        from backend.models.attendance import filter_attendance
        
        # 准备测试数据
        all_data = [
            {"employee_id": "001", "date": "2023-01-01", "status": "present", "department": "HR"},
            {"employee_id": "002", "date": "2023-01-01", "status": "absent", "department": "IT"}
        ]
        
        # 测试部门筛选
        hr_result = filter_attendance(all_data, {"department": "HR"})
        self.assertEqual(len(hr_result), 1, "应筛选出1条HR部门记录")
        
        # 测试状态筛选
        absent_result = filter_attendance(all_data, {"status": "absent"})
        self.assertEqual(len(absent_result), 1, "应筛选出1条缺勤记录")

    def test_attendance_exception(self):
        """测试考勤异常处理"""
        from backend.models.attendance import import_attendance_data
        
        # 测试无效日期格式
        invalid_date_data = [{"employee_id": "001", "date": "2023/01/01", "status": "present"}]
        with self.assertRaises(ValueError):
            import_attendance_data(invalid_date_data)
            
        # 测试无效工作时长
        invalid_hours_data = [{"employee_id": "001", "date": "2023-01-01", "hours": -1}]
        with self.assertRaises(ValueError):
            import_attendance_data(invalid_hours_data)

if __name__ == '__main__':
    unittest.main()