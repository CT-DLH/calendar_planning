from setuptools import setup, find_packages
import os

# 读取 requirements.txt 文件获取依赖
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

# 过滤掉带有平台条件的依赖
filtered_requirements = []
for req in requirements:
    if ';' not in req:
        filtered_requirements.append(req)
    elif 'platform_system == "Windows"' in req and os.name == 'nt':
        filtered_requirements.append(req.split(';')[0].strip())
    elif 'platform_system == "Darwin"' in req and os.name == 'posix' and 'darwin' in os.uname().sysname.lower():
        filtered_requirements.append(req.split(';')[0].strip())
    elif 'platform_system == "Linux"' in req and os.name == 'posix' and 'linux' in os.uname().sysname.lower():
        filtered_requirements.append(req.split(';')[0].strip())

setup(
    name="ai-calendar-manager",
    version="1.0.0",
    description="一个功能强大的 Python 日历 GUI 组件，支持 AI 辅助创建日程",
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your-email@example.com",
    url="https://github.com/your-username/ai-calendar-manager",
    packages=find_packages(),
    package_data={
        '': ['*.json'],
    },
    include_package_data=True,
    install_requires=filtered_requirements,
    entry_points={
        'console_scripts': [
            'ai-calendar=main:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
    ],
    python_requires='>=3.7',
)
