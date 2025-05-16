<template>
  <div class="app-container">
    <el-container>
      <el-aside width="200px">
        <div class="logo-container">
          <h2>HR助手</h2>
        </div>
        <el-menu
          router
          :default-active="$route.path"
          class="el-menu-vertical"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF">
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/attendance">
            <el-icon><Calendar /></el-icon>
            <span>考勤管理</span>
          </el-menu-item>
          <el-menu-item index="/attendance-rule-setting">
            <el-icon><Setting /></el-icon>
            <span>考勤规则设置</span>
          </el-menu-item>
          <el-menu-item index="/employee">
            <el-icon><User /></el-icon>
            <span>员工管理</span>
          </el-menu-item>
          <el-menu-item index="/position-levels">
            <el-icon><Rank /></el-icon>
            <span>职位职级</span>
          </el-menu-item>
          <el-menu-item index="/salary-group">
            <el-icon><Money /></el-icon>
            <span>薪资组管理</span>
          </el-menu-item>
          <el-menu-item index="/salary-items">
            <el-icon><List /></el-icon>
            <span>薪酬项管理</span>
          </el-menu-item>
          <el-menu-item index="/matching-rules">
            <el-icon><Setting /></el-icon>
            <span>匹配规则管理</span>
          </el-menu-item>
          <el-menu-item index="/social-security">
            <el-icon><Service /></el-icon>
            <span>社保管理</span>
          </el-menu-item>
          <el-menu-item index="/salary-calculation">
            <el-icon><Document /></el-icon>
            <span>薪资计算</span>
          </el-menu-item>
          <el-menu-item index="/data-analysis">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据分析</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header>
          <div class="header-right">
            <el-dropdown v-if="isLoggedIn">
              <span class="el-dropdown-link">
                <el-icon><UserFilled /></el-icon> {{ username }}
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>设置</el-dropdown-item>
                  <el-dropdown-item @click="handleLogout">
                    <el-icon><SwitchButton /></el-icon>退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <div v-else>
              <el-button type="primary" link @click="router.push('/login')">登录</el-button>
              <el-divider direction="vertical"></el-divider>
              <el-button type="primary" link @click="router.push('/register')">注册</el-button>
            </div>
          </div>
        </el-header>
        <el-main>
          <router-view />
        </el-main>
        <el-footer>
          <div class="footer-content">
            HR助手 &copy; {{ new Date().getFullYear() }} - 薪酬管理软件
          </div>
        </el-footer>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { HomeFilled, Calendar, User, Money, Service, Document, DataAnalysis, ArrowDown, List, Setting, Rank, SwitchButton, UserFilled } from '@element-plus/icons-vue';
import { isAuthenticated, logout as performLogout } from '@/api/authService';

const router = useRouter();
const isLoggedIn = ref(isAuthenticated());
// In a real app, you might fetch user details and store them
const username = ref(''); // Placeholder for username

const checkAuthStatus = () => {
  isLoggedIn.value = isAuthenticated();
  if (isLoggedIn.value) {
    // Potentially decode token to get username or fetch from an endpoint
    // For now, let's assume a generic user or retrieve from localStorage if stored
    const token = localStorage.getItem('token');
    if (token) {
        try {
            // Basic JWT decode (not secure for sensitive data, just for display)
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));
            const decodedToken = JSON.parse(jsonPayload);
            // Assuming the token has a 'sub' (subject) claim for user ID or username
            // Or if you store username directly after login
            username.value = decodedToken.sub || '用户'; 
        } catch (e) {
            username.value = '用户'; // Fallback
            console.error('Error decoding token:', e);
        }
    } else {
        username.value = '用户';
    }
  } else {
    username.value = '';
  }
};

onMounted(() => {
  checkAuthStatus();
  // Listen for storage changes to update login status (e.g., if logged out in another tab)
  window.addEventListener('storage', checkAuthStatus);
  // Also, re-check on route changes, especially after login/logout actions
  router.afterEach(() => {
    checkAuthStatus();
  });
});

const handleLogout = () => {
  performLogout();
  isLoggedIn.value = false;
  username.value = '';
  router.push('/login');
};
</script>

<style scoped>
.app-container {
  height: 100vh;
  width: 100%;
}

.el-header {
  background-color: #fff;
  color: #333;
  line-height: 60px;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.el-aside {
  background-color: #304156;
  color: #bfcbd9;
}

.el-main {
  background-color: #f0f2f5;
  color: #333;
  padding: 20px;
}

.el-footer {
  background-color: #fff;
  color: #333;
  text-align: center;
  line-height: 60px;
  border-top: 1px solid #e6e6e6;
}

.logo-container {
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #fff;
}

.header-right {
  margin-right: 20px;
}

.el-dropdown-link {
  cursor: pointer;
  color: #409EFF;
  display: flex;
  align-items: center;
}

.footer-content {
  font-size: 14px;
  color: #666;
}
</style>