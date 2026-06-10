import { defineStore } from 'pinia'
import { login as loginApi, getCurrentUser } from '../api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: null
  }),
  getters: {
    role: (state) => state.userInfo?.role || '',
    roleName: (state) => {
      const roleMap = {
        'inspector': '巡检员',
        'rectifier': '整改员',
        'tester': '送检员',
        'supervisor': '监管员'
      }
      return roleMap[state.userInfo?.role] || ''
    }
  },
  actions: {
    async login(loginForm) {
      const res = await loginApi(loginForm)
      this.token = res.access_token
      this.userInfo = res.user
      localStorage.setItem('token', res.access_token)
      return res
    },
    async getUserInfo() {
      const res = await getCurrentUser()
      this.userInfo = res
      return res
    },
    logout() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('token')
    }
  }
})
