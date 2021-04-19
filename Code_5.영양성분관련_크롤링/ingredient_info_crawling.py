from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import time
import pandas as pd

def pageInit():

    # initial setting
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.headless = True
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    options.add_argument("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15")
    options.add_argument("lang=ko_KR")

    try:
        driver = webdriver.Chrome("./chromedriver")
        driver.implicitly_wait(3)
    except:
        print("크롬 드라이버 없음. ")
        exit()
    try:
        search_url = "https://www.microsalts.com/diagnosis"
        driver.get(search_url)
        time.sleep(3)
    except:
        print("url 가져오는데 문제 발생. ")
        exit()
    # 광고창 뜨면 삭제
    try:
        driver.find_element_by_xpath('//*[@id="ch-plugin-core"]/div[4]/div/div[1]/div').click()
    except:
        pass
    print("웹 크롤 준비 완료.")
    return driver

def inputInfo(driver, relationship, sex, birth_year, height, weight, diagnosis, kidney_status, Cr_rate, info_error_msg_list):

    # paths
    relationship_path = {
        "self" : '//*[@id="relationType"]/div[2]/label[1]',
        "wife" : '//*[@id="relationType"]/div[2]/label[2]',
        "children" : '//*[@id="relationType"]/div[2]/label[3]',
        "parent" : '//*[@id="relationType"]/div[2]/label[4]',
        "else" : '//*[@id="relationType"]/div[2]/label[5]'
    }

    sex_path ={
        "male": '//*[@id="gender"]/div[2]/label[1]',
        "female": '//*[@id="gender"]/div[2]/label[2]'
    }

    birth_year_path = '//*[@id="bornYear"]/span/input'
    height_path = '//*[@id="height"]/span/input'
    weight_path = '//*[@id="weight"]/span/input'
    diagnosis_path = {
        "True" : '//*[@id="checkDiagnosis"]/div[2]/label[1]',
        "False": '//*[@id="checkDiagnosis"]/div[2]/label[2]'
    }
    kidney_status_path = {
        "1to3": '//*[@id="kidneyStatus"]/div[2]/label[1]',
        "4to5": '//*[@id="kidneyStatus"]/div[2]/label[2]',
        "in_dialysis": '//*[@id="kidneyStatus"]/div[2]/label[3]',
        "unknown": '//*[@id="kidneyStatus"]/div[2]/label[4]'
    }
    next_button = '//*[@id="__next"]/div[2]/div/div[2]/div[2]/form/button'

    creatinine_path = '//*[@id="__next"]/div[2]/div/div[2]/div[2]/form/div[6]/div[4]/div[1]/div/input'

    # return dict
    status = {
        "sex": sex,
        "relationship": relationship,
        "birth_Year": birth_year,
        "height": height,
        "weight": weight,
        "diagnosis": diagnosis,
        "kidney_status": kidney_status,
        "GFR" : ''
    }

    try:
        driver.find_element_by_xpath(relationship_path[relationship]).click()
        driver.find_element_by_xpath(sex_path[sex]).click()
    except:
        print(f"ERROR : {birth_year}년생 {sex}, {height}cm {weight}kg, 병원진단 = {diagnosis}")
        info_error_msg_list.append(f"{birth_year},{sex},{height},{weight},{diagnosis},{kidney_status}\n")

    # 입력 칸 모두 clear
    try:
        driver.find_element_by_xpath(birth_year_path).clear()
        driver.find_element_by_xpath(height_path).clear()
        driver.find_element_by_xpath(weight_path).clear()
        if kidney_status == "1to3" or kidney_status == "4to5" or kidney_status == "unknown":
            driver.find_element_by_xpath(creatinine_path).clear()

    except:
        print("input box clear error.\n")

    #정보 입력
    try:
        driver.find_element_by_xpath(birth_year_path).clear()
        driver.find_element_by_xpath(birth_year_path).send_keys(birth_year)
        driver.find_element_by_xpath(height_path).clear()
        driver.find_element_by_xpath(height_path).send_keys(height)
        driver.find_element_by_xpath(weight_path).clear()
        driver.find_element_by_xpath(weight_path).send_keys(weight)
        if diagnosis == False:
            driver.find_element_by_xpath(diagnosis_path["False"]).click()
        else:
            driver.find_element_by_xpath(diagnosis_path["True"]).click()
            driver.implicitly_wait(2)
            driver.find_element_by_xpath(kidney_status_path[kidney_status]).click()
            if kidney_status != "in_dialysis" or kidney_status != "unknown":
                #크레아티닌 수치 입력
                if Cr_rate >= 0:
                   driver.find_element_by_xpath(creatinine_path).send_keys(Cr_rate)
                   #사구체여과율 받기
                   GFR_ = driver.find_element_by_xpath('//*[@id="__next"]/div[2]/div/div[2]/div[2]/form/div[6]/div[4]/div[2]/div/span').text
                   status["GFR"] = GFR_[:-1]
        if not diagnosis:
           print(f"{birth_year}년생 {sex}, {height}cm {weight}kg, 병원진단 = {diagnosis} 정보 입력 완료.")
        else:
           print(f"{birth_year}년생 {sex}, {height}cm {weight}kg, 병원진단 = {diagnosis}, 질환 = {kidney_status}, 크레아티닌 = {Cr_rate} 정보 입력 완료.")
    except:
        print(f"ERROR : {birth_year}년생 {sex}, {height}cm {weight}kg, 병원진단 = {diagnosis}")
        info_error_msg_list.append(f"{birth_year},{sex},{height},{weight},{diagnosis},{kidney_status}\n")

        return status

    driver.find_element_by_xpath(next_button).click()
    driver.implicitly_wait(3)

    return status

