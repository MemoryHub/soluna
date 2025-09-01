#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接运行的云片模板测试
验证模板ID 6269322 是否正常工作
无需路径配置即可直接运行
"""

import os
import sys

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# 将父目录添加到路径
sys.path.insert(0, parent_dir)

# 现在可以直接导入
from yunpian_service import YunpianService
import os

def test_template_direct():
    """直接测试模板发送功能"""
    print("=== 直接运行云片模板测试 ===")
    
    # 使用环境变量中的API密钥或默认值
    api_key = os.getenv("YUNPIAN_API_KEY", "1670a9f2365d0aab56f6a50c3723ac96")
    yunpian = YunpianService(api_key)
    
    # 测试余额查询
    print("1. 查询账户余额...")
    balance_result = yunpian.get_balance()
    print(f"   余额结果: {balance_result}")
    
    # 测试验证码发送（使用模板）
    print("\n2. 测试模板发送验证码...")
    test_phone = "18611137800"  # 测试手机号
    test_code = "123456"  # 测试验证码
    
    send_result = yunpian.send_verification_code(test_phone, test_code)
    print(f"   发送结果: {send_result}")
    
    if send_result.get('success'):
        print("   ✅ 模板发送成功！")
    else:
        print(f"   ❌ 模板发送失败: {send_result.get('message')}")
    
    return send_result

if __name__ == "__main__":
    test_template_direct()