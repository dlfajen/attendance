from datetime import datetime
import re

WHO_LIST_REG_EX = "^.+\]\s([a-z|A-Z]{3,})\s.+<(.+)>"
WHO_LIST_BEGIN_REG_EX = "^Players on EverQuest:$"
WHO_LIST_END_REG_EX = "^There\s.*\.$"

REG_EX_DICT = {"^([a-z|A-Z]{3,})\s(backstabs|bashes|bites|crushes|hits|kicks|pierces|punches|slashes)\s.+\sfor\s[0-9]+\spoint[s]* of damage.$":'CHAR',
               "^([a-z|A-Z]{3,})\ssays,\s.+$":'CHAR',
               "^([a-z|A-Z]{3,})'s\s(armor|blood|body|brain|ears|eyes|face|feet|fist|flesh|hair|hammer|hand|hands|head|image|mind|muscles|skin|song|veins|weapon|weapons|world|wounds)\s.+.$":'CHAR',
               "^([a-z|A-Z]{3,})\s(becomes|begins|blinks|blisters|breathes|calls|calms|casts|chokes|clutches|convulses|creates|disappears|dissolves|doesn't|dons|doubles|exhales|experiences|fades|feels|flees|floats|gains|gasps|glances|goes|grins|grows|has|inhales|lets|lights|looks|opens|peers|pulses|regains|rises|screams|sends|shrieks|shivers|shudders|sighs|simmers|singes|sings|slows|smiles|spews|spouts|staggers|stands|starts|steps|stops|strikes|summons|sweats|takes|turns|winces|writhes)\s.+.$":'CHAR',
               "^([a-z|A-Z]{3,})\s(blinks|combusts|dies|fades|moans|pales|panics|rages|shrinks|staggers|stumbles|weakens|winces|yawns).$":'CHAR',
               "^([a-z|A-Z]{3,})\sgoes into a berserker frenzy!":'CHAR',
               "^([a-z|A-Z]{3,})\sis no longer berserk.":'CHAR',
               "^([a-z|A-Z]{3,})\sscores a critical hit!":'CHAR',
               "^([a-z|A-Z]{3,})\sis\s(adorned|bathed|blasted|blinded|bound|chilled|cloaked|coated|completely|consumed|covered|encased|engulfed|entombed|enveloped|immolated|lacerated|mauled|pelted|protected|resistant|sheathed|slammed|smashed|struck|stunned|surrounded)\s.+.$":'CHAR',
               "^Glug, glug, glug...\s\s([a-z|A-Z]{3,})\stakes a drink from\s.+.$":'CHAR',
               "^Chomp, chomp, chomp...\s\s([a-z|A-Z]{3,})\stakes a bite from\s.+.$":'CHAR',
               "^A missed note brings\s([a-z|A-Z]{3,})'s\ssong to a close!":'CHAR',
               "^.+\s(backstabs|bashes|bites|crushes|hits|kicks|pierces|punches|slashes)\s([a-z|A-Z]{3,})\sfor\s[0-9]+\spoint[s]* of damage.$":'MOB',
               "^.+\s(engages)\s([a-z|A-Z]{3,})!$":'MOB',
               "^(\S+)\ssays 'Sorry, Master..calming down.'$":'PET',
               "^(\S+)\ssays 'At your service Master.'$":'PET',
               "^(\S+)\ssays 'Guarding with my life..oh splendid one.'$":'PET',
               "^(\S+)\ssays 'No longer taunting attackers, Master.'$":'PET',
               "([a-z|A-Z]{3,})\stells the guild,\s.+$":'GUILD',
               ".*(DKP|DPK|dkp|dpk|BIDS|bids|5-100|5 - 100|5-350|5 - 350|5-500|5 - 500).*":'DKP'}
             
# Constants
GUILD_STATUS = 0
FIRST_HIT = 1
LAST_HIT = 2
INACTIVITY = 3
FIRST_WHO = 4
LAST_WHO = 5
                  
attendance_list = dict()
dkp_lines = list()
pet_list = list()
guild_list = dict()
guild_name = "Azure Guard"

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

is_azure_guard = raw_input("Is your guild " + guild_name + "? (Y/N) ")
if is_azure_guard == 'N' or is_azure_guard == 'n':
    guild_name = raw_input("Enter your guild name exactly how it appears without the <>: (i.e. Azure Guard) ")
    
