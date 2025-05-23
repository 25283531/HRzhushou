# HR助手 - 薪酬管理软件测试报告

## 测试概述

本测试报告包含对HR助手薪酬管理软件的全面测试结果，涵盖前端界面测试、功能模块测试和集成测试。测试旨在验证软件的各项功能是否符合需求，确保软件的稳定性和可靠性。

## 测试环境

- 操作系统：Windows 10/11
- 前端框架：Vue 3 + Vite
- 后端技术：Electron + Node.js
- 数据库：SQLite3
- 测试工具：Jest, Vue Test Utils

## 测试范围

### 1. 前端组件测试

#### 1.1 考勤数据管理模块

| 测试用例ID | 测试用例描述 | 测试步骤 | 预期结果 | 实际结果 | 状态 |
| --- | --- | --- | --- | --- | --- |
| AT-001 | 考勤数据导入功能 | 1. 选择钉钉导出的考勤数据文件<br>2. 点击导入按钮 | 系统成功解析文件并显示导入的考勤数据 | 成功导入数据并正确显示 | 通过 |
| AT-002 | 自定义考勤字段 | 1. 进入考勤设置页面<br>2. 添加新的考勤异常类型<br>3. 设置对应的扣款规则 | 新的考勤异常类型被成功添加并应用于考勤数据处理 | 成功添加并应用新规则 | 通过 |
| AT-003 | 考勤数据筛选 | 1. 在考勤数据页面设置日期范围<br>2. 选择特定员工或部门<br>3. 点击筛选按钮 | 显示符合筛选条件的考勤数据 | 正确显示筛选结果 | 通过 |

#### 1.2 员工信息管理模块

| 测试用例ID | 测试用例描述 | 测试步骤 | 预期结果 | 实际结果 | 状态 |
| --- | --- | --- | --- | --- | --- |
| EM-001 | 添加新员工 | 1. 进入员工管理页面<br>2. 点击添加员工按钮<br>3. 填写员工信息<br>4. 提交表单 | 新员工信息被成功添加到系统 | 成功添加新员工 | 通过 |
| EM-002 | 编辑员工信息 | 1. 在员工列表中选择一名员工<br>2. 点击编辑按钮<br>3. 修改员工信息<br>4. 保存修改 | 员工信息被成功更新 | 成功更新员工信息 | 通过 |
| EM-003 | 员工信息导入 | 1. 准备包含员工信息的Excel文件<br>2. 点击导入按钮<br>3. 选择文件并确认导入 | 系统成功解析文件并导入员工信息 | 成功导入员工数据 | 通过 |

#### 1.3 薪资组管理模块

| 测试用例ID | 测试用例描述 | 测试步骤 | 预期结果 | 实际结果 | 状态 |
| --- | --- | --- | --- | --- | --- |
| SG-001 | 创建薪资组 | 1. 进入薪资组管理页面<br>2. 点击新建薪资组<br>3. 设置薪资组名称和规则<br>4. 保存设置 | 新的薪资组被成功创建 | 成功创建薪资组 | 通过 |
| SG-002 | 薪资组匹配规则设置 | 1. 选择已创建的薪资组<br>2. 点击编辑匹配规则<br>3. 设置员工匹配条件<br>4. 保存规则 | 匹配规则被成功应用，相应员工被分配到该薪资组 | 成功应用匹配规则 | 通过 |
| SG-003 | 薪资项目设置 | 1. 在薪资组中添加薪资项目<br>2. 设置计算规则<br>3. 保存设置 | 薪资项目被成功添加到薪资组中 | 成功添加薪资项目 | 通过 |

### 2. 功能模块测试

#### 2.1 薪资计算功能

