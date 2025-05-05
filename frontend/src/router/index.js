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
    path: '/salary-items',
    name: 'SalaryItems',
    component: () => import('../views/salary/SalaryItems.vue'),
    meta: { title: '薪酬项管理' }
  },
  {
    path: '/matching-rules',
    name: 'MatchingRules',
    component: () => import('../views/salary/MatchingRules.vue'),
    meta: { title: '匹配规则管理' }
  },
  {
    path: '/position-levels',
    name: 'PositionLevels',
    component: () => import('../views/position/PositionLevels.vue'),
    meta: { title: '职位职级管理' }
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
  },
  {
    path: '/attendance-rule-setting',
    component: () => import('../views/attendance/AttendanceRuleSetting.vue')
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