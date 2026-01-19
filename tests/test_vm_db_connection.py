#!/usr/bin/env python3
"""
测试虚拟机数据库连接脚本
用于验证修改pg_hba.conf后是否能正常连接虚拟机中的PostgreSQL
"""

import sys
import os
from dotenv import load_dotenv
import asyncio
import psycopg2
from psycopg2 import OperationalError

# 加载环境变量
load_dotenv()

def test_sync_connection():
    """测试同步数据库连接"""
    print("=== 测试同步数据库连接 ===")
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', '10.211.55.3'),
            port=os.getenv('DB_PORT', '5432'),
            dbname=os.getenv('DB_NAME', 'qadatabase'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres')
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ 同步连接成功！PostgreSQL版本: {version.split()[1]}")
        cursor.close()
        conn.close()
        return True
    except OperationalError as e:
        print(f"❌ 同步连接失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 同步连接出错: {e}")
        return False

async def main():
    """主函数"""
    print("数据库连接测试脚本")
    print("=" * 40)
    
    # 测试环境变量
    print(f"测试参数:")
    print(f"  主机: {os.getenv('DB_HOST', '10.211.55.3')}")
    print(f"  端口: {os.getenv('DB_PORT', '5432')}")
    print(f"  数据库: {os.getenv('DB_NAME', 'qadatabase')}")
    print(f"  用户: {os.getenv('DB_USER', 'postgres')}")
    print()
    
    print("注意：网络测试显示TCP端口5432是连通的，可能数据库服务已经可以访问！")
    print()
    
    # 运行测试
    sync_result = test_sync_connection()
    
    print("\n" + "=" * 40)
    if sync_result:
        print("🎉 所有测试通过！数据库连接正常")
        sys.exit(0)
    else:
        print("❌ 测试失败！请检查:")
        print("   1. PostgreSQL服务是否正在运行")
        print("   2. pg_hba.conf是否正确添加了10.211.55.0/24网段")
        print("   3. postgresql.conf的listen_addresses是否设置为'*'")
        print("   4. 数据库用户密码是否正确")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
