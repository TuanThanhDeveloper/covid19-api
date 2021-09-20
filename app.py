from flask import Flask, jsonify
from flask_restful import Api, Resource
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
api = Api(app)
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False

opts = Options()
opts.add_argument("user-agent=1234")
opts.add_argument('headless')
opts.add_argument("--disable-gpu")
opts.add_argument("--no-sandbox")
driver1 = webdriver.Chrome(chrome_options=opts, executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(chrome_options=opts, executable_path=ChromeDriverManager().install())
url = "https://covid19.gov.vn/"


def total(driver):
    data1 = []
    driver.get(url)
    driver.switch_to.frame(0)
    for value in driver.find_elements_by_class_name("value"):
        data1.append(value.get_attribute("textContent"))
    for value in driver.find_elements_by_class_name("note"):
        data1.append(value.get_attribute("textContent"))
    driver.close()
    driver.quit()
    return data1


def detail(driver):
    citys = []
    totals = []
    day_now = []
    dies = []
    driver.get(url)
    driver.switch_to.frame(1)
    for city in driver.find_elements_by_class_name("city"):
        citys.append(city.text)
    for total1 in driver.find_elements_by_class_name("total"):
        totals.append(total1.text)
    for daynow in driver.find_elements_by_class_name("daynow"):
        day_now.append(daynow.text)
    for die in driver.find_elements_by_class_name("die"):
        dies.append(die.text)
    citys.pop(0)
    totals.pop(0)
    day_now.pop(0)
    dies.pop(0)
    data2 = []
    for i in range(len(citys)):
        data2.append({"province": citys[i],
                      "cases": totals[i],
                      "newCases": day_now[i][1:],
                      "death": dies[i]
                      })
    driver.close()
    driver.quit()
    return data2


def data():
    a = total(driver)
    data1 = {
        "Author": "https://www.facebook.com/trantuanthanh0803/",
        "surceUrl": "https://covid19.gov.vn/",
        "lastUpdatedAtSource": datetime.now(),
        "data": [{"Global": {"total": a[4],
                             "newCases": a[12][9:],
                             "activateCases": a[5],
                             "recovered": a[6],
                             "newRecovered": a[15][9:],
                             "death": a[7],
                             "newDeath": a[14][9:],
                             }},
                 {"VietNam": {"total": a[0],
                              "newCases": a[8][9:],
                              "activateCases": a[1],
                              "recovered": a[2],
                              "newRecovered": a[10][9:],
                              "death": a[3],
                              "newDeath": a[11][9:],
                              "detail": detail(driver1),
                              },
                  }]
            }
    return data1


response = data()


def update():
    global response
    response = data()
    print("update")


sched = BackgroundScheduler(daemon=True)
sched.add_job(update, 'interval', minutes=60)
sched.start()


class Covid(Resource):
    def get(self):
        if response:
            return jsonify(response)
        else:
            return {"message":"error"}


api.add_resource(Covid, "/covid")
if __name__ == '__main__':
    app.run(debug=True)
