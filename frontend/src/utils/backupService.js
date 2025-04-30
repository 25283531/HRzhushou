/**
 * 数据备份服务
 * 提供数据自动备份功能，防止数据丢失或损坏
 */

import { formatDate } from './dateParser';

// 默认备份设置
const DEFAULT_BACKUP_SETTINGS = {
  autoBackup: true,          // 是否启用自动备份
  backupInterval: 24 * 60 * 60 * 1000, // 备份间隔，默认24小时
  maxBackupCount: 10,        // 最大备份数量
  backupPath: 'backups',     // 备份路径
  includeAttendance: true,   // 是否备份考勤数据
  includeEmployees: true,    // 是否备份员工数据
  includeSalaryGroups: true, // 是否备份薪资组数据
  includeSalaryRecords: true // 是否备份薪资记录
};

// 备份服务实例
let backupServiceInstance = null;

/**
 * 数据备份服务类
 */
class BackupService {
  constructor() {
    if (backupServiceInstance) {
      return backupServiceInstance;
    }
    
    this.settings = { ...DEFAULT_BACKUP_SETTINGS };
    this.backupTimer = null;
    this.isBackingUp = false;
    this.lastBackupTime = null;
    
    // 从本地存储加载设置
    this.loadSettings();
    
    // 初始化自动备份
    if (this.settings.autoBackup) {
      this.startAutoBackup();
    }
    
    backupServiceInstance = this;
  }
  
  /**
   * 从本地存储加载备份设置
   */
  loadSettings() {
    try {
      const savedSettings = localStorage.getItem('backupSettings');
      if (savedSettings) {
        this.settings = { ...this.settings, ...JSON.parse(savedSettings) };
      }
    } catch (error) {
      console.error('加载备份设置失败:', error);
    }
  }
  
  /**
   * 保存备份设置到本地存储
   */
  saveSettings() {
    try {
      localStorage.setItem('backupSettings', JSON.stringify(this.settings));
    } catch (error) {
      console.error('保存备份设置失败:', error);
    }
  }
  
  /**
   * 更新备份设置
   * @param {Object} newSettings - 新的备份设置
   */
  updateSettings(newSettings) {
    this.settings = { ...this.settings, ...newSettings };
    this.saveSettings();
    
    // 重新启动自动备份
    this.stopAutoBackup();
    if (this.settings.autoBackup) {
      this.startAutoBackup();
    }
  }
  
  /**
   * 启动自动备份
   */
  startAutoBackup() {
    if (this.backupTimer) {
      this.stopAutoBackup();
    }
    
    this.backupTimer = setInterval(() => {
      this.createBackup();
    }, this.settings.backupInterval);
    
    // 添加页面关闭前的备份
    window.addEventListener('beforeunload', this.handleBeforeUnload);
  }
  
  /**
   * 停止自动备份
   */
  stopAutoBackup() {
    if (this.backupTimer) {
      clearInterval(this.backupTimer);
      this.backupTimer = null;
    }
    
    window.removeEventListener('beforeunload', this.handleBeforeUnload);
  }
  
  /**
   * 页面关闭前处理
   */
  handleBeforeUnload = () => {
    // 如果距离上次备份时间超过1小时，则创建备份
    if (!this.lastBackupTime || (Date.now() - this.lastBackupTime > 60 * 60 * 1000)) {
      this.createBackup(true);
    }
  }
  
  /**
   * 创建数据备份
   * @param {boolean} isExitBackup - 是否是退出时的备份
   * @returns {Promise<Object>} - 备份结果
   */
  async createBackup(isExitBackup = false) {
    if (this.isBackingUp) {
      return { success: false, message: '备份正在进行中' };
    }
    
    this.isBackingUp = true;
    
    try {
      // 获取要备份的数据
      const backupData = {};
      
      // 获取考勤数据
      if (this.settings.includeAttendance) {
        backupData.attendance = await this.fetchDataToBackup('attendance');
      }
      
      // 获取员工数据
      if (this.settings.includeEmployees) {
        backupData.employees = await this.fetchDataToBackup('employees');
      }
      
      // 获取薪资组数据
      if (this.settings.includeSalaryGroups) {
        backupData.salaryGroups = await this.fetchDataToBackup('salaryGroups');
      }
      
      // 获取薪资记录数据
      if (this.settings.includeSalaryRecords) {
        backupData.salaryRecords = await this.fetchDataToBackup('salaryRecords');
      }
      
      // 创建备份文件
      const backupFileName = this.generateBackupFileName(isExitBackup);
      const backupResult = await this.saveBackupFile(backupFileName, backupData);
      
      // 清理旧备份
      await this.cleanupOldBackups();
      
      // 更新最后备份时间
      this.lastBackupTime = Date.now();
      
      return backupResult;
    } catch (error) {
      console.error('创建备份失败:', error);
      return { success: false, message: `备份失败: ${error.message}` };
    } finally {
      this.isBackingUp = false;
    }
  }
  
  /**
   * 获取要备份的数据
   * @param {string} dataType - 数据类型
   * @returns {Promise<Array>} - 数据数组
   */
  async fetchDataToBackup(dataType) {
    // 这里应该调用相应的API获取数据
    // 示例实现，实际应该根据项目的API结构进行调整
    try {
      // 从localStorage获取数据（仅用于演示）
      const data = localStorage.getItem(dataType);
      return data ? JSON.parse(data) : [];
      
      // 实际项目中应该调用API
      // const response = await api.get(`/${dataType}`);
      // return response.data;
    } catch (error) {
      console.error(`获取${dataType}数据失败:`, error);
      return [];
    }
  }
  
