import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../store/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login/index.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/',
    component: () => import('../views/layout/index.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/dashboard/index.vue'),
        meta: { title: '首页', icon: 'HomeFilled', roles: ['inspector', 'rectifier', 'tester', 'supervisor'] }
      },
      {
        path: 'wells',
        name: 'Wells',
        component: () => import('../views/wells/index.vue'),
        meta: { title: '水井管理', icon: 'Watermelon', roles: ['inspector', 'supervisor'] }
      },
      {
        path: 'inspections',
        name: 'Inspections',
        component: () => import('../views/inspections/index.vue'),
        meta: { title: '巡检记录', icon: 'ClipboardCheck', roles: ['inspector', 'supervisor'] }
      },
      {
        path: 'rectifications',
        name: 'Rectifications',
        component: () => import('../views/rectifications/index.vue'),
        meta: { title: '整改记录', icon: 'Tools', roles: ['rectifier', 'supervisor'] }
      },
      {
        path: 'water-tests',
        name: 'WaterTests',
        component: () => import('../views/waterTests/index.vue'),
        meta: { title: '水质检测', icon: 'Cpu', roles: ['tester', 'supervisor'] }
      },
      {
        path: 'master-data',
        name: 'MasterData',
        component: () => import('../views/masterData/index.vue'),
        meta: { title: '基础数据', icon: 'Setting', roles: ['supervisor'] }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 农村自备水井管理系统` : '农村自备水井管理系统'
  next()
})

export default router
