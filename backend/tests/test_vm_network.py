#!/usr/bin/env python3
"""
测试虚拟机网络连通性脚本
用于诊断虚拟机网络问题
"""

import subprocess
import os
import sys

def run_command(cmd, timeout=5):
    """运行系统命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, shell=True, check=False, capture_output=True, text=True, timeout=timeout
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip(),
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'stdout': '',
            'stderr': f'Command timed out after {timeout} seconds',
            'returncode': 124
        }
    except Exception as e:
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': 1
        }

def test_ping(host):
    """测试ping连通性"""
    print(f"=== 测试ping连通性: {host} ===")
    cmd = f"ping -c 3 {host}"
    result = run_command(cmd)
    
    if result['success']:
        print("✅ Ping测试通过！")
        print(f"   响应:")
        for line in result['stdout'].split('\n')[-3:]:
            if line:
                print(f"   {line}")
        return True
    else:
        print(f"❌ Ping测试失败！")
        print(f"   错误: {result['stderr']}")
        return False

def test_tcp_port(host, port):
    """测试TCP端口连通性"""
    print(f"\n=== 测试TCP端口连通性: {host}:{port} ===")
    cmd = f"nc -zvw 3 {host} {port}"
    result = run_command(cmd)
    
    if result['success']:
        print("✅ TCP端口测试通过！")
        return True
    else:
        print(f"❌ TCP端口测试失败！")
        print(f"   错误: {result['stderr']}")
        return False

def test_dns_resolution(host):
    """测试DNS解析"""
    if '.' in host:  # 只有IP地址不需要DNS解析
        return True
        
    print(f"\n=== 测试DNS解析: {host} ===")
    cmd = f"nslookup {host}"
    result = run_command(cmd)
    
    if result['success']:
        print("✅ DNS解析测试通过！")
        return True
    else:
        print(f"❌ DNS解析测试失败！")
        print(f"   错误: {result['stderr']}")
        return False

def main():
    """主函数"""
    print("虚拟机网络连通性测试脚本")
    print("=" * 50)
    
    # 测试参数
    vm_ip = os.getenv('DB_HOST', '10.211.55.3')
    db_port = os.getenv('DB_PORT', '5432')
    
    print(f"测试目标:")
    print(f"  虚拟机IP: {vm_ip}")
    print(f"  数据库端口: {db_port}")
    print()
    
    # 运行测试
    test_results = {
        'dns': test_dns_resolution(vm_ip),
        'ping': test_ping(vm_ip),
        'tcp_port': test_tcp_port(vm_ip, db_port)
    }
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    for test, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test.title()}: {status}")
    
    print("\n" + "=" * 50)
    if all(test_results.values()):
        print("🎉 所有网络测试通过！网络连通正常")
        sys.exit(0)
    else:
        print("❌ 部分网络测试失败！请检查:")
        print("   1. 虚拟机是否正常运行")
        print("   2. 虚拟机网络配置是否正确")
        print("   3. 虚拟机防火墙是否允许5432端口访问")
        print("   4. 本地网络是否能访问虚拟机网段")
        sys.exit(1)

if __name__ == "__main__":
    main()
