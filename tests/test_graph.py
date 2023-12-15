from graphviz import Digraph

# 创建图形
dot = Digraph(comment='安踏品牌的营销策略研究框架')

# 添加主要章节节点
dot.node('A', '一 绪论')
dot.node('B', '二 安踏公司介绍')
dot.node('C', '三 安踏营销过程中的转折性上升')
dot.node('D', '四 安踏具体营销策略')
dot.node('E', '五 安踏当前营销固化危机与应对之道')
dot.node('F', '六 结论')

# 添加子节点和连接
dot.node('A1', '1.1 研究背景')
dot.node('A2', '1.2 文献综述')
dot.edges(['AA1', 'AA2'])

dot.node('B1', '2.1 安踏公司基本概况')
dot.node('B2', '2.2 安踏历代营销成效')
dot.node('B3', '2.3 安踏目前发展趋势')
dot.edges(['AB1', 'AB2', 'AB3'])

dot.node('C1', '3.1 争夺国家级代言扩大影响')
dot.node('C2', '3.2 吃定奥运红利创造记忆点')
dot.node('C3', '3.3 娱乐明星效应扩大市场')
dot.edges(['BC1', 'BC2', 'BC3'])

dot.node('D1', '4.1 直营模式助力提质增效')
dot.node('D2', '4.2 营销推动品牌影响')
dot.node('D3', '4.3 合购联名营销多方市场')
dot.edges(['CD1', 'CD2', 'CD3'])

dot.node('E1', '5.1 目前安踏困境')
dot.node('E2', '5.2 安踏做好当代营销的措施')
dot.edges(['DE1', 'DE2'])

# 连接章节和子节点
dot.edges(['AB', 'BC', 'CD', 'DE', 'EF'])

# 图形设置
dot.attr(size='10,10')
dot.node_attr.update(color='lightblue2', style='filled')

dot.render('./expanded_anta_research_framework', format='png', cleanup=True)
dot

