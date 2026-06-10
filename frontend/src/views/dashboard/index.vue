<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon bg-blue">
              <el-icon size="30"><Watermelon /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.wellCount }}</div>
              <div class="stat-label">水井总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon bg-red">
              <el-icon size="30"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value" style="color: #f56c6c">{{ stats.overdueCount }}</div>
              <div class="stat-label">逾期未巡检</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon bg-orange">
              <el-icon size="30"><Tools /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value" style="color: #e6a23c">{{ stats.rectifyingCount }}</div>
              <div class="stat-label">整改中</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon bg-green">
              <el-icon size="30"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value" style="color: #67c23a">{{ stats.qualifiedRate }}%</div>
              <div class="stat-label">水质合格率</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>逾期未巡检水井</span>
            <el-tag type="danger" size="small" style="margin-left: 10px">{{ overdueWells.length }} 口</el-tag>
          </template>
          <el-table :data="overdueWells" stripe style="width: 100%">
            <el-table-column prop="well_code" label="井编号" width="120" />
            <el-table-column prop="location" label="位置" min-width="150" />
            <el-table-column prop="village_name" label="所属村组" width="100" />
            <el-table-column prop="next_inspection_date" label="应巡检日期" width="120">
              <template #default="{ row }">
                {{ formatDate(row.next_inspection_date) }}
              </template>
            </el-table-column>
            <el-table-column label="逾期状态" width="100">
              <template #default>
                <el-tag type="danger" size="small">已逾期</el-tag>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="overdueWells.length === 0" description="暂无逾期未巡检水井" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>待整改记录</span>
            <el-tag type="warning" size="small" style="margin-left: 10px">{{ pendingRectifications.length }} 条</el-tag>
          </template>
          <el-table :data="pendingRectifications" stripe style="width: 100%">
            <el-table-column prop="well_code" label="井编号" width="100" />
            <el-table-column prop="well_location" label="位置" min-width="120" />
            <el-table-column prop="inspection_date" label="发现日期" width="100">
              <template #default="{ row }">
                {{ formatDate(row.inspection_date) }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="pendingRectifications.length === 0" description="暂无待整改记录" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>最近水质检测不合格记录</span>
          </template>
          <el-table :data="recentUnqualifiedItems" stripe style="width: 100%">
            <el-table-column prop="well_code" label="井编号" width="120" />
            <el-table-column prop="well_location" label="位置" min-width="150" />
            <el-table-column prop="indicator_name" label="检测指标" width="120" />
            <el-table-column label="检测结果" width="200">
              <template #default="{ row }">
                <span class="unqualified-text">
                  {{ row.measured_value }} {{ row.unit }}
                </span>
                <el-tag type="danger" size="small" style="margin-left: 10px">不合格</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="judgment_basis" label="判定依据" min-width="200" />
            <el-table-column prop="created_at" label="检测时间" width="160">
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="recentUnqualifiedItems.length === 0" description="暂无不合格记录" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Watermelon, Warning, Tools, CircleCheck } from '@element-plus/icons-vue'
import { getWells } from '../../api/wells'
import { getRectifications } from '../../api/rectifications'
import { getTestItems } from '../../api/waterTests'
import dayjs from 'dayjs'

const stats = ref({
  wellCount: 0,
  overdueCount: 0,
  rectifyingCount: 0,
  qualifiedRate: 0
})

const overdueWells = ref([])
const pendingRectifications = ref([])
const recentUnqualifiedItems = ref([])

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD')
}

const formatDateTime = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const getStatusType = (status) => {
  const typeMap = {
    'pending': 'info',
    'in_progress': 'warning',
    'completed': 'success',
    'verified': 'success'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'pending': '待整改',
    'in_progress': '整改中',
    'completed': '已完成',
    'verified': '已验收'
  }
  return textMap[status] || status
}

const loadData = async () => {
  try {
    const [wellsRes, rectRes, itemsRes] = await Promise.all([
      getWells({ page: 1, page_size: 1000 }),
      getRectifications({ page: 1, page_size: 1000 }),
      getTestItems({ page: 1, page_size: 100 })
    ])

    stats.value.wellCount = wellsRes.total
    stats.value.overdueCount = wellsRes.items.filter(w => w.inspection_overdue === 1).length
    overdueWells.value = wellsRes.items.filter(w => w.inspection_overdue === 1).slice(0, 5)

    const pendingList = rectRes.items.filter(r => r.status === 'pending' || r.status === 'in_progress')
    stats.value.rectifyingCount = pendingList.length
    pendingRectifications.value = pendingList.slice(0, 5)

    const unqualifiedList = itemsRes.items.filter(i => i.is_qualified === 0)
    recentUnqualifiedItems.value = unqualifiedList.slice(0, 5)

    if (itemsRes.total > 0) {
      const qualifiedCount = itemsRes.items.filter(i => i.is_qualified === 1).length
      stats.value.qualifiedRate = Math.round((qualifiedCount / itemsRes.items.length) * 100)
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.stat-card {
  border-radius: 8px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.bg-blue {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.bg-red {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.bg-orange {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.bg-green {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.unqualified-text {
  color: #f56c6c;
  font-weight: bold;
}
</style>
