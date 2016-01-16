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
                             "^(\S+)\sfeels much better.",
                             "^(\S+)\shas been struck by lightning.",
                             "^(\S+)\screates a shimmering dimensional portal.",
                             "^(\S+)'s\seye gleams with the power of Aegolism.",
                             "^(\S+)\sfeels the favor of the gods upon them.",
                             "^(\S+)\ssteps into the shadows and disappears.",
                             "^(\S+)\sfades away.",
                             "^(\S+)\sis surrounded by a summer haze.",
                             "^(\S+)'s\simage shimmers.",
                             "^(\S+)'s\swounds fade away.",
                             "^(\S+)'s\sskin sears.",
                             "^(\S+)'s\ssong ends abruptly."
                            ]
                            
MOB_VERIFIED_REG_EX_LIST = ["^.+\s(backstabs|bashes|bites|crushes|hits|kicks|pierces|punches|slashes)\s(\S+)\sfor\s[0-9]+\spoint[s]* of damage.$"
                  ]              

PET_VERIFIED_REG_EX_LIST = ["^(\S+)\ssays 'Sorry, Master..calming down.'$",
                            "^(\S+)\ssays 'At your service Master.'$"]
                  
verified_hits = dict()
dkp_lines = list()
pet_list = list()

file_name = raw_input("Enter log file name: ")

run_entire_file = raw_input("Do you want to run attendance for the entire file? (Y/N) ")
if run_entire_file == 'Y' or run_entire_file == 'y':
    is_entire_file = True
else:
    is_entire_file = False

if not is_entire_file:    
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
        
        # Check if timestamp is after raid_start_time and before raid_end_time or if running entire file
        if is_entire_file or (raid_start_time < date_object and date_object < raid_end_time):
        
            # Get data past timestamp
            log_data = line[27:]
        
            # If DKP or 5-250 or 5-100 in line, add to DKP list
            if re.search('.*(DKP|5-250|5 - 250|5-100|5 - 100).*', log_data, re.IGNORECASE):
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
                 
                for regex in PET_VERIFIED_REG_EX_LIST:
                    m = re.search(regex, log_data)
                    if m:
                        # If pet name not in list, add it
                        if m.group(1) not in pet_list:
                            pet_list.append(m.group(1))
                
        elif date_object > raid_end_time:
            # Past raid end time, break out of loop
            break

# Remove pets from verified hits
for pet in pet_list:
    if pet in verified_hits:
        del verified_hits[pet]
            
out_file = open("attendance.txt", "w")            
for k, v in sorted(verified_hits.items()):
    out_file.write(k + ", " + str(v[0]) + ", " + str(v[1]) + "\n")

for line in dkp_lines:
    out_file.write(line)

if len(pet_list) > 0:
    out_file.write("The following 'pets' were removed - please verify:\n")
    for pet in pet_list:
        out_file.write(pet + "\n")