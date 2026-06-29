import requests

url = "https://api.nhtsa.gov/complaints/complaintsByVehicle"
params = {"make": "Tesla", "model": "Model 3", "modelYear": "2020"}

r = requests.get(url, params=params)

print("状态码:", r.status_code)
print("实际请求的网址:", r.url)
print("返回内容前 500 字:")
print(r.text[:500])