def update_attendance( char_name, date_object, type ):
    "This function updates the attendance for the character"
    if char_name in attendance_list:
        if type == 'HIT':
            # If first hit is not set, then character only has who entries so far - create a new hit entry
            if attendance_list[char_name][FIRST_HIT] is None:
                attendance_list[char_name][FIRST_HIT] = date_object
                attendance_list[char_name][LAST_HIT] = date_object
            # Check if hit is before first entry (happens if file has been pieced together out of order)
            elif attendance_list[char_name][FIRST_HIT] > date_object:
                attendance_list[char_name][FIRST_HIT] = date_object
            # Check if hit is after second entry (in case file is out of order)
            elif attendance_list[char_name][LAST_HIT] < date_object:
                # Check elapsed time since last update
                elapsed = date_object - attendance_list [char_name][LAST_HIT] 
                # If elapsed time greater than current elapsed time, update it
                if attendance_list[char_name][INACTIVITY] < elapsed.seconds:
                    attendance_list[char_name][INACTIVITY] = elapsed.seconds
                            
                # Update last entry
                attendance_list[char_name][LAST_HIT] = date_object
        else:
            # If first who is not set, then character only has hits so far - create a new who entry
            if attendance_list[char_name][FIRST_WHO] is None:
                attendance_list[char_name][FIRST_WHO] = date_object
                attendance_list[char_name][LAST_WHO] = date_object
            # Check if who is before first entry (happens if file has been pieced together out of order)
            elif attendance_list[char_name][FIRST_WHO] > date_object:
                attendance_list[char_name][FIRST_WHO] = date_object
            # Check if who is after second entry (in case file is out of order)
            elif attendance_list[char_name][LAST_WHO] < date_object:    
                attendance_list[char_name][LAST_WHO] = date_object
    else:
        # If name not in list, add timestamp to both first and last entries
        if type == 'HIT':
            attendance_list[char_name] = ['Unknown', date_object, date_object, 0, None, None]
        else:
            attendance_list[char_name] = ['Unknown', None, None, 0, date_object, date_object]
    return

is_in_who_list = False
    
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
 
            # If we're not within a /who list, check if this is the start of /who list.
            #   If not the start, then check the rest of the regular expression lists
            #   If it is the start, go to the next line
            # If we're within a /who list, check if this is the end of /who list
            #   If not the end, find the guild member name and add to the verified hits list and go to the next line
            #   If it is the end, go to the next line
            if is_in_who_list == False:
                m = re.search(WHO_LIST_BEGIN_REG_EX, log_data)
                if m:
                    is_in_who_list = True
                    continue
            else:
                m = re.search(WHO_LIST_END_REG_EX, log_data)
                if m:
                    is_in_who_list = False
                    continue
                else:
                    m = re.search(WHO_LIST_REG_EX, log_data)
                    if m:
                        update_attendance( m.group(1), date_object, 'WHO' )
                        # If guild member name not in list, add it
                        if m.group(1) not in guild_list:
                            guild_list[m.group(1)] = m.group(2)
                    continue
 
            # Look for regular expression list in data
            for regex, activity_type in REG_EX_DICT.items():
                m = re.search(regex, log_data)
                if m:
                    if activity_type == 'CHAR': 
                        update_attendance( m.group(1), date_object, 'HIT' )
                    elif activity_type == 'MOB':
                        update_attendance( m.group(2), date_object, 'HIT' )
                    elif activity_type == 'PET':
                        # If pet name not in list, add it
                        if m.group(1) not in pet_list:
                            pet_list.append(m.group(1))
                    elif activity_type == 'GUILD':
                        # If guild member name not in list, add it
                        if m.group(1) not in guild_list:
                            guild_list[m.group(1)] = guild_name
                    elif activity_type == 'DKP':        
                        # If DKP in line, add to DKP list
                        dkp_lines.append(line)
                
        elif date_object > raid_end_time:
            # Past raid end time, continue to next line (in case file is out of order)
            continue

# Remove pets from verified hits
for pet in pet_list:
    if pet in attendance_list:
        del attendance_list[pet]

# Update guild member status        
for guild_member in guild_list:
    if guild_member in attendance_list:
        attendance_list[guild_member][GUILD_STATUS] = guild_list[guild_member]

# Print results file        
file_name_array = file_name.split('.')        
out_file = open(file_name_array[0] + "_attendance.txt", "w")
out_file.write("Name, Guild Name, First Activity, Last Activity, Total Hours, Largest Inactive Period in Minutes, First Who Entry, Last Who Entry\n")
for k, v in sorted(attendance_list.items(), key = lambda item: (item[1][0],item[0])):
    out_file.write(k + ", " + str(v[GUILD_STATUS]) + ", " + str(v[FIRST_HIT] if v[FIRST_HIT] else "") + ", " + str(v[LAST_HIT] if v[LAST_HIT] else "") + ", " + str(v[LAST_HIT] - v[FIRST_HIT] if (v[LAST_HIT] and v[FIRST_HIT]) else "") + ", " + str(v[INACTIVITY]/60 if v[INACTIVITY] else "") + ", " + str(v[FIRST_WHO] if v[FIRST_WHO] else "") + ", " + str(v[LAST_WHO] if v[LAST_WHO] else "") + "\n")
    
for line in dkp_lines:
    out_file.write(line)

if len(pet_list) > 0:
    out_file.write("\nThe following 'pets' were removed - please verify:\n")
    for pet in pet_list:
        out_file.write(pet + "\n")

out_file.write("\nEasy raid uploading JavaScript:\n")
out_file.write("myArray = [")
needs_comma = False
for k, v in sorted(attendance_list.items()):
    if needs_comma:
        out_file.write(",")
    needs_comma = True;
    out_file.write("\"" + k + "\"")
out_file.write("];for(var i = 0; i < document.getElementById('listLeft').options.length; i++){for(var j = 0; j < myArray.length; j++){if(document.getElementById('listLeft').options[i].innerHTML.indexOf(myArray[j]) > -1) {document.getElementById('listLeft').options[i].selected = true;break;} else {document.getElementById('listLeft').options[i].selected = false;}}}")    

        