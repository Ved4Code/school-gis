from boto3 import Session
import botocore
import logging
import time
import pandas as pd
import csv
import geopandas as gpd
import numpy as np
import math
from shapely.geometry import Point
from os import listdir
from os.path import isfile, join

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# amazon boto3 config below
index_name = "LocationRes"

aws_access_key_id = "AKIAVGND6SUABTEOFUNR"
aws_secret_access_key = "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"

location = Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name='us-east-1'
).client("location")

# read file

onlyfiles = [f for f in listdir('input/') if isfile(join('input/', f))]
print(onlyfiles)

for input_file_without_directory in onlyfiles:
    input_filename = 'input/' + input_file_without_directory
    file_numbers = list()
    first_set = list()
    second_set = list()
    flag = 0 
    for character_file_numbers in input_file_without_directory:
        if (character_file_numbers == "'"):
            flag = 1
        if (flag == 0):
            if (character_file_numbers.isdigit()):
                first_set.append(character_file_numbers)
        else:
            if (character_file_numbers.isdigit()):
                second_set.append(character_file_numbers)
    output_filename = 'out_segment ' 
    for i in range(len(first_set)):
        output_filename = output_filename + first_set[i]
    output_filename = output_filename + '_-_'
    for i in range(len(second_set)):
        output_filename = output_filename + second_set[i]
    output_filename = output_filename + '.csv'
    print (output_filename)
# change the "w" below with "a" to avoid overwriting the output file



# single_address = addresses[0]
# resp = geocode_address(single_address)
# print(resp)

# read files
    #input_filename = "2000_Schools/segment 4'-'1.csv"
    #output_filename = "out_segment 4_-_1.csv"
    address_column_name = "Address"
    pincode_file_name = "yiyiyiyi.shp"

    #load data into a datafram
    data = pd.read_csv(input_filename, encoding='utf8')
    pincodeDf = gpd.read_file(pincode_file_name)


    #change pincodes from string type to int and set it as index of the DataFrame
    #print(pincodeDf)
    pincodeDf['pincode'] = pincodeDf['pincode'].astype(int)
    pincodeDf.set_index('pincode', inplace = True)

    if address_column_name not in data.columns:
        raise ValueError("Missing Address column in input data")

    school_codes = data["School Code"].tolist()
    school_codes = (data["School Code"]).tolist()

    #Store the address and pincodes of schools in a list for iteration 
    addresses = data[address_column_name].tolist()
    addresses = (data[address_column_name]).tolist()
    pincodesSCH = (data['Pincode']).tolist()

    # headers for the output file
    fields = ["School Code", "Address", "Longitude", "Latitude","isCorrect"]

    # replace the missing values with a dummy value
    

    for index, postal in enumerate(pincodesSCH):
        if (type(postal) == str):
            if (postal != postal):
                pincodesSCH[index] = '999999'
            if (postal == ""):
                pincodesSCH[index] = '999999'
            if (postal == "Pincode"):
                pincodesSCH[index] = '999999'
        if (type(postal) == int) | (type(postal) == float):
            if (math.isnan(postal)):
                pincodesSCH[index] = 999999.0

    # convert the pincodes in the list from float type to int
    pincodesSCH = list(map(int, pincodesSCH))

    with open(output_filename, "w") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        print("wrote csv fields")

    def geocode_address(address_line):

        try:
            if address_line == "":
                raise ValueError("Missing address line")

            try:
                t1 = time.time()
                # text = ("%s, %s %s %s" %
                #         (address_line, municipality_name, state_code, post_code))
                response = location.search_place_index_for_text(
                    IndexName=index_name, Text=address_line)
                t2 = time.time()
                logger.info("Geocode Time: %.3f" % (t2 - t1))

                data = response["Results"]
                if len(data) >= 1:
                    print(data)
                    point = data[0]["Place"]["Geometry"]["Point"]
                    label = data[0]["Place"]["Label"]
                    logger.debug("Match: [%s,%s] %s" % (point[0], point[1], label))

                    response = {
                        "Longitude": point[0],
                        "Latitude": point[1],
                        "Label": label,
                        "MultipleMatch": False
                    }

                    if len(data) > 1:
                        response["MultipleMatch"] = True
                else:
                    logger.debug("No geocoding results found")

                    response = {
                        "Error": "No geocoding results found"
                    }
            except botocore.exceptions.ClientError as ce:
                logger.exception(ce.response)
                response = {
                    ce.response["Error"]["Code"]: ce.response["Error"]["Message"]
                }
            except botocore.exceptions.ParamValidationError as pve:
                logger.exception(pve)
                response = {
                    "ParamValidationError": str(pve)
                }
        except Exception as e:
            logger.exception(e)
            response = {
                "Exception": str(e)
            }

        logger.info(response)

        return response


    for index, address in enumerate(addresses):
    # get the address and the pincode of a particular pincode
        res = geocode_address(address)
        code = pincodesSCH[index]
        # check if the school code is in the Postal data
        try:
            if code not in pincodeDf.index:
                single_row = [school_codes[index],
                        address, res["Longitude"], res["Latitude"], False]
            else:
                polygon = pincodeDf['geometry'].loc[code]
                point = Point(res["Longitude"], res["Latitude"])
                single_row = [school_codes[index],
                        address, res["Longitude"], res["Latitude"], polygon.intersects(point.buffer(0.04))]
        except Exception as e:
            logger.exception(e)
            response = {
                "Exception": str(e)
            }
        with open(output_filename, "a") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(single_row)
            print("Geocoded: {}: {}".format(index, res))
        print("taking break before running iteration")
        # taking a break
        time.sleep(0.1)
