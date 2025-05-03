<template>
  <div class="position-levels">
    <!-- 职级类型管理 -->
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>职级类型管理</span>
          <el-button type="primary" @click="handleAddType">新增职级类型</el-button>
        </div>
      </template>
      
      <el-table :data="types" style="width: 100%">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="code" label="编码" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="is_active" label="状态">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="handleEditType(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDeleteType(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 职级管理 -->
    <el-card class="box-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>职级管理</span>
          <el-button type="primary" @click="handleAddLevel">新增职级</el-button>
        </div>
      </template>
      
      <div class="filter-container">
        <el-select v-model="selectedTypeId" placeholder="选择职级类型" clearable @change="handleTypeChange">
          <el-option
            v-for="type in types"
            :key="type.id"
            :label="type.name"
            :value="type.id"
          />
        </el-select>
      </div>
      
      <el-table :data="levels" style="width: 100%; margin-top: 20px;">
        <el-table-column prop="type_name" label="类型" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="code" label="编码" />
        <el-table-column prop="level" label="等级" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="is_active" label="状态">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="handleEditLevel(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDeleteLevel(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 职级类型对话框 -->
    <el-dialog
      :title="typeDialogTitle"
      v-model="typeDialogVisible"
      width="50%"
    >
      <el-form :model="typeForm" label-width="120px">
        <el-form-item label="名称" required>
          <el-input v-model="typeForm.name" />
        </el-form-item>
        <el-form-item label="编码" required>
          <el-input v-model="typeForm.code" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="typeForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="typeForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="typeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleTypeSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 职级对话框 -->
    <el-dialog
      :title="levelDialogTitle"
      v-model="levelDialogVisible"
      width="50%"
    >
      <el-form :model="levelForm" label-width="120px">
        <el-form-item label="职级类型" required>
          <el-select v-model="levelForm.type_id" placeholder="选择职级类型">
            <el-option
              v-for="type in types"
              :key="type.id"
              :label="type.name"
              :value="type.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="名称" required>
          <el-input v-model="levelForm.name" />
        </el-form-item>
        <el-form-item label="编码" required>
          <el-input v-model="levelForm.code" />
        </el-form-item>
        <el-form-item label="等级" required>
          <el-input-number v-model="levelForm.level" :min="1" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="levelForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="levelForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="levelDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleLevelSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getLevelTypes,
  createLevelType,
  updateLevelType,
  deleteLevelType,
  getPositionLevels,
  createPositionLevel,
  updatePositionLevel,
  deletePositionLevel
} from '@/api/position-levels'

// 数据
const types = ref([])
const levels = ref([])
const selectedTypeId = ref(null)

// 职级类型对话框
const typeDialogVisible = ref(false)
const typeDialogTitle = ref('')
const typeForm = ref({
  name: '',
  code: '',
  description: '',
  is_active: true
})
const currentTypeId = ref(null)

// 职级对话框
const levelDialogVisible = ref(false)
const levelDialogTitle = ref('')
const levelForm = ref({
  type_id: null,
  name: '',
  code: '',
  level: 1,
  description: '',
  is_active: true
})
const currentLevelId = ref(null)

// 获取职级类型列表
const fetchTypes = async () => {
  try {
    const res = await getLevelTypes()
    if (res.code === 0) {
      types.value = res.data
    }
  } catch (error) {
    ElMessage.error('获取职级类型列表失败')
  }
}

// 获取职级列表
const fetchLevels = async () => {
  try {
    const res = await getPositionLevels(selectedTypeId.value)
    if (res.code === 0) {
      levels.value = res.data
    }
  } catch (error) {
    ElMessage.error('获取职级列表失败')
  }
}

// 新增职级类型
const handleAddType = () => {
  typeDialogTitle.value = '新增职级类型'
  typeForm.value = {
    name: '',
    code: '',
    description: '',
    is_active: true
  }
  currentTypeId.value = null
  typeDialogVisible.value = true
}

// 编辑职级类型
const handleEditType = (row) => {
  typeDialogTitle.value = '编辑职级类型'
  typeForm.value = { ...row }
  currentTypeId.value = row.id
  typeDialogVisible.value = true
}

// 删除职级类型
const handleDeleteType = (row) => {
  ElMessageBox.confirm(
    '确定要删除该职级类型吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      const res = await deleteLevelType(row.id)
      if (res.code === 0) {
        ElMessage.success('删除成功')
        fetchTypes()
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 提交职级类型表单
const handleTypeSubmit = async () => {
  try {
    if (currentTypeId.value) {
      const res = await updateLevelType(currentTypeId.value, typeForm.value)
      if (res.code === 0) {
        ElMessage.success('更新成功')
        typeDialogVisible.value = false
        fetchTypes()
      }
    } else {
      const res = await createLevelType(typeForm.value)
      if (res.code === 0) {
        ElMessage.success('创建成功')
        typeDialogVisible.value = false
        fetchTypes()
      }
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 新增职级
const handleAddLevel = () => {
  levelDialogTitle.value = '新增职级'
  levelForm.value = {
    type_id: selectedTypeId.value,
    name: '',
    code: '',
    level: 1,
    description: '',
    is_active: true
  }
  currentLevelId.value = null
  levelDialogVisible.value = true
}

// 编辑职级
const handleEditLevel = (row) => {
  levelDialogTitle.value = '编辑职级'
  levelForm.value = { ...row }
  currentLevelId.value = row.id
  levelDialogVisible.value = true
}

// 删除职级
const handleDeleteLevel = (row) => {
  ElMessageBox.confirm(
    '确定要删除该职级吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      const res = await deletePositionLevel(row.id)
      if (res.code === 0) {
        ElMessage.success('删除成功')
        fetchLevels()
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 提交职级表单
const handleLevelSubmit = async () => {
  try {
    if (currentLevelId.value) {
      const res = await updatePositionLevel(currentLevelId.value, levelForm.value)
      if (res.code === 0) {
        ElMessage.success('更新成功')
        levelDialogVisible.value = false
        fetchLevels()
      }
    } else {
      const res = await createPositionLevel(levelForm.value)
      if (res.code === 0) {
        ElMessage.success('创建成功')
        levelDialogVisible.value = false
        fetchLevels()
      }
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 职级类型变更
const handleTypeChange = () => {
  fetchLevels()
}

onMounted(() => {
  fetchTypes()
  fetchLevels()
})
</script>

<style scoped>
.position-levels {
  padding: 20px;
}

.box-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-container {
  margin-bottom: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 