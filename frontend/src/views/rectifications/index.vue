<template>
  <div class="rectifications-page">
    <el-card>
      <div class="search-bar">
        <el-input v-model="searchForm.keyword" placeholder="搜索井编号/位置" style="width: 200px" clearable @keyup.enter="handleSearch" />
        <el-select v-model="searchForm.status" placeholder="整改状态" clearable style="width: 120px">
          <el-option label="待整改" value="pending" />
          <el-option label="整改中" value="in_progress" />
          <el-option label="已完成" value="completed" />
          <el-option label="已验收" value="verified" />
        </el-select>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button type="primary" style="margin-left: auto" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增整改
        </el-button>
      </div>

      <el-table :data="tableData" stripe style="width: 100%">
        <el-table-column prop="well_code" label="井编号" width="100" fixed />
        <el-table-column prop="well_location" label="位置" min-width="150" show-overflow-tooltip />
        <el-table-column prop="inspection_date" label="发现日期" width="110">
          <template #default="{ row }">{{ formatDate(row.inspection_date) }}</template>
        </el-table-column>
        <el-table-column prop="rectification_date" label="完成日期" width="110">
          <template #default="{ row }">{{ row.rectification_date ? formatDate(row.rectification_date) : '-' }}</template>
        </el-table-column>
        <el-table-column prop="measures" label="整改措施" min-width="180" show-overflow-tooltip />
        <el-table-column prop="result" label="整改结果" min-width="150" show-overflow-tooltip />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="rectifier_name" label="整改人" width="80" />
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="巡检记录" prop="inspection_id">
          <el-select v-model="formData.inspection_id" style="width: 100%" filterable>
            <el-option
              v-for="r in pendingInspections"
              :key="r.id"
              :label="`${r.well_code} - ${r.well_location} (${formatDate(r.inspection_date)})`"
              :value="r.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="整改措施" prop="measures">
          <el-input v-model="formData.measures" type="textarea" :rows="3" placeholder="请描述具体的整改措施" />
        </el-form-item>
        <el-form-item label="整改结果">
          <el-input v-model="formData.result" type="textarea" :rows="2" placeholder="请描述整改结果" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="整改日期">
              <el-date-picker v-model="formData.rectification_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="formData.status" style="width: 100%">
                <el-option label="待整改" value="pending" />
                <el-option label="整改中" value="in_progress" />
                <el-option label="已完成" value="completed" />
                <el-option label="已验收" value="verified" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="整改后照片">
          <el-input v-model="formData.photo_url" placeholder="请输入照片地址" />
        </el-form-item>
        <el-form-item label="验收备注" v-if="formData.status === 'verified'">
          <el-input v-model="formData.verification_remark" type="textarea" :rows="2" placeholder="请填写验收备注" />
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
import { getRectifications, createRectification, updateRectification, deleteRectification } from '../../api/rectifications'
import { getInspections } from '../../api/inspections'
import dayjs from 'dayjs'

const userStore = useUserStore()

const tableData = ref([])
const total = ref(0)
const pendingInspections = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const submitLoading = ref(false)
const formRef = ref()

const searchForm = reactive({
  keyword: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10
})

const formData = reactive({
  inspection_id: null,
  rectification_date: '',
  measures: '',
  result: '',
  photo_url: '',
  status: 'in_progress',
  verification_remark: ''
})

const formRules = {
  inspection_id: [{ required: true, message: '请选择巡检记录', trigger: 'change' }],
  measures: [{ required: true, message: '请输入整改措施', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD')

const getStatusType = (status) => {
  const map = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success',
    verified: 'primary'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    pending: '待整改',
    in_progress: '整改中',
    completed: '已完成',
    verified: '已验收'
  }
  return map[status] || status
}

const canEdit = (row) => {
  if (userStore.role === 'supervisor') return true
  if (userStore.role === 'rectifier' && row.rectifier_id === userStore.userInfo.id) return true
  return false
}

const loadPendingInspections = async () => {
  try {
    const res = await getInspections({ page: 1, page_size: 1000, needs_rectification: 1 })
    pendingInspections.value = res.items
  } catch (error) {
    ElMessage.error('加载待整改巡检记录失败')
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

    const res = await getRectifications(params)
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
  dialogTitle.value = '新增整改记录'
  Object.keys(formData).forEach(key => {
    if (key === 'status') formData[key] = 'in_progress'
    else formData[key] = ''
  })
  formData.inspection_id = null
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑整改记录'
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
      <p><strong>发现日期：</strong>${formatDate(row.inspection_date)}</p>
      <p><strong>整改措施：</strong>${row.measures}</p>
      <p><strong>整改结果：</strong>${row.result || '-'}</p>
      <p><strong>完成日期：</strong>${row.rectification_date ? formatDate(row.rectification_date) : '-'}</p>
      <p><strong>状态：</strong>${getStatusText(row.status)}</p>
      <p><strong>整改人：</strong>${row.rectifier_name}</p>
      <p v-if="row.verification_remark"><strong>验收备注：</strong>${row.verification_remark}</p>
    </div>
  `, '整改记录详情', {
    dangerouslyUseHTMLString: true,
    confirmButtonText: '确定'
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除这条整改记录吗？', '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await deleteRectification(row.id)
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
      await updateRectification(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await createRectification(formData)
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
  loadPendingInspections()
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