def crawlGuidance(driver):

    # ingredients path
    kcal_path = '//*[@id="__next"]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[1]/div/strong'
    carbo_path = '//*[@id="__next"]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[2]/div/strong'
    kalium_path = '//*[@id="__next"]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[3]/div/strong'
    natrium_path = '//*[@id="__next"]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[4]/div/strong'
    protein_path = '//*[@id="__next"]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[5]/div/strong'
    phosphorus_path = '//*[@id="__next"]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[6]/div/strong' # 인

    #WebDriverWait(driver, 3).until(
    #    EC.element_located_selection_state_to_be((By.TAG_NAME, '#__next > div.Layout__Content-ddysr6-1.jQDfjp > div.diagnosisReport__ReportSection-sc-18y0yn7-2.egHpmt > div > div > div.ant-col.ant-col-24 > div.DiagnosisReportNutritions__Wrapper-sc-1pzgp43-0.fCbnxS > div.DiagnosisReportNutritions__Nutritions-sc-1pzgp43-2.fMTueU > div:nth-child(1) > div > strong'), True)
    #)
    time.sleep(1)

    try:
        kcal = driver.find_element_by_xpath(kcal_path).text
        carbo = driver.find_element_by_xpath(carbo_path).text
        kalium = driver.find_element_by_xpath(kalium_path).text
        natrium = driver.find_element_by_xpath(natrium_path).text
        protein = driver.find_element_by_xpath(protein_path).text
        phosphorus = driver.find_element_by_xpath(phosphorus_path).text

    except:
        print("parsing 실패. ")
        ing_list = {"fail" : True}
        return ing_list

    ing_list = {
        "kcal" : kcal,
        "carbo" : carbo,
        "kalium" : kalium,
        "natrium" : natrium,
        "protein" : protein,
        "phosphorus" : phosphorus
    }

    #return 값으로 영양성분 크롤링한 리스트 반환
    return ing_list

''' ----- main ----- '''

'''variables'''

# information variable
'''
sex_info = {"male" : "male", "female" : "female"}
relationship_info = {"self" : "self", "wife" : "wife", "children" : "children", "parent" : "parent", "else" : "else"}
birth_year_info = [i for i in range(1900,2022)]
height_info = [i for i in range(100, 221)]
weight_info = [i for i in range(25,201)]
diagnosis = False # default : 일반 사용자 (저염식)
kidney_status_info = {"1to3" : "1to3", "4to5" : "4to5", "in_dialysis" : "in_dialysis", "unknown" : "unknown"}
'''
Try_count = 0

## test case
sex_info = {"male" : "male"}
relationship_info = {"self" : "self"}
birth_year_info = [1975,1997]
height_info = [150,180]
weight_info = [50,80]
diagnosis = True # default : 일반 사용자
kidney_status_info = {"1to3" : "1to3"}

