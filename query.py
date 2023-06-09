import requests
import json
# 接口2：参数查询
# 以下需要修改为东北大学服务器的ip port

def query():
  # ip = '192.168.117.173'
  # port = '30010'
  # ip = 'http://service-manager:8080/xw/param/query'
  # url = f'http://{ip}:{port}/xw/param/query'
  url = f'http://service-manager:8080/xw/param/query'
  data = {
    "moduleCode": "pku",
    "paramType": ["baseTime"]
  }

  json_data = json.dumps(data)
  # print(json_data)
  response = requests.post(url, data=json_data, headers={'Content-Type': 'application/json'})

  # print(response.status_code)
  # print(response.text)
  return response

if __name__ == '__main__':
  query()
