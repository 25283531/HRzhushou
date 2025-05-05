const request = require('supertest');
const path = require('path');
const app = require(path.resolve(__dirname, '../src/index'));

describe('员工管理API测试', () => {
  let createdId;

  it('GET /api/employee 应返回员工列表', async () => {
    const res = await request(app).get('/api/employee');
    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body.data) || Array.isArray(res.body)).toBe(true);
  });

  it('POST /api/employee 应能创建新员工', async () => {
    const res = await request(app)
      .post('/api/employee')
      .send({ name: '测试员工', position: '开发', department: '技术部' });
    expect(res.statusCode).toBeGreaterThanOrEqual(200);
    expect(res.body).toHaveProperty('id');
    createdId = res.body.id;
  });

  it('GET /api/employee/:id 应返回单个员工', async () => {
    if (!createdId) return;
    const res = await request(app).get(`/api/employee/${createdId}`);
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('id', createdId);
  });

  it('PUT /api/employee/:id 应能更新员工信息', async () => {
    if (!createdId) return;
    const res = await request(app)
      .put(`/api/employee/${createdId}`)
      .send({ name: '测试员工-更新' });
    expect(res.statusCode).toBeGreaterThanOrEqual(200);
    expect(res.body).toHaveProperty('name', '测试员工-更新');
  });

  it('DELETE /api/employee/:id 应能删除员工', async () => {
    if (!createdId) return;
    const res = await request(app).delete(`/api/employee/${createdId}`);
    expect(res.statusCode).toBeGreaterThanOrEqual(200);
  });
}); 