# API请求故障排查指南

## 问题摘要

**错误类型**：功能Bug - API请求404错误

**复现步骤**：
1. 启动前端应用（端口5567）
2. 启动后端服务（端口3000）
3. 访问前端页面，多个API请求返回404错误

**影响范围**：所有API请求，包括员工数据、考勤数据、薪资组等核心功能

## 排查过程

### 1. 日志与错误分析

分析错误日志发现所有API请求都返回404 Not Found错误：
```
GET http://localhost:5567/api/employee/list?name=&employee_number=&department=&page=1&page_size=10&_t=1746283176164 404 (Not Found)
GET http://localhost:5567/api/attendance/list?month=2025-05&page=1&page_size=10 404 (Not Found)
GET http://localhost:5567/api/salary-groups 404 (Not Found)
```

### 2. 代码级调试

#### 前端API配置检查

检查前端API请求配置文件：
```javascript
// frontend/src/api/index.js
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})
```

#### 环境变量配置检查

检查前端环境变量配置：
```
# frontend/.env
VITE_API_BASE_URL=http://localhost:5566
```

#### Vite代理配置检查

检查Vite代理配置：
```javascript
// vite.config.js
server: {
  port: 5567,
  strictPort: true,
  proxy: {
    '/api': {
      target: 'http://localhost:3000', // 后端服务地址
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
      secure: false,
      ws: true
    }
  }
}
```

#### 后端路由配置检查

检查后端路由配置：
```javascript
// backend/src/index.js
app.use('/api', routes);
```

```javascript
// backend/src/routes/index.js
router.use('/employee', employeeRoutes);
router.use('/attendance', attendanceRoutes);
router.use('/salary', salaryRoutes);
router.use('/analysis', analysisRoutes);
router.use('/salary-groups', salaryGroupRoutes);
router.use('/position-levels', positionLevelsRoutes);
```

## 根因分析

通过5Why分析法追溯问题根源：

1. **为什么API请求返回404？**  
   因为请求路径与后端路由不匹配

2. **为什么路径不匹配？**  
   因为Vite代理配置中的`rewrite`规则会去除`/api`前缀，但后端路由已经包含了`/api`前缀

3. **为什么会有两个`/api`前缀？**  
   因为前端API请求配置中的`baseURL`设置为`/api`，而Vite代理又将`/api`前缀去除，导致最终请求路径错误

4. **为什么环境变量没有生效？**  
   因为环境变量配置的端口（5566）与实际运行端口（5567）不一致，导致回退到默认值`/api`

## 修复方案

### 1. 修复前端API配置

修改`frontend/src/api/index.js`文件：
```javascript
// 修改前
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  ...
})

// 修改后
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 10000,
  ...
})
```

### 2. 修复Vite代理配置

修改`vite.config.js`文件：
```javascript
// 修改前
proxy: {
  '/api': {
    target: 'http://localhost:3000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, ''),
    secure: false,
    ws: true
  }
}

// 修改后
proxy: {
  '/api': {
    target: 'http://localhost:3000',
    changeOrigin: true,
    // 不再去除/api前缀，因为后端路由已经包含了/api前缀
    // rewrite: (path) => path.replace(/^\/api/, ''),
    secure: false,
    ws: true
  }
}
```

### 3. 更新环境变量配置（可选）

修改`frontend/.env`文件，确保端口一致：
```
# 修改前
VITE_API_BASE_URL=http://localhost:5566

# 修改后
VITE_API_BASE_URL=http://localhost:5567
```

## 验证步骤

1. 重启前端开发服务器：`npm run dev`
2. 重启后端服务器：`cd backend && npm start`
3. 访问前端页面，验证API请求是否正常返回数据

## 预防措施

1. 添加API路径自动化测试，确保前后端路径配置一致
2. 在CI/CD流程中集成`check-api-paths.js`脚本，防止硬编码的API路径
3. 统一环境变量命名和使用规范，避免配置不一致
4. 完善API请求错误处理机制，提供更明确的错误信息