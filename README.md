# interview

## 题目
请按要求完成以下api 功能
 Token Api: 通过手机号验证用户(不需要实现发短信功能)
Method: POST
Resource: /token
Payload: {“mobile”: “+86-12388888888”, “otp”: “123456”}
Response: {“access_token”: “xxx”, “refresh_token”: “xxx”, “expiry”: 12345}
 Profile Api: 获取用户本人基本信息
Method: GET
Resource: /profile
Authorization: Bearer token
Response: {“id”: 123, “first_name”: “tom”, “last_name”: “Jerry”}
技术要求：
1) 基于python, flask, Postgresql/MySql，如需要其他请自行决定
2) 通过docker-compose 运行
3) 代码上传到github/gitlab, 完成后请提供git url
4) 请在一周内完成以上功能