#list variable
info_error_msg_list = []
table_dict = {
    "sex" : [],
    "relationship" : [],
    "birth_Year" : [],
    "height" : [],
    "weight" : [],
    "diagnosis" : [],
    "kidney_status" : [],
    "Cr_rate" : [],
    "GFR" : [],
    "kcal": [],
    "carbo": [],
    "kalium": [],
    "natrium": [],
    "protein": [],
    "phosphorus": []
}

''' --- run --- '''
driver = pageInit()



if not diagnosis: #일반 저염식 사용자
    for sex in sex_info:
        for birth_year in birth_year_info:
            for height in height_info:
                for weight in weight_info:
                    status_list = inputInfo(driver, "self", sex, birth_year, height, weight, diagnosis, "",-1, info_error_msg_list)
                    ingredient_list = crawlGuidance(driver)

                    try: #예외 발생시 저장
                        if "fail" in ingredient_list.keys():
                            info_error_msg_list.append(f"{birth_year},{sex},{height},{weight},{diagnosis},-\n")
                        else: #크롤 정상적으로 진행시
                            table_dict["sex"].append(sex)
                            table_dict["relationship"].append("self")
                            table_dict["birth_Year"].append(birth_year)
                            table_dict["height"].append(height)
                            table_dict["weight"].append(weight)
                            table_dict["kidney_status"].append("-")
                            table_dict["GFR"].append("-")
                            table_dict["diagnosis"].append(diagnosis)
                            table_dict["kcal"].append(ingredient_list["kcal"])
                            table_dict["carbo"].append(ingredient_list["carbo"])
                            table_dict["kalium"].append(ingredient_list["kalium"])
                            table_dict["natrium"].append(ingredient_list["natrium"])
                            table_dict["protein"].append(ingredient_list["protein"])
                            table_dict["phosphorus"].append(ingredient_list["phosphorus"])
                    except:
                        print("크롤한 정보를 자료 저장하는데 실패. \n")

                    try:
                        # 정보 입력 page로 돌아가기
                        driver.find_element_by_xpath('//*[@id="__next"]/div[2]/div[2]/div/div/div[2]/div[1]/div[3]/a').click()
                        driver.implicitly_wait(3)
                    except:
                        print("건강정보 페이지 돌아가기 실패. driver 재시작.")
                        driver.close()
                        driver = pageInit()

diagnosis = True

