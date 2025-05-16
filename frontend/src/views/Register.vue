<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <h2>用户注册</h2>
        </div>
      </template>
      <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" @submit.prevent="handleRegister">
        <el-form-item prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input type="password" v-model="registerForm.password" placeholder="请输入密码" show-password>
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input type="password" v-model="registerForm.confirmPassword" placeholder="请确认密码" show-password>
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" style="width: 100%;">注册</el-button>
        </el-form-item>
      </el-form>
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      <div class="login-link">
        已有账户? <router-link to="/login">立即登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { User, Lock } from '@element-plus/icons-vue';
import { register } from '@/api/authService';

const router = useRouter();
const registerFormRef = ref(null);
const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: '',
});
const loading = ref(false);
const error = ref('');

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'));
  } else {
    if (registerForm.value.confirmPassword !== '') {
      if (!registerFormRef.value) return;
      registerFormRef.value.validateField('confirmPassword');
    }
    callback();
  }
};
const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'));
  } else if (value !== registerForm.value.password) {
    callback(new Error("两次输入密码不一致!"));
  } else {
    callback();
  }
};

const registerRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ validator: validatePass, trigger: 'blur' }],
  confirmPassword: [{ validator: validatePass2, trigger: 'blur' }],
};

const handleRegister = async () => {
  if (!registerFormRef.value) return;
  registerFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      error.value = '';
      try {
                await register({ 
          username: registerForm.value.username, 
          password: registerForm.value.password 
        });
        ElMessage.success('注册成功');
        router.push('/login'); // 跳转到登录页面

      } catch (err) {
        error.value = err.response?.data?.message || '注册失败，请稍后再试';
        ElMessage.error(error.value);
      }
      loading.value = false;
    }
  });
};
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5; /* Optional: Add a background color */
}

.register-card {
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

.login-link {
  margin-top: 20px;
  text-align: center;
}
</style>