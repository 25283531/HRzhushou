<template>
  <div class="matching-rules">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>匹配规则管理</span>
          <el-button type="primary" @click="handleAdd">新增匹配规则</el-button>
        </div>
      </template>
      
      <el-table :data="rules" style="width: 100%">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="priority" label="优先级" />
        <el-table-column prop="is_active" label="状态">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
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
      width="60%"
    >
      <el-form :model="form" label-width="120px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
        <el-form-item label="优先级" required>
          <el-input-number v-model="form.priority" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" />
        </el-form-item>
        <el-form-item label="匹配条件">
          <el-input v-model="form.conditions" type="textarea" :rows="4" />
          <div class="form-tip">请输入JSON格式的匹配条件</div>
        </el-form-item>
        <el-form-item label="关联薪酬项">
          <el-select
            v-model="form.salary_items"
            multiple
            filterable
            placeholder="请选择薪酬项"
            style="width: 100%"
          >
            <el-option
              v-for="item in salaryItems"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
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
import { getMatchingRules, createMatchingRule, updateMatchingRule, deleteMatchingRule } from '@/api/salary'
import { getSalaryItems } from '@/api/salary'

const rules = ref([])
const salaryItems = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const form = ref({
  name: '',
  description: '',
  priority: 0,
  is_active: true,
  conditions: '{}',
  salary_items: []
})
const currentId = ref(null)

// 获取匹配规则列表
const fetchRules = async () => {
  try {
    const res = await getMatchingRules()
    if (res.code === 0) {
      rules.value = res.data
    }
  } catch (error) {
    ElMessage.error('获取匹配规则列表失败')
  }
}

// 获取薪酬项列表
const fetchSalaryItems = async () => {
  try {
    const res = await getSalaryItems()
    if (res.code === 0) {
      salaryItems.value = res.data
    }
  } catch (error) {
    ElMessage.error('获取薪酬项列表失败')
  }
}

// 新增匹配规则
const handleAdd = () => {
  dialogTitle.value = '新增匹配规则'
  form.value = {
    name: '',
    description: '',
    priority: 0,
    is_active: true,
    conditions: '{}',
    salary_items: []
  }
  currentId.value = null
  dialogVisible.value = true
}

// 编辑匹配规则
const handleEdit = (row) => {
  dialogTitle.value = '编辑匹配规则'
  form.value = {
    ...row,
    conditions: typeof row.conditions === 'string' ? row.conditions : JSON.stringify(row.conditions),
    salary_items: typeof row.salary_items === 'string' ? JSON.parse(row.salary_items) : row.salary_items
  }
  currentId.value = row.id
  dialogVisible.value = true
}

// 删除匹配规则
const handleDelete = (row) => {
  ElMessageBox.confirm(
    '确定要删除该匹配规则吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      const res = await deleteMatchingRule(row.id)
      if (res.code === 0) {
        ElMessage.success('删除成功')
        fetchRules()
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 提交表单
const handleSubmit = async () => {
  try {
    const submitData = {
      ...form.value,
      conditions: form.value.conditions,
      salary_items: JSON.stringify(form.value.salary_items)
    }
    
    if (currentId.value) {
      const res = await updateMatchingRule(currentId.value, submitData)
      if (res.code === 0) {
        ElMessage.success('更新成功')
        dialogVisible.value = false
        fetchRules()
      }
    } else {
      const res = await createMatchingRule(submitData)
      if (res.code === 0) {
        ElMessage.success('创建成功')
        dialogVisible.value = false
        fetchRules()
      }
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  fetchRules()
  fetchSalaryItems()
})
</script>

<style scoped>
.matching-rules {
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

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style> 