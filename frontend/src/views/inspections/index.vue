<template>
  <div class="inspections-page">
    <el-card>
      <div class="search-bar">
        <el-input v-model="searchForm.keyword" placeholder="搜索井编号/位置" style="width: 200px" clearable @keyup.enter="handleSearch" />
        <el-select v-model="searchForm.status" placeholder="巡检状态" clearable style="width: 120px">
          <el-option label="已完成" value="completed" />
          <el-option label="整改中" value="rectifying" />
          <el-option label="已整改" value="rectified" />
        </el-select>
        <el-select v-model="searchForm.needs_rectification" placeholder="是否需整改" clearable style="width: 120px">
          <el-option label="是" :value="1" />
          <el-option label="否" :value="0" />
        </el-select>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button type="primary" style="margin-left: auto" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增巡检
        </el-button>
      </div>

      <el-table :data="tableData" stripe style="width: 100%">
        <el-table-column prop="well_code" label="井编号" width="100" fixed />
        <el-table-column prop="well_location" label="位置" min-width="150" show-overflow-tooltip />
        <el-table-column prop="inspection_date" label="巡检日期" width="110">
          <template #default="{ row }">{{ formatDate(row.inspection_date) }}</template>
        </el-table-column>
        <el-table-column label="井盖" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.cover_status === 'normal' ? 'success' : 'danger'" size="small">
              {{ getStatusText(row.cover_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="水泵" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.pump_status === 'normal' ? 'success' : 'danger'" size="small">
              {{ getPumpStatus(row.pump_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="排水" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.drainage_status === 'normal' ? 'success' : 'warning'" size="small">
              {{ getDrainageStatus(row.drainage_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="设备" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.equipment_status === 'normal' ? 'success' : 'danger'" size="small">
              {{ getEquipmentStatus(row.equipment_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="余氯" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.residual_chlorine">{{ row.residual_chlorine }} mg/L</span>
            <span v-else>-</span>
            <el-tag v-if="row.residual_chlorine_status" :type="getChlorineType(row.residual_chlorine_status)" size="small" style="margin-left: 5px">
              {{ getChlorineText(row.residual_chlorine_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="hidden_dangers" label="问题隐患" min-width="150" show-overflow-tooltip />
        <el-table-column label="需整改" width="70" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.needs_rectification === 1" type="danger" size="small">是</el-tag>
            <el-tag v-else type="success" size="small">否</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getInspectionStatusType(row.status)" size="small">
              {{ getInspectionStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="inspector_name" label="巡检人" width="80" />
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">查看</el-button>
            <el-button type="primary" link size="small" @click="handleEdit(row)" v-if="canEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)" v-if="userStore.role === 'supervisor'">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        style="margin-top: 20px; justify-content: flex-end"
        background
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pagination.page_size"
        :current-page="pagination.page"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="水井" prop="well_id">
              <el-select v-model="formData.well_id" style="width: 100%" filterable>
                <el-option v-for="w in wells" :key="w.id" :label="`${w.well_code} - ${w.location}`" :value="w.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="巡检日期" prop="inspection_date">
              <el-date-picker v-model="formData.inspection_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="井盖状态" prop="cover_status">
              <el-select v-model="formData.cover_status" style="width: 100%">
                <el-option label="正常" value="normal" />
                <el-option label="损坏" value="damaged" />
                <el-option label="丢失" value="missing" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="水泵状态" prop="pump_status">
              <el-select v-model="formData.pump_status" style="width: 100%">
                <el-option label="正常" value="normal" />
                <el-option label="故障" value="faulty" />
                <el-option label="离线" value="offline" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="排水状态" prop="drainage_status">
              <el-select v-model="formData.drainage_status" style="width: 100%">
                <el-option label="正常" value="normal" />
                <el-option label="堵塞" value="blocked" />
                <el-option label="较差" value="poor" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备状态" prop="equipment_status">
              <el-select v-model="formData.equipment_status" style="width: 100%">
                <el-option label="正常" value="normal" />
                <el-option label="故障" value="faulty" />
                <el-option label="维护中" value="maintenance" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="余氯检测值">
              <el-input v-model="formData.residual_chlorine" placeholder="mg/L" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="现场照片">
          <el-input v-model="formData.photo_url" placeholder="请输入照片地址" />
        </el-form-item>
        <el-form-item label="问题隐患">
          <el-input v-model="formData.hidden_dangers" type="textarea" :rows="3" placeholder="请描述发现的问题隐患" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="需要整改" prop="needs_rectification">
              <el-radio-group v-model="formData.needs_rectification">
                <el-radio :value="0">否</el-radio>
                <el-radio :value="1">是</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="整改期限" v-if="formData.needs_rectification === 1">
              <el-date-picker v-model="formData.rectification_deadline" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useUserStore } from '../../store/user'
import { getInspections, createInspection, updateInspection, deleteInspection } from '../../api/inspections'
import { getWells } from '../../api/wells'
import dayjs from 'dayjs'

const userStore = useUserStore()

const tableData = ref([])
const total = ref(0)
const wells = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref()

const searchForm = reactive({
  keyword: '',
  status: '',
  needs_rectification: null
})

const pagination = reactive({
  page: 1,
  page_size: 10
})

const formData = reactive({
  well_id: null,
  inspection_date: '',
  cover_status: 'normal',
  pump_status: 'normal',
  drainage_status: 'normal',
  equipment_status: 'normal',
  photo_url: '',
  hidden_dangers: '',
  residual_chlorine: '',
  needs_rectification: 0,
  rectification_deadline: ''
})

const formRules = {
  well_id: [{ required: true, message: '请选择水井', trigger: 'change' }],
  inspection_date: [{ required: true, message: '请选择巡检日期', trigger: 'change' }],
  cover_status: [{ required: true, message: '请选择井盖状态', trigger: 'change' }],
  pump_status: [{ required: true, message: '请选择水泵状态', trigger: 'change' }],
  drainage_status: [{ required: true, message: '请选择排水状态', trigger: 'change' }],
  equipment_status: [{ required: true, message: '请选择设备状态', trigger: 'change' }],
  needs_rectification: [{ required: true, message: '请选择是否需要整改', trigger: 'change' }]
}

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD')

const getStatusText = (status) => {
  const map = { normal: '正常', damaged: '损坏', missing: '丢失' }
  return map[status] || status
}

const getPumpStatus = (status) => {
  const map = { normal: '正常', faulty: '故障', offline: '离线' }
  return map[status] || status
}

const getDrainageStatus = (status) => {
  const map = { normal: '正常', blocked: '堵塞', poor: '较差' }
  return map[status] || status
}

const getEquipmentStatus = (status) => {
  const map = { normal: '正常', faulty: '故障', maintenance: '维护中' }
  return map[status] || status
}

const getChlorineType = (status) => {
  const map = { normal: 'success', low: 'warning', high: 'danger', unknown: 'info' }
  return map[status] || 'info'
}

const getChlorineText = (status) => {
  const map = { normal: '正常', low: '偏低', high: '偏高', unknown: '未知' }
  return map[status] || status
}

const getInspectionStatusType = (status) => {
  const map = { completed: 'success', rectifying: 'warning', rectified: 'primary' }
  return map[status] || 'info'
}

const getInspectionStatusText = (status) => {
  const map = { completed: '已完成', rectifying: '整改中', rectified: '已整改' }
  return map[status] || status
}

const canEdit = (row) => {
  if (userStore.role === 'supervisor') return true
  if (userStore.role === 'inspector' && row.inspector_id === userStore.userInfo.id) return true
  return false
}

const loadWells = async () => {
  try {
    const res = await getWells({ page: 1, page_size: 1000 })
    wells.value = res.items
  } catch (error) {
    ElMessage.error('加载水井列表失败')
  }
}

const loadData = async () => {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    if (!params.keyword) delete params.keyword
    if (!params.status) delete params.status
    if (params.needs_rectification === null) delete params.needs_rectification

    const res = await getInspections(params)
    tableData.value = res.items
    total.value = res.total
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.status = ''
  searchForm.needs_rectification = null
  pagination.page = 1
  loadData()
}

const handleSizeChange = (size) => {
  pagination.page_size = size
  loadData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadData()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增巡检记录'
  Object.keys(formData).forEach(key => {
    if (key === 'needs_rectification') formData[key] = 0
    else if (['cover_status', 'pump_status', 'drainage_status', 'equipment_status'].includes(key)) formData[key] = 'normal'
    else formData[key] = ''
  })
  formData.well_id = null
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑巡检记录'
  Object.keys(formData).forEach(key => {
    formData[key] = row[key]
  })
  dialogVisible.value = true
}

const handleView = (row) => {
  ElMessageBox.alert(`
    <div style="line-height: 2">
      <p><strong>井编号：</strong>${row.well_code}</p>
      <p><strong>位置：</strong>${row.well_location}</p>
      <p><strong>巡检日期：</strong>${formatDate(row.inspection_date)}</p>
      <p><strong>井盖：</strong>${getStatusText(row.cover_status)}</p>
      <p><strong>水泵：</strong>${getPumpStatus(row.pump_status)}</p>
      <p><strong>排水：</strong>${getDrainageStatus(row.drainage_status)}</p>
      <p><strong>余氯：</strong>${row.residual_chlorine || '-'} mg/L</p>
      <p><strong>问题隐患：</strong>${row.hidden_dangers || '无'}</p>
      <p><strong>需要整改：</strong>${row.needs_rectification === 1 ? '是' : '否'}</p>
      <p><strong>状态：</strong>${getInspectionStatusText(row.status)}</p>
      <p><strong>巡检人：</strong>${row.inspector_name}</p>
    </div>
  `, '巡检记录详情', {
    dangerouslyUseHTMLString: true,
    confirmButtonText: '确定'
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除这条巡检记录吗？', '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await deleteInspection(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitLoading.value = true

    if (isEdit.value) {
      await updateInspection(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await createInspection(formData)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error(error)
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  loadWells()
  loadData()
})
</script>

<style scoped>
.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}
</style>
