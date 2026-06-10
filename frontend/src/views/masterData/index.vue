<template>
  <div class="master-data-page">
    <el-card>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="村组管理" name="village">
          <div class="table-header">
            <el-button type="primary" @click="handleAddVillage">
              <el-icon><Plus /></el-icon>
              新增村组
            </el-button>
          </div>
          <el-table :data="villageList" stripe style="width: 100%">
            <el-table-column prop="code" label="村组编码" width="150" />
            <el-table-column prop="name" label="村组名称" width="200" />
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right" align="center">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleEditVillage(row)">编辑</el-button>
                <el-button type="danger" link size="small" @click="handleDeleteVillage(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="井类型管理" name="wellType">
          <div class="table-header">
            <el-button type="primary" @click="handleAddWellType">
              <el-icon><Plus /></el-icon>
              新增井类型
            </el-button>
          </div>
          <el-table :data="wellTypeList" stripe style="width: 100%">
            <el-table-column prop="name" label="类型名称" width="200" />
            <el-table-column prop="inspection_cycle_days" label="巡检周期(天)" width="150" align="center" />
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right" align="center">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleEditWellType(row)">编辑</el-button>
                <el-button type="danger" link size="small" @click="handleDeleteWellType(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="水质指标管理" name="standard">
          <div class="table-header">
            <el-select v-model="categoryFilter" placeholder="按分类筛选" clearable style="width: 150px" @change="loadStandards">
              <el-option label="微生物指标" value="微生物" />
              <el-option label="毒理指标" value="毒理" />
              <el-option label="感官性状" value="感官" />
              <el-option label="一般化学指标" value="一般化学" />
              <el-option label="放射性指标" value="放射性" />
            </el-select>
            <el-button type="primary" @click="handleAddStandard">
              <el-icon><Plus /></el-icon>
              新增水质指标
            </el-button>
          </div>
          <el-table :data="standardList" stripe style="width: 100%">
            <el-table-column prop="priority" label="优先级" width="80" align="center" />
            <el-table-column prop="category" label="分类" width="100">
              <template #default="{ row }">
                <el-tag :type="getCategoryType(row.category)" size="small">{{ row.category }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="indicator_code" label="指标编码" width="100" />
            <el-table-column prop="indicator_name" label="指标名称" width="140" />
            <el-table-column label="限值" width="150">
              <template #default="{ row }">
                {{ row.comparison_type }} {{ row.limit_value }} {{ row.unit }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right" align="center">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleEditStandard(row)">编辑</el-button>
                <el-button type="danger" link size="small" @click="handleDeleteStandard(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="villageDialogVisible" :title="villageDialogTitle" width="400px" destroy-on-close>
      <el-form ref="villageFormRef" :model="villageFormData" :rules="villageFormRules" label-width="80px">
        <el-form-item label="编码" prop="code">
          <el-input v-model="villageFormData.code" placeholder="请输入村组编码" />
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="villageFormData.name" placeholder="请输入村组名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="villageDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleVillageSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="wellTypeDialogVisible" :title="wellTypeDialogTitle" width="400px" destroy-on-close>
      <el-form ref="wellTypeFormRef" :model="wellTypeFormData" :rules="wellTypeFormRules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="wellTypeFormData.name" placeholder="请输入井类型名称" />
        </el-form-item>
        <el-form-item label="巡检周期" prop="inspection_cycle_days">
          <el-input-number v-model="wellTypeFormData.inspection_cycle_days" :min="1" :max="365" style="width: 100%" />
          <span style="color: #909399; font-size: 12px">单位：天</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="wellTypeDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleWellTypeSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="standardDialogVisible" :title="standardDialogTitle" width="500px" destroy-on-close>
      <el-form ref="standardFormRef" :model="standardFormData" :rules="standardFormRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="指标编码" prop="indicator_code">
              <el-input v-model="standardFormData.indicator_code" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="指标名称" prop="indicator_name">
              <el-input v-model="standardFormData.indicator_name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分类" prop="category">
              <el-select v-model="standardFormData.category" style="width: 100%">
                <el-option label="微生物" value="微生物" />
                <el-option label="毒理" value="毒理" />
                <el-option label="感官" value="感官" />
                <el-option label="一般化学" value="一般化学" />
                <el-option label="放射性" value="放射性" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-input-number v-model="standardFormData.priority" :min="1" :max="10" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="单位" prop="unit">
              <el-input v-model="standardFormData.unit" placeholder="如 mg/L" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="比较方式" prop="comparison_type">
              <el-select v-model="standardFormData.comparison_type" style="width: 100%">
                <el-option label="<=" value="<=" />
                <el-option label=">=" value=">=" />
                <el-option label="<" value="<" />
                <el-option label=">" value=">" />
                <el-option label="==" value="==" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="限值" prop="limit_value">
              <el-input-number v-model="standardFormData.limit_value" :precision="4" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="standardDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleStandardSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getVillages, createVillage, updateVillage, deleteVillage,
  getWellTypes, createWellType, updateWellType, deleteWellType,
  getWaterQualityStandards, createWaterQualityStandard, updateWaterQualityStandard, deleteWaterQualityStandard
} from '../../api/masterData'
import dayjs from 'dayjs'

const activeTab = ref('village')
const categoryFilter = ref('')
const villageList = ref([])
const wellTypeList = ref([])
const standardList = ref([])

const villageDialogVisible = ref(false)
const villageDialogTitle = ref('')
const wellTypeDialogVisible = ref(false)
const wellTypeDialogTitle = ref('')
const standardDialogVisible = ref(false)
const standardDialogTitle = ref('')
const isEdit = ref(false)
const editId = ref(null)
const submitLoading = ref(false)

const villageFormRef = ref()
const wellTypeFormRef = ref()
const standardFormRef = ref()

const villageFormData = reactive({
  code: '',
  name: ''
})

const wellTypeFormData = reactive({
  name: '',
  inspection_cycle_days: 30
})

const standardFormData = reactive({
  indicator_code: '',
  indicator_name: '',
  category: '一般化学',
  unit: '',
  comparison_type: '<=',
  limit_value: 0,
  priority: 1
})

const villageFormRules = {
  code: [{ required: true, message: '请输入村组编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入村组名称', trigger: 'blur' }]
}

const wellTypeFormRules = {
  name: [{ required: true, message: '请输入井类型名称', trigger: 'blur' }],
  inspection_cycle_days: [{ required: true, message: '请输入巡检周期', trigger: 'blur' }]
}

const standardFormRules = {
  indicator_code: [{ required: true, message: '请输入指标编码', trigger: 'blur' }],
  indicator_name: [{ required: true, message: '请输入指标名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  unit: [{ required: true, message: '请输入单位', trigger: 'blur' }],
  comparison_type: [{ required: true, message: '请选择比较方式', trigger: 'change' }],
  limit_value: [{ required: true, message: '请输入限值', trigger: 'blur' }],
  priority: [{ required: true, message: '请输入优先级', trigger: 'blur' }]
}

const formatDateTime = (date) => dayjs(date).format('YYYY-MM-DD HH:mm:ss')

const getCategoryType = (category) => {
  const map = {
    '微生物': 'danger',
    '毒理': 'warning',
    '感官': 'info',
    '一般化学': 'primary',
    '放射性': 'success'
  }
  return map[category] || 'info'
}

const loadVillages = async () => {
  try {
    const res = await getVillages()
    villageList.value = res
  } catch (error) {
    ElMessage.error('加载村组数据失败')
  }
}

const loadWellTypes = async () => {
  try {
    const res = await getWellTypes()
    wellTypeList.value = res
  } catch (error) {
    ElMessage.error('加载井类型数据失败')
  }
}

const loadStandards = async () => {
  try {
    const params = categoryFilter.value ? { category: categoryFilter.value } : {}
    const res = await getWaterQualityStandards(params)
    standardList.value = res
  } catch (error) {
    ElMessage.error('加载水质指标数据失败')
  }
}

const handleAddVillage = () => {
  isEdit.value = false
  villageDialogTitle.value = '新增村组'
  villageFormData.code = ''
  villageFormData.name = ''
  villageDialogVisible.value = true
}

const handleEditVillage = (row) => {
  isEdit.value = true
  editId.value = row.id
  villageDialogTitle.value = '编辑村组'
  villageFormData.code = row.code
  villageFormData.name = row.name
  villageDialogVisible.value = true
}

const handleDeleteVillage = (row) => {
  ElMessageBox.confirm(`确定要删除村组【${row.name}】吗？`, '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await deleteVillage(row.id)
      ElMessage.success('删除成功')
      loadVillages()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleVillageSubmit = async () => {
  try {
    await villageFormRef.value.validate()
    submitLoading.value = true
    if (isEdit.value) {
      await updateVillage(editId.value, villageFormData)
      ElMessage.success('更新成功')
    } else {
      await createVillage(villageFormData)
      ElMessage.success('创建成功')
    }
    villageDialogVisible.value = false
    loadVillages()
  } catch (error) {
    console.error(error)
  } finally {
    submitLoading.value = false
  }
}

const handleAddWellType = () => {
  isEdit.value = false
  wellTypeDialogTitle.value = '新增井类型'
  wellTypeFormData.name = ''
  wellTypeFormData.inspection_cycle_days = 30
  wellTypeDialogVisible.value = true
}

const handleEditWellType = (row) => {
  isEdit.value = true
  editId.value = row.id
  wellTypeDialogTitle.value = '编辑井类型'
  wellTypeFormData.name = row.name
  wellTypeFormData.inspection_cycle_days = row.inspection_cycle_days
  wellTypeDialogVisible.value = true
}

const handleDeleteWellType = (row) => {
  ElMessageBox.confirm(`确定要删除井类型【${row.name}】吗？`, '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await deleteWellType(row.id)
      ElMessage.success('删除成功')
      loadWellTypes()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleWellTypeSubmit = async () => {
  try {
    await wellTypeFormRef.value.validate()
    submitLoading.value = true
    if (isEdit.value) {
      await updateWellType(editId.value, wellTypeFormData)
      ElMessage.success('更新成功')
    } else {
      await createWellType(wellTypeFormData)
      ElMessage.success('创建成功')
    }
    wellTypeDialogVisible.value = false
    loadWellTypes()
  } catch (error) {
    console.error(error)
  } finally {
    submitLoading.value = false
  }
}

const handleAddStandard = () => {
  isEdit.value = false
  standardDialogTitle.value = '新增水质指标'
  Object.keys(standardFormData).forEach(key => {
    if (key === 'limit_value') standardFormData[key] = 0
    else if (key === 'priority') standardFormData[key] = 1
    else if (key === 'comparison_type') standardFormData[key] = '<='
    else if (key === 'category') standardFormData[key] = '一般化学'
    else standardFormData[key] = ''
  })
  standardDialogVisible.value = true
}

const handleEditStandard = (row) => {
  isEdit.value = true
  editId.value = row.id
  standardDialogTitle.value = '编辑水质指标'
  Object.keys(standardFormData).forEach(key => {
    standardFormData[key] = row[key]
  })
  standardDialogVisible.value = true
}

const handleDeleteStandard = (row) => {
  ElMessageBox.confirm(`确定要删除水质指标【${row.indicator_name}】吗？`, '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await deleteWaterQualityStandard(row.id)
      ElMessage.success('删除成功')
      loadStandards()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleStandardSubmit = async () => {
  try {
    await standardFormRef.value.validate()
    submitLoading.value = true
    if (isEdit.value) {
      await updateWaterQualityStandard(editId.value, standardFormData)
      ElMessage.success('更新成功')
    } else {
      await createWaterQualityStandard(standardFormData)
      ElMessage.success('创建成功')
    }
    standardDialogVisible.value = false
    loadStandards()
  } catch (error) {
    console.error(error)
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  loadVillages()
  loadWellTypes()
  loadStandards()
})
</script>

<style scoped>
.table-header {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}
</style>
