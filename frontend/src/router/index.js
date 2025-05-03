import { createRouter, createWebHashHistory } from 'vue-router'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/attendance',
    name: 'Attendance',
    component: () => import('../views/attendance/Index.vue'),
    meta: { requiresAuth: true, title: '考勤管理' }
  },
  {
    path: '/employee',
    name: 'Employee',
    component: () => import('../views/employee/Index.vue'),
    meta: { title: '员工管理' }
  },
  {
    path: '/salary-group',
    name: 'SalaryGroup',
    component: () => import('../views/salary-group/Index.vue'),
    meta: { title: '薪资组管理' }
  },
  {
    path: '/social-security',
    name: 'SocialSecurity',
    component: () => import('../views/social-security/Index.vue'),
    meta: { title: '社保管理' }
  },
  {
    path: '/salary-calculation',
    name: 'SalaryCalculation',
    component: () => import('../views/salary-calculation/Index.vue'),
    meta: { title: '薪资计算' }
  },
  {
    path: '/data-analysis',
    name: 'DataAnalysis',
    component: () => import('../views/data-analysis/Index.vue'),
    meta: { title: '数据分析' }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 路由前置守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - HR助手` : 'HR助手 - 薪酬管理软件'
  next()
})

export default router