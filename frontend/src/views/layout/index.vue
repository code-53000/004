<template>
  <div class="layout-container">
    <el-container>
      <el-aside width="220px" class="sidebar">
        <div class="logo">
          <el-icon size="28"><Watermelon /></el-icon>
          <span>水井管理系统</span>
        </div>
        <el-menu
          :default-active="$route.path"
          router
          class="sidebar-menu"
          background-color="#001529"
          text-color="#b8c4ce"
          active-text-color="#409EFF"
        >
          <template v-for="item in menuItems" :key="item.path">
            <el-menu-item :index="item.path">
              <el-icon><component :is="item.icon" /></el-icon>
              <span>{{ item.title }}</span>
            </el-menu-item>
          </template>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="header">
          <div class="header-left">
            <span class="page-title">{{ $route.meta.title }}</span>
          </div>
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-icon><UserFilled /></el-icon>
                <span>{{ userStore.userInfo?.full_name }}</span>
                <el-tag size="small" type="primary">{{ userStore.roleName }}</el-tag>
                <el-icon><CaretBottom /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        <el-main class="main-content">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { Watermelon, UserFilled, CaretBottom, HomeFilled, ClipboardCheck, Tools, Cpu, Setting } from '@element-plus/icons-vue'
import { useUserStore } from '../../store/user'

const router = useRouter()
const userStore = useUserStore()

const menuItems = computed(() => {
  const role = userStore.role
  const allMenus = [
    { path: '/dashboard', title: '首页', icon: 'HomeFilled', roles: ['inspector', 'rectifier', 'tester', 'supervisor'] },
    { path: '/wells', title: '水井管理', icon: 'Watermelon', roles: ['inspector', 'supervisor'] },
    { path: '/inspections', title: '巡检记录', icon: 'ClipboardCheck', roles: ['inspector', 'supervisor'] },
    { path: '/rectifications', title: '整改记录', icon: 'Tools', roles: ['rectifier', 'supervisor'] },
    { path: '/water-tests', title: '水质检测', icon: 'Cpu', roles: ['tester', 'supervisor'] },
    { path: '/master-data', title: '基础数据', icon: 'Setting', roles: ['supervisor'] }
  ]
  return allMenus.filter(item => item.roles.includes(role))
})

const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    }).catch(() => {})
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #001529;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 100;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid #1f3a53;
}

.sidebar-menu {
  border-right: none;
}

.header {
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  position: fixed;
  top: 0;
  right: 0;
  left: 220px;
  z-index: 99;
  height: 60px;
}

.page-title {
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #606266;
}

.main-content {
  margin-top: 60px;
  margin-left: 220px;
  background: #f0f2f5;
  min-height: calc(100vh - 60px);
  padding: 20px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
