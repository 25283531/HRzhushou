/**
 * API路径验证测试用例
 * 用于测试API请求路径是否符合规范（不包含硬编码的/api前缀）
 */
import { validateApiPath, validateApiModule, testApiPaths } from '../utils/apiPathValidator';

// 模拟API模块进行测试
const mockApiModule = {
  // 正确的API路径
  getEmployees: () => fetch('/employee/list'),
  getSalary: () => fetch('/salary/items'),
  
  // 错误的API路径（包含/api前缀）
  getWrongPath: () => fetch('/api/employee/list'),
};

// 测试validateApiPath函数
console.log('===== 测试单个API路径 =====');
const validPath = '/employee/list';
const invalidPath = '/api/employee/list';

console.log(`路径 ${validPath} 验证结果:`, validateApiPath(validPath) ? '通过' : '不通过');
console.log(`路径 ${invalidPath} 验证结果:`, validateApiPath(invalidPath) ? '通过' : '不通过');

// 测试validateApiModule函数
console.log('\n===== 测试API模块 =====');
const moduleResult = validateApiModule(mockApiModule);
console.log('API模块验证结果:', moduleResult.valid ? '通过' : '不通过');
if (!moduleResult.valid) {
  console.log('错误信息:', moduleResult.errors);
}

// 测试一组API路径
console.log('\n===== 测试一组API路径 =====');
const pathsToTest = [
  '/employee/list',
  '/salary/items',
  '/api/employee/list', // 错误路径
  '/position-levels/types',
  '/api/salary-items/rules', // 错误路径
];

const batchResults = testApiPaths(pathsToTest);
console.log('批量测试结果:', batchResults.allValid ? '全部通过' : '存在不符合规范的路径');
console.log('详细结果:', batchResults.results);

/**
 * 如何运行测试：
 * 1. 在终端中进入项目根目录
 * 2. 执行命令: node frontend/src/tests/apiPathValidator.test.js
 * 
 * 预期输出：
 * - 符合规范的路径应显示为"通过"
 * - 不符合规范的路径应显示为"不通过"
 * - API模块验证应检测出包含硬编码/api前缀的函数
 */