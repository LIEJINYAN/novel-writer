import sys
sys.path.insert(0, '.')

from core.methods.registry import METHOD_REGISTRY, get_method, list_methods

print('=== 写作方法注册表 ===')
print('方法数量:', len(METHOD_REGISTRY))
print('所有key:', list(METHOD_REGISTRY.keys()))

method = get_method('three-act')
print('get_method("three-act") 返回:', method)
if method:
    print('  方法名:', method.name)
    print('  节点数:', len(method.plot_nodes))
    for node in method.plot_nodes[:2]:
        print('    -', node.name)

print()
print('=== list_methods ===')
for m in list_methods()[:3]:
    print('  ', m.id, '-', m.name)