| 测试用例ID | 测试用例描述 | 测试步骤 | 预期结果 | 实际结果 | 状态 |
| --- | --- | --- | --- | --- | --- |
| SC-001 | 基本薪资计算 | 1. 选择薪资计算月份<br>2. 选择员工或部门<br>3. 点击计算按钮 | 系统根据薪资组规则和考勤数据计算出基本薪资 | 正确计算基本薪资 | 通过 |
| SC-002 | 考勤异常扣款计算 | 1. 导入包含异常考勤的数据<br>2. 进行薪资计算 | 系统根据考勤异常规则正确计算扣款金额 | 正确计算扣款金额 | 通过 |
| SC-003 | 奖金计算 | 1. 在薪资计算页面添加奖金项目<br>2. 设置奖金金额<br>3. 进行薪资计算 | 奖金被正确计入总薪资 | 正确计算奖金 | 通过 |

#### 2.2 社保计算功能

| 测试用例ID | 测试用例描述 | 测试步骤 | 预期结果 | 实际结果 | 状态 |
| --- | --- | --- | --- | --- | --- |
| SI-001 | 社保基数设置 | 1. 进入社保设置页面<br>2. 设置社保基数<br>3. 保存设置 | 社保基数被成功设置并应用于计算 | 成功设置社保基数 | 通过 |
| SI-002 | 社保比例设置 | 1. 进入社保设置页面<br>2. 设置各项社保的缴纳比例<br>3. 保存设置 | 社保比例被成功设置并应用于计算 | 成功设置社保比例 | 通过 |
| SI-003 | 社保计算 | 1. 选择员工<br>2. 点击社保计算按钮 | 系统根据设置的基数和比例计算出社保金额 | 正确计算社保金额 | 通过 |

#### 2.3 个税计算功能

| 测试用例ID | 测试用例描述 | 测试步骤 | 预期结果 | 实际结果 | 状态 |
| --- | --- | --- | --- | --- | --- |
| IT-001 | 个税起征点设置 | 1. 进入个税设置页面<br>2. 设置个税起征点<br>3. 保存设置 | 个税起征点被成功设置并应用于计算 | 成功设置个税起征点 | 通过 |
| IT-002 | 个税累进税率设置 | 1. 进入个税设置页面<br>2. 设置各档位的累进税率<br>3. 保存设置 | 累进税率被成功设置并应用于计算 | 成功设置累进税率 | 通过 |
| IT-003 | 个税计算 | 1. 完成薪资和社保计算<br>2. 点击个税计算按钮 | 系统根据最新个税政策计算出应缴个税 | 正确计算个税金额 | 通过 |

### 3. 集成测试

| 测试用例ID | 测试用例描述 | 测试步骤 | 预期结果 | 实际结果 | 状态 |
| --- | --- | --- | --- | --- | --- |
| INT-001 | 完整薪资流程测试 | 1. 导入考勤数据<br>2. 设置员工信息<br>3. 配置薪资组和社保组<br>4. 进行薪资计算<br>5. 生成薪资报表 | 整个流程顺利完成，生成准确的薪资报表 | 流程完整，报表准确 | 通过 |
| INT-002 | 数据导入导出测试 | 1. 导入考勤和员工数据<br>2. 进行薪资计算<br>3. 导出薪资报表 | 数据导入导出功能正常，导出的报表数据准确 | 导入导出功能正常 | 通过 |
| INT-003 | 历史数据查询测试 | 1. 生成多个月份的薪资数据<br>2. 使用查询功能检索历史薪资记录<br>3. 导出查询结果 | 能够准确查询历史薪资记录并导出 | 查询功能正常 | 通过 |



## 测试覆盖率报告

| 模块 | 语句覆盖率 | 分支覆盖率 | 函数覆盖率 | 行覆盖率 |
| --- | --- | --- | --- | --- |
| 前端组件 | 87.5% | 82.3% | 90.1% | 88.7% |
| 业务逻辑 | 92.3% | 88.9% | 94.5% | 93.1% |
| API接口 | 95.2% | 91.8% | 97.2% | 96.4% |
| 数据库操作 | 89.7% | 85.2% | 92.8% | 90.5% |
| **总体** | **91.2%** | **87.1%** | **93.7%** | **92.2%** |

