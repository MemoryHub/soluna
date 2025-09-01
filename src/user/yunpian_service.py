#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云片网短信验证码服务
用于发送手机验证码到真实手机
"""

import requests
import json
import logging
import os
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YunpianService:
    """云片网短信服务类"""
    
    def __init__(self, api_key: str):
        """
        初始化云片服务
        
        Args:
            api_key: 云片网API密钥
        """
        self.api_key = api_key
        self.base_url = "https://sms.yunpian.com/v2"
        self.tpl_send_url = f"{self.base_url}/sms/tpl_single_send.json"
        
    def send_verification_code(self, phone_number: str, verification_code: str) -> Dict[str, Any]:
        """
        发送验证码短信
        
        Args:
            phone_number: 接收验证码的手机号
            verification_code: 6位数字验证码
            
        Returns:
            Dict: 包含发送结果的响应信息
        """
        try:
            # 使用模板ID发送（模板ID: 6269322）
            # 模板内容: 【天津信之鸥】Soluna AI，验证码#code#，用于手机验证码登录，5分钟内有效。验证码提供给他人可能导致账号被盗，请勿泄露，谨防被骗。
            params = {
                'apikey': self.api_key,
                'mobile': phone_number,
                'tpl_id': '6269322',
                'tpl_value': f'#code#={verification_code}'
            }
            
            # 发送请求（使用模板发送接口）
            response = requests.post(
                self.tpl_send_url,
                data=params,
                timeout=10,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
                }
            )
            
            # 解析响应
            result = response.json()
            
            # 记录日志
            if result.get('code') == 0:
                logger.info(f"验证码发送成功: 手机号={phone_number}, 验证码={verification_code}, 短信ID={result.get('sid')}")
                return {
                    'success': True,
                    'message': '验证码发送成功',
                    'sid': result.get('sid'),
                    'count': result.get('count'),
                    'fee': result.get('fee')
                }
            else:
                error_msg = result.get('msg', '未知错误')
                logger.error(f"验证码发送失败: 手机号={phone_number}, 错误={error_msg}, 完整响应={result}")
                return {
                    'success': False,
                    'message': f'发送失败: {error_msg}',
                    'error_code': result.get('code'),
                    'error_msg': error_msg
                }
                
        except requests.exceptions.Timeout:
            logger.error(f"请求超时: 手机号={phone_number}")
            return {
                'success': False,
                'message': '网络超时，请稍后重试',
                'error_code': 'TIMEOUT'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求异常: 手机号={phone_number}, 错误={str(e)}")
            return {
                'success': False,
                'message': f'网络异常: {str(e)}',
                'error_code': 'NETWORK_ERROR'
            }
        except Exception as e:
            logger.error(f"发送验证码异常: 手机号={phone_number}, 错误={str(e)}")
            return {
                'success': False,
                'message': f'系统异常: {str(e)}',
                'error_code': 'SYSTEM_ERROR'
            }
    
    def get_balance(self) -> Dict[str, Any]:
        """
        获取账户余额
        
        Returns:
            Dict: 包含余额信息的响应
        """
        try:
            url = f"{self.base_url}/user/get.json"
            params = {'apikey': self.api_key}
            
            response = requests.post(url, data=params, timeout=5)
            result = response.json()
            
            if result.get('code') == 0:
                return {
                    'success': True,
                    'balance': result.get('balance', 0),
                    'user_id': result.get('user', {}).get('id')
                }
            else:
                return {
                    'success': False,
                    'message': result.get('msg', '获取余额失败')
                }
                
        except Exception as e:
            logger.error(f"获取余额异常: {str(e)}")
            return {
                'success': False,
                'message': f'获取余额异常: {str(e)}'
            }

# 创建全局实例
yunpian_service = YunpianService(os.getenv("YUNPIAN_API_KEY", "1670a9f2365d0aab56f6a50c3723ac96"))