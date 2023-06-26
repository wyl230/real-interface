from collections import defaultdict

class Multimap:
    def __init__(self):
        self.dict = defaultdict(list)

    def add(self, key, value):
        self.dict[key].append(value)

    def get(self, key):
        return self.dict[key]

    def remove(self, key, value):
        self.dict[key].remove(value)

    def get_dict(self):
        return self.dict

# # 示例用法
# mmap = Multimap()
# mmap.add("foo", 1)
# mmap.add("foo", 2)
# mmap.add("bar", 3)

# print(mmap.get("foo")) # 输出 [1, 2]
# print(mmap.get("bar")) # 输出 [3]

# mmap.remove("foo", 1)
# print(mmap.get("foo")) # 输出 [2]