from boto3 import Session
import botocore
import logging
import time
import pandas as pd
import csv

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# amazon boto3 config below
index_name = "LocationRes"

aws_access_key_id = ""
aws_secret_access_key = ""

location = Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name='us-east-1'
).client("location")

# read file
input_filename = "./segment1-17.csv"
output_filename = "outfile.csv"
address_column_name = "Address"

data = pd.read_csv(input_filename, encoding='utf8')

if address_column_name not in data.columns:
    raise ValueError("Missing Address column in input data")

school_codes = data["School Code"].tolist()
school_codes = (data["School Code"]).tolist()

addresses = data[address_column_name].tolist()
addresses = (data[address_column_name]).tolist()

# headers for the output file
fields = ["School Code", "Address", "Longitude", "Latitude"]

# change the "w" below with "a" to avoid overwriting the output file
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


# single_address = addresses[0]
# resp = geocode_address(single_address)
# print(resp)

for index, address in enumerate(addresses):
    res = geocode_address(address)
    single_row = [school_codes[index],
                  address, res["Longitude"], res["Latitude"]]
    with open(output_filename, "a") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(single_row)
        print("Geocoded: {}: {}".format(index, res))
    print("taking break before running iteration")
    # taking a break
    time.sleep(1)
