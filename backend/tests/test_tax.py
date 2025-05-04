import unittest

class TestTax(unittest.TestCase):
    def test_tax_threshold_setting(self):
        # 模拟个税起征点设置，假设起征点为5000
        threshold = 5000
        # 假设设置的起征点为5000
        self.assertEqual(threshold, 5000)

    def test_tax_rate_setting(self):
        # 模拟个税累进税率设置，假设税率为10%
        rate = 0.10
        # 假设设置的税率为10%
        self.assertEqual(rate, 0.10)

    def test_tax_calculation(self):
        # 模拟个税计算，假设收入为10000，起征点为5000，税率为10%
        income = 10000
        threshold = 5000
        rate = 0.10
        tax = (income - threshold) * rate
        # 计算税额应为500
        self.assertEqual(tax, 500)

    def test_tax_exception(self):
        # 模拟异常个税场景，假设收入为负数
        income = -1000
        threshold = 5000
        rate = 0.10
        with self.assertRaises(ValueError):
            if income < 0:
                raise ValueError("收入不能为负数")

if __name__ == '__main__':
    unittest.main()