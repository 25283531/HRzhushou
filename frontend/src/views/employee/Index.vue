<template>
  <div class="employee-container">
    <el-card class="employee-card">
      <template #header>
        <div class="card-header">
          <h2>员工信息管理</h2>
          <div class="header-actions">
            <el-button type="primary" @click="showAddDialog">
              <el-icon><Plus /></el-icon> 添加员工
            </el-button>
            <el-button type="success" @click="showImportDialog">
              <el-icon><Upload /></el-icon> 批量导入
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 搜索区域 -->
      <div class="search-container">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="员工姓名">
            <el-input v-model="searchForm.name" placeholder="请输入员工姓名" clearable />
          </el-form-item>
          <el-form-item label="工号">
            <el-input v-model="searchForm.employeeNumber" placeholder="请输入工号" clearable />
          </el-form-item>
          <el-form-item label="部门">
            <el-select v-model="searchForm.department" placeholder="请选择部门" clearable>
              <el-option v-for="item in departmentOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon> 搜索
            </el-button>
            <el-button @click="resetSearch">
              <el-icon><Refresh /></el-icon> 重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 员工数据表格 -->
      <el-table
        v-loading="loading"
        :data="employeeData"
        border
        style="width: 100%"
        max-height="500">
        <el-table-column prop="name" label="员工姓名" width="120" />
        <el-table-column prop="employee_number" label="工号" width="120" />
        <el-table-column prop="id_card_number" label="身份证号" width="180" />
        <el-table-column prop="department_level1" label="一级部门" width="120" />
        <el-table-column prop="department_level2" label="二级部门" width="120" />
        <el-table-column prop="position" label="职务" width="120" />
        <el-table-column prop="entry_date" label="入职日期" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag
              :type="scope.row.status === '在职' ? 'success' : 'info'"
              effect="plain">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
            <el-button size="small" type="info" @click="viewDetail(scope.row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange" />
      </div>
    </el-card>
    
    <!-- 添加/编辑员工对话框 -->
    <el-dialog
      v-model="employeeDialogVisible"
      :title="isEdit ? '编辑员工' : '添加员工'"
      width="700px">
      <el-form :model="employeeForm" :rules="employeeRules" ref="employeeFormRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="员工姓名" prop="name">
              <el-input v-model="employeeForm.name" placeholder="请输入员工姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工号" prop="employee_number">
              <el-input v-model="employeeForm.employee_number" placeholder="请输入工号" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="身份证号" prop="id_card_number">
              <el-input v-model="employeeForm.id_card_number" placeholder="请输入身份证号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号码" prop="phone">
              <el-input v-model="employeeForm.phone" placeholder="请输入手机号码" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="一级部门" prop="department_level1">
              <el-select v-model="employeeForm.department_level1" placeholder="请选择一级部门" style="width: 100%">
                <el-option v-for="item in departmentLevel1Options" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="二级部门" prop="department_level2">
              <el-select v-model="employeeForm.department_level2" placeholder="请选择二级部门" style="width: 100%">
                <el-option v-for="item in departmentLevel2Options" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="职务" prop="position">
              <el-input v-model="employeeForm.position" placeholder="请输入职务" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入职日期" prop="entry_date">
              <el-date-picker v-model="employeeForm.entry_date" type="date" placeholder="选择入职日期" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="employeeForm.status" placeholder="请选择状态" style="width: 100%">
                <el-option label="在职" value="在职" />
                <el-option label="离职" value="离职" />
                <el-option label="试用期" value="试用期" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="薪资组" prop="salary_group">
              <el-select v-model="employeeForm.salary_group" placeholder="请选择薪资组" style="width: 100%">
                <el-option v-for="item in salaryGroupOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="社保组" prop="social_security_group">
              <el-select v-model="employeeForm.social_security_group" placeholder="请选择社保组" style="width: 100%">
                <el-option v-for="item in socialSecurityGroupOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="银行卡号" prop="bank_account">
              <el-input v-model="employeeForm.bank_account" placeholder="请输入银行卡号" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="备注" prop="remarks">
          <el-input v-model="employeeForm.remarks" type="textarea" :rows="3" placeholder="请输入备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="employeeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEmployeeForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 批量导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="批量导入员工"
      width="700px">
      <el-form :model="importForm" label-width="120px">
        <el-form-item label="员工数据文件">
          <el-upload
            class="upload-demo"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".xlsx,.xls,.csv">
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 Excel 或 CSV 格式文件，请确保文件格式正确
              </div>
            </template>
          </el-upload>
          <el-button type="primary" style="margin-left: 20px" @click="downloadTemplate">下载导入模板</el-button>
        </el-form-item>
        <el-form-item v-if="sheetNames.length > 1" label="选择工作表">
          <el-select v-model="selectedSheet" placeholder="请选择要导入的工作表" style="width: 250px">
            <el-option v-for="name in sheetNames" :key="name" :label="name" :value="name" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="sheetPreview.length" label="表格预览">
          <el-table :data="sheetPreview" border height="200" style="width: 100%">
            <el-table-column v-for="col in previewColumns" :key="col" :prop="col" :label="col" />
          </el-table>
        </el-form-item>
        <el-form-item v-if="mappingStep && importForm.file && selectedSheet && Array.isArray(fieldMappings) && fieldMappings.length > 0" label="字段映射">
          <el-table :data="fieldMappings.filter(item => !!item && typeof item === 'object')" border style="width: 100%">
            <el-table-column prop="dbField" label="数据库字段" width="180">
              <template #default="{ row }">
                {{ dbFields.find(f => f.dbField === row.dbField)?.label || row.dbField }}
              </template>
            </el-table-column>
            <el-table-column label="Excel列名">
              <template #default="{ row }">
                <el-select v-if="row" v-model="row.excelField" placeholder="请选择Excel列名" style="width: 200px">
                  <el-option v-for="col in previewColumns" :key="col" :label="col" :value="col" />
                </el-select>
                <span v-else style="color: #f56c6c;">无数据</span>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button v-if="!mappingStep && sheetPreview.length" type="primary" @click="confirmMapping">下一步</el-button>
          <el-button v-if="mappingStep" type="primary" @click="submitImport">导入</el-button>
        </span>
      </template>
    </el-dialog>
    <!-- 员工详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="员工详情"
      width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="员工姓名">{{ detailEmployee.name }}</el-descriptions-item>
        <el-descriptions-item label="工号">{{ detailEmployee.employee_number }}</el-descriptions-item>
        <el-descriptions-item label="身份证号">{{ detailEmployee.id_card_number }}</el-descriptions-item>
        <el-descriptions-item label="手机号码">{{ detailEmployee.phone }}</el-descriptions-item>
        <el-descriptions-item label="一级部门">{{ detailEmployee.department_level1 }}</el-descriptions-item>
        <el-descriptions-item label="二级部门">{{ detailEmployee.department_level2 }}</el-descriptions-item>
        <el-descriptions-item label="职务">{{ detailEmployee.position }}</el-descriptions-item>
        <el-descriptions-item label="入职日期">{{ detailEmployee.entry_date }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ detailEmployee.status }}</el-descriptions-item>
        <el-descriptions-item label="薪资组">{{ detailEmployee.salary_group }}</el-descriptions-item>
        <el-descriptions-item label="社保组">{{ detailEmployee.social_security_group }}</el-descriptions-item>
        <el-descriptions-item label="银行卡号">{{ detailEmployee.bank_account }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detailEmployee.remarks }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, UploadFilled, Search, Refresh } from '@element-plus/icons-vue'