if diagnosis: #콩팥 질환자
    #성별
    for sex in sex_info:
        #나이
        for birth_year in birth_year_info:
            #콩팥질환자
            for kidney_status in kidney_status_info:
                #키
                for height in height_info:
                    #몸무게
                    for weight in weight_info:
                        # 크레아티닌 수치
                        if kidney_status == "1to3":
                            for Cr_rate in range(30,121):
                                 status_list = inputInfo(driver, "self", sex, birth_year, height, weight, diagnosis, kidney_status, Cr_rate, info_error_msg_list)
                                 ingredient_list = crawlGuidance(driver)
                                 # 예외 발생시 저장
                                 if "fail" in ingredient_list.keys():
                                     info_error_msg_list.append(f"{birth_year},{sex},{height},{weight},{diagnosis},-\n")
                                 # 크롤 정상적으로 진행시
                                 else:
                                     table_dict["sex"].append(sex)
                                     table_dict["relationship"].append("self")
                                     table_dict["birth_Year"].append(birth_year)
                                     table_dict["height"].append(height)
                                     table_dict["weight"].append(weight)
                                     table_dict["kidney_status"].append(kidney_status)
                                     table_dict["Cr_rate"].append(Cr_rate)
                                     table_dict["GFR"].append(status_list["GFR"])
                                     table_dict["diagnosis"].append(diagnosis)
                                     table_dict["kcal"].append(ingredient_list["kcal"])
                                     table_dict["carbo"].append(ingredient_list["carbo"])
                                     table_dict["kalium"].append(ingredient_list["kalium"])
                                     table_dict["natrium"].append(ingredient_list["natrium"])
                                     table_dict["protein"].append(ingredient_list["protein"])
                                     table_dict["phosphorus"].append(ingredient_list["phosphorus"])

                                     print("해당 정보 table에 저장 완료. ")

                                 try:
                                     # 정보 입력 page로 돌아가기
                                     driver.find_element_by_xpath('//*[@id="__next"]/div[2]/div[2]/div/div/div[2]/div[1]/div[3]/a').click()
                                     driver.implicitly_wait(3)
                                 except:
                                     print(f"건강정보 페이지 돌아가기 실패. driver 재시작. 시도 : {Try_count}(6되면 멈춥니다.)")
                                     driver.close()
                                     time.sleep(5)
                                     Try_count = Try_count + 1
                                     if Try_count > 5:
                                         print("문제가 있어 저장 후 프로그램을 종료합니다.")
                                         try:
                                             df = pd.DataFrame().from_dict(table_dict, orient='index').transpose()
                                             df.head(10)
                                         except:
                                             print("데이터프레임화 실패 ")
                                         try:
                                             df.to_csv('타겟 고객 영양정보_미완.csv', index=True)
                                         except:
                                             print("csv파일 만들기 실패.. ㅠㅠ")

                                         driver.close()
                                         exit()
                                     driver = pageInit()

                        elif kidney_status == "4to5":
                            for Cr_rate in range(0,30):
                                 status_list = inputInfo(driver, "self", sex, birth_year, height, weight, diagnosis, kidney_status, Cr_rate, info_error_msg_list)
                                 ingredient_list = crawlGuidance(driver)
                                 # 예외 발생시 저장
                                 if "fail" in ingredient_list.keys():
                                     info_error_msg_list.append(f"{birth_year},{sex},{height},{weight},{diagnosis},-\n")
                                 # 크롤 정상적으로 진행시
                                 else:
                                     table_dict["sex"].append(sex)
                                     table_dict["relationship"].append("self")
                                     table_dict["birth_Year"].append(birth_year)
                                     table_dict["height"].append(height)
                                     table_dict["weight"].append(weight)
                                     table_dict["kidney_status"].append(kidney_status)
                                     table_dict["GFR"].append(status_list["GFR"])
                                     table_dict["diagnosis"].append(diagnosis)
                                     table_dict["kcal"].append(ingredient_list["kcal"])
                                     table_dict["carbo"].append(ingredient_list["carbo"])
                                     table_dict["kalium"].append(ingredient_list["kalium"])
                                     table_dict["natrium"].append(ingredient_list["natrium"])
                                     table_dict["protein"].append(ingredient_list["protein"])
                                     table_dict["phosphorus"].append(ingredient_list["phosphorus"])

                                     print("해당 정보 table에 저장 완료. ")
                                 try:
                                     # 정보 입력 page로 돌아가기
                                     driver.find_element_by_xpath('//*[@id="__next"]/div[2]/div[2]/div/div/div[2]/div[1]/div[3]/a').click()
                                     driver.implicitly_wait(3)
                                 except:
                                     print(f"건강정보 페이지 돌아가기 실패. driver 재시작. 시도 : {Try_count}(6되면 멈춥니다.)")
                                     driver.close()
                                     time.sleep(5)
                                     Try_count = Try_count + 1
                                     if Try_count > 5:
                                         print("문제가 있어 저장 후 프로그램을 종료합니다.")
                                         try:
                                             df = pd.DataFrame().from_dict(table_dict, orient='index').transpose()
                                             df.head(10)
                                         except:
                                             print("데이터프레임화 실패 ")
                                         try:
                                             df.to_csv('타겟 고객 영양정보_미완.csv', index=True)
                                         except:
                                             print("csv파일 만들기 실패.. ㅠㅠ")

                                         driver.close()
                                         exit()

                                     driver = pageInit()

# error message 저장
if len(info_error_msg_list) >= 1:
    with open("error.txt", mode= "wb") as w:
        for elem in info_error_msg_list:
            w.write(elem)

#dataframe으로 저장
try:
    df = pd.DataFrame().from_dict(table_dict, orient='index').transpose()
    df.head(10)
except:
    print("데이터프레임화 실패 ")
try:
    df.to_csv('타겟 고객 영양정보.csv', index= True)
except:
    print("csv파일 만들기 실패.. ㅠㅠ")


driver.close()
