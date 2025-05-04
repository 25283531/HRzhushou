# API路径规范指南

## 概述

为确保项目中API请求路径的一致性和可维护性，本文档提供了API路径规范指南。遵循这些规范可以避免硬编码的API前缀问题，提高代码质量和可维护性。

## API路径规范

### 基本原则

1. **使用相对路径**：所有API请求应使用相对路径，不要在路径中硬编码`/api`前缀
2. **统一配置**：API基础URL应通过环境变量或配置文件统一设置
3. **一致性**：保持所有API调用的一致格式
4. **全面覆盖**：规范适用于所有API调用，包括常规请求、文件上传等各种场景

### 正确示例

```javascript
// 正确：使用相对路径
api.get('/employee/list')

// 正确：使用模板字符串构建路径，不包含/api前缀
api.put(`/employee/${id}`)

// 正确：在axios实例中使用环境变量设置baseURL
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || ''
})
```

### 错误示例

```javascript
// 错误：路径中包含硬编码的/api前缀
api.get('/api/employee/list')

// 错误：在模板字符串中包含/api前缀
api.put(`/api/employee/${id}`)

// 错误：在axios实例中硬编码/api前缀
const service = axios.create({
  baseURL: '/api'
})
```

## 环境配置

### .env文件配置

```
# 正确配置：不包含/api后缀
VITE_API_BASE_URL=http://localhost:5566

# 错误配置：包含/api后缀
VITE_API_BASE_URL=http://localhost:5566/api
```

### Vite代理配置

```javascript
// 正确配置：将/api前缀替换为空字符串
proxy: {
  '/api': {
    target: 'http://localhost:3000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, ''),
  }
}

// 错误配置：将/api前缀替换为另一个包含/api的路径
proxy: {
  '/api': {
    target: 'http://localhost:3000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, '/api'),
  }
}
```

## 特殊组件的API路径规范

### 文件上传组件

在使用Element Plus的上传组件或其他上传组件时，也需要遵循相同的API路径规范：

```html
<!-- 正确：使用相对路径 -->
<el-upload
  action="/attendance/import"
  :auto-upload="true">
</el-upload>

<!-- 错误：使用硬编码的/api前缀 -->
<el-upload
  action="/api/attendance/import"
  :auto-upload="true">
</el-upload>
```

### 动态设置上传路径

对于需要动态设置上传路径的场景，建议使用计算属性或方法：

```javascript
// 在Vue组件中
const uploadUrl = computed(() => {
  return `/attendance/import?type=${type}`
})
```

```html
<el-upload :action="uploadUrl"></el-upload>
```

## PR审查清单

在审查PR时，请检查以下内容：

- [ ] API请求路径不包含硬编码的`/api`前缀
- [ ] Axios实例的`baseURL`配置不包含硬编码的`/api`前缀
- [ ] 环境变量中的API基础URL不包含`/api`后缀
- [ ] Vite代理配置中正确处理了路径重写
- [ ] 所有API调用保持一致的路径格式
- [ ] 上传组件的action属性不包含硬编码的`/api`前缀

## 自动化测试

项目中已添加API路径验证工具，可以用于检查API请求路径是否符合规范：

```javascript
// 导入验证工具
import { validateApiPath, validateApiModule } from '../utils/apiPathValidator';

// 验证单个路径
const isValid = validateApiPath('/employee/list'); // 应返回true
const isInvalid = validateApiPath('/api/employee/list'); // 应返回false

// 验证整个API模块
const moduleResult = validateApiModule(apiModule);
if (!moduleResult.valid) {
  console.error('API模块中存在不规范的路径:', moduleResult.errors);
}
```

## 常见问题解决

1. **问题**：修改API路径后，请求返回404
   **解决方案**：检查Vite代理配置是否正确，确保路径重写规则将`/api`前缀正确替换

2. **问题**：环境变量不生效
   **解决方案**：确保在使用环境变量时使用了`import.meta.env`前缀，并提供了默认值

3. **问题**：不同环境下API路径不一致
   **解决方案**：为不同环境创建对应的`.env`文件（如`.env.development`、`.env.production`）

4. **问题**：上传组件的action属性设置后请求失败
   **解决方案**：确保上传路径不包含`/api`前缀，并检查后端是否正确处理了上传请求

5. **问题**：自动化检查工具未能检测到上传组件中的硬编码API前缀
   **解决方案**：已更新检查工具，现在可以检测常规API调用和上传组件中的硬编码前缀

## 结论

遵循本文档中的API路径规范，可以确保项目中的API请求路径保持一致性和可维护性，避免硬编码的API前缀问题。在代码审查中严格执行这些规范，可以提高代码质量和开发效率。