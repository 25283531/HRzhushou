/**
 * API路径验证工具
 * 用于检查API请求路径是否符合规范（不包含硬编码的/api前缀）
 */

/**
 * 验证API路径是否符合规范
 * @param {string} path - API路径
 * @returns {boolean} - 是否符合规范
 */
export function validateApiPath(path) {
  // API路径不应该以/api开头
  if (path.startsWith('/api/')) {
    console.error(`API路径不规范: ${path}，不应该包含硬编码的/api前缀`);
    return false;
  }
  return true;
}

/**
 * 批量验证API路径
 * @param {Object} apiModule - API模块对象
 * @returns {Object} - 验证结果，包含是否通过和错误信息
 */
export function validateApiModule(apiModule) {
  const errors = [];
  const functions = Object.keys(apiModule);
  
  for (const funcName of functions) {
    const func = apiModule[funcName];
    if (typeof func === 'function' && func.toString().includes('/api/')) {
      errors.push(`函数 ${funcName} 中包含硬编码的/api前缀`);
    }
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * PR审查指南 - API路径规范
 * 
 * 在审查PR时，请注意以下API路径规范：
 * 
 * 1. API请求路径不应包含硬编码的/api前缀
 * 2. 应使用相对路径，例如：'/employee/list'而不是'/api/employee/list'
 * 3. API基础URL应通过环境变量或配置文件设置
 * 4. Axios实例的baseURL不应硬编码包含/api
 * 
 * 常见错误示例：
 * - 错误：axios.get('/api/employee/list')
 * - 正确：axios.get('/employee/list')
 * 
 * - 错误：baseURL: '/api'
 * - 正确：baseURL: import.meta.env.VITE_API_BASE_URL || ''
 */

// 导出测试用例函数，用于自动化测试
export function testApiPaths(paths) {
  const results = paths.map(path => ({
    path,
    valid: validateApiPath(path),
    message: validateApiPath(path) ? '路径格式正确' : '路径不应包含/api前缀'
  }));
  
  return {
    allValid: results.every(r => r.valid),
    results
  };
}