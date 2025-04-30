<template>
  <div class="social-insurance-calculator">
    <el-card class="insurance-card">
      <template #header>
        <div class="card-header">
          <h3>社保计算</h3>
        </div>
      </template>
      
      <!-- 社保计算表单 -->
      <el-form :model="form" label-width="120px">
        <el-form-item label="计算月份">
          <el-date-picker
            v-model="form.month"
            type="month"
            placeholder="选择月份"
            format="YYYY年MM月"
            value-format="YYYY-MM"
            style="width: 100%">
          </el-date-picker>
        </el-form-item>
        
        <el-form-item label="员工">
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
        
        <el-form-item label="社保基数">
          <el-input-number
            v-model="form.social_base"
            :min="socialBase.min"
            :max="socialBase.max"
            :precision="2"
            :step="100"
            style="width: 100%">
          </el-input-number>
          <div class="base-range">
            基数范围: {{ socialBase.min.toFixed(2) }} - {{ socialBase.max.toFixed(2) }}
          </div>
        </el-form-item>
        
        <el-form-item label="中途入职/离职">
          <el-switch v-model="form.hasEntryExit" @change="handleEntryExitChange"></el-switch>
        </el-form-item>
        
        <template v-if="form.hasEntryExit">
          <el-form-item label="入职日期">
            <el-date-picker
              v-model="form.entry_date"
              type="date"
              placeholder="选择入职日期"
              value-format="YYYY-MM-DD"
              :disabled="!form.is_entry"
              style="width: 100%">
            </el-date-picker>
            <el-checkbox v-model="form.is_entry" style="margin-top: 5px">本月入职</el-checkbox>
          </el-form-item>
          
          <el-form-item label="离职日期">
            <el-date-picker
              v-model="form.exit_date"
              type="date"
              placeholder="选择离职日期"
              value-format="YYYY-MM-DD"
              :disabled="!form.is_exit"
              style="width: 100%">
            </el-date-picker>
            <el-checkbox v-model="form.is_exit" style="margin-top: 5px">本月离职</el-checkbox>
          </el-form-item>
        </template>
        
        <el-form-item>
          <el-button type="primary" @click="calculateInsurance" :loading="calculating">计算社保</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 计算结果 -->
      <div v-if="result" class="calculation-result">
        <h3>计算结果</h3>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="社保基数">{{ result.base.toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="实际工作天数">{{ result.workDays }}天 ({{ (result.workRatio * 100).toFixed(2) }}%)</el-descriptions-item>
          
          <el-descriptions-item label="养老保险(个人)" :span="2">
            {{ result.employee.pension.toFixed(2) }}
            <span class="rate-info">({{ socialRates.pension.employee }}%)</span>
          </el-descriptions-item>
          
          <el-descriptions-item label="医疗保险(个人)" :span="2">
            {{ result.employee.medical.toFixed(2) }}
            <span class="rate-info">({{ socialRates.medical.employee }}%)</span>
          </el-descriptions-item>
          
          <el-descriptions-item label="失业保险(个人)" :span="2">
            {{ result.employee.unemployment.toFixed(2) }}
            <span class="rate-info">({{ socialRates.unemployment.employee }}%)</span>
          </el-descriptions-item>
          
          <el-descriptions-item label="住房公积金(个人)" :span="2">
            {{ result.employee.housing.toFixed(2) }}
            <span class="rate-info">({{ socialRates.housing.employee }}%)</span>
          </el-descriptions-item>
          
          <el-descriptions-item label="个人缴纳合计">
            {{ result.employee.total.toFixed(2) }}
          </el-descriptions-item>
          
          <el-descriptions-item label="单位缴纳合计">
            {{ result.company.total.toFixed(2) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="calculation-note" v-if="form.hasEntryExit && result.workRatio < 1">
          <el-alert
            title="按比例计算说明"
            type="info"
            :closable="false">
            <p>由于员工为中途入职或离职，社保金额已按实际工作天数比例计算。</p>
            <p>本月应缴天数: {{ result.workDays }}天，比例: {{ (result.workRatio * 100).toFixed(2) }}%</p>
          </el-alert>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'
import { calculateSocialInsurance } from '../../utils/workerService'
import { parseDate, formatDate } from '../../utils/dateParser'

// 员工列表
const employees = ref([])

// 社保基数范围
const socialBase = reactive({
  min: 3000,
  max: 25000
})

// 社保比例
const socialRates = reactive({
  pension: {
    employee: 8,
    company: 16
  },
  medical: {
    employee: 2,
    company: 8
  },
  unemployment: {
    employee: 0.5,
    company: 0.5
  },
  housing: {
    employee: 7,
    company: 7
  }
})

// 表单数据
const form = reactive({
  month: formatDate(new Date(), 'YYYY-MM'),
  employee_id: '',
  employee_name: '',
  social_base: 0,
  hasEntryExit: false,
  is_entry: false,
  is_exit: false,
  entry_date: '',
  exit_date: ''
})

// 计算状态
const calculating = ref(false)

// 计算结果
const result = ref(null)

// 生命周期钩子
onMounted(() => {
  fetchEmployees()
  fetchSocialSettings()
})

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
        base_salary: 15000,
        social_base: 15000
      },
      {
        id: 2,
        name: '李四',
        number: '002',
        position: '产品经理',
        base_salary: 18000,
        social_base: 18000
      }
    ]
  }, 500)
}

