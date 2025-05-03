const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const url = require('url');
const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');

// 保持对window对象的全局引用，如果不这么做的话，当JavaScript对象被
// 垃圾回收的时候，window对象将会自动的关闭
let mainWindow;
let pythonProcess;
let backendStarted = false;

// 启动Python后端服务
function startPythonBackend() {
  // 检查Python可执行文件路径
  const isProd = !process.env.ELECTRON_IS_DEV;
  let pythonPath;
  let scriptPath;
  
  if (isProd) {
    // 生产环境下，使用打包后的路径
    pythonPath = path.join(process.resourcesPath, 'python', 'python.exe');
    scriptPath = path.join(process.resourcesPath, 'backend', 'app.py');
  } else {
    // 开发环境下，使用系统Python
    pythonPath = 'python';
    scriptPath = path.join(__dirname, '..', 'backend', 'app.py');
  }
  
  // 启动Python进程
  pythonProcess = spawn(pythonPath, [scriptPath]);
  
  // 监听Python进程的输出
  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python stdout: ${data}`);
    if (data.toString().includes('Running on')) {
      backendStarted = true;
      // 后端启动成功后，加载前端页面
      if (mainWindow) {
        mainWindow.webContents.send('backend-started');
      }
    }
  });
  
  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python stderr: ${data}`);
  });
  
  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
    backendStarted = false;
    // 如果Python进程异常退出，尝试重启
    if (code !== 0 && !app.isQuitting) {
      console.log('Attempting to restart Python backend...');
      startPythonBackend();
    }
  });
}

function createWindow() {
  // 创建浏览器窗口
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: path.join(__dirname, 'preload.js')
    }
  });
  
  // 加载应用的入口页面
  const isProd = !process.env.ELECTRON_IS_DEV;
  
  if (isProd) {
    // 生产环境下，加载打包后的前端文件
    mainWindow.loadURL(
      url.format({
        pathname: path.join(__dirname, '../dist/index.html'),
        protocol: 'file:',
        slashes: true
      })
    );
  } else {
    // 开发环境下，加载开发服务器地址
    mainWindow.loadURL('http://localhost:5566');
    
    // 打开开发者工具
    mainWindow.webContents.openDevTools();
  }
  
  // 当窗口关闭时触发
  mainWindow.on('closed', function() {
    mainWindow = null;
  });
}

// 当Electron完成初始化并准备创建浏览器窗口时调用此方法
app.on('ready', () => {
  // 先启动后端服务
  startPythonBackend();
  
  // 创建窗口
  createWindow();
  
  // 等待后端启动
  const checkBackendInterval = setInterval(() => {
    if (backendStarted) {
      clearInterval(checkBackendInterval);
      console.log('Backend started successfully');
    }
  }, 1000);
});

// 当所有窗口关闭时退出应用
app.on('window-all-closed', function() {
  // 在macOS上，除非用户用Cmd + Q确定地退出，
  // 否则绝大部分应用及其菜单栏会保持激活
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', function() {
  // 在macOS上，当点击dock图标并且没有其他窗口打开时，
  // 通常在应用程序中重新创建一个窗口
  if (mainWindow === null) {
    createWindow();
  }
});

// 在应用退出前清理
app.on('before-quit', () => {
  app.isQuitting = true;
  // 终止Python进程
  if (pythonProcess) {
    pythonProcess.kill();
  }
});

// IPC通信处理
ipcMain.on('restart-backend', () => {
  if (pythonProcess) {
    pythonProcess.kill();
    // Python进程结束后会自动重启
  }
});

// 检查后端状态
ipcMain.handle('check-backend-status', () => {
  return backendStarted;
});