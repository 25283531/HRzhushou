<template>
  <div class="salary-calculation-container">
    <h1>薪资计算</h1>
    
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <span>薪资计算</span>
          <el-button type="primary" @click="calculateSalary">计算薪资</el-button>
        </div>
      </template>
      
      <div class="filter-container">
        <el-form :inline="true" :model="filterForm" class="form-inline">
          <el-form-item label="计算月份">
            <el-date-picker
              v-model="filterForm.month"
              type="month"
              placeholder="选择月份"
              format="YYYY年MM月"
              value-format="YYYY-MM"
            />
          </el-form-item>
          <el-form-item label="薪资组">
            <el-select v-model="filterForm.salaryGroupId" placeholder="选择薪资组">
              <el-option
                v-for="item in salaryGroups"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="员工">
            <el-select v-model="filterForm.employeeId" placeholder="选择员工" clearable>
              <el-option
                v-for="item in employees"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadSalaryData">查询</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <el-table
        v-loading="loading"
        :data="salaryData"
        border
        style="width: 100%"
      >
        <el-table-column prop="employee_name" label="员工姓名" width="120" />
        <el-table-column prop="employee_number" label="工号" width="100" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="position" label="职位" width="120" />
        <el-table-column prop="base_salary" label="基本工资" width="120">
          <template #default="scope">
            {{ formatCurrency(scope.row.base_salary) }}
          </template>
        </el-table-column>
        <el-table-column prop="attendance_deduction" label="考勤扣款" width="120">
          <template #default="scope">
            {{ formatCurrency(scope.row.attendance_deduction) }}
          </template>
        </el-table-column>
        <el-table-column prop="bonus" label="奖金" width="120">
          <template #default="scope">
            {{ formatCurrency(scope.row.bonus) }}
          </template>
        </el-table-column>
        <el-table-column prop="social_security" label="社保" width="120">
          <template #default="scope">
            {{ formatCurrency(scope.row.social_security) }}
          </template>
        </el-table-column>
        <el-table-column prop="tax" label="个税" width="120">
          <template #default="scope">
            {{ formatCurrency(scope.row.tax) }}
          </template>
        </el-table-column>
        <el-table-column prop="net_salary" label="实发工资" width="120">
          <template #default="scope">
            <span class="net-salary">{{ formatCurrency(scope.row.net_salary) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === '已发放' ? 'success' : 'warning'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="viewDetail(scope.row)">详情</el-button>
            <el-button type="success" size="small" @click="exportSalary(scope.row)" :disabled="scope.row.status !== '已计算'">导出</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 薪资详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="薪资详情"
      width="600px"
    >
      <div v-if="currentSalary" class="salary-detail">
        <h3>{{ currentSalary.employee_name }} - {{ filterForm.month }}薪资明细</h3>
        
        <el-descriptions :column="1" border>
          <el-descriptions-item label="员工姓名">{{ currentSalary.employee_name }}</el-descriptions-item>
          <el-descriptions-item label="工号">{{ currentSalary.employee_number }}</el-descriptions-item>
          <el-descriptions-item label="部门">{{ currentSalary.department }}</el-descriptions-item>
          <el-descriptions-item label="职位">{{ currentSalary.position }}</el-descriptions-item>
          <el-descriptions-item label="基本工资">{{ formatCurrency(currentSalary.base_salary) }}</el-descriptions-item>
          <el-descriptions-item label="考勤扣款">{{ formatCurrency(currentSalary.attendance_deduction) }}</el-descriptions-item>
          <el-descriptions-item label="奖金">{{ formatCurrency(currentSalary.bonus) }}</el-descriptions-item>
          <el-descriptions-item label="社保">{{ formatCurrency(currentSalary.social_security) }}</el-descriptions-item>
          <el-descriptions-item label="个税">{{ formatCurrency(currentSalary.tax) }}</el-descriptions-item>
          <el-descriptions-item label="实发工资">{{ formatCurrency(currentSalary.net_salary) }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ currentSalary.status }}</el-descriptions-item>
          <el-descriptions-item label="计算时间">{{ currentSalary.calculate_time }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { validateExcelFile } from '../../utils/dataValidator'

// 数据加载状态
const loading = ref(false)

// 薪资组列表
const salaryGroups = ref([])

// 员工列表
const employees = ref([])

// 薪资数据
const salaryData = ref([])

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 筛选表单
const filterForm = reactive({
  month: new Date().toISOString().slice(0, 7), // 默认当前月份
  salaryGroupId: '',
  employeeId: ''
})

// 详情对话框
const detailDialogVisible = ref(false)
const currentSalary = ref(null)

// 初始化数据
onMounted(() => {
  loadSalaryGroups()
  loadEmployees()
  loadSalaryData()
})

// 加载薪资组数据
const loadSalaryGroups = async () => {
  try {
    // 导入API模块
    const { default: api } = await import('../../api')
    
    // 调用API获取薪资组数据
    const response = await api.get('/salary-groups')
    
    if (response.success) {
      salaryGroups.value = response.data || []
    } else {
      ElMessage.error(response.error || '加载薪资组失败')
      salaryGroups.value = []
    }
  } catch (error) {
    console.error('加载薪资组失败:', error)
    ElMessage.error('加载薪资组失败')
  }
}

// 加载员工数据
const loadEmployees = async () => {
  try {
    // 导入API模块
    const { default: api } = await import('../../api')
    
    // 调用API获取员工数据
    const response = await api.get('/employee/list')
    
    if (response.success) {
      employees.value = response.data || []
    } else {
      ElMessage.error(response.error || '加载员工失败')
      employees.value = []
    }
  } catch (error) {
    console.error('加载员工失败:', error)
    ElMessage.error('加载员工失败')
  }
}

// 加载薪资数据
const loadSalaryData = async () => {
  loading.value = true
   try {
    // 导入API模块
    const { default: api } = await import('../../api')
    
    // 构建查询参数
    const params = {
      month: filterForm.month,
      salary_group_id: filterForm.salaryGroupId,
      employee_id: filterForm.employeeId,
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    // 调用API获取薪资数据
    const response = await api.get('/salary/history', { params })
    
    if (response.success) {
      salaryData.value = response.data.items || []
      total.value = response.data.total || 0
    } else {
      ElMessage.error(response.error || '获取薪资数据失败')
      salaryData.value = []
      total.value = 0
    }
    loading.value = false
  } catch (error) {
    console.error('加载薪资数据失败:', error)
    ElMessage.error('加载薪资数据失败')
    loading.value = false
  }
}

// 重置筛选条件
const resetFilter = () => {
  filterForm.month = new Date().toISOString().slice(0, 7)
  filterForm.salaryGroupId = ''
  filterForm.employeeId = ''
  loadSalaryData()
}

// 计算薪资
const calculateSalary = () => {
  ElMessageBox.confirm(
    `确定要计算${filterForm.month}的薪资数据吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    loading.value = true
    try {
      // 导入API模块
      const { default: api } = await import('../../api')
      
      // 调用API计算薪资
      const response = await api.post('/salary/calculate', {
        month: filterForm.month,
        salary_group_id: filterForm.salaryGroupId,
        employee_id: filterForm.employeeId
      })
      
      if (response.success) {
        ElMessage.success('薪资计算成功')
        loadSalaryData() // 刷新数据
      } else {
        ElMessage.error(response.error || '薪资计算失败')
      }
      loading.value = false
    } catch (error) {
      console.error('薪资计算失败:', error)
      ElMessage.error('薪资计算失败')
      loading.value = false
    }
  }).catch(() => {
    // 取消计算
  })
}

// 查看薪资详情
const viewDetail = (row) => {
  currentSalary.value = row
  detailDialogVisible.value = true
}

// 导出薪资单
const exportSalary = (row) => {
  try {
    loading.value = true
    ElMessage.info(`正在准备导出${row.employee_name}的薪资单...`)
    
    // 导入API模块
    import('../../api').then(({ default: api }) => {
      // 创建导出请求 - 使用Blob方式处理文件下载
      api.get(`/salary/export`, {
        params: { id: row.id },
        responseType: 'blob' // 指定响应类型为blob
      }).then(response => {
        // 创建Blob对象
        const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        
        // 创建下载链接
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `薪资单_${row.employee_name}_${filterForm.month}.xlsx`)
        document.body.appendChild(link)
        
        // 触发点击下载
        link.click()
        
        // 清理资源
        window.URL.revokeObjectURL(url)
        document.body.removeChild(link)
        
        ElMessage.success(`${row.employee_name}的薪资单导出成功`)
        loading.value = false
      }).catch(error => {
        console.error('导出薪资单失败:', error)
        ElMessage.error('导出薪资单失败，请稍后重试')
        loading.value = false
      })
    })
  } catch (error) {
    console.error('导出薪资单失败:', error)
    ElMessage.error('导出薪资单失败')
    loading.value = false
  }
}

// 格式化货币
const formatCurrency = (value) => {
  if (value === undefined || value === null) return '0.00'
  return `¥${parseFloat(value).toFixed(2)}`
}

// 分页大小变化
const handleSizeChange = (val) => {
  pageSize.value = val
  loadSalaryData()
}

// 当前页变化
const handleCurrentChange = (val) => {
  currentPage.value = val
  loadSalaryData()
}
</script>

<style scoped>
.salary-calculation-container {
  padding: 20px;
}

.main-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-container {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.net-salary {
  font-weight: bold;
  color: #409EFF;
}

.salary-detail h3 {
  margin-bottom: 20px;
  text-align: center;
}
</style>