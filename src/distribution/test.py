import distribution_task_functions as func
import json

# 将数据存储在字典中

json_string = '''
[
    {
      "totalNums": 200,
      "terminalType":"1",
      "locationType": "2",
      "modelType": "1",
      "model": "1",
      "longitude": 123.32,
      "latitude": 43.34,
      "range": 200
    },
    {
      "totalNums": 200,
      "terminalType":"1",
      "locationType": "2",
      "modelType": "1",
      "model": "1",
      "longitude": 123.32,
      "latitude": 43.34,
      "range": 200
    }
]
'''

json_string = ''' [ { "totalNums":10, "terminalType":"车载终端", "locationType":1, "modelType":2, "model":1, "longitude":"116", "latitude":"40", "range":"50" } ] '''

# data = json.loads(json_string)
# print(data)


# 输出 JSON 字符串
# print(json_output)
json_string = json.loads(json_string)

ans = func.location_config(json_string)
# print(ans)
# print(type(ans))

# 业务配置测试
# 将数据存储在字典中
data2 = {
    "composition": [
    {
      "bizType": "1",
      "weight": 0.3
    },
    {
      "bizType": "2",
      "weight": 0.7
    }
    ],
    "time": "1",
    "totalNum": 100,
    "timeRange": [0, 468352476]
}

# 将字典转化为 JSON 字符串
json_output2 = json.dumps(data2, ensure_ascii=False)

# 输出 JSON 字符串
# print(json_output)
task_ans = func.task_config(json_output2)
# print(task_ans)

with open('task_data.json', 'w') as f:
    json.dump(task_ans, f)

  
with open('position.json', 'w') as f:
    json.dump(ans, f)

