
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

WBS_FROM_FILE = 'WBS_FROM_FILE'
OUTCOME = 'OUTCOME'

######Part1#####################################################
# populate WBS with WON2SAP data
start_time = time.time()
with open(path, encoding="utf-8") as inputFile:
    input_csv_reader = csv.DictReader(inputFile, delimiter=';')   
    filename = os.path.join(folder, f'{file}.output.csv')
    errors_filename = os.path.join(folder, f'{errors}.output.csv')
    input_rows = list(input_csv_reader)
    
    modified_input = filename;
    with open(filename, 'w', newline='', encoding="utf-8") as outfile:
        fieldnames = input_csv_reader.fieldnames
        fieldnames = list(fieldnames)
        fieldnames.append(WBS_FROM_FILE)
        fieldnames.append(OUTCOME)
        output_csv_writer = csv.DictWriter(outfile, delimiter=';', fieldnames=fieldnames)

        with open(pathErrors) as inputErrors:      
            errors_csv_reader = csv.DictReader(inputErrors, delimiter='|')
            fieldnames = errors_csv_reader.fieldnames
            fieldnames = list(fieldnames)
            fieldnames.append(OUTCOME)
            error_rows = list(errors_csv_reader)
            
            with open(errors_filename, 'w', newline='', encoding="utf-8") as outputErrors:      
                errors_csv_writer = csv.DictWriter(outputErrors, delimiter='|', fieldnames=fieldnames)

#index with ProjectNumber and ResellerCode
                dumpDict1 = {}
            
    # fill index for full match (ProjectNumber + ResellerCode)
                errorsLen = len(error_rows)

                for rowfd in error_rows:
                    keys = list(rowfd)  
                    if (len(keys) > 0):
                        # 4 - STATUS
                        if (rowfd['STATUS'] == ERROR_MATCH_NOT_FOUND):
                            new_key = (rowfd['CONTRACT_NUMBER'], rowfd['PRODUCTION_NUMBER'], rowfd['RESELLER_CODE'])
                            if (new_key in dumpDict1):
                                dd = dumpDict1[new_key]
                                dd[rows_column].append(rowfd)
                        
                            # rowfd[1] - CONTRACT_NUMBER, rowfd[2] - , rowfd[3] - RESELLER_CODE
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
                   
                dumpDict3 = {}
                for row in input_rows:
                    keys = list(row)
                    if (len(keys) > 0):     
                        new_key = (row['ContractID'], row['ProductionNumber'], row['Reseller'].split(' ')[0])
                        if new_key in dumpDict3:
                            dd1 = dumpDict3[new_key]
                            dd1[rows_column].append(row)
                        else:
                            val = {rows_column : [row]}
                            dumpDict3[new_key] = val
                    
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
                            wbs.append(r['WBS_ELEMENT'])
                    
                        val[WBS_FROM_FILE] = ', '.join(wbs)
                        if count == 1:
                            val[OUTCOME] = "MATCH"
                            match_count += 1
                        
                        if count > 1:
                            val[OUTCOME] = "MULTIPLE MATCHES"
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
                
                for row in error_rows:
                    key = (row['CONTRACT_NUMBER'], row['PRODUCTION_NUMBER'], row['RESELLER_CODE'])
                    if key in dumpDict3:
                        record = dumpDict3[key]
                        inner_rows = record['rows']
                        inner_rows_count = len(inner_rows)
                        if (inner_rows_count == 1):
                            row[OUTCOME] = 'IN SUORALINJA'
                        if (inner_rows_count > 1):
                            row[OUTCOME] = 'IN SUORALINJA - MULTIPLE MATCHES'
                
                errors_csv_writer.writeheader()
                errors_csv_writer.writerows(error_rows)
                        
                    
                    
                
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
                    




