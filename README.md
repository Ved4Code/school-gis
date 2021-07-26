# School GIS (School Mapping)

The objective of the project is to create a public domain database for schools and habitats from state level to village to individual school level with standard names and codes.

## Contributing

Currently, we are looking for people who can share resources to help us geocode addresses. Kindly reach out to us if you are interested, we would love to have you on board.

## Geocoding

Geocoding is the process of taking a text-based description of a location (i.e. address) and finding out its longitude and latitude to identify them on the map.

Here, we have a database of addresses of schools across India. Upon geocoding them all, we would be able to effectively map them.

### Prerequisites

- A Google Cloud Platform account (free to create with a credit card).
- Python 3.x installed on your system.

### Instructions

1. Once you have set up your GCP Account, log into the console.
2. Navigate to _APIs & Services_ and search for **Google Maps Geocoding API**. Click on **Enable**.
3. Now, search for **Credentials**. Proceed with _Create Credentials_ > _API Key_ and copy the newly generated key. You can optionally give a name to your API key (and can now safely close the GCP console).
4. Open our [Github Repository](https://github.com/digvijaysrathore/school-map) on a web browser and clone/download it (make sure to extract the downloaded zip file).
5. **Instructions for downloading addresses and placing them correctly are to be added**.
6. Open the folder in your preferred code editor and replace `API_KEY = 'your_api_key'` on line 41 with the API key we created in the 3rd step.
7. Run the python script with the name _geocoding.py_ with the following command `python geocoding.py`.
