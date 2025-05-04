import unittest

class TestSalary(unittest.TestCase):
    def test_basic_salary_calculation(self):
        """测试基本薪资计算功能"""
        from backend.models.salary import calculate_basic_salary
        
        # 测试正常计算
        result = calculate_basic_salary(10000, 5000)
        self.assertEqual(result, 5000, "基本薪资计算结果应为5000")
        
        # 测试边界值
        result = calculate_basic_salary(5000, 5000)
        self.assertEqual(result, 0, "起征点边界值计算结果应为0")

    def test_attendance_deduction(self):
        """测试考勤扣款功能"""
        from backend.models.salary import calculate_attendance_deduction
        
        # 测试正常扣款
        result = calculate_attendance_deduction(5000, 2)
        self.assertEqual(result, 200, "应扣款200元")
        
        # 测试无扣款
        result = calculate_attendance_deduction(5000, 0)
        self.assertEqual(result, 0, "无缺勤不应扣款")

    def test_bonus_calculation(self):
        """测试奖金计算功能"""
        from backend.models.salary import calculate_bonus
        
        # 测试正常奖金
        result = calculate_bonus(5000, 0.1)
        self.assertEqual(result, 500, "奖金计算结果应为500")
        
        # 测试零奖金
        result = calculate_bonus(5000, 0)
        self.assertEqual(result, 0, "零奖金率计算结果应为0")

    def test_salary_exception(self):
        """测试薪资模块异常处理"""
        from backend.models.salary import calculate_basic_salary
        
        # 测试负薪资
        with self.assertRaises(ValueError):
            calculate_basic_salary(-1000, 5000)
            
        # 测试无效起征点
        with self.assertRaises(ValueError):
            calculate_basic_salary(10000, -5000)

if __name__ == '__main__':
    unittest.main()