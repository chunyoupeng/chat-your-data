def generate_statements(markdown_str):
    lines = markdown_str.split("\n")
    hierarchy = []
    results = {}

    for line in lines:
        if not line.startswith("#"):
            continue

        # Count the number of '#' to determine the level of the title
        level = line.count('#')
        title = line.strip('# ').strip()

        # Update the hierarchy list based on the current level
        hierarchy = hierarchy[:level - 1] + [title]

        # For three or four level titles, generate the statements
        if level >= 3:
            statement = "中的".join(hierarchy)
            results[line] = statement

    return results

markdown_str = """
# 雷电天气下民航飞机的飞行风险及预防措施分析
## 绪论
### 研究背景
### 国内外研究进展
#### 国外研究进展
##### For test.....
#### 国内研究进展
### 研究意义及内容
---
## 雷雨天气过程及其影响概述
### 雷雨天对民航航班的影响
#### 起飞延误
#### 降落延误
#### 航班取消
### 多普勒天气雷达资料分析
---
## 雷电对民航机场电子设备的危害
### 机场电子设备与雷击
### 安装合理的避雷系统
### 对通信的电磁干扰影响
---
## 雷雨天气下的民航航班优化对策
### 调整航班计划
### 加强天气监测和预警
### 加强机组培训和准备
### 加强设备和设施安全
---
## 结语
### 总结
### 展望
"""

results = generate_statements(markdown_str)
print(results)
# for k, v in results.items():
#     print(f"{k}: {v}")
