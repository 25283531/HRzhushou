<template>
  <div class="salary-items">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>薪酬项管理</span>
          <el-button type="primary" @click="handleAdd">新增薪酬项</el-button>
        </div>
      </template>
      
      <el-table :data="items" style="width: 100%">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="code" label="编码" />
        <el-table-column prop="type" label="类型" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="is_fixed" label="是否固定值">
          <template #default="scope">
            <el-tag :type="scope.row.is_fixed ? 'success' : 'warning'">
              {{ scope.row.is_fixed ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="default_value" label="默认值" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="50%"
    >
      <el-form :model="form" label-width="120px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="编码" required>
          <el-input v-model="form.code" />
        </el-form-item>
        <el-form-item label="类型" required>
          <el-select v-model="form.type" placeholder="请选择类型">
            <el-option label="收入" value="income" />
            <el-option label="支出" value="expense" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
        <el-form-item label="计算公式">
          <el-input v-model="form.calculation_formula" />
        </el-form-item>
        <el-form-item label="是否固定值">
          <el-switch v-model="form.is_fixed" />
        </el-form-item>
        <el-form-item label="默认值">
          <el-input-number v-model="form.default_value" :precision="2" :step="0.1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSalaryItems, createSalaryItem, updateSalaryItem, deleteSalaryItem } from '@/api/salary'

const items = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const form = ref({
  name: '',
  code: '',
  type: '',
  description: '',
  calculation_formula: '',
  is_fixed: true,
  default_value: 0
})
const currentId = ref(null)

// 获取薪酬项列表
const fetchItems = async () => {
  try {
    const res = await getSalaryItems()
    if (res.code === 0) {
      items.value = res.data
    }
  } catch (error) {
    ElMessage.error('获取薪酬项列表失败')
  }
}

// 新增薪酬项
const handleAdd = () => {
  dialogTitle.value = '新增薪酬项'
  form.value = {
    name: '',
    code: '',
    type: '',
    description: '',
    calculation_formula: '',
    is_fixed: true,
    default_value: 0
  }
  currentId.value = null
  dialogVisible.value = true
}

// 编辑薪酬项
const handleEdit = (row) => {
  dialogTitle.value = '编辑薪酬项'
  form.value = { ...row }
  currentId.value = row.id
  dialogVisible.value = true
}

// 删除薪酬项
const handleDelete = (row) => {
  ElMessageBox.confirm(
    '确定要删除该薪酬项吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      const res = await deleteSalaryItem(row.id)
      if (res.code === 0) {
        ElMessage.success('删除成功')
        fetchItems()
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 提交表单
const handleSubmit = async () => {
  try {
    if (currentId.value) {
      const res = await updateSalaryItem(currentId.value, form.value)
      if (res.code === 0) {
        ElMessage.success('更新成功')
        dialogVisible.value = false
        fetchItems()
      }
    } else {
      const res = await createSalaryItem(form.value)
      if (res.code === 0) {
        ElMessage.success('创建成功')
        dialogVisible.value = false
        fetchItems()
      }
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  fetchItems()
})
</script>

<style scoped>
.salary-items {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 