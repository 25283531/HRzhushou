<template>
  <div class="group-matching-container">
    <el-card class="matching-card">
      <template #header>
        <div class="card-header">
          <h2>{{ currentGroup.name }} - 薪资组匹配规则</h2>
          <div class="header-actions">
            <el-button type="primary" @click="showAddMatchDialog">
              <el-icon><Plus /></el-icon> 添加匹配规则
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 匹配规则列表 -->
      <el-table
        v-loading="loading"
        :data="matchRules"
        border
        style="width: 100%">
        <el-table-column prop="type" label="匹配类型" width="120">
          <template #default="scope">
            <el-tag :type="getMatchTypeTag(scope.row.type)">
              {{ scope.row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_name" label="匹配对象" width="180" />
        <el-table-column prop="priority" label="优先级" width="100" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button size="small" type="danger" @click="handleDeleteMatch(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 添加匹配规则对话框 -->
    <el-dialog
      v-model="matchDialogVisible"
      title="添加匹配规则"
      width="500px">
      <el-form :model="matchForm" :rules="matchFormRules" ref="matchFormRef" label-width="100px">
        <el-form-item label="匹配类型" prop="type">
          <el-select v-model="matchForm.type" placeholder="请选择匹配类型" style="width: 100%">
            <el-option label="部门" value="部门" />
            <el-option label="职级" value="职级" />
            <el-option label="员工" value="员工" />
          </el-select>
        </el-form-item>
        <el-form-item label="匹配对象" prop="target_id">
          <el-select 
            v-model="matchForm.target_id" 
            placeholder="请选择匹配对象" 
            style="width: 100%"
            filterable
            remote
            :remote-method="remoteSearch"
            :loading="searchLoading">
            <el-option 
              v-for="item in matchTargets" 
              :key="item.id" 
              :label="item.name" 
              :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-input-number v-model="matchForm.priority" :min="1" :max="100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="matchForm.description" type="textarea" :rows="2" placeholder="请输入描述信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="matchDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitMatchForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, defineProps, defineEmits, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { salaryGroupApi } from '@/api/salaryGroup'

const props = defineProps({
  groupId: {
    type: [Number, String],
    required: true
  },
  currentGroup: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update'])

// 数据加载状态
const loading = ref(false)
const searchLoading = ref(false)

// 匹配规则数据
const matchRules = ref([])
const matchTargets = ref([])

// 匹配规则对话框
const matchDialogVisible = ref(false)
const matchFormRef = ref(null)
const matchForm = reactive({
  type: '部门',
  target_id: '',
  target_name: '',
  priority: 10,
  description: ''
})

// 匹配规则表单验证
const matchFormRules = {
  type: [
    { required: true, message: '请选择匹配类型', trigger: 'change' }
  ],
  target_id: [
    { required: true, message: '请选择匹配对象', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请设置优先级', trigger: 'blur' }
  ]
}

// 监听组ID变化
watch(() => props.groupId, (newVal) => {
  if (newVal) {
    fetchMatchRules()
  }
})

// 获取匹配规则数据
const fetchMatchRules = async () => {
  if (!props.groupId) return
  
  loading.value = true
  try {
    const res = await salaryGroupApi.getGroupMatches(props.groupId)
    matchRules.value = res || []
  } catch (error) {
    console.error('获取匹配规则失败:', error)
    ElMessage.error('获取匹配规则失败')
  } finally {
    loading.value = false
  }
}

// 根据匹配类型获取标签类型
const getMatchTypeTag = (type) => {
  const typeMap = {
    '部门': 'success',
    '职级': 'warning',
    '员工': 'info'
  }
  return typeMap[type] || 'default'
}

// 显示添加匹配规则对话框
const showAddMatchDialog = () => {
  Object.keys(matchForm).forEach(key => {
    if (key === 'type') {
      matchForm[key] = '部门'
    } else if (key === 'priority') {
      matchForm[key] = 10
    } else {
      matchForm[key] = ''
    }
  })
  matchTargets.value = []
  matchDialogVisible.value = true
}

// 远程搜索匹配对象
const remoteSearch = async (query) => {
  if (!query) return
  
  searchLoading.value = true
  try {
    // 根据不同的匹配类型调用不同的API
    let res = []
    if (matchForm.type === '部门') {
      // 这里应该调用部门搜索API
      res = await mockSearchDepartments(query)
    } else if (matchForm.type === '职级') {
      // 这里应该调用职级搜索API
      res = await mockSearchLevels(query)
    } else if (matchForm.type === '员工') {
      // 这里应该调用员工搜索API
      res = await mockSearchEmployees(query)
    }
    matchTargets.value = res
  } catch (error) {
    console.error('搜索匹配对象失败:', error)
  } finally {
    searchLoading.value = false
  }
}

// 提交匹配规则表单
const submitMatchForm = async () => {
  matchFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 设置目标名称
        const target = matchTargets.value.find(item => item.id === matchForm.target_id)
        if (target) {
          matchForm.target_name = target.name
        }
        
        // 添加匹配规则
        await salaryGroupApi.addGroupMatch(props.groupId, matchForm)
        ElMessage.success('匹配规则添加成功')
        matchDialogVisible.value = false
        fetchMatchRules()
        emit('update')
      } catch (error) {
        console.error('添加匹配规则失败:', error)
        ElMessage.error('添加匹配规则失败')
      }
    } else {
      return false
    }
  })
}

// 处理删除匹配规则
const handleDeleteMatch = (row) => {
  ElMessageBox.confirm(
    '确定要删除该匹配规则吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        await salaryGroupApi.deleteGroupMatch(props.groupId, row.id)
        ElMessage.success('删除成功')
        fetchMatchRules()
        emit('update')
      } catch (error) {
        console.error('删除匹配规则失败:', error)
        ElMessage.error('删除匹配规则失败')
      }
    })
    .catch(() => {
      // 取消删除
    })
}

// 模拟API调用 - 实际项目中应替换为真实API
const mockSearchDepartments = (query) => {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve([
        { id: 1, name: '技术部' },
        { id: 2, name: '人力资源部' },
        { id: 3, name: '财务部' },
        { id: 4, name: '市场部' },
        { id: 5, name: '销售部' }
      ].filter(item => item.name.includes(query)))
    }, 300)
  })
}

const mockSearchLevels = (query) => {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve([
        { id: 1, name: '初级' },
        { id: 2, name: '中级' },
        { id: 3, name: '高级' },
        { id: 4, name: '专家' },
        { id: 5, name: '总监' }
      ].filter(item => item.name.includes(query)))
    }, 300)
  })
}

const mockSearchEmployees = (query) => {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve([
        { id: 1, name: '张三' },
        { id: 2, name: '李四' },
        { id: 3, name: '王五' },
        { id: 4, name: '赵六' },
        { id: 5, name: '钱七' }
      ].filter(item => item.name.includes(query)))
    }, 300)
  })
}

// 初始化
fetchMatchRules()
</script>

<style scoped>
.group-matching-container {
  margin-top: 20px;
}

.matching-card {
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
</style>