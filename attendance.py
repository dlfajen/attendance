from datetime import datetime
import re

CHAR_VERIFIED_REG_EX_LIST = ["^(\S+)\sbegins to cast a spell.$",
                             "^(\S+)\s(backstabs|bashes|bites|crushes|hits|kicks|pierces|punches|slashes)\s.+\sfor\s[0-9]+\spoint[s]* of damage.$",
                             "^(\S+)\ssays,\s.+$",
                             "^(\S+)'s\shand is covered with a dull aura.$",
                             "^(\S+)\sbegins to walk faster.$",
                             "^(\S+)\sis completely healed.$",
                             "^(\S+)\slooks\s.+.$",
                             "^(\S+)\sbegins to regenerate.$",
                             "^(\S+)'s\seyes gleam with heroic resolution.$",
                             "^(\S+)\sfeels much better."
                            ]
                            
MOB_VERIFIED_REG_EX_LIST = ["^.+\s(backstabs|bashes|bites|crushes|hits|kicks|pierces|punches|slashes)\s(\S+)\sfor\s[0-9]+\spoint[s]* of damage.$"
                  ]              
                  
verified_hits = dict()
dkp_lines = list()

file_name = raw_input("Enter log file name: ")

raid_start = raw_input("Enter raid start time (YYYY-MM-DD HH:MM:SS format): ")
raid_start_time = datetime.strptime(raid_start, '%Y-%m-%d %H:%M:%S')

raid_end = raw_input("Enter raid end time (YYYY-MM-DD HH:MM:SS format): ")
raid_end_time = datetime.strptime(raid_end, '%Y-%m-%d %H:%M:%S')

file = open(file_name)
for line in file:
    if line.startswith("["):
        # Get timestamp
        date_string = line[1:25]
        date_object = datetime.strptime(date_string, '%a %b %d %H:%M:%S %Y')
        
        # Check if timestamp is after raid_start_time and before raid_end_time
        if raid_start_time < date_object and date_object < raid_end_time:
        
            # Get data past timestamp
            log_data = line[27:]
        
            # If DKP or 5-250 in line, add to DKP list
            if re.search('.*(DKP|5-250).*', log_data, re.IGNORECASE):
                dkp_lines.append(log_data)
            else:
            
                # Look for regular expression list in data
                for regex in CHAR_VERIFIED_REG_EX_LIST:
                    m = re.search(regex, log_data)
                    if m:
                        if m.group(1) in verified_hits:
                            # Update last entry
                            verified_hits[m.group(1)][1] = date_object
                        else:
                            # If name not in list, add timestamp to both first and last entries
                            verified_hits[m.group(1)] = [date_object, date_object]
            
                for regex in MOB_VERIFIED_REG_EX_LIST:
                    m = re.search(regex, log_data)
                    if m:
                        if m.group(2) in verified_hits:
                            # Update last entry
                            verified_hits[m.group(2)][1] = date_object
                        else:
                            # If name not in list, add timestamp to both first and last entries
                            verified_hits[m.group(2)] = [date_object, date_object]
                        
        elif date_object > raid_end_time:
            # Past raid end time, break out of loop
            break

out_file = open("attendance.txt", "w")            
for k, v in sorted(verified_hits.items()):
    out_file.write(k + ": " + str(v[0]) + ", " + str(v[1]) + "\n")

for line in dkp_lines:
    out_file.write(line)