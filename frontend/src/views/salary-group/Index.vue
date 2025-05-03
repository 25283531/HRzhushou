<template>
  <div class="salary-group-container">
    <el-card class="salary-group-card">
      <template #header>
        <div class="card-header">
          <h2>薪资组管理</h2>
          <div class="header-actions">
            <el-button type="primary" @click="showAddGroupDialog">
              <el-icon><Plus /></el-icon> 添加薪资组
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 薪资组列表 -->
      <el-table
        v-loading="loading"
        :data="salaryGroups"
        border
        style="width: 100%"
        @row-click="handleRowClick">
        <el-table-column prop="name" label="薪资组名称" width="180" />
        <el-table-column prop="item_count" label="薪酬项数量" width="120" />
        <el-table-column prop="formula" label="计算公式" show-overflow-tooltip />
        <el-table-column prop="remarks" label="备注" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click.stop="handleEditGroup(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click.stop="handleDeleteGroup(scope.row)">删除</el-button>
            <el-button size="small" type="primary" @click.stop="handleManageItems(scope.row)">管理薪酬项</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 薪酬项管理卡片，点击薪资组后显示 -->
    <el-card v-if="currentGroup.id" class="salary-items-card">
      <template #header>
        <div class="card-header">
          <h2>{{ currentGroup.name }} - 薪酬项管理</h2>
          <div class="header-actions">
            <el-button type="primary" @click="showAddItemDialog">
              <el-icon><Plus /></el-icon> 添加薪酬项
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 薪酬项列表 -->
      <el-table
        v-loading="itemsLoading"
        :data="salaryItems"
        border
        style="width: 100%">
        <el-table-column prop="name" label="薪酬项名称" width="180" />
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="scope">
            {{ scope.row.amount.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.type === '收入' ? 'success' : 'danger'">
              {{ scope.row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleEditItem(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDeleteItem(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 薪资计算公式编辑器 -->
      <div class="formula-editor">
        <h3>薪资计算公式</h3>
        <div class="formula-content">
          <el-input
            v-model="currentGroup.formula"
            type="textarea"
            :rows="3"
            placeholder="请输入薪资计算公式，例如：基本工资 + 绩效工资 - 社保扣款"
          />
          <div class="formula-help">
            <p>可用的薪酬项：</p>
            <el-tag 
              v-for="item in salaryItems" 
              :key="item.id"
              class="formula-tag"
              @click="insertItemToFormula(item.name)">
              {{ item.name }}
            </el-tag>
          </div>
          <div class="formula-operators">
            <p>可用的运算符：</p>
            <el-button size="small" @click="insertOperatorToFormula('+')">+</el-button>
            <el-button size="small" @click="insertOperatorToFormula('-')">-</el-button>
            <el-button size="small" @click="insertOperatorToFormula('*')">*</el-button>
            <el-button size="small" @click="insertOperatorToFormula('/')">÷</el-button>
            <el-button size="small" @click="insertOperatorToFormula('(')">（</el-button>
            <el-button size="small" @click="insertOperatorToFormula(')')">）</el-button>
          </div>
          <div class="formula-actions">
            <el-button type="primary" @click="saveFormula">保存公式</el-button>
            <el-button @click="testFormula">测试计算</el-button>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 添加/编辑薪资组对话框 -->
    <el-dialog
      v-model="groupDialogVisible"
      :title="isEditGroup ? '编辑薪资组' : '添加薪资组'"
      width="500px">
      <el-form :model="groupForm" :rules="groupRules" ref="groupFormRef" label-width="100px">
        <el-form-item label="薪资组名称" prop="name">
          <el-input v-model="groupForm.name" placeholder="请输入薪资组名称" />
        </el-form-item>
        <el-form-item label="备注" prop="remarks">
          <el-input v-model="groupForm.remarks" type="textarea" :rows="3" placeholder="请输入备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="groupDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitGroupForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 添加/编辑薪酬项对话框 -->
    <el-dialog
      v-model="itemDialogVisible"
      :title="isEditItem ? '编辑薪酬项' : '添加薪酬项'"
      width="500px">
      <el-form :model="itemForm" :rules="itemRules" ref="itemFormRef" label-width="100px">
        <el-form-item label="薪酬项名称" prop="name">
          <el-input v-model="itemForm.name" placeholder="请输入薪酬项名称" />
        </el-form-item>
        <el-form-item label="金额" prop="amount">
          <el-input-number v-model="itemForm.amount" :precision="2" :step="100" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="itemForm.type" placeholder="请选择类型" style="width: 100%">
            <el-option label="收入" value="收入" />
            <el-option label="支出" value="支出" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="itemForm.description" type="textarea" :rows="2" placeholder="请输入描述信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="itemDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitItemForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 公式测试对话框 -->
    <el-dialog
      v-model="formulaTestDialogVisible"
      title="公式测试计算"
      width="500px">
      <div class="formula-test-content">
        <p class="formula-display">{{ currentGroup.formula }}</p>
        <div class="formula-test-result">
          <p>计算结果：</p>
          <h2>{{ formulaTestResult }}</h2>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="formulaTestDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 薪资组匹配规则卡片 -->
    <GroupMatching 
      v-if="currentGroup.id" 
      :group-id="currentGroup.id" 
      :current-group="currentGroup"
      @update="fetchSalaryGroups"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { validateSalaryGroup, validateExcelFile } from '../../utils/dataValidator'
import { salaryGroupApi, formulaUtils } from '@/api/salaryGroup'
import GroupMatching from '@/components/salary-group/GroupMatching.vue'

// 数据加载状态
const loading = ref(false)
const itemsLoading = ref(false)

// 薪资组数据
const salaryGroups = ref([])
const currentGroup = ref({})

// 薪酬项数据
const salaryItems = ref([])

// 薪资组对话框
const groupDialogVisible = ref(false)
const isEditGroup = ref(false)
const groupFormRef = ref(null)
const groupForm = reactive({
  id: '',
  name: '',
  formula: '',
  remarks: ''
})

// 薪资组表单验证规则
const groupRules = {
  name: [
    { required: true, message: '请输入薪资组名称', trigger: 'blur' }
  ]
}

// 薪酬项对话框
const itemDialogVisible = ref(false)
const isEditItem = ref(false)
const itemFormRef = ref(null)
const itemForm = reactive({
  id: '',
  group_id: '',
  name: '',
  amount: 0,
  type: '收入',
  description: ''
})

// 薪酬项表单验证规则
const itemRules = {
  name: [
    { required: true, message: '请输入薪酬项名称', trigger: 'blur' }
  ],
  amount: [
    { required: true, message: '请输入金额', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择类型', trigger: 'change' }
  ]
}

// 公式测试对话框
const formulaTestDialogVisible = ref(false)
const formulaTestResult = ref(0)

// 生命周期钩子
onMounted(() => {
  fetchSalaryGroups()
})

// 获取薪资组数据
const fetchSalaryGroups = async () => {
  loading.value = true
  try {
    const res = await salaryGroupApi.getAllGroups()
    if (res.success) {
      salaryGroups.value = res.data.items || []
    } else {
      ElMessage.error(res.error || '获取薪资组失败')
      salaryGroups.value = []
    }
  } catch (error) {
    console.error('获取薪资组失败:', error)
    ElMessage.error('获取薪资组失败')
    salaryGroups.value = []
  } finally {
    loading.value = false
  }
}

// 获取薪酬项数据
const fetchSalaryItems = async (groupId) => {
  if (!groupId) return
  
  itemsLoading.value = true
  try {
    const res = await salaryGroupApi.getGroupItems(groupId)
    salaryItems.value = res || []
  } catch (error) {
    console.error('获取薪酬项失败:', error)
    ElMessage.error('获取薪酬项失败')
  } finally {
    itemsLoading.value = false
  }
}

// 处理行点击
const handleRowClick = (row) => {
  currentGroup.value = { ...row }
  fetchSalaryItems(row.id)
}

// 显示添加薪资组对话框
const showAddGroupDialog = () => {
  isEditGroup.value = false
  Object.keys(groupForm).forEach(key => {
    groupForm[key] = ''
  })
  groupDialogVisible.value = true
}

// 显示编辑薪资组对话框
const handleEditGroup = (row) => {
  isEditGroup.value = true
  Object.keys(groupForm).forEach(key => {
    groupForm[key] = row[key] || ''
  })
  groupDialogVisible.value = true
}

// 提交薪资组表单
const submitGroupForm = () => {
  groupFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEditGroup.value) {
          await salaryGroupApi.updateGroup(groupForm.id, groupForm)
        } else {
          await salaryGroupApi.createGroup(groupForm)
        }
        ElMessage.success(isEditGroup.value ? '薪资组更新成功' : '薪资组添加成功')
        groupDialogVisible.value = false
        fetchSalaryGroups() // 刷新数据
      } catch (error) {
        console.error('保存薪资组失败:', error)
        ElMessage.error('保存失败')
      }
    } else {
      return false
    }
  })
}

// 处理删除薪资组
const handleDeleteGroup = (row) => {
  ElMessageBox.confirm(
    '删除薪资组将同时删除其下所有薪酬项，确定要删除吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        await salaryGroupApi.deleteGroup(row.id)
        ElMessage({
          type: 'success',
          message: '删除成功',
        })
        fetchSalaryGroups() // 刷新数据
        if (currentGroup.value.id === row.id) {
          currentGroup.value = {}
          salaryItems.value = []
        }
      } catch (error) {
        console.error('删除薪资组失败:', error)
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {
      // 取消删除
    })
}

// 管理薪酬项
const handleManageItems = (row) => {
  currentGroup.value = { ...row }
  fetchSalaryItems(row.id)
}

// 显示添加薪酬项对话框
const showAddItemDialog = () => {
  if (!currentGroup.value.id) {
    ElMessage.warning('请先选择一个薪资组')
    return
  }
  
  isEditItem.value = false
  Object.keys(itemForm).forEach(key => {
    if (key === 'group_id') {
      itemForm[key] = currentGroup.value.id
    } else if (key === 'type') {
      itemForm[key] = '收入'
    } else if (key === 'amount') {
      itemForm[key] = 0
    } else {
      itemForm[key] = ''
    }
  })
  itemDialogVisible.value = true
}

// 显示编辑薪酬项对话框
const handleEditItem = (row) => {
  isEditItem.value = true
  Object.keys(itemForm).forEach(key => {
    itemForm[key] = row[key] || (key === 'amount' ? 0 : '')
  })
  itemDialogVisible.value = true
}

// 提交薪酬项表单
const submitItemForm = () => {
  itemFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEditItem.value) {
          await salaryGroupApi.updateItem(currentGroup.value.id, itemForm.id, itemForm)
        } else {
          await salaryGroupApi.createItem(currentGroup.value.id, itemForm)
        }
        ElMessage.success(isEditItem.value ? '薪酬项更新成功' : '薪酬项添加成功')
        itemDialogVisible.value = false
        fetchSalaryItems(currentGroup.value.id) // 刷新数据
        // 刷新薪资组列表以更新薪酬项数量
        fetchSalaryGroups()
      } catch (error) {
        console.error('保存薪酬项失败:', error)
        ElMessage.error('保存失败')
      }
    } else {
      return false
    }
  })
}

