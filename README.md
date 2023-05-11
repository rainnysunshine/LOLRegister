# LOLRegister
# Contents
- 用于自动化注册lol账号
- 暂时只实现台服账号的自动注册，之后会支持其他地区账号注册
- 针对hcaptcha的三种验证图片类型，暂时实现了最常见的图片类型验证（我创了30个小号遇到其他情形的概率很低，等我再遇到时我再记录一下html格式然后完成其他类型图片的验证）
- 如果验证图片为九宫格图片之外的图片类型，暂时请尝试重新运行

# settings
## 验证图片所需api_key暂请自行提供
   在constants.py中填写api_key
## 账号设置 in settings/config.yaml
### 在config.yaml中，有两种账号设置方法
### 1. 直接在accounts下，自定义账号序号，设置username和password
### 2. 在settings中，设置autofill_account为true，此时1方法失效，实现账号按顺序命名注册
       例：注册3个账号，username从"apple4"命名到"apple6"，密码均为"123"
       则设置：account_nums: 3
              prefix_username: "apple"
              begin_num: 4
              common_password: "123"
