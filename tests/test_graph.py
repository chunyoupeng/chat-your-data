from graphviz import Digraph

dot = Digraph(comment='格力电器发展历程')

# 定义节点
dot.node('A', '1991年: 成立')
dot.node('B', '1994年: 探索线上市场')
dot.node('C', '2000年: 收购海尔')
dot.node('D', '2002年: 国际化发展')
dot.node('E', '2005年: 全球知名品牌')
dot.node('F', '2006年: 自主研发')
dot.node('G', '2012年: 投资管理信息化')
dot.node('H', '董明珠: 推动创新和技术升级')

# 定义节点之间的关系
dot.edges(['AB', 'BC', 'CD', 'DE', 'EF', 'FG'])
dot.edge('G', 'H', '董明珠的领导')

# 打印和渲染图像
print(dot.source)
dot.render('格力电器发展历程', view=True, format='png')
