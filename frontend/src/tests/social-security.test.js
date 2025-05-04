import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import SocialSecurityView from '../views/social-security/Index.vue';

describe('社保管理模块', () => {
  it('应正确渲染社保页面', () => {
    const wrapper = mount(SocialSecurityView);
    expect(wrapper.text()).toContain('社保');
  });
  // TODO: 增加基数设置、比例设置、计算等功能和异常场景测试
});