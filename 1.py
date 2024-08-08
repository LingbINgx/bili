import pymysql
import time
import datetime
import asyncio
from bili_api.user_card import user_information as info
from bili_api.Response import Request

cnx = pymysql.connect(
    user='',
    password='',
    host='',
    database='',
    port="",
)
cursor = cnx.cursor()


def personinfo():
    query = "SELECT * FROM information ORDER BY mid DESC LIMIT 1"
    cursor.execute(query)
    result = cursor.fetchone()
    print(result)
    if result is not None:
        mid = result[0]
    else:
        mid = 490696436
    id = 0
    while mid < 999999999:
        mid += 1
        id += 1
        print(id, end='\t')
        response = info(net).user_card_info(mid=mid)
        res = asyncio.run(analyse(response=response, mid=mid))
        if res == '-412':
            mid -= 1
    cnx.commit()
    cursor.close()
    cnx.close()


async def analyse(response: dict, mid: int):
    t = 1.9
    if response["code"] == 0:
        task1 = asyncio.create_task(sleep(sleeptime=t))
        task2 = asyncio.create_task(write_sql(response=response))
        await asyncio.gather(task1, task2)
        return '0'
    elif response["code"] == -412:
        print("412 wait " + str(mid))
        time.sleep(3)
        return '-412'
    else:
        print("no return " + str(mid))
        task3 = asyncio.create_task(sleep(sleeptime=t))
        await task3
        return 'no return'


async def sleep(sleeptime):
    await asyncio.sleep(sleeptime)


async def write_sql(response: dict):
    insert_data = [
        (
            response["data"]["card"]["mid"],
            response["data"]["card"]["name"],
            response["data"]["card"]["sex"],
            response["data"]["card"]["level_info"]["current_level"],
            response["data"]["card"]["vip"]["type"],
            response["data"]["card"]["fans"],
            response["data"]["card"]["birthday"],
            response["data"]["card"]["face"],
            response["data"]["archive_count"],
            response["data"]["card"]["Official"]["role"]
        )
    ]
    insert_statement = (
        "INSERT INTO information (mid, name, sex, level, viptype, fans, birth, face, archive_count, official) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    for data in insert_data:
        cursor.execute(insert_statement, data)
    cnx.commit()
    print(datetime.datetime.now().strftime('%m-%d %H:%M:%S'), end='  ')
    print(
        response["data"]["card"]["mid"],
        response["data"]["card"]["name"],
        response["data"]["card"]["sex"],
        response["data"]["card"]["level_info"]["current_level"],
        response["data"]["card"]["vip"]["type"],
        response["data"]["card"]["fans"],
        response["data"]["card"]["birthday"],
        response["data"]["card"]["face"],
        response["data"]["archive_count"],
        response["data"]["card"]["Official"]["role"]
    )


if __name__ == '__main__':
    while True:
        try:
            net = Request()
            personinfo()
        except:
            print("ERROR!")
            time.sleep(3)
