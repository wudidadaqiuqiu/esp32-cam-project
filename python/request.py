import requests

# 目标 URL
url = 'http://10.248.98.2/cgi-bin/rad_user_info?callback=jQuery11240024302433711785865_1725983144325&_=1725983144326'

# 发送 GET 请求
response = requests.get(url)

# 获取状态码
print(f"Status Code: {response.status_code}")

# 获取响应内容
if response.status_code == 200:
    # print(f"Response Data: {response.json()}")
    print(response.text)
else:
    print(f"Failed to retrieve data: {response.status_code}")
