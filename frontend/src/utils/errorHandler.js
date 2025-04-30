/**
 * 错误处理服务
 * 提供统一的错误处理机制，友好的用户提示和日志记录
 */

import { ElMessage, ElMessageBox } from 'element-plus';

// 错误类型枚举
const ErrorType = {
  NETWORK: 'network',       // 网络错误
  API: 'api',               // API错误
  VALIDATION: 'validation', // 数据验证错误
  BUSINESS: 'business',     // 业务逻辑错误
  SYSTEM: 'system',         // 系统错误
  UNKNOWN: 'unknown'        // 未知错误
};

// 错误严重程度枚举
const ErrorSeverity = {
  INFO: 'info',         // 信息
  WARNING: 'warning',   // 警告
  ERROR: 'error',       // 错误
  FATAL: 'fatal'        // 致命错误
};

/**
 * 创建错误对象
 * @param {string} message - 错误消息
 * @param {string} type - 错误类型，使用ErrorType枚举
 * @param {string} severity - 错误严重程度，使用ErrorSeverity枚举
 * @param {Object} details - 错误详情
 * @returns {Object} - 错误对象
 */
function createError(message, type = ErrorType.UNKNOWN, severity = ErrorSeverity.ERROR, details = {}) {
  return {
    message,
    type,
    severity,
    details,
    timestamp: new Date().toISOString()
  };
}

/**
 * 处理网络错误
 * @param {Error} error - 错误对象
 * @returns {Object} - 格式化的错误对象
 */
function handleNetworkError(error) {
  let message = '网络连接错误，请检查您的网络连接';
  let severity = ErrorSeverity.ERROR;
  
  if (error.message.includes('timeout')) {
    message = '请求超时，请稍后重试';
  } else if (error.message.includes('Network Error')) {
    message = '网络连接错误，请检查您的网络连接';
  } else if (error.response) {
    const status = error.response.status;
    
    switch (status) {
      case 401:
        message = '未授权，请重新登录';
        break;
      case 403:
        message = '拒绝访问，没有权限';
        break;
      case 404:
        message = '请求的资源不存在';
        break;
      case 500:
        message = '服务器错误，请稍后重试';
        severity = ErrorSeverity.FATAL;
        break;
      default:
        message = `请求错误 (${status})`;
    }
  }
  
  return createError(message, ErrorType.NETWORK, severity, {
    originalError: error,
    response: error.response
  });
}

/**
 * 处理API错误
 * @param {Object} response - API响应对象
 * @returns {Object} - 格式化的错误对象
 */
function handleApiError(response) {
  const message = response.message || '操作失败，请稍后重试';
  const code = response.code || 'UNKNOWN';
  let severity = ErrorSeverity.ERROR;
  
  // 根据错误码设置严重程度
  if (code.startsWith('WARN_')) {
    severity = ErrorSeverity.WARNING;
  } else if (code.startsWith('FATAL_')) {
    severity = ErrorSeverity.FATAL;
  }
  
  return createError(message, ErrorType.API, severity, {
    code,
    data: response.data
  });
}

/**
 * 处理数据验证错误
 * @param {Object} validationResult - 验证结果对象
 * @returns {Object} - 格式化的错误对象
 */
function handleValidationError(validationResult) {
  const message = validationResult.errors && validationResult.errors.length > 0
    ? validationResult.errors[0]
    : '数据验证失败';
  
  return createError(message, ErrorType.VALIDATION, ErrorSeverity.WARNING, {
    errors: validationResult.errors,
    invalidRecords: validationResult.invalidRecords
  });
}

/**
 * 处理业务逻辑错误
 * @param {string} message - 错误消息
 * @param {Object} details - 错误详情
 * @returns {Object} - 格式化的错误对象
 */
function handleBusinessError(message, details = {}) {
  return createError(message, ErrorType.BUSINESS, ErrorSeverity.WARNING, details);
}

/**
 * 处理系统错误
 * @param {Error} error - 错误对象
 * @returns {Object} - 格式化的错误对象
 */
function handleSystemError(error) {
  return createError(
    '系统错误，请联系管理员',
    ErrorType.SYSTEM,
    ErrorSeverity.FATAL,
    { originalError: error }
  );
}

/**
 * 处理未知错误
 * @param {Error} error - 错误对象
 * @returns {Object} - 格式化的错误对象
 */
function handleUnknownError(error) {
  let message = '发生未知错误';
  
  if (error instanceof Error) {
    message = error.message || message;
  } else if (typeof error === 'string') {
    message = error;
  }
  
  return createError(message, ErrorType.UNKNOWN, ErrorSeverity.ERROR, {
    originalError: error
  });
}

/**
 * 显示错误消息
 * @param {Object} error - 错误对象
 */
function showErrorMessage(error) {
  switch (error.severity) {
    case ErrorSeverity.INFO:
      ElMessage.info(error.message);
      break;
    case ErrorSeverity.WARNING:
      ElMessage.warning(error.message);
      break;
    case ErrorSeverity.ERROR:
      ElMessage.error(error.message);
      break;
    case ErrorSeverity.FATAL:
      ElMessageBox.alert(
        error.message,
        '系统错误',
        { confirmButtonText: '确定', type: 'error' }
      );
      break;
    default:
      ElMessage.error(error.message);
  }
}

/**
 * 记录错误日志
 * @param {Object} error - 错误对象
 */
function logError(error) {
  // 根据错误严重程度使用不同的日志级别
  switch (error.severity) {
    case ErrorSeverity.INFO:
      console.info('[ERROR]', error);
      break;
    case ErrorSeverity.WARNING:
      console.warn('[ERROR]', error);
      break;
    case ErrorSeverity.ERROR:
    case ErrorSeverity.FATAL:
      console.error('[ERROR]', error);
      break;
    default:
      console.error('[ERROR]', error);
  }
  
  // 这里可以添加将错误日志发送到服务器的逻辑
  // 例如使用Sentry或自定义的日志服务
}

/**
 * 统一错误处理函数
 * @param {Error|Object} error - 错误对象
 * @param {boolean} showMessage - 是否显示错误消息，默认为true
 * @returns {Object} - 格式化的错误对象
 */
function handleError(error, showMessage = true) {
  let formattedError;
  
  // 根据错误类型进行处理
  if (error.response) {
    // Axios错误
    formattedError = handleNetworkError(error);
  } else if (error.code && error.message) {
    // API错误
    formattedError = handleApiError(error);
  } else if (error.errors && Array.isArray(error.errors)) {
    // 验证错误
    formattedError = handleValidationError(error);
  } else if (error.type && Object.values(ErrorType).includes(error.type)) {
    // 已格式化的错误
    formattedError = error;
  } else if (error instanceof Error) {
    // JavaScript错误
    formattedError = handleSystemError(error);
  } else {
    // 未知错误
    formattedError = handleUnknownError(error);
  }
  
  // 记录错误日志
  logError(formattedError);
  
  // 显示错误消息
  if (showMessage) {
    showErrorMessage(formattedError);
  }
  
  return formattedError;
}

// 导出错误处理相关函数和枚举
export {
  ErrorType,
  ErrorSeverity,
  createError,
  handleNetworkError,
  handleApiError,
  handleValidationError,
  handleBusinessError,
  handleSystemError,
  handleUnknownError,
  showErrorMessage,
  logError,
  handleError
};

// 默认导出统一错误处理函数
export default handleError;