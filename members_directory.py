# -*- coding: utf-8 -*-

import pymysql.cursors
import json

def getConnection():
    return pymysql.connect(host='memberdirectory.ckmg7ngdlvgc.ap-south-1.rds.amazonaws.com',
                           user='DhuperInfotech',
                           password='tushar1997',
                           db='membersdirectory',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)


def get_aws_image(bcid):
    if bcid == "":
        return ""
    aws_base_url = "https://s3.ap-south-1.amazonaws.com/dhcba/"
    return str(aws_base_url + str(bcid).replace("/", "x").replace(' ','').lower() + ".jpg").replace(' ','')


def get_member_directory_ByID(idz):
    # Connect to the database
    connection = getConnection()

    try:

        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * from hcba where ID = '{0}';".format(idz)
            try:
                cursor.execute(sql)
                response = cursor.fetchone()
                result = response
                image_id = get_aws_image(response["eno"])

            except Exception as e:
                print(e)
                # print "error"
                return {"status": "unsuccessful"}
            return_this = {"status": "successful", "data": result, "image": image_id}

            # #print return_this
            return return_this
    finally:
        connection.close()


def get_member_directory_ByNameSuggestionPagination(alpha, suggestion, offset):
    # Connect to the database
    connection = getConnection()

    try:

        with connection.cursor() as cursor:
            # Read a single record
            if suggestion == True:
                sql = "SELECT * from hcba where NAME LIKE '%{1}%' ORDER BY Name ASC LIMIT 100 OFFSET {0};".format(offset,alpha)
            else:
                sql = "SELECT * from hcba where NAME LIKE '{1}%' ORDER BY Name ASC LIMIT 100 OFFSET {0};".format(offset,alpha)
                # print sql
            #sql = "SELECT * from hcba where NAME COLLATE UTF8_GENERAL_CI  LIKE '%{1}%' ORDER BY Name ASC LIMIT 100 OFFSET {0};".format(offset,alpha)
            try:
                cursor.execute(sql)
                response = cursor.fetchall()
                result_arr = []
                for i in response:
                    i["image"] = get_aws_image(i["eno"])
                    # #print i
                    result_arr.append(i)
                # result = json.dumps(result_arr)
                result = result_arr
                # #print result
            except Exception as e:
                print(e)
                # print "error"
                return {"status": "unsuccessful"}
            return_this = {"status": "successful", "data": result}

            # #print return_this
            return return_this
    finally:
        connection.close()


def get_member_directory_ByNameSuggestion(alpha, suggestion):
    # Connect to the database
    connection = getConnection()

    try:

        with connection.cursor() as cursor:
            # Read a single record
            if suggestion == True:
                sql = "SELECT * from hcba where NAME LIKE '%{0}%' ORDER BY Name ASC;".format(alpha)
            else:
                sql = "SELECT * from hcba where NAME LIKE '{0}%' ORDER BY Name ASC;".format(alpha)
                # print sql
            #sql = "SELECT * from hcba where NAME COLLATE UTF8_GENERAL_CI LIKE '%{0}%' ORDER BY Name ASC;".format(alpha)
            try:
                cursor.execute(sql)
                response = cursor.fetchall()
                result_arr = []
                for i in response:
                    i["image"] = get_aws_image(i["eno"])
                    # #print i
                    result_arr.append(i)
                # result = json.dumps(result_arr)
                result = result_arr
                # #print result
            except Exception as e:
                print(e)
                # print "error"
                return {"status": "unsuccessfull"}
            return_this = {"status": "successful", "data": result}

            # #print return_this
            return return_this
    finally:
        connection.close()

def get_member_directory_ByEno(idz):
    # Connect to the database
    connection = getConnection()

    try:

        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * from hcba where eno = '{0}';".format(idz)
            try:
                cursor.execute(sql)
                response = cursor.fetchone()
                result = response
                image_id = get_aws_image(response["eno"])

            except Exception as e:
                print(e)
                # print "error"
                return {"status": "unsuccessful"}
            return_this = {"status": "successful", "data": result, "image": image_id}

            # #print return_this
            return return_this
    finally:
        connection.close()


def get_member_directory_ByStartingWord(keyword, starting_word):
    # Connect to the database
    connection = getConnection()

    try:

        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * from hcba where NAME COLLATE UTF8_GENERAL_CI  LIKE '{}%{}%' ORDER BY Name ASC;".format(starting_word, keyword[1:] if keyword[0].lower() == starting_word.lower() else keyword)
                # print sql
            try:
                cursor.execute(sql)
                response = cursor.fetchall()
                result_arr = []
                for i in response:
                    i["image"] = get_aws_image(i["eno"])
                    # #print i
                    result_arr.append(i)
                # result = json.dumps(result_arr)
                result = result_arr
                # #print result
            except Exception as e:
                print(e)
                # print "error"
                return {"status": "unsuccessful"}
            return_this = {"status": "successful", "data": result}

            # #print return_this
            return return_this
    finally:
        connection.close()

