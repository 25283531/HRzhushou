<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>用户登录</h2>
        </div>
      </template>
      <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input type="password" v-model="loginForm.password" placeholder="请输入密码" show-password>
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" style="width: 100%;">登录</el-button>
        </el-form-item>
      </el-form>
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      <div class="register-link">
        还没有账户? <router-link to="/register">立即注册</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { User, Lock } from '@element-plus/icons-vue';
import { login } from '@/api/authService';

const router = useRouter();
const loginFormRef = ref(null);
const loginForm = ref({
  username: '',
  password: '',
});
const loading = ref(false);
const error = ref('');

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
};

const handleLogin = async () => {
  if (!loginFormRef.value) return;
  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      error.value = '';
      try {
                const response = await login(loginForm.value);
        // localStorage.setItem('token', response.access_token); // authService.login already does this
        ElMessage.success('登录成功');
        router.push(router.currentRoute.value.query.redirect || '/'); // 跳转到首页或重定向地址
      } catch (err) {
        error.value = err.response?.data?.message || '登录失败，请稍后再试';
        ElMessage.error(error.value);
      }
      loading.value = false;
    }
  });
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5; /* Optional: Add a background color */
}

.login-card {
  width: 400px;
  padding: 20px;
}

.card-header h2 {
  text-align: center;
  margin-bottom: 20px;
}

.error-message {
  color: red;
  text-align: center;
  margin-top: 10px;
}

.register-link {
  margin-top: 20px;
  text-align: center;
}
</style>