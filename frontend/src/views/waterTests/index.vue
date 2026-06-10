<template>
  <div class="water-tests-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-tabs v-model="activeTab" @tab-change="handleTabChange">
            <el-tab-pane label="检测批次" name="batches" />
            <el-tab-pane label="检测明细" name="items" />
          </el-tabs>
        </div>
      </template>

      <div v-if="activeTab === 'batches'">
        <div class="search-bar">
          <el-input v-model="searchForm.keyword" placeholder="搜索批次号/机构" style="width: 200px" clearable @keyup.enter="handleSearch" />
          <el-select v-model="searchForm.overall_result" placeholder="检测结果" clearable style="width: 120px">
            <el-option label="待出" value="pending" />
            <el-option label="合格" value="qualified" />
            <el-option label="不合格" value="unqualified" />
          </el-select>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="primary" style="margin-left: auto" @click="handleAddBatch">
            <el-icon><Plus /></el-icon>
            新增批次
          </el-button>
        </div>

        <el-table :data="batchTableData" stripe style="width: 100%">
          <el-table-column prop="batch_no" label="批次号" width="140" fixed />
          <el-table-column prop="test_date" label="检测日期" width="110">
            <template #default="{ row }">{{ formatDate(row.test_date) }}</template>
          </el-table-column>
          <el-table-column prop="sample_date" label="采样日期" width="110">
            <template #default="{ row }">{{ formatDate(row.sample_date) }}</template>
          </el-table-column>
          <el-table-column prop="lab_name" label="检测机构" min-width="120" show-overflow-tooltip />
          <el-table-column label="检测结果" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="getResultType(row.overall_result)" size="small">
                {{ getResultText(row.overall_result) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="tester_name" label="送检人" width="80" />
          <el-table-column label="操作" width="200" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleViewBatch(row)">查看详情</el-button>
              <el-button type="success" link size="small" @click="handleAddItem(row)" v-if="canEditBatch(row)">添加检测项</el-button>
              <el-button type="danger" link size="small" @click="handleDeleteBatch(row)" v-if="userStore.role === 'supervisor'">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          style="margin-top: 20px; justify-content: flex-end"
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="batchTotal"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pagination.page_size"
          :current-page="pagination.page"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <div v-else>
        <div class="search-bar">
          <el-input v-model="itemSearchForm.keyword" placeholder="搜索井编号/位置/指标" style="width: 220px" clearable @keyup.enter="handleItemSearch" />
          <el-select v-model="itemSearchForm.is_qualified" placeholder="是否合格" clearable style="width: 100px">
            <el-option label="合格" :value="1" />
            <el-option label="不合格" :value="0" />
          </el-select>
          <el-button type="primary" @click="handleItemSearch">搜索</el-button>
          <el-button @click="handleItemReset">重置</el-button>
        </div>

        <el-table :data="itemTableData" stripe style="width: 100%">
          <el-table-column prop="well_code" label="井编号" width="100" fixed />
          <el-table-column prop="well_location" label="位置" min-width="140" show-overflow-tooltip />
          <el-table-column prop="indicator_name" label="检测指标" width="120" />
          <el-table-column label="检测结果" width="180">
            <template #default="{ row }">
              <span :class="{ 'text-danger': row.is_qualified === 0 }">
                {{ row.measured_value }} {{ row.unit }}
              </span>
              <el-tag :type="row.is_qualified === 1 ? 'success' : 'danger'" size="small" style="margin-left: 10px">
                {{ row.is_qualified === 1 ? '合格' : '不合格' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="限值" width="120">
            <template #default="{ row }">
              {{ row.comparison_type }} {{ row.limit_value }} {{ row.unit }}
            </template>
          </el-table-column>
          <el-table-column prop="judgment_basis" label="判定依据" min-width="200" show-overflow-tooltip />
          <el-table-column prop="created_at" label="录入时间" width="160">
            <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="80" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="danger" link size="small" @click="handleDeleteItem(row)" v-if="userStore.role === 'supervisor'">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          style="margin-top: 20px; justify-content: flex-end"
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="itemTotal"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="itemPagination.page_size"
          :current-page="itemPagination.page"
          @size-change="handleItemSizeChange"
          @current-change="handleItemCurrentChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="batchDialogVisible" :title="batchDialogTitle" width="500px" destroy-on-close>
      <el-form ref="batchFormRef" :model="batchFormData" :rules="batchFormRules" label-width="100px">
        <el-form-item label="批次号" prop="batch_no">
          <el-input v-model="batchFormData.batch_no" placeholder="请输入批次号" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="采样日期" prop="sample_date">
              <el-date-picker v-model="batchFormData.sample_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="检测日期" prop="test_date">
              <el-date-picker v-model="batchFormData.test_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="检测机构">
          <el-input v-model="batchFormData.lab_name" placeholder="请输入检测机构名称" />
        </el-form-item>
        <el-form-item label="报告地址">
          <el-input v-model="batchFormData.report_url" placeholder="请输入检测报告地址" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="batchFormData.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleBatchSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="itemDialogVisible" title="添加检测项" width="600px" destroy-on-close>
      <el-form ref="itemFormRef" :model="itemFormData" :rules="itemFormRules" label-width="100px">
        <el-form-item label="水井" prop="well_id">
          <el-select v-model="itemFormData.well_id" style="width: 100%" filterable>
            <el-option v-for="w in wells" :key="w.id" :label="`${w.well_code} - ${w.location}`" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="检测指标" prop="standard_id">
          <el-select v-model="itemFormData.standard_id" style="width: 100%" filterable>
            <el-option
              v-for="s in standards"
              :key="s.id"
              :label="`${s.indicator_name} (${s.limit_value}${s.unit} ${s.comparison_type})`"
              :value="s.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="检测值" prop="measured_value">
          <el-input-number v-model="itemFormData.measured_value" :precision="4" :step="0.1" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="itemDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleItemSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="batchDetailVisible" title="批次详情" width="900px" destroy-on-close>
      <div v-if="currentBatch">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="批次号">{{ currentBatch.batch_no }}</el-descriptions-item>
          <el-descriptions-item label="检测结果">
            <el-tag :type="getResultType(currentBatch.overall_result)" size="small">
              {{ getResultText(currentBatch.overall_result) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="采样日期">{{ formatDate(currentBatch.sample_date) }}</el-descriptions-item>
          <el-descriptions-item label="检测日期">{{ formatDate(currentBatch.test_date) }}</el-descriptions-item>
          <el-descriptions-item label="检测机构">{{ currentBatch.lab_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="送检人">{{ currentBatch.tester_name }}</el-descriptions-item>
          <el-descriptions-item label="报告地址" :span="2">
            <a v-if="currentBatch.report_url" :href="currentBatch.report_url" target="_blank">{{ currentBatch.report_url }}</a>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ currentBatch.remark || '-' }}</el-descriptions-item>
        </el-descriptions>

        <h4 style="margin: 20px 0 10px 0">检测明细</h4>
        <el-table :data="currentBatch.test_items" stripe style="width: 100%">
          <el-table-column prop="well_code" label="井编号" width="100" />
          <el-table-column prop="well_location" label="位置" min-width="140" show-overflow-tooltip />
          <el-table-column prop="indicator_name" label="检测指标" width="120" />
          <el-table-column label="检测值" width="120">
            <template #default="{ row }">{{ row.measured_value }} {{ row.unit }}</template>
          </el-table-column>
          <el-table-column label="限值" width="140">
            <template #default="{ row }">
              {{ row.comparison_type }} {{ row.limit_value }} {{ row.unit }}
            </template>
          </el-table-column>
          <el-table-column label="结果" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_qualified === 1 ? 'success' : 'danger'" size="small">
                {{ row.is_qualified === 1 ? '合格' : '不合格' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="judgment_basis" label="判定依据" min-width="180" show-overflow-tooltip />
        </el-table>
        <el-empty v-if="!currentBatch.test_items || currentBatch.test_items.length === 0" description="暂无检测数据" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useUserStore } from '../../store/user'
import {
  getTestBatches, getTestBatch, createTestBatch, addTestItem,
  getTestItems, deleteTestBatch, deleteTestItem
} from '../../api/waterTests'
import { getWells } from '../../api/wells'
import { getWaterQualityStandards } from '../../api/masterData'
import dayjs from 'dayjs'

const userStore = useUserStore()

const activeTab = ref('batches')
const batchTableData = ref([])
const batchTotal = ref(0)
const itemTableData = ref([])
const itemTotal = ref(0)
const wells = ref([])
const standards = ref([])

const batchDialogVisible = ref(false)
const batchDialogTitle = ref('')
const itemDialogVisible = ref(false)
const batchDetailVisible = ref(false)
const currentBatch = ref(null)
const currentBatchId = ref(null)
const submitLoading = ref(false)
const batchFormRef = ref()
const itemFormRef = ref()

const searchForm = reactive({
  keyword: '',
  overall_result: ''
})

const itemSearchForm = reactive({
  keyword: '',
  is_qualified: null
})

const pagination = reactive({
  page: 1,
  page_size: 10
})

const itemPagination = reactive({
  page: 1,
  page_size: 10
})

const batchFormData = reactive({
  batch_no: '',
  test_date: '',
  sample_date: '',
  lab_name: '',
  report_url: '',
  remark: ''
})

const itemFormData = reactive({
  well_id: null,
  standard_id: null,
  measured_value: 0
})

const batchFormRules = {
  batch_no: [{ required: true, message: '请输入批次号', trigger: 'blur' }],
  test_date: [{ required: true, message: '请选择检测日期', trigger: 'change' }],
  sample_date: [{ required: true, message: '请选择采样日期', trigger: 'change' }]
}

const itemFormRules = {
  well_id: [{ required: true, message: '请选择水井', trigger: 'change' }],
  standard_id: [{ required: true, message: '请选择检测指标', trigger: 'change' }],
  measured_value: [{ required: true, message: '请输入检测值', trigger: 'blur' }]
}

const formatDate = (date) => dayjs(date).format('YYYY-MM-DD')
const formatDateTime = (date) => dayjs(date).format('YYYY-MM-DD HH:mm')

const getResultType = (result) => {
  const map = { pending: 'info', qualified: 'success', unqualified: 'danger' }
  return map[result] || 'info'
}

const getResultText = (result) => {
  const map = { pending: '待出', qualified: '合格', unqualified: '不合格' }
  return map[result] || result
}

const canEditBatch = (row) => {
  if (userStore.role === 'supervisor') return true
  if (userStore.role === 'tester' && row.tester_id === userStore.userInfo.id) return true
  return false
}

const loadMasterData = async () => {
  try {
    const [wellsRes, standardsRes] = await Promise.all([
      getWells({ page: 1, page_size: 1000 }),
      getWaterQualityStandards()
    ])
    wells.value = wellsRes.items
    standards.value = standardsRes
  } catch (error) {
    ElMessage.error('加载基础数据失败')
  }
}

const loadBatches = async () => {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    if (!params.keyword) delete params.keyword
    if (!params.overall_result) delete params.overall_result

    const res = await getTestBatches(params)
    batchTableData.value = res.items
    batchTotal.value = res.total
  } catch (error) {
    ElMessage.error('加载批次数据失败')
  }
}

const loadItems = async () => {
  try {
    const params = {
      page: itemPagination.page,
      page_size: itemPagination.page_size,
      ...itemSearchForm
    }
    if (!params.keyword) delete params.keyword
    if (params.is_qualified === null) delete params.is_qualified

    const res = await getTestItems(params)
    itemTableData.value = res.items
    itemTotal.value = res.total
  } catch (error) {
    ElMessage.error('加载明细数据失败')
  }
}

const handleTabChange = () => {
  if (activeTab.value === 'batches') {
    loadBatches()
  } else {
    loadItems()
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadBatches()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.overall_result = ''
  pagination.page = 1
  loadBatches()
}

const handleItemSearch = () => {
  itemPagination.page = 1
  loadItems()
}

const handleItemReset = () => {
  itemSearchForm.keyword = ''
  itemSearchForm.is_qualified = null
  itemPagination.page = 1
  loadItems()
}

const handleSizeChange = (size) => {
  pagination.page_size = size
  loadBatches()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadBatches()
}

const handleItemSizeChange = (size) => {
  itemPagination.page_size = size
  loadItems()
}

const handleItemCurrentChange = (page) => {
  itemPagination.page = page
  loadItems()
}

const handleAddBatch = () => {
  batchDialogTitle.value = '新增检测批次'
  Object.keys(batchFormData).forEach(key => {
    batchFormData[key] = ''
  })
  batchDialogVisible.value = true
}

const handleBatchSubmit = async () => {
  try {
    await batchFormRef.value.validate()
    submitLoading.value = true
    await createTestBatch(batchFormData)
    ElMessage.success('创建成功')
    batchDialogVisible.value = false
    loadBatches()
  } catch (error) {
    console.error(error)
  } finally {
    submitLoading.value = false
  }
}

const handleAddItem = (row) => {
  currentBatchId.value = row.id
  Object.keys(itemFormData).forEach(key => {
    if (key === 'measured_value') itemFormData[key] = 0
    else itemFormData[key] = null
  })
  itemDialogVisible.value = true
}

const handleItemSubmit = async () => {
  try {
    await itemFormRef.value.validate()
    submitLoading.value = true
    await addTestItem(currentBatchId.value, itemFormData)
    ElMessage.success('添加成功')
    itemDialogVisible.value = false
    loadBatches()
  } catch (error) {
    console.error(error)
  } finally {
    submitLoading.value = false
  }
}

const handleViewBatch = async (row) => {
  try {
    const res = await getTestBatch(row.id)
    currentBatch.value = res
    batchDetailVisible.value = true
  } catch (error) {
    ElMessage.error('加载详情失败')
  }
}

const handleDeleteBatch = (row) => {
  ElMessageBox.confirm(`确定要删除批次【${row.batch_no}】吗？`, '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await deleteTestBatch(row.id)
      ElMessage.success('删除成功')
      loadBatches()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleDeleteItem = (row) => {
  ElMessageBox.confirm('确定要删除这条检测记录吗？', '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await deleteTestItem(row.id)
      ElMessage.success('删除成功')
      loadItems()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  loadMasterData()
  loadBatches()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.text-danger {
  color: #f56c6c;
  font-weight: bold;
}
</style>
