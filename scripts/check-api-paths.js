/**
 * API路径检查脚本
 * 用于在构建过程中检查项目中的API路径是否符合规范
 * 
 * 使用方法：
 * 1. 在终端中执行: node scripts/check-api-paths.js
 * 2. 可以集成到package.json的scripts中: "check-api": "node scripts/check-api-paths.js"
 */

const fs = require('fs');
const path = require('path');

// 需要检查的目录
const DIRS_TO_CHECK = [
  path.join(__dirname, '../frontend/src/api'),
  path.join(__dirname, '../frontend/src/utils'),
  path.join(__dirname, '../frontend/src/views')
];

// 需要检查的文件扩展名
const FILE_EXTENSIONS = ['.js', '.vue'];

// 检查文件中是否包含硬编码的/api前缀
function checkFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  
  // 排除文档和测试文件中的示例代码
  if (filePath.includes('apiPathValidator.js') || 
      filePath.includes('api-path-guidelines.md') ||
      filePath.includes('test') ||
      filePath.includes('docs')) {
    return true;
  }
  
  // 检查常规API调用中的硬编码/api前缀
  const apiRegex = /['"\`]\/api\/[\w\-\/]+['"\`]/g;
  const matches = content.match(apiRegex);
  
  // 检查上传组件action属性中的硬编码/api前缀
  const uploadActionRegex = /action\s*=\s*['"\`]\/api\/[\w\-\/]+['"\`]/g;
  const uploadMatches = content.match(uploadActionRegex);
  
  const allMatches = [];
  if (matches) allMatches.push(...matches);
  if (uploadMatches) allMatches.push(...uploadMatches);
  
  if (allMatches.length > 0) {
    console.error(`\x1b[31m文件 ${filePath} 中包含硬编码的/api前缀:\x1b[0m`);
    allMatches.forEach(match => {
      console.error(`  - ${match}`);
    });
    return false;
  }
  return true;
}

// 递归检查目录中的所有文件
function checkDirectory(dir) {
  let isValid = true;
  const files = fs.readdirSync(dir);
  
  for (const file of files) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      // 递归检查子目录
      const subDirValid = checkDirectory(filePath);
      isValid = isValid && subDirValid;
    } else if (FILE_EXTENSIONS.includes(path.extname(file))) {
      // 检查符合扩展名的文件
      const fileValid = checkFile(filePath);
      isValid = isValid && fileValid;
    }
  }
  
  return isValid;
}

// 主函数
function main() {
  console.log('开始检查API路径格式...');
  let allValid = true;
  
  for (const dir of DIRS_TO_CHECK) {
    console.log(`检查目录: ${dir}`);
    try {
      const dirValid = checkDirectory(dir);
      allValid = allValid && dirValid;
    } catch (error) {
      console.error(`检查目录 ${dir} 时出错:`, error);
      allValid = false;
    }
  }
  
  if (allValid) {
    console.log('\x1b[32m✓ 所有API路径格式检查通过!\x1b[0m');
    process.exit(0);
  } else {
    console.error('\x1b[31m✗ API路径格式检查失败! 请修复上述问题.\x1b[0m');
    process.exit(1);
  }
}

// 执行主函数
main();