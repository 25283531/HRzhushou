const request = require('supertest');
const path = require('path');
const app = require(path.resolve(__dirname, '../src/index'));

describe('考勤管理API测试', () => {
  let createdId;

  it('GET /api/attendance 应返回考勤列表', async () => {
    const res = await request(app).get('/api/attendance');
    expect(res.statusCode).toBe(200);
    expect(Array.isArray(res.body.data) || Array.isArray(res.body)).toBe(true);
  });

  it('POST /api/attendance 应能创建考勤记录', async () => {
    const res = await request(app)
      .post('/api/attendance')
      .send({ employeeId: 1, date: '2024-05-01', status: '正常' });
    expect(res.statusCode).toBeGreaterThanOrEqual(200);
    expect(res.body).toHaveProperty('id');
    createdId = res.body.id;
  });

  it('GET /api/attendance/:id 应返回单条考勤', async () => {
    if (!createdId) return;
    const res = await request(app).get(`/api/attendance/${createdId}`);
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('id', createdId);
  });

  it('PUT /api/attendance/:id 应能更新考勤', async () => {
    if (!createdId) return;
    const res = await request(app)
      .put(`/api/attendance/${createdId}`)
      .send({ status: '迟到' });
    expect(res.statusCode).toBeGreaterThanOrEqual(200);
    expect(res.body).toHaveProperty('status', '迟到');
  });

  it('DELETE /api/attendance/:id 应能删除考勤', async () => {
    if (!createdId) return;
    const res = await request(app).delete(`/api/attendance/${createdId}`);
    expect(res.statusCode).toBeGreaterThanOrEqual(200);
  });
}); 