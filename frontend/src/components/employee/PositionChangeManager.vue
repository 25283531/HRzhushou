<template>
  <div class="position-change-manager">
    <el-card class="position-change-card">
      <template #header>
        <div class="card-header">
          <h3>职位变动管理</h3>
          <el-button type="primary" size="small" @click="showAddDialog">
            <el-icon><Plus /></el-icon> 添加职位变动记录
          </el-button>
        </div>
      </template>
      
      <!-- 职位变动记录表格 -->
      <el-table
        v-loading="loading"
        :data="positionChanges"
        border
        style="width: 100%">
        <el-table-column prop="employee_name" label="员工姓名" width="120" />
        <el-table-column prop="employee_number" label="工号" width="100" />
        <el-table-column prop="old_position" label="原职位" width="120" />
        <el-table-column prop="new_position" label="新职位" width="120" />
        <el-table-column prop="old_salary" label="原基本工资" width="120">
          <template #default="scope">
            {{ scope.row.old_salary.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="new_salary" label="新基本工资" width="120">
          <template #default="scope">
            {{ scope.row.new_salary.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="effective_date" label="生效日期" width="120" />
        <el-table-column prop="remarks" label="备注" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 添加/编辑职位变动对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑职位变动记录' : '添加职位变动记录'"
      width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="员工" prop="employee_id">
          <el-select
            v-model="form.employee_id"
            filterable
            placeholder="请选择员工"
            style="width: 100%"
            @change="handleEmployeeChange">
            <el-option
              v-for="item in employees"
              :key="item.id"
              :label="`${item.name} (${item.number})`"
              :value="item.id">
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="原职位" prop="old_position">
          <el-input v-model="form.old_position" disabled></el-input>
        </el-form-item>
        
        <el-form-item label="原基本工资" prop="old_salary">
          <el-input-number v-model="form.old_salary" :precision="2" :step="100" :min="0" disabled style="width: 100%"></el-input-number>
        </el-form-item>
        
        <el-form-item label="新职位" prop="new_position">
          <el-input v-model="form.new_position" placeholder="请输入新职位"></el-input>
        </el-form-item>
        
        <el-form-item label="新基本工资" prop="new_salary">
          <el-input-number v-model="form.new_salary" :precision="2" :step="100" :min="0" style="width: 100%"></el-input-number>
        </el-form-item>
        
        <el-form-item label="生效日期" prop="effective_date">
          <el-date-picker
            v-model="form.effective_date"
            type="date"
            placeholder="选择生效日期"
            style="width: 100%"
            value-format="YYYY-MM-DD">
          </el-date-picker>
        </el-form-item>
        
        <el-form-item label="备注" prop="remarks">
          <el-input
            v-model="form.remarks"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息">
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { formatDate } from '../../utils/dateParser'
import backupService from '../../utils/backupService'

// 数据加载状态
const loading = ref(false)

// 职位变动记录
const positionChanges = ref([])

// 员工列表
const employees = ref([])

// 对话框显示状态
const dialogVisible = ref(false)
const isEdit = ref(false)

// 表单引用
const formRef = ref(null)

// 表单数据
const form = reactive({
  id: null,
  employee_id: '',
  employee_name: '',
  employee_number: '',
  old_position: '',
  new_position: '',
  old_salary: 0,
  new_salary: 0,
  effective_date: '',
  remarks: ''
})

// 表单验证规则
const rules = {
  employee_id: [
    { required: true, message: '请选择员工', trigger: 'change' }
  ],
  new_position: [
    { required: true, message: '请输入新职位', trigger: 'blur' }
  ],
  new_salary: [
    { required: true, message: '请输入新基本工资', trigger: 'blur' }
  ],
  effective_date: [
    { required: true, message: '请选择生效日期', trigger: 'change' }
  ]
}

// 生命周期钩子
onMounted(() => {
  fetchPositionChanges()
  fetchEmployees()
})

// 获取职位变动记录
const fetchPositionChanges = () => {
  loading.value = true
  
  // 这里应该是实际的API调用
  // 示例代码
  setTimeout(() => {
    positionChanges.value = [
      {
        id: 1,
        employee_id: 1,
        employee_name: '张三',
        employee_number: '001',
        old_position: '工程师',
        new_position: '高级工程师',
        old_salary: 10000,
        new_salary: 15000,
        effective_date: '2023-11-15',
        remarks: '晋升'
      }
    ]
    loading.value = false
  }, 500)
}

// 获取员工列表
const fetchEmployees = () => {
  // 这里应该是实际的API调用
  // 示例代码
  setTimeout(() => {
    employees.value = [
      {
        id: 1,
        name: '张三',
        number: '001',
        position: '高级工程师',
        base_salary: 15000
      },
      {
        id: 2,
        name: '李四',
        number: '002',
        position: '产品经理',
        base_salary: 18000
      }
    ]
  }, 500)
}

// 显示添加对话框
const showAddDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 处理编辑
const handleEdit = (row) => {
  isEdit.value = true
  resetForm()
  
  // 填充表单数据
  Object.keys(form).forEach(key => {
    if (key in row) {
      form[key] = row[key]
    }
  })
  
  dialogVisible.value = true
}

// 处理删除
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除 ${row.employee_name} 的职位变动记录吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    // 这里应该是实际的API调用
    // 示例代码
    setTimeout(() => {
      positionChanges.value = positionChanges.value.filter(item => item.id !== row.id)
      ElMessage.success('删除成功')
      
      // 创建数据备份
      backupService.createBackup()
    }, 500)
  }).catch(() => {
    // 取消删除
  })
}

// 处理员工选择变更
const handleEmployeeChange = (employeeId) => {
  const employee = employees.value.find(item => item.id === employeeId)
  if (employee) {
    form.employee_name = employee.name
    form.employee_number = employee.number
    form.old_position = employee.position
    form.old_salary = employee.base_salary
    
    // 默认新职位和新工资与旧的相同
    if (!isEdit.value) {
      form.new_position = employee.position
      form.new_salary = employee.base_salary
    }
  }
}

// 提交表单
const submitForm = () => {
  formRef.value.validate((valid) => {
    if (valid) {
      // 这里应该是实际的API调用
      // 示例代码
      setTimeout(() => {
        if (isEdit.value) {
          // 更新现有记录
          const index = positionChanges.value.findIndex(item => item.id === form.id)
          if (index !== -1) {
            positionChanges.value[index] = { ...form }
          }
          ElMessage.success('更新成功')
        } else {
          // 添加新记录
          const newRecord = { ...form, id: Date.now() } // 使用时间戳作为临时ID
          positionChanges.value.push(newRecord)
          ElMessage.success('添加成功')
        }
        
        // 创建数据备份
        backupService.createBackup()
        
        dialogVisible.value = false
      }, 500)
    } else {
      return false
    }
  })
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  
  // 重置表单数据
  Object.keys(form).forEach(key => {
    if (key === 'id') {
      form[key] = null
    } else if (key === 'old_salary' || key === 'new_salary') {
      form[key] = 0
    } else {
      form[key] = ''
    }
  })
}
</script>

<style scoped>
.position-change-manager {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>