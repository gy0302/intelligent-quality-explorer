#!/usr/bin/env python3
"""
测试不同数据库配置参数的工具脚本
"""
import os
import sys
import psycopg2
from psycopg2 import OperationalError

print("=== 数据库连接配置测试工具 ===")
print("\n请根据DBWeaver的实际连接配置填写以下信息:")

# 默认配置（根据.env文件）
default_config = {
    "host": "10.211.55.3",
    "port": 5432,
    "database": "qadatabase",
    "user": "postgres",
    "password": "postgres",
}

# 提示用户输入配置
print(f"\n当前默认配置:")
for key, value in default_config.items():
    print(f"  {key}: {value}")

print("\n请修改以下配置（按Enter使用默认值）:")

config = {}
for key, default_value in default_config.items():
    if key == "port":
        user_input = input(f"{key} [{default_value}]: ").strip()
        config[key] = int(user_input) if user_input else default_value
    else:
        user_input = input(f"{key} [{default_value}]: ").strip()
        config[key] = user_input if user_input else default_value

print(f"\n使用以下配置进行测试:")
for key, value in config.items():
    print(f"  {key}: {value}")

# 测试连接
print("\n测试连接中...")
try:
    conn = psycopg2.connect(**config)
    cursor = conn.cursor()
    
    # 测试基本查询
    cursor.execute("SELECT version()")
    version = cursor.fetchone()[0]
    
    cursor.execute("SELECT current_database()")
    dbname = cursor.fetchone()[0]
    
    cursor.execute("SELECT current_user")
    current_user = cursor.fetchone()[0]
    
    cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
    table_count = cursor.fetchone()[0]
    
    print(f"✓ 连接成功!")
    print(f"  PostgreSQL版本: {version.split()[1]}")
    print(f"  当前数据库: {dbname}")
    print(f"  当前用户: {current_user}")
    print(f"  public模式下的表数量: {table_count}")
    
    # 测试是否可以修改数据
    try:
        cursor.execute("CREATE TABLE IF NOT EXISTS test_table (id serial PRIMARY KEY, name varchar(50))")
        cursor.execute("INSERT INTO test_table (name) VALUES (%s) RETURNING id", ("test_data",))
        inserted_id = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM test_table WHERE id = %s", (inserted_id,))
        inserted_data = cursor.fetchone()
        cursor.execute("DELETE FROM test_table WHERE id = %s", (inserted_id,))
        conn.commit()
        print(f"✓ 数据操作测试成功 (插入ID: {inserted_id})")
    except Exception as e:
        conn.rollback()
        print(f"⚠️  数据操作测试失败: {e}")
    
    cursor.close()
    conn.close()
    
    # 生成.env文件更新建议
    print("\n=== .env文件更新建议 ===")
    print(f"将.env文件中的DATABASE_URL修改为:")
    print(f"DATABASE_URL=postgresql+asyncpg://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}")
    
    # 生成项目连接测试命令
    print("\n=== 项目连接测试命令 ===")
    print(f"使用新配置测试项目连接:")
    print(f"python -m tests.test_database")
    
except OperationalError as e:
    print(f"✗ 连接失败!")
    print(f"  错误信息: {e}")
    print(f"\n可能的解决方法:")
    print(f"1. 检查网络连接: ping {config['host']}")
    print(f"2. 检查PostgreSQL服务是否运行在{config['host']}:{config['port']}")
    print(f"3. 检查用户名和密码是否正确")
    print(f"4. 检查数据库是否存在")
    print(f"5. 检查防火墙/安全组设置")

except Exception as e:
    print(f"✗ 测试过程中发生意外错误: {e}")
    import traceback
    traceback.print_exc()

print("\n=== 测试完成 ===")
