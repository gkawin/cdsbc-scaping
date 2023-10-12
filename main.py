import base64
import csv
import itertools
import json

import requests
import xmltodict

# data.map((item) => {
#     const contact_id = item.contact_id
#     const practiceAddress = http.get(`"https://rest.cdsbc.org/restservice/details?id={contact_id}&what=practiceAddress";`)
# })

def lookup(l_name: str, region: str) -> list:
    s = base64.b64encode(json.dumps({
        "cidname":"dentist",
        "lName": l_name.upper(),
        "region": region,
        "showLimitations":"false"
    }).encode('utf-8')).decode('utf-8')

    lookup_url = f"https://rest.cdsbc.org/restservice/lookup?ipp=5000&pg=1&sp={s}"
    lookup = requests.get(lookup_url, 'GET')
    dict_data = xmltodict.parse(lookup.content)

    if not dict_data.get("string"):
        print(l_name + " " + region, lookup.status_code, dict_data)
        return []
    
    data_dict = json.loads(dict_data.get("string").get("#text"))
    print(l_name + " " + region, lookup.status_code)
    return data_dict[0]


if __name__ == '__main__':
    list_regions = ["Fraser Valley", "Vancouver", "Vancouver Island"]
    list_last_names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
                          "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
                            "U", "V", "W", "Y", "Z"]
    
    # data = []
    # for region in list_regions:
    #     for l_name in list_last_names:
    #         data.append(lookup(l_name, region))

    #     with open(f"{region}.json", 'a', newline='') as csvfile:
    #         shallow_list = list(itertools.chain(*data))
    #         json.dump(shallow_list, csvfile)
    ##########################################################


    result = []
    for region in list_regions:
        f = open(f"{region}.json", 'r')
        list_data = json.load(f)
       
        for idx, item in enumerate(list_data):
            contact_id = item['contactid']
            p_addr = requests.get(f"https://rest.cdsbc.org/restservice/details?id={contact_id}&what=practiceAddress", 'GET')
            dict_data = xmltodict.parse(p_addr.content)

            data_dict = json.loads(dict_data.get("string").get("#text"))
            if not data_dict: continue

            email = data_dict[0].get("emailaddress")[::-1]

            result.append([
                data_dict[0].get("firstname"),
                data_dict[0].get("lastname"),
                email,
                data_dict[0].get("cdsbc_phone"),
                data_dict[0].get("cdsbc_fax"),
                data_dict[0].get("cdsbc_street1"),
                data_dict[0].get("cdsbc_street2"),
                data_dict[0].get("cdsbc_street3"),
                data_dict[0].get("cdsbc_city"),
                data_dict[0].get("cdsbc_province"),
                data_dict[0].get("cdsbc_postalcode"),
                data_dict[0].get("cdsbc_countryidname")
            ])
            print(contact_id + " " + region, p_addr.status_code , "done")
            
        f.close()

    with open('dentists_contact.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['firstname','lastname','emailaddress','phone','fax','street1', 'street2', 'street3', 'city', 'province', 'postalcode', 'country'])
        for row in result:
            writer.writerow(row)