// 处理删除薪酬项
const handleDeleteItem = (row) => {
  ElMessageBox.confirm(
    '确定要删除该薪酬项吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        await salaryGroupApi.deleteItem(currentGroup.value.id, row.id)
        ElMessage({
          type: 'success',
          message: '删除成功',
        })
        fetchSalaryItems(currentGroup.value.id) // 刷新数据
        // 刷新薪资组列表以更新薪酬项数量
        fetchSalaryGroups()
      } catch (error) {
        console.error('删除薪酬项失败:', error)
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {
      // 取消删除
    })
}

// 向公式中插入薪酬项
const insertItemToFormula = (itemName) => {
  currentGroup.value.formula += itemName
}

// 向公式中插入运算符
const insertOperatorToFormula = (operator) => {
  currentGroup.value.formula += ` ${operator} `
}

// 保存公式
const saveFormula = async () => {
  if (!currentGroup.value.formula) {
    ElMessage.warning('请输入薪资计算公式')
    return
  }
  
  // 验证公式是否有效
  if (!formulaUtils.validateFormula(currentGroup.value.formula, salaryItems.value)) {
    ElMessage.error('公式无效，请检查后重试')
    return
  }
  
  try {
    await salaryGroupApi.updateFormula(currentGroup.value.id, currentGroup.value.formula)
    ElMessage.success('薪资计算公式保存成功')
    fetchSalaryGroups() // 刷新数据
  } catch (error) {
    console.error('保存公式失败:', error)
    ElMessage.error('保存失败')
  }
}

