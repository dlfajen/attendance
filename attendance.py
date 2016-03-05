from datetime import datetime
import re

CHAR_VERIFIED_REG_EX_LIST = ["^([a-z|A-Z]{3,})\s(backstabs|bashes|bites|crushes|hits|kicks|pierces|punches|slashes)\s.+\sfor\s[0-9]+\spoint[s]* of damage.$",
                             "^([a-z|A-Z]{3,})\ssays,\s.+$",
                             "^([a-z|A-Z]{3,})'s\s(armor|blood|body|brain|ears|eyes|face|feet|fist|flesh|hair|hammer|hand|hands|head|image|mind|muscles|skin|song|veins|weapon|weapons|world|wounds)\s.+.$",
                             "^([a-z|A-Z]{3,})\s(becomes|begins|blinks|blisters|breathes|calls|calms|casts|chokes|clutches|convulses|creates|disappears|dissolves|doesn't|dons|doubles|exhales|fades|feels|flees|floats|gains|gasps|glances|goes|grins|grows|has|inhales|lets|lights|looks|opens|peers|pulses|rises|screams|sends|shrieks|shivers|shudders|sighs|simmers|singes|sings|slows|smiles|spews|spouts|staggers|stands|starts|steps|stops|strikes|summons|sweats|takes|turns|winces|writhes)\s.+.$",
                             "^([a-z|A-Z]{3,})\s(blinks|combusts|dies|fades|moans|pales|panics|rages|shrinks|staggers|stumbles|weakens|winces|yawns).$",
                             "^([a-z|A-Z]{3,})\sgoes into a berserker frenzy!",
                             "^([a-z|A-Z]{3,})\sis no longer berserk.",
                             "^([a-z|A-Z]{3,})\sis\s(adorned|bathed|blasted|blinded|bound|chilled|cloaked|coated|completely|consumed|covered|encased|engulfed|entombed|enveloped|immolated|lacerated|mauled|pelted|protected|resistant|sheathed|slammed|smashed|struck|stunned|surrounded)\s.+.$"
                            ]
                            
MOB_VERIFIED_REG_EX_LIST = ["^.+\s(backstabs|bashes|bites|crushes|hits|kicks|pierces|punches|slashes)\s([a-z|A-Z]{3,})\sfor\s[0-9]+\spoint[s]* of damage.$"
                  ]              

PET_VERIFIED_REG_EX_LIST = ["^(\S+)\ssays 'Sorry, Master..calming down.'$",
                            "^(\S+)\ssays 'At your service Master.'$",
                            "^(\S+)\ssays 'Guarding with my life..oh splendid one.'$",
                            "^(\S+)\ssays 'No longer taunting attackers, Master.'$"]
                            
GUILD_VERIFIED_REG_EX_LIST = ["([a-z|A-Z]{3,})\stells the guild,\s.+$"]                            

DKP_REG_EX_LIST = [".*(SEND BIDS|DKP|5-350|5 - 350|5-100|5 - 100).*"]

# Constants
GUILD_STATUS = 0
FIRST_HIT = 1
SECOND_HIT = 2
INACTIVITY = 3                  
                  
verified_hits = dict()
dkp_lines = list()
pet_list = list()
guild_list = list()

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

def update_verified_hits( char_name, date_object ):
    "This function updates the verified hits for the character"
    if char_name in verified_hits:
        # Check if hit is before first entry (happens if file has been pieced together out of order)
        if verified_hits[char_name][FIRST_HIT] > date_object:
            verified_hits[char_name][FIRST_HIT] = date_object
        # Check if hit is after second entry (in case file is out of order)
        elif verified_hits[char_name][SECOND_HIT] < date_object:    
            # Check elapsed time since last update
            elapsed = date_object - verified_hits [char_name][SECOND_HIT] 
            # If elapsed time greater than current elapsed time, update it
            if verified_hits[char_name][INACTIVITY] < elapsed.seconds:
                verified_hits[char_name][INACTIVITY] = elapsed.seconds
                            
            # Update last entry
            verified_hits[char_name][SECOND_HIT] = date_object
    else:
        # If name not in list, add timestamp to both first and last entries
        verified_hits[char_name] = ['Unknown', date_object, date_object, 0]
    return
    
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
 
            # Look for regular expression list in data
            for regex in CHAR_VERIFIED_REG_EX_LIST:
                m = re.search(regex, log_data)
                if m:
                    char_name = m.group(1)
                    update_verified_hits( char_name, date_object )
            
            for regex in MOB_VERIFIED_REG_EX_LIST:
                m = re.search(regex, log_data)
                if m:
                    char_name = m.group(2)
                    update_verified_hits( char_name, date_object )
                 
            for regex in PET_VERIFIED_REG_EX_LIST:
                m = re.search(regex, log_data)
                if m:
                    # If pet name not in list, add it
                    if m.group(1) not in pet_list:
                        pet_list.append(m.group(1))
                            
            for regex in GUILD_VERIFIED_REG_EX_LIST:
                m = re.search(regex, log_data)
                if m:
                    # If guild member name not in list, add it
                    if m.group(1) not in guild_list:
                        guild_list.append(m.group(1))
                            
            for regex in DKP_REG_EX_LIST:
                m = re.search(regex, log_data, re.IGNORECASE)
                if m:
                    # If DKP in line, add to DKP list
                    dkp_lines.append(line)
                
        elif date_object > raid_end_time:
            # Past raid end time, continue to next line (in case file is out of order)
            continue

# Remove pets from verified hits
for pet in pet_list:
    if pet in verified_hits:
        del verified_hits[pet]
        
for guild_member in guild_list:
    if guild_member in verified_hits:
        verified_hits[guild_member][GUILD_STATUS] = "Guild Member"
            
out_file = open("attendance.txt", "w")            
for k, v in sorted(verified_hits.items()):
    out_file.write(k + ", " + str(v[GUILD_STATUS]) + ", " + str(v[FIRST_HIT]) + ", " + str(v[SECOND_HIT]) + ", " + str(v[SECOND_HIT] - v[FIRST_HIT]) + ", " + str(v[INACTIVITY]/60) + "\n")

for line in dkp_lines:
    out_file.write(line)

if len(pet_list) > 0:
    out_file.write("The following 'pets' were removed - please verify:\n")
    for pet in pet_list:
        out_file.write(pet + "\n")
