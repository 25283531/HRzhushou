/**
 * 日期格式解析工具
 * 用于解决考勤数据导入时日期格式解析的问题
 */

/**
 * 支持多种日期格式的解析
 * @param {string} dateStr - 日期字符串
 * @returns {Date|null} - 解析后的Date对象，解析失败返回null
 */
export function parseDate(dateStr) {
  if (!dateStr) return null;
  
  // 去除字符串两端空格
  dateStr = dateStr.trim();
  
  // 尝试直接解析
  let date = new Date(dateStr);
  if (!isNaN(date.getTime())) return date;
  
  // 常见日期格式的正则表达式
  const patterns = [
    // yyyy-MM-dd 或 yyyy/MM/dd
    /^(\d{4})[-\/](\d{1,2})[-\/](\d{1,2})$/,
    // dd-MM-yyyy 或 dd/MM/yyyy
    /^(\d{1,2})[-\/](\d{1,2})[-\/](\d{4})$/,
    // yyyy年MM月dd日
    /^(\d{4})年(\d{1,2})月(\d{1,2})日$/,
    // MM月dd日, yyyy
    /^(\d{1,2})月(\d{1,2})日[,\s]+(\d{4})$/
  ];
  
  for (const pattern of patterns) {
    const match = dateStr.match(pattern);
    if (match) {
      if (pattern === patterns[0]) {
        // yyyy-MM-dd
        return new Date(parseInt(match[1]), parseInt(match[2]) - 1, parseInt(match[3]));
      } else if (pattern === patterns[1]) {
        // dd-MM-yyyy
        return new Date(parseInt(match[3]), parseInt(match[2]) - 1, parseInt(match[1]));
      } else if (pattern === patterns[2]) {
        // yyyy年MM月dd日
        return new Date(parseInt(match[1]), parseInt(match[2]) - 1, parseInt(match[3]));
      } else if (pattern === patterns[3]) {
        // MM月dd日, yyyy
        return new Date(parseInt(match[3]), parseInt(match[1]) - 1, parseInt(match[2]));
      }
    }
  }
  
  // 尝试解析Excel日期序列号
  if (/^\d+$/.test(dateStr)) {
    const excelEpoch = new Date(1899, 11, 30);
    const daysSinceEpoch = parseInt(dateStr);
    const millisecondsPerDay = 24 * 60 * 60 * 1000;
    return new Date(excelEpoch.getTime() + daysSinceEpoch * millisecondsPerDay);
  }
  
  return null;
}

/**
 * 格式化日期为指定格式
 * @param {Date} date - 日期对象
 * @param {string} format - 格式字符串，默认为'yyyy-MM-dd'
 * @returns {string} - 格式化后的日期字符串
 */
export function formatDate(date, format = 'yyyy-MM-dd') {
  if (!date || isNaN(date.getTime())) return '';
  
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();
  const hours = date.getHours();
  const minutes = date.getMinutes();
  const seconds = date.getSeconds();
  
  return format
    .replace('yyyy', year)
    .replace('MM', month.toString().padStart(2, '0'))
    .replace('dd', day.toString().padStart(2, '0'))
    .replace('HH', hours.toString().padStart(2, '0'))
    .replace('mm', minutes.toString().padStart(2, '0'))
    .replace('ss', seconds.toString().padStart(2, '0'));
}