import { validateEmployeeRecords, validateExcelFile } from '../../utils/dataValidator'
import * as XLSX from 'xlsx'

// 数据加载状态
const loading = ref(false)

// 员工数据
const employeeData = ref([])

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 搜索表单
const searchForm = reactive({
  name: '',
  employeeNumber: '',
  department: ''
})

// 部门选项
const departmentOptions = ref([
  { value: '技术部', label: '技术部' },
  { value: '人事部', label: '人事部' },
  { value: '财务部', label: '财务部' },
  { value: '市场部', label: '市场部' },
  { value: '销售部', label: '销售部' }
])

// 一级部门选项
const departmentLevel1Options = ref([
  { value: '技术部', label: '技术部' },
  { value: '人事部', label: '人事部' },
  { value: '财务部', label: '财务部' },
  { value: '市场部', label: '市场部' },
  { value: '销售部', label: '销售部' }
])

// 二级部门选项
const departmentLevel2Options = ref([
  { value: '开发组', label: '开发组' },
  { value: '测试组', label: '测试组' },
  { value: '运维组', label: '运维组' },
  { value: '招聘组', label: '招聘组' },
  { value: '培训组', label: '培训组' }
])

// 薪资组选项
const salaryGroupOptions = ref([
  { value: 1, label: '普通员工薪资组' },
  { value: 2, label: '管理层薪资组' },
  { value: 3, label: '技术专家薪资组' }
])

