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
          <el-menu-item index="/employee">
            <el-icon><User /></el-icon>
            <span>员工管理</span>
          </el-menu-item>
          <el-menu-item index="/salary-group">
            <el-icon><Money /></el-icon>
            <span>薪资组管理</span>
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
            <el-dropdown>
              <span class="el-dropdown-link">
                管理员
                <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item>设置</el-dropdown-item>
                  <el-dropdown-item>退出</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
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
import { HomeFilled, Calendar, User, Money, Service, Document, DataAnalysis } from '@element-plus/icons-vue'
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