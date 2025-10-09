# 分支定价算法调试指南

## 关键调试点

### 1. 列生成过程
```python
# 在 column_generation.py 的 solve 方法中设置断点
def solve(self, time_limit: int):
    # 断点1: 检查初始状态
    while not self.check_termination():
        # 断点2: 每次迭代开始
        self.invokeMaster(self.new_columns, time_limit)
        # 断点3: 主问题求解后
        self.new_columns = self.invokePricing(time_limit, self.dual)
        # 断点4: 定价问题求解后
```

### 2. 主问题求解
```python
# 在 master_problem.py 中
def solveMaster(self, time_limit):
    # 断点: 检查列数和约束
    print(f"当前列数: {len(self.varMap)}")
    # 断点: 求解后检查解
```

### 3. 定价问题求解
```python
# 在 exact_pricing_solver.py 中
def generate_columns(self, time_limit):
    # 断点: 检查对偶价格
    print(f"对偶价格: {self.dual}")
    # 断点: 检查生成的列
```

## 监视表达式建议

在 Watch 面板中添加：
- `self.iteration` - 当前迭代次数
- `self.masterObjective` - 主问题目标值
- `len(self.new_columns)` - 新生成的列数
- `self.dual` - 对偶变量值
- `self.upper_bound - self.lower_bound` - 优化间隙

## 条件断点示例

1. **特定迭代**: `self.iteration == 5`
2. **找到新列时**: `len(self.new_columns) > 0`
3. **收敛时**: `abs(self.upper_bound - self.lower_bound) < 0.01`
4. **特定顶点**: `any(0 in col.vertex_set for col in self.new_columns)`

## 调试会话流程

1. **启动调试** - 选择 "Python: 集成测试"
2. **设置断点** - 在关键位置
3. **逐步执行** - 使用 F10/F11
4. **检查状态** - 查看变量和表达式
5. **修改测试** - 根据发现的问题调整
6. **重新运行** - Ctrl+Shift+F5

## 常见问题调试

### 问题1: 主问题不可行
- 断点: `master_problem.solveMaster()`
- 检查: `len(self.column_pool.columns)`
- 解决: 确保有足够的初始列

### 问题2: 定价问题无解
- 断点: `pricing_solver.generate_columns()`
- 检查: `self.auxiliary_graph.weight_v`
- 解决: 验证对偶价格更新

### 问题3: 无限循环
- 断点: `column_generation.check_termination()`
- 检查: 终止条件逻辑
- 监视: 目标值变化趋势