// 社保组选项
const socialSecurityGroupOptions = ref([
  { value: 1, label: '标准社保组' },
  { value: 2, label: '高级社保组' }
])

// 员工对话框
const employeeDialogVisible = ref(false)
const isEdit = ref(false)
const employeeFormRef = ref(null)
const employeeForm = reactive({
  id: '',
  name: '',
  employee_number: '',
  id_card_number: '',
  phone: '',
  department_level1: '',
  department_level2: '',
  position: '',
  entry_date: '',
  status: '在职',
  salary_group: '',
  social_security_group: '',
  bank_account: '',
  remarks: ''
})

// 员工表单验证规则
const employeeRules = {
  name: [
    { required: true, message: '请输入员工姓名', trigger: 'blur' }
  ],
  employee_number: [
    { required: true, message: '请输入工号', trigger: 'blur' }
  ],
  id_card_number: [
    { required: true, message: '请输入身份证号', trigger: 'blur' },
    { pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/, message: '请输入正确的身份证号', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  department_level1: [
    { required: true, message: '请选择一级部门', trigger: 'change' }
  ],
  entry_date: [
    { required: true, message: '请选择入职日期', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 导入对话框
const importDialogVisible = ref(false)
const importForm = reactive({ file: null, workbook: null })
const selectedSheet = ref('')
const sheetNames = ref([])
const sheetPreview = ref([])
const previewColumns = ref([])
const mappingStep = ref(false)
const fieldMappings = ref([])
const dbFields = ref([
  { dbField: 'name', label: '员工姓名' },
  { dbField: 'employee_number', label: '工号' },
  { dbField: 'id_card_number', label: '身份证号' },
  { dbField: 'department_level1', label: '一级部门' },
  { dbField: 'department_level2', label: '二级部门' },
  { dbField: 'position', label: '职务' },
  { dbField: 'entry_date', label: '入职日期' },
  { dbField: 'status', label: '状态' },
  { dbField: 'salary_group', label: '薪资组' },
  { dbField: 'social_security_group', label: '社保组' },
  { dbField: 'bank_account', label: '银行卡号' },
  { dbField: 'phone', label: '手机号码' },
  { dbField: 'remarks', label: '备注' }
])

function handleSizeChange(val) {
  pageSize.value = val
  currentPage.value = 1
  fetchEmployeeData()
}
function handleCurrentChange(val) {
  currentPage.value = val
  fetchEmployeeData()
}
function handleFileChange(fileObj) {
  const file = fileObj.raw || fileObj
  importForm.file = file
  const result = validateExcelFile(file)
  if (!result.valid) {
    ElMessage.error(result.errors.join('，'))
    return
  }
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target.result)
      const workbook = XLSX.read(data, { type: 'array' })
      sheetNames.value = workbook.SheetNames
      importForm.workbook = workbook
      if (sheetNames.value.length === 1) {
        selectedSheet.value = sheetNames.value[0]
        showSheetPreview(workbook, selectedSheet.value)
      } else {
        selectedSheet.value = ''
        sheetPreview.value = []
      }
      mappingStep.value = false
      fieldMappings.value = []
    } catch (err) {
      ElMessage.error('解析Excel文件失败: ' + err.message)
    }
  }
  reader.readAsArrayBuffer(file)
}

watch(selectedSheet, (val) => {
  if (val && importForm.workbook) {
    showSheetPreview(importForm.workbook, val)
  }
})

function showSheetPreview(workbook, sheetName) {
  const ws = workbook.Sheets[sheetName]
  const json = XLSX.utils.sheet_to_json(ws, { header: 1 })
  if (!json.length) {
    sheetPreview.value = []
    previewColumns.value = []
    return
  }
  previewColumns.value = json[0]
  sheetPreview.value = json.slice(1, 6).map(row => {
    const obj = {}
    previewColumns.value.forEach((col, idx) => {
      obj[col] = row[idx]
    })
    return obj
  })
}

function confirmMapping() {
  if (!sheetPreview.value.length) {
    ElMessage.error('请先上传并选择包含表头的Excel文件')
    fieldMappings.value = []
    return
  }
  // 生成映射数组
  fieldMappings.value = dbFields.value.map(f => ({
    dbField: f.dbField,
    excelField: previewColumns.value.includes(f.label) ? f.label : (previewColumns.value[0] || '')
  }))
  mappingStep.value = true
}

function submitImport() {
  if (!fieldMappings.value.length) {
    ElMessage.error('请先完成字段映射')
    return
  }
  const ws = importForm.workbook.Sheets[selectedSheet.value]
  const json = XLSX.utils.sheet_to_json(ws, { header: 1 })
  if (!json.length) {
    ElMessage.error('Excel数据为空')
    return
  }
  const header = json[0]
  const dataRows = json.slice(1)
  const mappedData = dataRows.map(row => {
    const obj = {}
    fieldMappings.value.forEach(map => {
      const colIdx = header.indexOf(map.excelField)
      obj[map.dbField] = colIdx > -1 ? row[colIdx] : ''
    })
    return obj
  })
  // 校验数据
  const valid = validateEmployeeRecords(mappedData)
  if (!valid) {
    ElMessage.error('数据校验失败，请检查导入内容')
    return
  }
  // 提交到后端
  import('../../api').then(({ default: api }) => {
    api.post('/employee/import', { data: mappedData }).then(response => {
      if (response.results) {
        ElMessage.success('导入完成')
        importDialogVisible.value = false
        fetchEmployeeData()
      } else {
        ElMessage.error('导入失败')
      }
    }).catch(err => {
      ElMessage.error('导入失败: ' + (err.error?.message || err.message))
    })
  })
}
const detailDialogVisible = ref(false)
const showAddDialog = () => {
  employeeDialogVisible.value = true
  isEdit.value = false
}
const showImportDialog = () => {
  importDialogVisible.value = true
}

function fetchEmployeeData() {
  loading.value = true
  // 这里假设有api模块，实际按你的接口调整
  import('../../api').then(({ default: api }) => {
    api.get('/employee/list', {
      params: {
        name: searchForm.name,
        employeeNumber: searchForm.employeeNumber,
        department: searchForm.department,
        page: currentPage.value,
        pageSize: pageSize.value
      }
    }).then(res => {
      // 兼容 data 为数组或对象
      if (res && Array.isArray(res.data)) {
        employeeData.value = res.data
        total.value = res.data.length
      } else if (res && res.data && Array.isArray(res.data.list)) {
        employeeData.value = res.data.list
        total.value = res.data.total || res.data.list.length || 0
      } else {
        employeeData.value = []
        total.value = 0
      }
    }).catch(() => {
      employeeData.value = []
      total.value = 0
    }).finally(() => {
      loading.value = false
    })
  })
}

function handleSearch() {
  currentPage.value = 1
  fetchEmployeeData()
}

function resetSearch() {
  searchForm.name = ''
  searchForm.employeeNumber = ''
  searchForm.department = ''
  currentPage.value = 1
  fetchEmployeeData()
}

onMounted(() => {
  fetchEmployeeData()
})
</script>

<style scoped>
.employee-container {
  padding: 20px;
}

.employee-card {
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

.search-container {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.import-actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>