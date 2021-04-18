from selenium import webdriver
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

def inputInfo(driver, relationship, sex, birth_year, height, weight, diagnosis, kidney_status, info_error_msg_list):
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

    status = {
        "sex": sex,
        "relationship": relationship,
        "birth_Year": birth_year,
        "height": height,
        "weight": weight,
        "diagnosis": diagnosis,
        "kidney_status": kidney_status,
    }
    try:
        driver.find_element_by_xpath(relationship_path[relationship]).click()
        driver.find_element_by_xpath(sex_path[sex]).click()
        driver.find_element_by_xpath(birth_year_path).send_keys(birth_year)
        driver.find_element_by_xpath(height_path).send_keys(height)
        driver.find_element_by_xpath(weight_path).send_keys(weight)
        if diagnosis == False:
            driver.find_element_by_xpath(diagnosis_path["False"]).click()
        else:
            driver.find_element_by_xpath(diagnosis_path["True"]).click()
            driver.implicitly_wait(2)
            driver.find_element_by_xpath(kidney_status_path[kidney_status]).click()

        print(f"{birth_year}년생 {sex}, {height}cm {weight}kg, 병원진단 = {diagnosis} 정보 입력 완료.")
    except:
        print(f"ERROR : {birth_year}년생 {sex}, {height}cm {weight}kg, 병원진단 = {diagnosis}")
        info_error_msg_list.append(f"{birth_year},{sex},{height},{weight},{diagnosis},{kidney_status}\n")
        return status

    driver.find_element_by_xpath(next_button).click()
    driver.implicitly_wait(3)

    return status



def crawlGuidance(driver, info_error_msg_list):

    # ingredients path
    kcal_path = '//*[@id="__next"]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[1]/div/strong'
    carbo_path = '//*[@id="__next"]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[2]/div/strong'
    kalium_path = '//*[@id="__next"]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[3]/div/strong'
    natrium_path = '//*[@id="__next"]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[4]/div/strong'
    protein_path = '//*[@id="__next"]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[5]/div/strong'
    phosphorus_path = '//*[@id="__next"]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[6]/div/strong' # 인

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

''' --- variables --- '''

# information variable
sex_info = {"male" : "male", "female" : "female"}
relationship_info = {"self" : "self", "wife" : "wife", "children" : "children", "parent" : "parent", "else" : "else"}
birth_year_info = [i for i in range(1900,2022)]
height_info = [i for i in range(100, 221)]
weight_info = [i for i in range(25,201)]
diagnosis = False # default : 일반 사용자 (저염식)
kidney_status_info = {"1to3" : "1to3", "4to5" : "4to5", "in_dialysis" : "in_dialysis", "unknown" : "unknown"}

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
                    status_list = inputInfo(driver, "self", sex, birth_year, height, weight, diagnosis, "", info_error_msg_list)
                    ingredient_list = crawlGuidance(driver)

                    #예외 발생시 저장
                    if ingredient_list["fail"] == True:
                        info_error_msg_list.append(f"{birth_year},{sex},{height},{weight},{diagnosis},-\n")
                    #크롤 정상적으로 진행시
                    else:
                        table_dict["sex"].append(sex)
                        table_dict["relationship"].append("self")
                        table_dict["birth_Year"].append(birth_year)
                        table_dict["height"].append(height)
                        table_dict["weight"].append(weight)
                        table_dict["kidney_status"].append("-")
                        table_dict["diagnosis"].append(diagnosis)
                        table_dict["kcal"].append(ingredient_list["kcal"])
                        table_dict["carbo"].append(ingredient_list["carbo"])
                        table_dict["kalium"].append(ingredient_list["kalium"])
                        table_dict["natrium"].append(ingredient_list["natrium"])
                        table_dict["protein"].append(ingredient_list["protein"])
                        table_dict["phosphorus"].append(ingredient_list["phosphorus"])

                    try:
                        # 정보 입력 page로 돌아가기
                        driver.find_element_by_xpath('//*[@id="__next"]/div[2]/div[2]/div/div/div[2]/div[1]/div[3]/a').click()
                        driver.implicitly_wait(3)
                    except:
                        print("건강정보 페이지 돌아가기 실패. driver 재시작.")
                        driver.close()
                        driver = pageInit()

if diagnosis: #콩팥 질환자
    for sex in sex_info:
        for birth_year in birth_year_info:
            for kidney_status in kidney_status_info:
                for height in height_info:
                    for weight in weight_info:
                        status_list = inputInfo(driver, "self", sex, birth_year, height, weight, diagnosis, kidney_status, info_error_msg_list)
                        ingredient_list = crawlGuidance(driver)
                        # 예외 발생시 저장
                        if ingredient_list["fail"] == True:
                            info_error_msg_list.append(f"{birth_year},{sex},{height},{weight},{diagnosis},-\n")
                        # 크롤 정상적으로 진행시
                        else:
                            table_dict["sex"].append(sex)
                            table_dict["relationship"].append("self")
                            table_dict["birth_Year"].append(birth_year)
                            table_dict["height"].append(height)
                            table_dict["weight"].append(weight)
                            table_dict["kidney_status"].append(kidney_status)
                            table_dict["diagnosis"].append(diagnosis)
                            table_dict["kcal"].append(ingredient_list["kcal"])
                            table_dict["carbo"].append(ingredient_list["carbo"])
                            table_dict["kalium"].append(ingredient_list["kalium"])
                            table_dict["natrium"].append(ingredient_list["natrium"])
                            table_dict["protein"].append(ingredient_list["protein"])
                            table_dict["phosphorus"].append(ingredient_list["phosphorus"])

                    try:
                        # 정보 입력 page로 돌아가기
                        driver.find_element_by_xpath('//*[@id="__next"]/div[2]/div[2]/div/div/div[2]/div[1]/div[3]/a').click()
                        driver.implicitly_wait(3)
                    except:
                        print("건강정보 페이지 돌아가기 실패. driver 재시작.")
                        driver.close()
                        driver = pageInit()

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
