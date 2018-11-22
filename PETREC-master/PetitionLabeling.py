import csv

def csv_dict_reader(file_obj):
    """
    Read a CSV file using csv.DictReader
    """
    catDict={}
    reader = csv.DictReader(file_obj, delimiter=',')
    for line in reader:
        if line["Category1"] in catDict:
            catDict[line["Category1"]]+=1
        else:
            catDict[line["Category1"]]=0
        if line["Category2"] in catDict:
            catDict[line["Category2"]]+=1
        else:
            catDict[line["Category2"]]=0
        if line["Category3"] in catDict:
            catDict[line["Category3"]]+=1
        else:
            catDict[line["Category3"]]=0
        if line["Category4"] in catDict:
            catDict[line["Category4"]] += 1
        else:
            catDict[line["Category4"]] = 0
        if line["Category5"] in catDict:
            catDict[line["Category5"]] += 1
        else:
            catDict[line["Category5"]] = 0
    return catDict



if __name__ == "__main__":
    with open("High_level_labeling_petitions.csv") as f_obj:
        highLevelCatDict=csv_dict_reader(f_obj)
    with open('High_level_categories.csv', 'wb') as csv_high_level_categories:
        writer = csv.writer(csv_high_level_categories)
        for key, value in highLevelCatDict.items():
            writer.writerow([key, value])

    with open("Labeling_petitions.csv") as f_obj:
        labelingCatDict=csv_dict_reader(f_obj)
    with open('Labeling_categories.csv', 'wb') as csv_labeling_categories:
        writer = csv.writer(csv_labeling_categories)
        for key, value in labelingCatDict.items():
            writer.writerow([key, value])
