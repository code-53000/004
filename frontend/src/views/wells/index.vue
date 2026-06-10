<template>
  <div class="wells-page">
    <el-card>
      <div class="search-bar">
        <el-input v-model="searchForm.keyword" placeholder="搜索井编号/位置" style="width: 200px" clearable @keyup.enter="handleSearch" />
        <el-select v-model="searchForm.village_id" placeholder="选择村组" clearable style="width: 150px">
          <el-option v-for="v in villages" :key="v.id" :label="v.name" :value="v.id" />
        </el-select>
        <el-select v-model="searchForm.overdue_only" placeholder="是否逾期" clearable style="width: 120px">
          <el-option label="是" :value="1" />
          <el-option label="否" :value="0" />
        </el-select>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button type="primary" style="margin-left: auto" @click="handleAdd" v-if="userStore.role === 'supervisor'">
          <el-icon><Plus /></el-icon>
          新增水井
        </el-button>
      </div>

      <el-table :data="tableData" stripe style="width: 100%" :row-class-name="tableRowClassName">
        <el-table-column prop="well_code" label="井编号" width="120" fixed />
        <el-table-column prop="village_name" label="村组" width="100" />
        <el-table-column prop="well_type_name" label="类型" width="100" />
        <el-table-column prop="location" label="位置" min-width="180" show-overflow-tooltip />
        <el-table-column prop="household_count" label="供水户数" width="90" align="center" />
        <el-table-column label="设备状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.equipment_status === 'normal' ? 'success' : 'danger'" size="small">
              {{ getStatusText(row.equipment_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="井盖" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.cover_status === 'normal' ? 'success' : 'danger'" size="small">
              {{ getCoverStatus(row.cover_status) }}
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
        <el-table-column prop="hidden_dangers" label="问题隐患" min-width="150" show-overflow-tooltip />
        <el-table-column prop="last_inspection_date" label="上次巡检" width="110">
          <template #default="{ row }">
            {{ row.last_inspection_date ? formatDate(row.last_inspection_date) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="next_inspection_date" label="下次巡检" width="110">
          <template #default="{ row }">
            {{ row.next_inspection_date ? formatDate(row.next_inspection_date) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.inspection_overdue === 1" type="danger" size="small" effect="dark">
              已逾期
            </el-tag>
            <el-tag v-else type="success" size="small">正常</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">查看</el-button>
            <el-button type="primary" link size="small" @click="handleEdit(row)" v-if="userStore.role === 'supervisor'">编辑</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="井编号" prop="well_code">
              <el-input v-model="formData.well_code" :disabled="isEdit" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="村组" prop="village_id">
              <el-select v-model="formData.village_id" style="width: 100%">
                <el-option v-for="v in villages" :key="v.id" :label="v.name" :value="v.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="井类型" prop="well_type_id">
              <el-select v-model="formData.well_type_id" style="width: 100%">
                <el-option v-for="t in wellTypes" :key="t.id" :label="t.name" :value="t.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供水户数" prop="household_count">
              <el-input-number v-model="formData.household_count" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="位置" prop="location">
          <el-input v-model="formData.location" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="经度">
              <el-input v-model="formData.longitude" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="纬度">
              <el-input v-model="formData.latitude" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="井盖状态">
              <el-select v-model="formData.cover_status" style="width: 100%">
                <el-option label="正常" value="normal" />
                <el-option label="损坏" value="damaged" />
                <el-option label="丢失" value="missing" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="水泵状态">
              <el-select v-model="formData.pump_status" style="width: 100%">
                <el-option label="正常" value="normal" />
                <el-option label="故障" value="faulty" />
                <el-option label="离线" value="offline" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="排水状态">
              <el-select v-model="formData.drainage_status" style="width: 100%">
                <el-option label="正常" value="normal" />
                <el-option label="堵塞" value="blocked" />
                <el-option label="较差" value="poor" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="设备状态">
          <el-select v-model="formData.equipment_status" style="width: 100%">
            <el-option label="正常" value="normal" />
            <el-option label="故障" value="faulty" />
            <el-option label="维护中" value="maintenance" />
          </el-select>
        </el-form-item>
        <el-form-item label="问题隐患">
          <el-input v-model="formData.hidden_dangers" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="整改负责人">
          <el-input v-model="formData.rectification_responsible" />
        </el-form-item>
        <el-form-item label="照片地址">
          <el-input v-model="formData.photo_url" />
        </el-form-item>
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
import { getWells, createWell, updateWell, deleteWell } from '../../api/wells'
import { getVillages, getWellTypes } from '../../api/masterData'
import dayjs from 'dayjs'

const userStore = useUserStore()

const tableData = ref([])
const total = ref(0)
const villages = ref([])
const wellTypes = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref()

const searchForm = reactive({
  keyword: '',
  village_id: null,
  overdue_only: null
})

const pagination = reactive({
  page: 1,
  page_size: 10
})

const formData = reactive({
  well_code: '',
  village_id: null,
  well_type_id: null,
  location: '',
  longitude: '',
  latitude: '',
  household_count: 1,
  equipment_status: 'normal',
  cover_status: 'normal',
  pump_status: 'normal',
  drainage_status: 'normal',
  hidden_dangers: '',
  rectification_responsible: '',
  photo_url: ''
})

const formRules = {
  well_code: [{ required: true, message: '请输入井编号', trigger: 'blur' }],
  village_id: [{ required: true, message: '请选择村组', trigger: 'change' }],
  well_type_id: [{ required: true, message: '请选择井类型', trigger: 'change' }],
  location: [{ required: true, message: '请输入位置', trigger: 'blur' }],
  household_count: [{ required: true, message: '请输入供水户数', trigger: 'blur' }]
}

const tableRowClassName = ({ row }) => {
  if (row.inspection_overdue === 1) {
    return 'overdue-row'
  }
  return ''
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD')
}

const getStatusText = (status) => {
  const map = { normal: '正常', faulty: '故障', maintenance: '维护中' }
  return map[status] || status
}

const getCoverStatus = (status) => {
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

const loadMasterData = async () => {
  try {
    const [villageRes, typeRes] = await Promise.all([getVillages(), getWellTypes()])
    villages.value = villageRes
    wellTypes.value = typeRes
  } catch (error) {
    ElMessage.error('加载基础数据失败')
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
    if (!params.village_id) delete params.village_id
    if (params.overdue_only === null) delete params.overdue_only

    const res = await getWells(params)
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
  searchForm.village_id = null
  searchForm.overdue_only = null
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
  dialogTitle.value = '新增水井'
  Object.keys(formData).forEach(key => {
    if (key === 'household_count') formData[key] = 1
    else if (['equipment_status', 'cover_status', 'pump_status', 'drainage_status'].includes(key)) formData[key] = 'normal'
    else formData[key] = ''
  })
  formData.village_id = null
  formData.well_type_id = null
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑水井'
  Object.keys(formData).forEach(key => {
    formData[key] = row[key]
  })
  dialogVisible.value = true
}

const handleView = (row) => {
  ElMessageBox.alert(`
    <div style="line-height: 2">
      <p><strong>井编号：</strong>${row.well_code}</p>
      <p><strong>位置：</strong>${row.location}</p>
      <p><strong>村组：</strong>${row.village_name}</p>
      <p><strong>类型：</strong>${row.well_type_name}</p>
      <p><strong>供水户数：</strong>${row.household_count}</p>
      <p><strong>设备状态：</strong>${getStatusText(row.equipment_status)}</p>
      <p><strong>问题隐患：</strong>${row.hidden_dangers || '无'}</p>
      <p><strong>上次巡检：</strong>${row.last_inspection_date ? formatDate(row.last_inspection_date) : '-'}</p>
    </div>
  `, '水井详情', {
    dangerouslyUseHTMLString: true,
    confirmButtonText: '确定'
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除水井【${row.well_code}】吗？`, '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await deleteWell(row.id)
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
      await updateWell(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await createWell(formData)
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
  loadMasterData()
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

:deep(.overdue-row) {
  background-color: #fef0f0 !important;
}

:deep(.overdue-row:hover > td) {
  background-color: #fde2e2 !important;
}
</style>