  /**
   * 生成备份文件名
   * @param {boolean} isExitBackup - 是否是退出时的备份
   * @returns {string} - 备份文件名
   */
  generateBackupFileName(isExitBackup) {
    const now = new Date();
    const dateStr = formatDate(now, 'yyyyMMdd_HHmmss');
    const prefix = isExitBackup ? 'exit_backup' : 'auto_backup';
    return `${prefix}_${dateStr}.json`;
  }
  
  /**
   * 保存备份文件
   * @param {string} fileName - 文件名
   * @param {Object} data - 备份数据
   * @returns {Promise<Object>} - 保存结果
   */
  async saveBackupFile(fileName, data) {
    try {
      // 在实际的Electron应用中，这里应该使用Node.js的fs模块写入文件
      // 但在前端环境中，我们可以使用localStorage或IndexedDB进行模拟
      
      // 获取现有备份列表
      const backupList = this.getBackupList();
      
      // 添加新备份
      const newBackup = {
        fileName,
        createdAt: new Date().toISOString(),
        size: JSON.stringify(data).length,
        data
      };
      
      backupList.push(newBackup);
      
      // 保存备份列表
      localStorage.setItem('backupList', JSON.stringify(backupList.map(backup => {
        // 不在列表中存储实际数据，只存储元数据
        const { data, ...meta } = backup;
        return meta;
      })));
      
      // 单独存储备份数据
      localStorage.setItem(`backup_${fileName}`, JSON.stringify(data));
      
      return { 
        success: true, 
        message: '备份创建成功', 
        fileName,
        createdAt: newBackup.createdAt
      };
    } catch (error) {
      console.error('保存备份文件失败:', error);
      return { success: false, message: `保存备份文件失败: ${error.message}` };
    }
  }
  
  /**
   * 获取备份列表
   * @returns {Array} - 备份列表
   */
  getBackupList() {
    try {
      const backupList = localStorage.getItem('backupList');
      return backupList ? JSON.parse(backupList) : [];
    } catch (error) {
      console.error('获取备份列表失败:', error);
      return [];
    }
  }
  
  /**
   * 清理旧备份
   * @returns {Promise<void>}
   */
  async cleanupOldBackups() {
    try {
      const backupList = this.getBackupList();
      
      // 如果备份数量超过最大限制，删除最旧的备份
      if (backupList.length > this.settings.maxBackupCount) {
        // 按创建时间排序
        backupList.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
        
        // 需要删除的备份
        const backupsToDelete = backupList.slice(0, backupList.length - this.settings.maxBackupCount);
        
        // 删除旧备份
        for (const backup of backupsToDelete) {
          localStorage.removeItem(`backup_${backup.fileName}`);
        }
        
        // 更新备份列表
        const newBackupList = backupList.slice(backupList.length - this.settings.maxBackupCount);
        localStorage.setItem('backupList', JSON.stringify(newBackupList));
      }
    } catch (error) {
      console.error('清理旧备份失败:', error);
    }
  }
  
  /**
   * 恢复备份
   * @param {string} fileName - 备份文件名
   * @returns {Promise<Object>} - 恢复结果
   */
  async restoreBackup(fileName) {
    try {
      // 获取备份数据
      const backupData = localStorage.getItem(`backup_${fileName}`);
      if (!backupData) {
        return { success: false, message: '备份文件不存在' };
      }
      
      const data = JSON.parse(backupData);
      
      // 恢复数据
      // 这里应该调用相应的API恢复数据
      // 示例实现，实际应该根据项目的API结构进行调整
      
      // 恢复考勤数据
      if (data.attendance) {
        localStorage.setItem('attendance', JSON.stringify(data.attendance));
        // await api.post('/attendance/restore', data.attendance);
      }
      
      // 恢复员工数据
      if (data.employees) {
        localStorage.setItem('employees', JSON.stringify(data.employees));
        // await api.post('/employees/restore', data.employees);
      }
      
      // 恢复薪资组数据
      if (data.salaryGroups) {
        localStorage.setItem('salaryGroups', JSON.stringify(data.salaryGroups));
        // await api.post('/salary-groups/restore', data.salaryGroups);
      }
      
      // 恢复薪资记录数据
      if (data.salaryRecords) {
        localStorage.setItem('salaryRecords', JSON.stringify(data.salaryRecords));
        // await api.post('/salary-records/restore', data.salaryRecords);
      }
      
      return { success: true, message: '备份恢复成功' };
    } catch (error) {
      console.error('恢复备份失败:', error);
      return { success: false, message: `恢复备份失败: ${error.message}` };
    }
  }
  
  /**
   * 删除备份
   * @param {string} fileName - 备份文件名
   * @returns {Promise<Object>} - 删除结果
   */
  async deleteBackup(fileName) {
    try {
      // 删除备份数据
      localStorage.removeItem(`backup_${fileName}`);
      
      // 更新备份列表
      const backupList = this.getBackupList();
      const newBackupList = backupList.filter(backup => backup.fileName !== fileName);
      localStorage.setItem('backupList', JSON.stringify(newBackupList));
      
      return { success: true, message: '备份删除成功' };
    } catch (error) {
      console.error('删除备份失败:', error);
      return { success: false, message: `删除备份失败: ${error.message}` };
    }
  }
}

// 导出单例实例
export default new BackupService();