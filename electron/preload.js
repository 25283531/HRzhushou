// 预加载脚本，用于在渲染进程中提供与主进程通信的接口
const { contextBridge, ipcRenderer } = require('electron');

// 暴露给渲染进程的API
contextBridge.exposeInMainWorld('electronAPI', {
  // 检查后端状态
  checkBackendStatus: () => ipcRenderer.invoke('check-backend-status'),
  
  // 重启后端
  restartBackend: () => ipcRenderer.send('restart-backend'),
  
  // 监听后端启动事件
  onBackendStarted: (callback) => {
    ipcRenderer.on('backend-started', callback);
    return () => ipcRenderer.removeListener('backend-started', callback);
  },
  
  // 获取应用版本
  getAppVersion: () => process.env.npm_package_version || '1.0.0',
  
  // 获取操作系统信息
  getOsInfo: () => ({
    platform: process.platform,
    arch: process.arch,
    version: process.getSystemVersion()
  })
});

// 在页面加载完成后通知渲染进程
window.addEventListener('DOMContentLoaded', () => {
  // 替换页面中的应用版本号
  const versionElement = document.getElementById('app-version');
  if (versionElement) {
    versionElement.innerText = process.env.npm_package_version || '1.0.0';
  }
  
  // 检查后端状态并通知渲染进程
  ipcRenderer.invoke('check-backend-status').then(status => {
    window.postMessage({ type: 'backend-status', status }, '*');
  });
});