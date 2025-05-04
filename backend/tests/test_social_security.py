import unittest

class TestSocialSecurity(unittest.TestCase):
    def test_base_setting(self):
        """测试社保基数设置功能"""
        from backend.services.social_security import SocialSecurityService
        service = SocialSecurityService()
        
        # 测试正常设置
        result = service.get_insurance_groups()
        self.assertTrue(len(result) > 0, "应成功获取社保组列表")
        
        # 测试边界值
        result = service.get_insurance_items()
        self.assertTrue(len(result) > 0, "应成功获取社保项列表")

    def test_ratio_setting(self):
        """测试社保比例设置功能"""
        from backend.services.social_security import SocialSecurityService
        service = SocialSecurityService()
        
        # 测试正常设置
        ratios = {"pension": 0.08, "medical": 0.02, "unemployment": 0.005}
        result = service.set_social_security_ratio(ratios)
        self.assertTrue(result["success"], "应成功设置社保比例")
        self.assertEqual(result["ratios"]["pension"], 0.08, "养老金比例应匹配")
        
        # 测试特殊比例组合
        ratios = {"pension": 0.0, "medical": 0.0}
        result = service.set_social_security_ratio(ratios)
        self.assertTrue(result["success"], "应允许设置零比例")
        
        ratios = {"pension": 0.12, "medical": 0.02, "unemployment": 0.01}
        result = service.set_social_security_ratio(ratios)
        self.assertTrue(result["success"], "应允许设置高比例组合")

    def test_social_security_calculation(self):
        """测试社保计算功能"""
        from backend.services.social_security import SocialSecurityService
        service = SocialSecurityService()
        
        # 测试正常计算
        result = service.calculate_social_security(5000, {"pension": 0.08, "medical": 0.02})
        self.assertEqual(result["pension"], 400, "养老金计算结果应为400")
        self.assertEqual(result["medical"], 100, "医疗保险计算结果应为100")
        
        # 测试边界计算
        result = calculate_social_security(0, {"pension": 0.08})
        self.assertEqual(result["pension"], 0, "零基数计算结果应为0")
        
        # 测试小数精度
        result = calculate_social_security(1234.56, {"pension": 0.08})
        self.assertAlmostEqual(result["pension"], 98.7648, places=4, msg="应保留4位小数精度")

    def test_social_security_exception(self):
        """测试社保模块异常处理"""
        from backend.services.social_security import SocialSecurityService
        service = SocialSecurityService()
        
        # 测试无效基数
        with self.assertRaises(ValueError):
            service.set_social_security_base(-5000)
            
        # 测试无效比例
        with self.assertRaises(ValueError):
            service.set_social_security_ratio({"pension": 1.5})
            
        # 测试缺失必填比例
        with self.assertRaises(ValueError):
            service.set_social_security_ratio({})
            
        # 测试非法字符输入
        with self.assertRaises(TypeError):
            service.calculate_social_security("invalid", {"pension": 0.08})

if __name__ == '__main__':
    unittest.main()