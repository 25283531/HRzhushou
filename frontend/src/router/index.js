import { createRouter, createWebHashHistory } from 'vue-router';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';

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
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { title: '注册' }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 路由前置守卫
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('token'); // 检查token是否存在

  if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
    // 如果路由需要认证但用户未认证，则重定向到登录页
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else if ((to.name === 'Login' || to.name === 'Register') && isAuthenticated) {
    // 如果用户已认证且尝试访问登录或注册页，则重定向到首页
    next({ name: 'Home' });
  } else {
    // 设置页面标题
    document.title = to.meta.title ? `${to.meta.title} - HR助手` : 'HR助手 - 薪酬管理软件';
    next();
  }
});

export default router