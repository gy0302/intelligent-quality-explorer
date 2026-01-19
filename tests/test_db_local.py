#!/usr/bin/env python3
"""
测试本地数据库连接
"""
import os
import sys

print("=== 测试本地数据库连接 ===")

# 测试1: 检查本地PostgreSQL服务是否运行
print("\n1. 检查本地PostgreSQL服务是否运行...")
try:
    import subprocess
    result = subprocess.run(
        ["ps", "aux"], 
        capture_output=True, 
        text=True
    )
    
    if "postgres" in result.stdout:
        print("✓ 本地有PostgreSQL进程在运行")
        # 查看具体的PostgreSQL进程
        pg_processes = [line for line in result.stdout.splitlines() if "postgres" in line]
        for proc in pg_processes[:5]:  # 只显示前5个进程
            print(f"   {proc[:100]}...")
    else:
        print("✗ 本地没有PostgreSQL进程在运行")
except Exception as e:
    print(f"✗ 检查失败: {e}")

# 测试2: 测试连接到localhost
try:
    import psycopg2
    from psycopg2 import OperationalError
    
    print("\n2. 测试连接到localhost:5432...")
    
    conn_params = {
        "host": "localhost",
        "port": 5432,
        "database": "qadatabase",
        "user": "postgres",
        "password": "postgres",
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        cursor.execute("SELECT current_database()")
        dbname = cursor.fetchone()[0]
        
        print(f"✓ 连接localhost成功!")
        print(f"  PostgreSQL版本: {version.split()[1]}")
        print(f"  当前数据库: {dbname}")
        
        cursor.close()
        conn.close()
    except OperationalError as e:
        print(f"✗ 连接localhost失败: {e}")
    
except ImportError:
    print("✗ psycopg2未安装")

# 测试3: 测试连接到127.0.0.1
try:
    import psycopg2
    from psycopg2 import OperationalError
    
    print("\n3. 测试连接到127.0.0.1:5432...")
    
    conn_params = {
        "host": "127.0.0.1",
        "port": 5432,
        "database": "qadatabase",
        "user": "postgres",
        "password": "postgres",
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        cursor.execute("SELECT current_database()")
        dbname = cursor.fetchone()[0]
        
        print(f"✓ 连接127.0.0.1成功!")
        print(f"  PostgreSQL版本: {version.split()[1]}")
        print(f"  当前数据库: {dbname}")
        
        cursor.close()
        conn.close()
    except OperationalError as e:
        print(f"✗ 连接127.0.0.1失败: {e}")
    
except ImportError:
    print("✗ psycopg2未安装")

# 测试4: 检查DBWeaver的配置（如果有）
print("\n4. 检查DBWeaver配置建议...")
print("请打开DBWeaver，检查您的连接配置:")
print("   - 主机名/IP地址: 是localhost、127.0.0.1还是10.211.55.3?")
print("   - 端口: 是5432吗?")
print("   - 数据库名: 是qadatabase吗?")
print("   - 用户名/密码: 是postgres/postgres吗?")
print("   - 连接类型: 是TCP/IP、Unix Socket还是其他?")

# 测试5: 检查环境变量
try:
    print("\n5. 检查环境变量...")
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        print(f"DATABASE_URL环境变量: {db_url}")
    else:
        print("DATABASE_URL环境变量未设置")
        
    # 检查.env文件
    if os.path.exists(".env"):
        print(".env文件存在，内容如下:")
        with open(".env", "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    print(f"   {line.strip()}")
except Exception as e:
    print(f"✗ 检查环境变量失败: {e}")

print("\n=== 测试完成 ===")
print("\n如果DBWeaver可以连接但Python脚本不能，可能的原因:")
print("1. DBWeaver使用了不同的网络环境（如VPN）")
print("2. DBWeaver使用了本地连接（localhost/127.0.0.1）而不是IP")
print("3. DBWeaver使用了不同的连接参数")
print("4. Python环境的网络限制")
