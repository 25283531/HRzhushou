const request = require('supertest');
const app = require('./index');

describe('基础API路由测试', () => {
  it('GET / 应返回 200 和欢迎信息', async () => {
    const res = await request(app).get('/');
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('message', 'HR助手API服务');
    expect(res.body).toHaveProperty('version');
    expect(res.body).toHaveProperty('endpoints');
  });

  it('GET /api/health 应返回 200 和 status: ok', async () => {
    const res = await request(app).get('/api/health');
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('status', 'ok');
    expect(res.body).toHaveProperty('timestamp');
  });
}); 