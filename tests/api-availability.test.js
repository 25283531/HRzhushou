console.log('index.js path:', require('path').resolve(__dirname, '../src/index'));
const request = require('supertest');
const path = require('path');
const app = require(path.resolve(__dirname, '../src/index'));

describe('后端主要API可用性自动检测', () => {
  const apis = [
    { name: '员工列表', url: '/api/employee' },
    { name: '考勤列表', url: '/api/attendance' },
    { name: '薪资组列表', url: '/api/salary-groups' },
    { name: '薪酬项列表', url: '/api/salary-items' },
    { name: '职级类型列表', url: '/api/position-levels' },
    { name: '数据分析', url: '/api/analysis' },
  ];

  apis.forEach(api => {
    it(`GET ${api.url} (${api.name}) 应返回 200`, async () => {
      const res = await request(app).get(api.url);
      expect(res.statusCode).toBe(200);
    });
  });
}); 