/**
 * Web Worker服务包装器
 * 提供简单的接口来使用Web Worker进行计算操作
 */

// 任务ID计数器
let taskIdCounter = 0;

// 任务回调映射
const taskCallbacks = new Map();

// 创建Worker实例
let worker = null;

/**
 * 初始化Worker
 */
function initWorker() {
  if (worker) return;
  
  // 创建Worker实例
  worker = new Worker(new URL('./calculationWorker.js', import.meta.url), { type: 'module' });
  
  // 监听Worker消息
  worker.addEventListener('message', (event) => {
    const { type, taskId, result, error } = event.data;
    
    // 获取任务回调
    const callbacks = taskCallbacks.get(taskId);
    if (!callbacks) return;
    
    // 根据消息类型调用相应回调
    if (type === 'success') {
      callbacks.resolve(result);
    } else if (type === 'error') {
      callbacks.reject(new Error(error));
    }
    
    // 删除已完成的任务回调
    taskCallbacks.delete(taskId);
  });
}

/**
 * 发送任务到Worker
 * @param {string} type - 任务类型
 * @param {Object} data - 任务数据
 * @returns {Promise} - 任务结果Promise
 */
function sendTask(type, data) {
  // 确保Worker已初始化
  initWorker();
  
  // 生成任务ID
  const taskId = ++taskIdCounter;
  
  // 创建Promise
  return new Promise((resolve, reject) => {
    // 存储任务回调
    taskCallbacks.set(taskId, { resolve, reject });
    
    // 发送任务到Worker
    worker.postMessage({ type, data, taskId });
  });
}

/**
 * 计算薪资
 * @param {Object} data - 薪资计算所需数据
 * @returns {Promise<Object>} - 计算结果Promise
 */
export function calculateSalary(data) {
  return sendTask('calculateSalary', data);
}

/**
 * 计算社保
 * @param {Object} data - 社保计算所需数据
 * @returns {Promise<Object>} - 计算结果Promise
 */
export function calculateSocialInsurance(data) {
  return sendTask('calculateSocialInsurance', data);
}

/**
 * 计算个税
 * @param {Object} data - 个税计算所需数据
 * @returns {Promise<Object>} - 计算结果Promise
 */
export function calculateIncomeTax(data) {
  return sendTask('calculateIncomeTax', data);
}

/**
 * 处理考勤数据
 * @param {Object} data - 考勤数据处理所需数据
 * @returns {Promise<Object>} - 处理结果Promise
 */
export function processAttendanceData(data) {
  return sendTask('processAttendanceData', data);
}

/**
 * 终止Worker
 */
export function terminateWorker() {
  if (worker) {
    worker.terminate();
    worker = null;
    taskCallbacks.clear();
  }
}