// 获取社保设置
const fetchSocialSettings = () => {
  // 这里应该是实际的API调用
  // 示例代码
  setTimeout(() => {
    // 更新社保基数范围
    socialBase.min = 3000
    socialBase.max = 25000
    
    // 更新社保比例
    socialRates.pension.employee = 8
    socialRates.pension.company = 16
    socialRates.medical.employee = 2
    socialRates.medical.company = 8
    socialRates.unemployment.employee = 0.5
    socialRates.unemployment.company = 0.5
    socialRates.housing.employee = 7
    socialRates.housing.company = 7
  }, 500)
}

// 处理员工选择变更
const handleEmployeeChange = (employeeId) => {
  const employee = employees.value.find(item => item.id === employeeId)
  if (employee) {
    form.employee_name = employee.name
    form.social_base = employee.social_base || employee.base_salary
  }
}

// 处理入职/离职状态变更
const handleEntryExitChange = (value) => {
  if (!value) {
    // 重置入职/离职相关字段
    form.is_entry = false
    form.is_exit = false
    form.entry_date = ''
    form.exit_date = ''
  }
}

// 计算社保
const calculateInsurance = () => {
  // 验证表单
  if (!form.month) {
    ElMessage.warning('请选择计算月份')
    return
  }
  
  if (!form.employee_id) {
    ElMessage.warning('请选择员工')
    return
  }
  
  if (form.hasEntryExit) {
    if (form.is_entry && !form.entry_date) {
      ElMessage.warning('请选择入职日期')
      return
    }
    
    if (form.is_exit && !form.exit_date) {
      ElMessage.warning('请选择离职日期')
      return
    }
  }
  
  // 显示加载指示器
  calculating.value = true
  const loadingInstance = ElLoading.service({
    target: '.insurance-card',
    text: '正在计算...',
    background: 'rgba(255, 255, 255, 0.7)'
  })
  
  // 准备入职/离职记录
  const entryExitRecords = []
  
  if (form.hasEntryExit) {
    if (form.is_entry && form.entry_date) {
      entryExitRecords.push({
        type: 'entry',
        date: form.entry_date
      })
    }
    
    if (form.is_exit && form.exit_date) {
      entryExitRecords.push({
        type: 'exit',
        date: form.exit_date
      })
    }
  }
  
  // 获取员工信息
  const employee = employees.value.find(item => item.id === form.employee_id)
  
  // 使用Web Worker计算社保
  calculateSocialInsurance({
    employee,
    month: form.month,
    socialBase: socialBase,
    socialRates: socialRates,
    entryExitRecords
  }).then(calculationResult => {
    result.value = calculationResult
    calculating.value = false
    loadingInstance.close()
  }).catch(error => {
    console.error('计算社保失败:', error)
    ElMessage.error(`计算社保失败: ${error.message}`)
    calculating.value = false
    loadingInstance.close()
  })
}

// 重置表单
const resetForm = () => {
  // 重置表单数据
  form.month = formatDate(new Date(), 'YYYY-MM')
  form.employee_id = ''
  form.employee_name = ''
  form.social_base = 0
  form.hasEntryExit = false
  form.is_entry = false
  form.is_exit = false
  form.entry_date = ''
  form.exit_date = ''
  
  // 清除计算结果
  result.value = null
}
</script>

<style scoped>
.social-insurance-calculator {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.base-range {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.calculation-result {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}

.rate-info {
  font-size: 12px;
  color: #909399;
  margin-left: 5px;
}

.calculation-note {
  margin-top: 15px;
}
</style>