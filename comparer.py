
import csv
import argparse
import os
import time

parser = argparse.ArgumentParser(description="Compare errors and populate",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-f", "--file", help="input .csv file, example, WBS.csv", required=True)
parser.add_argument("-e", "--errors", help="file with matching errors", required=True)
args = parser.parse_args()
config = vars(args)
path = args.file
pathErrors = args.errors
file =os.path.splitext(os.path.basename(path))[0]
errors =os.path.splitext(os.path.basename(pathErrors))[0]
folder = os.path.dirname(path)

ERROR_MATCH_NOT_FOUND = 'ERROR - MATCH NOT FOUND'
rows_column = 'rows'

######Part1#####################################################
# populate WBS with WON2SAP data
start_time = time.time()
with open(path, encoding="utf-8") as inputFile:
    input_csv_reader = csv.DictReader(inputFile, delimiter=';')   
    filename = os.path.join(folder, f'{file}.output.csv')
    input_rows = list(input_csv_reader)
    
    modified_input = filename;
    with open(filename, 'w', newline='', encoding="utf-8") as outfile:
        fieldnames = input_csv_reader.fieldnames
        fieldnames = list(fieldnames)
        fieldnames.append('WBS_from_file')
        fieldnames.append('Outcome')
        output_csv_writer = csv.DictWriter(outfile, delimiter=';', fieldnames=fieldnames)

        with open(pathErrors) as inputErrors:      
            errors_csv_reader = csv.reader(inputErrors, delimiter='|')

            rows = list(errors_csv_reader)

#index with ProjectNumber and ResellerCode
            dumpDict1 = {}
            
# fill index for full match (ProjectNumber + ResellerCode)
            errorsLen = len(rows)

            for rowfd in rows:
                keys = list(rowfd)  
                if (len(keys) > 0):
                    # 4 - STATUS
                    if (keys[4] == ERROR_MATCH_NOT_FOUND):
                        new_key = (rowfd[1], rowfd[2], rowfd[3])
                        if (new_key in dumpDict1):
                            dd = dumpDict1[new_key]
                            dd[rows_column].append(rowfd)
                        
                        # rowfd[1] - CONTRACT_NUMBER, rowfd[2] - PRODUCTION_NUMBER, rowfd[3] - RESELLER_CODE
                        else:
                            val = { rows_column: [rowfd] }
                            dumpDict1[new_key] = val
            
            indexLen = len(list(dumpDict1.keys()))
            
            

            dumpDict2 = {}
            for row in input_rows:
                keys = list(row)
                if (len(keys) > 0):                    
                    # rowfd[21] - CONTRACT_NUMBER, rowfd[23] - PRODUCTION_NUMBER, rowfd[1] - RESELLER_CODE
                    dumpDict2[(row['ContractID'], row['ProductionNumber'], row['Reseller'].split(' ')[0])] = row
                    
            keys = list(dumpDict2.keys())
            
            match_count = 0;
            multi_match_count = 0;
            
            for key in keys:
                val = dumpDict2[key]
                if key in dumpDict1:
                    rows = dumpDict1[key][rows_column]
                    count = len(rows)
                    wbs = []
                    for r in rows:
                        wbs.append(r[0])
                    
                    val['WBS_from_file'] = ', '.join(wbs)
                    if count == 1:
                        val['Outcome'] = "MATCH"
                        match_count += 1
                        
                    if count > 1:
                        val['Outcome'] = "MULTIPLE MATCHES"
                        multi_match_count += 1
             
            input_result = []
            for row in input_rows:
                if len(list(row)) > 0:
                    key = (row['ContractID'], row['ProductionNumber'], row['Reseller'].split(' ')[0])
                    if key in dumpDict2:
                        val = dumpDict2[key]
                        row = val
                        input_result.append(row)
                        
            output_csv_writer.writeheader()
            output_csv_writer.writerows(input_result)
                
# counters for fillings
            # ref23_fill = 0
            # ref2_fill = 0
            # no_fill = 0
            # rows = list(input_csv_reader)
            # for row in rows:

                
                    
            #     output_csv_writer.writerow(newrow)


print("--- Matches:  %s, Multiple matches %s" % (match_count, multi_match_count))
######Part2########################################
print("--- %s seconds ---" % (time.time() - start_time))
                    




