todo:
- mqtt消息连接测试：修改保持时间，或者减少重连时间
- 丢包率，修改receiver

注意：视频流或音频流，业务id设置成23023


以下忽略
<!-- 1. 接口1,3,4在routes.py中
2. 接口2在query.py中
3. 接口5在app.py中

东北系统发来的请求用curl工具代替测试，
东北系统发来的mqtt请求用mosquitto_pub工具代替测试， -->

<!-- 业务流启动测试 


2、接口定义：
生成用户分布接口
东北调北大，HTTP Post
url: http://ip:port/terminal/generate
request body:
{
  "config": [
    {
      "totalNums": 300, //总用户数
      ### 此处有修改
      "terminalType":"1",//终端类型
      "locationType": "1", //"1"静止，"2"运动
      "modelType": "1", //分布模型类型，确定性或区域随机或其他
      "model": "1", //指定具体的分布模型，如果是确定性分布，指定是使领馆还是省会城市还是其他，如果是随机分布，指定是中心分布还是其他
      "longitude": 123.32, //选择随机分布时，分布中心的经度
      "latitude": 43.34, //选择随机分布时，分布中心的维度
      "range": 200 //选择随机分布时，分布范围的半径，单位km
    },
    {
      "totalNums": 300, //总用户数
      ### 此处有修改
      "terminalType":"1",//终端类型
      "locationType": "1", //"1"静止，"2"运动
      "modelType": "1", //分布模型类型，确定性或区域随机或其他
      "model": "1", //指定具体的分布模型，如果是确定性分布，指定是使领馆还是省会城市还是其他，如果是随机分布，指定是中心分布还是其他
      "longitude": 123.32, //选择随机分布时，分布中心的经度
      "latitude": 43.34, //选择随机分布时，分布中心的维度
      "range": 200 //选择随机分布时，分布范围的半径，单位km
    }
  ]
}

response body:
{
  terminals: [
    {
      // 06-06修改：需要返回用户ID
      "terminalId": 1,
      "terminalName": "终端_1", //终端名称
      "terminalType", "1", //终端类型
      "locationType": "1", //"1"静止，"2"运动
      "longitude": 123.32, //如果是静止终端，终端的经度
      "latitude": "43.34, //如果是静止终端，终端的维度
      "positions": [ //如果是运动的终端，终端在每一时刻的位置
        {
          "timestamp": 957110400000,
          "longitude": 123.23,
          "latitude": 43.34
        },
        {
          "timestamp": 957110410000,
          "longitude": 123.23,
          "latitude": 43.34
        },
        {
          "timestamp": 957110420000,
          "longitude": 123.23,
          "latitude": 43.34
        },
        {
          "timestamp": 957110430000,
          "longitude": 123.23,
          "latitude": 43.34
        }
      ]
    },
    {
      // 06-06修改：需要返回用户ID
      "terminalId": 2,
      "terminalName": "终端_1", //终端名称
      "terminalType", "1", //终端类型
      "locationType": "1", //"1"静止，"2"运动
      "longitude": 123.32, //如果是静止终端，终端的经度
      "latitude": "43.34, //如果是静止终端，终端的维度
      "positions": [ //如果是运动的终端，终端在每一时刻的位置
        {
          "timestamp": 957110400000,
          "longitude": 123.23,
          "latitude": 43.34
        },
        {
          "timestamp": 957110410000,
          "longitude": 123.23,
          "latitude": 43.34
        },
        {
          "timestamp": 957110420000,
          "longitude": 123.23,
          "latitude": 43.34
        },
        {
          "timestamp": 957110430000,
          "longitude": 123.23,
          "latitude": 43.34
        }
      ]
    }
  ]
}

回复：修改部分在request body中，每次调用接口生成一个区域的某种用户终端的分布【对于随机分布是如此】。

import time
print(round((time.time() * 1000)))

1686194336080


curl -X POST -H "Content-Type: application/json" -d '{ "param": [ { "paramType": "baseTime", "paramName": "realTime", "paramValue": "1686194336080" }, { "paramType": "baseTime", "paramName": "simulationTime", "paramValue": "0" } ] }' http://127.0.0.1:5001/param/config

curl -X POST -H "Content-Type: application/json" -d '{ "param": [{ "insId": 1, "startTime": 2000, "endTime": 10000, "source": 153, "destination": 283, "bizType": "1" }, { "insId": 2, "startTime": 4000, "endTime": 6000, "source": 154, "destination": 284, "bizType": "1" } ] }' http://127.0.0.1:5001/simulation/loadStream


{ "param": [{ "insId": 1, "startTime": 2000, "endTime": 10000, "source": 153, "destination": 283, "bizType": "1" }, { "insId": 2, "startTime": 4000, "endTime": 6000, "source": 154, "destination": 284, "bizType": "1" } ] }

{
 "param": [{
   "insId": 1,
   "startTime": 2000,
   "endTime": 10000,
   "source": 153,
   "destination": 283,
   "bizType": "1"
  },
  {
   "insId": 2,
   "startTime": 4000,
   "endTime": 6000,
   "source": 154,
   "destination": 284,
   "bizType": "1"
  }
 ]
} -->
