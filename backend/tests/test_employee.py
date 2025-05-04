import unittest

class TestEmployee(unittest.TestCase):
    def test_add_employee(self):
        """测试添加新员工功能"""
        from backend.models.employee import add_employee
        
        # 测试正常添加
        employee_data = {
            "name": "张三",
            "employee_id": "E001",
            "department": "HR",
            "position": "HR Manager"
        }
        result = add_employee(employee_data)
        self.assertTrue(result["success"], "应成功添加员工")
        self.assertEqual(result["employee_id"], "E001", "员工ID应匹配")

    def test_edit_employee(self):
        """测试编辑员工信息功能"""
        from backend.models.employee import add_employee, edit_employee
        
        # 先添加测试员工
        employee_data = {"name": "李四", "employee_id": "E002"}
        add_employee(employee_data)
        
        # 测试编辑
        updated_data = {"name": "李四(更新)", "department": "IT"}
        result = edit_employee("E002", updated_data)
        self.assertTrue(result["success"], "应成功编辑员工")
        self.assertEqual(result["name"], "李四(更新)", "姓名应更新")

    def test_import_employee(self):
        """测试批量导入员工数据功能"""
        from backend.models.employee import import_employees
        
        # 测试正常导入
        employees = [
            {"name": "王五", "employee_id": "E003"},
            {"name": "赵六", "employee_id": "E004"}
        ]
        result = import_employees(employees)
        self.assertEqual(result["success_count"], 2, "应成功导入2条记录")
        self.assertEqual(len(result["failed"]), 0, "不应有失败记录")

    def test_employee_exception(self):
        """测试员工模块异常处理"""
        from backend.models.employee import add_employee
        
        # 测试重复员工ID
        with self.assertRaises(ValueError):
            add_employee({"name": "测试", "employee_id": "E001"})
            add_employee({"name": "测试", "employee_id": "E001"})
            
        # 测试无效数据
        with self.assertRaises(ValueError):
            add_employee({"name": "", "employee_id": "E005"})

if __name__ == '__main__':
    unittest.main()