// 测试公式计算
const testFormula = async () => {
  if (!currentGroup.value.formula) {
    ElMessage.warning('请先输入薪资计算公式')
    return
  }
  
  try {
    // 使用API计算或使用本地工具计算
    let result
    try {
      // 尝试使用API计算
      const res = await salaryGroupApi.calculateFormula(currentGroup.value.id, currentGroup.value.formula)
      result = res.result
    } catch (error) {
      // 如果API调用失败，使用本地工具计算
      console.warn('API计算失败，使用本地计算:', error)
      result = formulaUtils.parseFormula(currentGroup.value.formula, salaryItems.value)
    }
    
    formulaTestResult.value = typeof result === 'number' ? result.toFixed(2) : '计算错误'
    formulaTestDialogVisible.value = true
  } catch (error) {
    console.error('公式计算失败:', error)
    ElMessage.error('公式计算失败，请检查公式是否正确')
  }
}
</script>

<style scoped>
.salary-group-container {
  padding: 20px;
}

.salary-group-card,
.salary-items-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 18px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.formula-editor {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.formula-editor h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
}

.formula-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.formula-help,
.formula-operators {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.formula-help p,
.formula-operators p {
  margin: 0;
  font-weight: bold;
  margin-right: 10px;
}

.formula-tag {
  cursor: pointer;
}

.formula-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.formula-test-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.formula-display {
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
}

.formula-test-result {
  text-align: center;
}

.formula-test-result p {
  margin-bottom: 5px;
  color: #606266;
}

.formula-test-result h2 {
  margin: 0;
  font-size: 24px;
  color: #409EFF;
}
</style>