import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-A0010-001"
params = {"Authorization": "CWA-4EE11799-4069-4DF2-A50B-B98BF5478258"}
res = requests.get(URL, params=params, verify=False)
print(res.status_code)
try:
    data = res.json()
    if "records" in data:
        print(list(data["records"].keys()))
        locations = data["records"].get("location", [])
        if locations:
            print("locationName:", locations[0].get("locationName"))
            weathers = locations[0].get("weatherElement", [])
            print("weatherElements:", [w.get("elementName") for w in weathers])
            if weathers:
                print("First element time keys:", list(weathers[0].get("time", [{}])[0].keys()))
                
except Exception as e:
    print(e)
