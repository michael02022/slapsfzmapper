# VERSION 0.1

import re
import sys
import argparse
import sys
import os
from natsort import os_sorted
from searchbin import _search_loop, text_to_pattern
import ctypes

def only_nums(str):
    r = re.sub(r'[^\d]+', '', str)
    return r

def get_str(str, sep, offset):
    str_list = re.split(sep, str)
    return str_list[offset]

def normalize_note(str):
    note = ""
    middle = ""
    num = ""
    offset = 0
    for i in range(len(str)):
        try:
            if str[i] in NOTES:
                if note == "":
                    note = str[i]
                    offset = i
                    pass
                # verify is not a false flat the next trash characters
                elif str[i] in FLAT_ALIAS and i <= offset + 3:
                    # print(str[i])
                    if middle == "":
                        middle = "b"
                        pass

            if str[i] in SHARP_ALIAS:
                # print(str[i])
                if middle == "":
                    middle = "#"
                    pass

            if isinstance(int(str[i]), int):
                if num == "":
                    num = str[i]
                    pass
        except:
            pass
    return note.upper() + middle + num

def process_vel(str, lines):
    global formats
    if str.endswith(formats):
        vel_dyn = str.rsplit(".")[:-1][0]
    else:
        vel_dyn = str
    char = ""
    val = 0
    for line in lines:
        str_ls = re.split("=", line)
        char = str_ls[0]
        val = int(str_ls[1])
        # if vel_dyn.find(char) != -1:
        if vel_dyn in char and vel_dyn == char:
            return val

def inv_num(n):
    f = 0
    if n > 0:
        f = -abs(n)
    elif n < 0:
        f = abs(n)
    else:
        None

    return f

def get_midi_note(_note, center, current):
    global formats
    global byte_note
    global p_in

    if byte_note:
        smpl_data = SampleFile() 
        smpl_path = p_in + "\\" + current
        f = open(smpl_path, "rb")
        get_metadata(smpl_data, f)
        f.close
        return smpl_data.key
    
    if center is None:
        r = only_nums(_note)
        return r
    # removes any .* extension and convert the generated list into string
    if _note.endswith(formats):
        note = normalize_note(_note.rsplit(".")[:-1][0])
    else:
        note = normalize_note(_note)
    
    if isinstance(note, str):
        note_name = note

        key = note_name[:-1]  # eg C, Db
        octave = note_name[-1]   # eg 3, 4
        answer = -1

        octb = int(center[-1])
        try:
            if 'b' in key:
                pos = NOTES_FLAT.index(key)
            else:
                pos = NOTES_SHARP.index(key)
        except:
            print(f'The key is not valid: {_note} -> {note} -> {key}')
            sys.exit(0)
            return answer
        
        f_oct =  inv_num(octb - 5)

        answer += pos + 12 * (int(octave) + f_oct) + 1
        return answer

# non duplicated names
def get_names_list(ls, sep, offset, name_off_ls):
    names = []
    # print(ls)
    for i in range(len(ls)):
        name = reformat(ls[i], sep, offset, name_off_ls)[offset] # selects the composite name
        # str_list = re.split(sep, ls[i])
        # name = str_list[offset]
        # print(name)
        if name not in names:
            names.append(name)
        else:
            None #skip
    return names

def get_rr_list(ls, sep, rr_offset):
    names = []
    # print(ls)
    for i in range(len(ls)):
        name = get_str(ls[i], sep, rr_offset) # selects the composite name
        if name not in names:
            names.append(name)
        else:
            None #skip
    return names
        
def get_vel_list(lst, sep, offset):
    r = []
    for i in range(len(lst)):
        c = re.split(sep, lst[i])
        r.append(only_nums(c[offset]))
    return r

def get_group_by_name(ls, str, sep, offset, name_off_ls):
    final_ls = []
    for i in range(len(ls)):
        if str in reformat(ls[i], sep, offset, name_off_ls):
            final_ls.append(ls[i])
        else:
            None #skip
    return final_ls

def sort_list_by_root(ls, sep, offset, center):
    result = []
    str_result = []
    if offset == False and not isinstance(offset, int):
        return ls
    elif offset == None and center == None:
        for i in range(len(ls)):
            key = get_midi_note("", center, ls[i])
            #print(f"{ls[i]} {key}")
            str_result.append(ls[i])
            result.append([key, i])
    else:
        for i in range(len(ls)):
            str = re.split(sep, ls[i])
            name = str[offset]
            key = get_midi_note(name, center, ls[i])
            str_result.append(ls[i])
            result.append([key, i])

    #print(result)
    x = sorted(result, key=lambda seq: (int(seq[0]), int(seq[1])))
    # print(x)
    y = []
    for j in range(len(x)):
        z = x[j]
        y.append(str_result[int(z[1])])
    #print(y)

    return y

def reformat(str, sep, offset, name_off_ls):
    # print(str)
    # print(str_ls)
    '''
    if len(name_off_ls) == 1:
        new_str = []
        new_str.append(get_str(str, sep, offset))
        new_str.append(0) # the [offset] thing from get_names_list() will be 0, so here we make sure we select the entire name and not the first char
        #print(new_str)
    else:
    '''
    full_name = ""
    # print(re.split(sep, str_ls[i]))
    # get full name
    for j in range(len(name_off_ls)):
        full_name += get_str(str, sep, name_off_ls[j])
        if j == (len(name_off_ls) - 1):
            break
        full_name += "_"
        # print(full_name)
    new_str = re.split(sep, str)
    new_str[offset] = full_name
    # print(new_str)
    full_name = ""
    # replace first element with the new full name
    # for j in range(len(current)):
    #     print(current[j])
    return new_str

def gen_vel_curve(vel_ls, growth, min_amp):
    if min_amp != None:
        try:
            min = int(min_amp)
            if min > 127:
                min_amp = 127
            else:
                min_amp = min
        except:
            min_amp = 1
    else:
        min_amp = 1
    
    max_amp = 127
    # growth = 1.001
    if growth != None:
        match growth:
            case "c-5":
                growth = 1.05
            case "c-4":
                growth = 1.04
            case "c-3":
                growth = 1.03
            case "c-2":
                growth = 1.02
            case "c-1":
                growth = 1.01
            case "c":
                growth = 1.0000001 # linear
            case "c+1":
                growth = 0.99
            case "c+2":
                growth = 0.98
            case "c+3":
                growth = 0.97
            case "c+4":
                growth = 0.96
            case "c+5":
                growth = 0.95
            case _:
                if isinstance(growth, (int, float)):
                    pass
                else:
                    growth = 1.0000001
    else:
        growth = 1.0000001
    
    periods = len(vel_ls)
    #print(vel_ls)
    ls = []
    rint = []
    #print(periods)
    # generate value list

    for i in range(periods + 1):
        #print(i)
        result = min_amp+(((min_amp*growth**i)-min_amp)*(max_amp-min_amp)/((min_amp*growth**periods)-min_amp))
        #bruh = vel_ls[i]
        rint.append(int(result))
        if i == (periods):
            #print("XD")
            rint.append(127)
            rint.pop(0)

    for i in range(periods):
        ls.append([rint[i], vel_ls[i]])
    return ls
    
    '''
    for i in range(periods):
        result = min_amp+(((min_amp*growth**i)-min_amp)*(max_amp-min_amp)/((min_amp*growth**periods)-min_amp))
        ls.append([int(result), vel_ls[i]])
    return ls
    '''

def process_veldyn(str, _vel_set):
    for i in range(len(_vel_set)):
        if _vel_set[i][1] == str:
            return _vel_set[i][0] # return the vel number equivalent of the string

class SampleFile:
    def __init__(self):
        self.format = None
        self.start_lp = None
        self.end_lp = None
        self.key = None
        self.tune = None
        self.lp_mode = ["forward", "no_loop"]
    
    def _format(self, str):
        self.format = str
    
    def _start_lp(self, num):
        self.start_lp = num
    
    def _end_lp(self, num):
        self.end_lp = num
    
    def _key(self, num):
        if num == 0:
            pass
        else:
            self.key = num

    def _tune(self, num):
        global fix_tune
        if num == 0:
            pass
        else:
            if fix_tune:
                self.tune = inv_num(num)
            else:
                self.tune = num

    def _lp_mode(self, num):
        if self.format == "WAV":
            match num:
                case 0:
                    self.lp_mode = ["forward", "loop_continuous"]
                case 1:
                    self.lp_mode = ["alternate", "loop_continuous"]
                case 2:
                    self.lp_mode = ["backward", "loop_continuous"]
        elif self.format == "AIFF":
            match num:
                case 0:
                    self.lp_mode = ["forward", "no_loop"]
                case 1:
                    self.lp_mode = ["forward", "loop_continuous"]
                case 2:
                    self.lp_mode = ["alternate", "loop_continuous"]
    
    def get_opcodes(self):
        ls = [["tune=", self.tune], ["loop_start=", self.start_lp], ["loop_end=", self.end_lp], ["loop_mode=", self.lp_mode[1]], ["loop_type=", self.lp_mode[0]]]
        f = []
        str = ""
        for i in range(len(ls)):
            if ls[i][1] != None:
                f.append(ls[i])
        for opcode in f:
            str += f"{opcode[0]}{opcode[1]} "
        return str
    
    def stats(self):
        print(f"Format: {self.format}\nStart Loop: {self.start_lp}\nEnd Loop: {self.end_lp}\nKey: {self.key}\nTune: {self.tune}\nLoop Mode: {self.lp_mode}")

def wavbytes_to_tune(bytes):
    return round(ctypes.c_long(int.from_bytes(bytes)).value / 0x80000000 * 50.0)

def get_metadata(sample, f):
    global endlp
    ID_SZ = 4
    CHUNK_SZ = 4
    MARKER_ID = 2
    MARKER_POS = 4

    f.seek(0)

    f_id = f.read(4).decode()

    for i in range(len(file_ids)):
        f_id = _search_loop(0, None, 1024, text_to_pattern(file_ids[i]), 1, None, False, f.name, f.read, f.seek)
        f.seek(0)
        if f_id != None:
            f_id = file_ids[i]
            #print(f_id)
            break

    match f_id:
        case "FORM":
            sample._format("AIFF")

            f.seek(0)
            MARK_offset = _search_loop(0, None, 1024, text_to_pattern(chunk_ids[1]), 1, None, False, f.name, f.read, f.seek)

            if MARK_offset == None:
                return

            # read MARK
            f.seek(MARK_offset + ID_SZ) # skip MARK
            chunk_size = int.from_bytes(f.read(CHUNK_SZ), "big")
            mark_chunk = f.read(chunk_size) # get the chunk
            num_markers = int.from_bytes(mark_chunk[:2], "big")

            if num_markers != 0:
                off = 2 # skip num_markers
                for i in range(num_markers):
                    off+=MARKER_ID
                    sample_pos = int.from_bytes(mark_chunk[off : off+MARKER_POS]);off+=MARKER_POS
                    str_size = int.from_bytes(mark_chunk[off : off+1]);off+=1
                    mrk_name = mark_chunk[off : off+str_size].decode();off+=str_size
                    match mrk_name:
                        case "beg loop":
                            sample._start_lp(sample_pos)
                        case "LpBeg ":
                            sample._start_lp(sample_pos)
                        case "end loop":
                            sample._end_lp(sample_pos - endlp)
                        case "LpEnd ":
                            sample._end_lp(sample_pos - endlp)
                    off += 1 # 0x00 byte at the end of every mark
                
                # read INST
                f.seek(0)
                INST_offset = _search_loop(0, None, 1024, text_to_pattern(chunk_ids[2]), 1, None, False, f.name, f.read, f.seek)
                f.seek(0)
                f.seek(INST_offset + ID_SZ) # skip MARK
                chunk_size = int.from_bytes(f.read(CHUNK_SZ), "big")
                inst_chunk = f.read(chunk_size) # get the chunk
                sample._key(int.from_bytes(inst_chunk[0:1], "big")) # midi note
                sample._tune(ctypes.c_byte(int.from_bytes(inst_chunk[1:2])).value) # signed byte
                sample._lp_mode(int.from_bytes(inst_chunk[8:10])) # skips the rest of byte data to go straight to the loop mode
                #sample.stats()
            else:
                None
        case "WAVE":
                sample._format("WAV")

                f.seek(0)
                smpl_offset = _search_loop(0, None, 1024, text_to_pattern(chunk_ids[0]), 1, None, False, f.name, f.read, f.seek)
                if smpl_offset == None:
                    return

                # read smpl
                f.seek(smpl_offset + ID_SZ) # skip smpl
                chunk_size = int.from_bytes(f.read(CHUNK_SZ), "little")
                smpl_chunk = f.read(chunk_size) # get the chunk

                sample._key(int.from_bytes(smpl_chunk[12:16], "little"))
                sample._tune(wavbytes_to_tune(smpl_chunk[16:20]))
                num_loops = int.from_bytes(smpl_chunk[28:32], "little") # number of loop CHUNKS
                if num_loops > 0:
                    # int.from_bytes(smpl_chunk[36:40], "little") # ID
                    sample._lp_mode(int.from_bytes(smpl_chunk[40:44], "little")) # loop mode
                    sample._start_lp(int.from_bytes(smpl_chunk[44:48], "little")) # start loop
                    sample._end_lp(int.from_bytes(smpl_chunk[48:52], "little") - endlp) # end loop
                    #sample.stats()
                    # int.from_bytes(smpl_chunk[52:56], "little") # tune loop, unusual for most samplers/editors (if not all)

def process_regions(__group, key_mode, key_offset, center, vel_mode, vel_offset, vel_curve, vel_crv_min, rr):
    None
    global vel_lines
    global rr_len
    global rr_idx
    global sfz_header
    global rr_step
    global p_in
    global metadata
    global byte_note
    global ign_root
    global key_verbose
    config = []
    _group = []
    group = []
    keycenters = []
    vel_opcodes = []
    result = ""
    #if str(sfz_header) == "" and rr_idx == 0 and rr != False:
    #    result += f"<global>\n"

    #if rr_len > 1 and rr_idx == 0:
    #    result += f"seq_length={rr_len}\n"
    
    if rr_len > 1:
        rr_step += 1
        result += f"<group> seq_length={rr_len} seq_position={rr_step}\n"
    else:
        result += f"<group>\n"

    vel_list = []

    # if there is velocity
    if vel_mode[1] != None or vel_offset != None:
        if vel_mode[1] == "velraw":
            # sort the group again based on velocity and then root note
            for idx in range(len(__group)):
                vel_list.append([only_nums(get_str(__group[idx], sep, vel_offset)), idx]) # [vel value, index]
            
            vel_list_b = sorted(vel_list, key=lambda seq: (int(seq[0]), int(seq[1]))) # from minor to major, first velocity and then key

            for idx in range(len(__group)): # shuffle the original group with the new order
                current_vel = vel_list_b[idx]
                _group.append(__group[current_vel[1]])
            
            vel_list = sorted(get_vel_list(_group, sep, vel_offset), reverse=True) # list all velocities from the group
            vel_set = sorted(list(set(get_vel_list(_group, sep, vel_offset))), reverse=True) # documents all kinds of velocities of the group, reverse because in that way the order is minor to major
        
        elif vel_mode[1] == "veldict":
            _vel_list = []
            for idx in range(len(__group)):
                _vel_list.append([get_str(__group[idx], sep, vel_offset), idx])
            
            #print(_vel_list)
            
            # vel_lines = vel_dict.readlines()
            for k in range(len(_vel_list)):
                vel_list.append([process_vel(_vel_list[k][0], vel_lines), _vel_list[k][1]])
            
            #print(vel_list)
            
            vel_list_b = sorted(vel_list, key=lambda seq: (int(seq[0]), int(seq[1])))

            # print(vel_list_b)
            vel_list_c = []

            for idx in range(len(__group)): # shuffle the original group with the new order
                current_vel = vel_list_b[idx]
                vel_list_c.append(current_vel[0])
                _group.append(__group[current_vel[1]])
            
            vel_list = sorted(vel_list_c) # list all velocities from the group
            vel_set = sorted(list(set(vel_list))) # documents all kinds of velocities of the group, reverse because in that way the order is minor to major

        elif vel_mode[1] == "veldyn":
            _vel_list = []
            for idx in range(len(__group)):
                _vel_list.append([get_str(__group[idx], sep, vel_offset), idx])
            
            _vel_list_b = sorted(_vel_list, key=lambda seq: (str(seq[0]), int(seq[1])))

            ## convert the vel indexes into midi vel
            cra = []
            # list the set of velocities
            for idx in range(len(_vel_list_b)):
                cra.append(_vel_list_b[idx][0])
            
            crb = list(set(cra))

            # generate the midi value with the str value -> [[str, midi_vel_equivalent], ...]
            _vel_set = gen_vel_curve(os_sorted(crb), vel_curve, vel_crv_min)
            
            for idx in range(len(_vel_set)):
                for idxb in range(len(_vel_list_b)):
                    # check if the string match and replace the value
                    if _vel_set[idx][1] == _vel_list_b[idxb][0]:
                        _vel_list_b[idxb][0] = _vel_set[idx][0]
            
            _vel_list = []
            #print(_vel_set)
            # now we can use it as a velraw
            for idx in range(len(__group)):
                _vel_list.append(_vel_list_b[idx]) # [vel value, index]
                vel_list.append(_vel_list_b[idx][0]) # list the vel_set already

            #print(vel_list)
            #print("bruhxd", len(_vel_list))
            vel_list_b = sorted(_vel_list, key=lambda seq: (int(seq[0]), int(seq[1]))) # from minor to major, first velocity and then key

            #print(vel_list_b)

            #print(len(__group))
            #print("bruh", len(vel_list_b))
            for idx in range(len(__group)): # shuffle the original group with the new order
                #print(vel_list_b[idx])
                current_vel = vel_list_b[idx]
                _group.append(__group[current_vel[1]])
            #print(_group)
            
            vel_set = list(set(vel_list))
            vel_set.sort()

            #print(_vel_list)
            #print(vel_list)
            #print(vel_set)

            #sys.exit(0)
            None
    else:
        # if theres no velocity then all samples are 0-127
        vel_list = [127] * len(__group)
        vel_set = [127]
    
    # process each key range and velocity range mapping to group them into one file
    for idx_a in range(len(vel_set)): 
        group = [] # reset group each time a group is done
        
        # if there is velocity -> split them
        if vel_mode[1] != None or vel_offset != None:
            if vel_mode[1] == "velraw":
                for idx_b in range(len(_group)): # ordena los indexes con los velocities
                    if vel_set[idx_a] == only_nums(get_str(_group[idx_b], sep, vel_offset)):
                        group.append(_group[idx_b])
            elif vel_mode[1] == "veldict":
                for idx_b in range(len(_group)): # ordena los indexes con los velocities
                    if vel_set[idx_a] == process_vel(get_str(_group[idx_b], sep, vel_offset), vel_lines):
                        group.append(_group[idx_b])
            elif vel_mode[1] == "veldyn":
                # TODO FIX _group
                for idx_b in range(len(_group)): # ordena los indexes con los velocities
                    #print(get_str(_group[idx_b], sep, vel_offset))
                    if vel_set[idx_a] == process_veldyn(get_str(_group[idx_b], sep, vel_offset), _vel_set):
                        group.append(_group[idx_b])
                #print("-----")
        # otherwise the whole group is the same thing
        else:
            group = __group

        keycenters = []
        # get the list of root notes
        for i in range(len(group)):
            current = group[i]
            # print(get_str(current, sep, key_offset))
            #print(current)
            if byte_note:
                keycenters.append(get_midi_note("", center, current))
            elif ign_root:
                keycenters.append(60)
            else:
                keycenters.append(get_midi_note(get_str(current, sep, key_offset), center, current))
        
        # print(keycenters)
        
        # get the set of root notes
        key_set = sorted(list(set(keycenters)))

        # process the velocity opcodes
        vel_opcodes = []

        if len(vel_set) > 1:
            match vel_mode[0]:
                case "lo":
                    for grp_idx in range(len(group)):
                        if idx_a == 0:
                            vel_opcodes.append(f"lovel=0 hivel={int(vel_set[idx_a + 1]) - 1}")
                        elif idx_a == (len(vel_set) - 1):
                            vel_opcodes.append(f"lovel={vel_set[idx_a]} hivel=127")
                        else:
                            vel_opcodes.append(f"lovel={vel_set[idx_a]} hivel={int(vel_set[idx_a + 1]) - 1}")
                case "hi":
                    for grp_idx in range(len(group)):
                        if idx_a == 0:
                            vel_opcodes.append(f"lovel=0 hivel={vel_set[idx_a]}")
                        elif idx_a == (len(vel_set) - 1):
                            vel_opcodes.append(f"lovel={int(vel_set[idx_a - 1]) + 1} hivel=127")
                        else:
                            vel_opcodes.append(f"lovel={int(vel_set[idx_a - 1]) + 1} hivel={vel_set[idx_a]}")
                case "none":
                    for grp_idx in range(len(group)):
                        vel_opcodes.append(f"lovel={vel_list[grp_idx]} hivel={vel_list[grp_idx]}")
        else:
            for j in range(len(group)):
                vel_opcodes.append("")
        
        # get metadata to be printed   
        # process regions
        pan_opcode = ""
        step = 0
        match key_mode:
            case "lo":               
                for grp_idx in range(len(group)):
                    if metadata:
                        # METADATA ===============
                        smpl_data = SampleFile() 
                        smpl_path = p_in + "\\" + group[grp_idx]
                        f = open(smpl_path, "rb")
                        get_metadata(smpl_data, f)
                        f.close
                        misc_opcodes = smpl_data.get_opcodes()
                        #smpl_data.stats()
                    else:
                        misc_opcodes = ""
                    # MONO L/R
                    str_lr = os.path.splitext(group[grp_idx])[0]
                    match str_lr[-2:]:
                        case "-L":
                            pan_opcode = "pan=-100"
                        case "-R":
                            pan_opcode = "pan=100"
                    #print(key_set)
                    #print(group[grp_idx])
                    # print(step)
                    # write only 1 sample
                    if len(keycenters) == 1 and len(key_set) == 1:
                        result += f"<region> sample={group[grp_idx]} pitch_keycenter={keycenters[grp_idx]} lokey=0 hikey=127 {vel_opcodes[grp_idx]} {misc_opcodes}\n"
                    else:
                        if key_set[step] != keycenters[grp_idx]:
                            step += 1
                        if step == 0:
                            result += f"<region> sample={group[grp_idx]} pitch_keycenter={keycenters[grp_idx]} lokey=0 hikey={int(key_set[step + 1]) - 1} {vel_opcodes[grp_idx]} {misc_opcodes} {pan_opcode}\n"
                        elif step == (len(key_set) - 1):
                            result += f"<region> sample={group[grp_idx]} pitch_keycenter={keycenters[grp_idx]} lokey={key_set[step]} hikey=127 {vel_opcodes[grp_idx]} {misc_opcodes} {pan_opcode}\n"
                        else:
                            result += f"<region> sample={group[grp_idx]} pitch_keycenter={keycenters[grp_idx]} lokey={key_set[step]} hikey={int(key_set[step + 1]) - 1} {vel_opcodes[grp_idx]} {misc_opcodes} {pan_opcode}\n"
            case "hi":
                for grp_idx in range(len(group)):
                    if metadata:
                        # METADATA ===============
                        smpl_data = SampleFile() 
                        smpl_path = p_in + "\\" + group[grp_idx]
                        f = open(smpl_path, "rb")
                        get_metadata(smpl_data, f)
                        f.close
                        misc_opcodes = smpl_data.get_opcodes()
                        #smpl_data.stats()
                    else:
                        misc_opcodes = ""
                    # MONO L/R
                    str_lr = os.path.splitext(group[grp_idx])[0]
                    match str_lr[-2:]:
                        case "-L":
                            pan_opcode = "pan=-100"
                        case "-R":
                            pan_opcode = "pan=100"
                    
                    if len(keycenters) == 1 and len(key_set) == 1:
                        result += f"<region> sample={group[grp_idx]} pitch_keycenter={keycenters[grp_idx]} lokey=0 hikey=127 {vel_opcodes[grp_idx]} {misc_opcodes}\n"
                    else:
                        if key_set[step] != keycenters[grp_idx]:
                            step += 1
                        if step == 0:
                            result += f"<region> sample={group[grp_idx]} pitch_keycenter={keycenters[grp_idx]} lokey=0 hikey={key_set[step]} {vel_opcodes[grp_idx]} {misc_opcodes} {pan_opcode}\n"
                        elif step == (len(key_set) - 1):
                            result += f"<region> sample={group[grp_idx]} pitch_keycenter={keycenters[grp_idx]} lokey={int(key_set[step - 1]) + 1} hikey=127 {vel_opcodes[grp_idx]} {misc_opcodes} {pan_opcode}\n"
                        else:
                            result += f"<region> sample={group[grp_idx]} pitch_keycenter={keycenters[grp_idx]} lokey={int(key_set[step - 1]) + 1} hikey={key_set[step]} {vel_opcodes[grp_idx]} {misc_opcodes} {pan_opcode}\n"
            case "none":
                for grp_idx in range(len(group)):
                    if metadata:
                        # METADATA ===============
                        smpl_data = SampleFile() 
                        smpl_path = p_in + "\\" + group[grp_idx]
                        f = open(smpl_path, "rb")
                        get_metadata(smpl_data, f)
                        f.close
                        misc_opcodes = smpl_data.get_opcodes()
                        #smpl_data.stats()
                    else:
                        misc_opcodes = ""
                    # MONO L/R
                    str_lr = os.path.splitext(group[grp_idx])[0]
                    match str_lr[-2:]:
                        case "-L":
                            pan_opcode = "pan=-100"
                        case "-R":
                            pan_opcode = "pan=100"

                    if len(keycenters) == 1 and len(key_set) == 1:
                        if key_verbose:
                            result += f"<region> sample={group[grp_idx]} pitch_keycenter={keycenters[grp_idx]} lokey={keycenters[grp_idx]} hikey={keycenters[grp_idx]} {vel_opcodes[grp_idx]} {misc_opcodes}\n"
                        else:
                            result += f"<region> sample={group[grp_idx]} key={keycenters[grp_idx]} {vel_opcodes[grp_idx]} {misc_opcodes}\n"
                    else:
                        if step == (len(key_set) - 1):
                            if key_verbose:
                                result += f"<region> sample={group[grp_idx]} pitch_keycenter={keycenters[grp_idx]} lokey={keycenters[grp_idx]} hikey={keycenters[grp_idx]} {vel_opcodes[grp_idx]} {misc_opcodes} {pan_opcode}\n"
                            else:
                                result += f"<region> sample={group[grp_idx]} key={keycenters[grp_idx]} {vel_opcodes[grp_idx]} {misc_opcodes}\n"
                        else:
                            if key_verbose:
                                result += f"<region> sample={group[grp_idx]} pitch_keycenter={keycenters[grp_idx]} lokey={keycenters[grp_idx]} hikey={keycenters[grp_idx]} {vel_opcodes[grp_idx]} {misc_opcodes} {pan_opcode}\n"
                            else:
                                result += f"<region> sample={group[grp_idx]} key={keycenters[grp_idx]} {vel_opcodes[grp_idx]} {misc_opcodes}\n"
        if key_mode != "none":
            result += "\n"
    return result

def generate_path(dots, ls):
    r = ""
    for i in range(dots):
        r += f"..\\"
    for j in range(len(ls)):
        r += f"{ls[j]}\\"
    return r

def write_sfz(header, sfzgroup, filename, outpath):
    global p_in
    global num_name
    global list_names
    path_none = False
    sfz_content = ""
    
    if outpath != None:
        if len(outpath.split(os.sep)) == 1:
            if outpath.endswith('.sfz'):
                filename = os.path.splitext(outpath)[0]
                outpath = os.path.normpath(p_in + os.sep + os.pardir) # a folder back
                _outpath = outpath
            elif outpath == "*":
                path_none = True
                outpath = os.path.normpath(p_in) # same folder as samples
                _outpath = outpath
        else:
            if outpath.endswith('.sfz'):
                filename = os.path.splitext(outpath)[0]
                _outpath = outpath
                outpath = os.path.dirname(_outpath) # get the path without the filename
            else:
                _outpath = outpath # use the path as it is
    else:
        path_none = True
        outpath = os.path.normpath(p_in + os.sep + os.pardir) # a folder back
        _outpath = outpath
        #print(outpath)
        #sys.exit(0)
        # os.path.split(p_in)[-1]

    if outpath != os.path.normpath(p_in):
        common_path = os.path.commonprefix([p_in, outpath]) # gets the common path from root
        inpath_list = p_in.split(os.sep) # convert path into list
        dots = len(outpath.split(os.sep)) - (len(common_path.split(os.sep)) - 1) # -1 because the list generates an empty string at the end
        m = (len(common_path.split(os.sep)) - 1) - len(p_in.split(os.sep)) # get the negative value to extract the path of samples from inpath_list
        sfz_outpath = generate_path(dots, inpath_list[m:])

        sfz_content += f"<control>\ndefault_path={sfz_outpath}\n" # get the last folder of the current path
    else:
        sfz_content += f"<control>\n"

    # insert header if user specified
    if header != "":
        sfz_content += "\n" + header
    
    sfz_content += "\n" + sfzgroup

    # writing sfz file
    if filename is None:
        #print(filename)
        #print(outpath)
        _filename = os.path.basename(_outpath)
        #print(_filename)
        if _filename.endswith('.sfz'):
            #print("PASA IF")
            filename = os.path.splitext(_filename)[0] # get the sfz name given by the user
        else:
            #print("PASA ELSE")
            tmp = p_in.split(os.sep)[-1:]
            filename = os.path.splitext(tmp[0])[0] # use the name folder for the sfz file
            #filename = str(num_name)
            #num_name += 1
    else:
        if _outpath.endswith('.sfz'):
            try:
                filename = os.path.splitext(_filename)[0] # get the sfz name given by the user (no path)
            except: # _filename does not exist
                tmp = _outpath.split(os.sep)[-1:]
                filename = os.path.splitext(tmp[0])[0] # get filename from path + sfz name
                #print(filename)
        try:
            if len(list_names) != 1 and path_none == False:
                #print(_outpath)
                filename = filename + "-" + str(num_name)
                num_name += 1
            else:
                pass
        except:
            pass
    
    # write sfz file
    f_sfz = open(os.path.normpath(outpath + "\\" + str(filename) + ".sfz"), "w", encoding="utf8")
    f_sfz.write(sfz_content)
    f_sfz.close()
    print(f"""{os.path.normpath(str(filename) + ".sfz")} written.""")


if __name__ == "__main__":
    # TODO agregar los argumentos config (insertar el path en el opcode sample | normalizar cada sample con veltrack )
    NOTES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    NOTES_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    NOTES = ("C", "D", "E", "F", "G", "A", "B", "c", "d", "e", "f", "g", "a", "b")
    SHARP_ALIAS = ('#', 'S', 's')
    FLAT_ALIAS = ('B', 'b', 'F', 'f')

    chunk_ids = ("smpl", "MARK", "INST")
    file_ids = ("WAVE", "FORM")
    formats = ('.wav', '.aiff', '.aif', '.aifc', '.flac', '.ogg')
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--folderin", help="folder input")
    parser.add_argument("-o", "--folderout", help="folder output+name.sfz")
    parser.add_argument("-sep", "--separator", help="separator char")
    parser.add_argument("-spr", "--spread", help="spread mode for velocity and key")
    parser.add_argument("-ls", "--list", help="list of arguments to parser the splitted strings")
    parser.add_argument("-tmpl", "--template", help="insert a sfz template")
    parser.add_argument("-dict", "--dictionary", help="select a dictionary for vel")
    parser.add_argument("-crv", "--curve", help="specify the curve value for veldyn")
    parser.add_argument("-opt", "--options", help="options for the sfz")

    args = parser.parse_args()

    print("folderin:", args.folderin)
    print("folderout:", args.folderout)
    print("separator:", args.separator)
    print("spread:", args.spread)
    print("list:", args.list)
    print("template:", args.template)
    print("dictionaries:", args.dictionary)
    print("velocity curve:", args.curve)
    print("options:", args.options)
    print("=======================")

    # init
    sep = args.separator
    keyspr = None
    velspr = None
    ign = []
    name = None
    name_off_ls = []
    root = None
    c = None 
    rr = [False]
    rr_len = 0
    veltype = [None, None]
    keytype = [None, None]
    template = None
    vel_dict = None
    vel_dict_txt = "veldict_a.txt"
    metadata = False
    byte_root = False
    endlp = 0
    byte_note = False
    fix_tune = False
    ign_root = False
    key_verbose = False
    
    file_list = []

    if args.folderin is None:
        # get the current working path
        p_in = os.path.normpath(os.getcwd())
    else:
        p_in = os.path.normpath(args.folderin)

    if args.folderout is None:
        # the folder out will be a folder back where the samples are
        p_out = None
    else:
        p_out = os.path.normpath(args.folderout)
    
    # load the SFZ header template
    pypath = os.path.dirname(__file__)
    if args.template is not None:
        template = os.path.normpath(str(pypath) + "\\templates\\" + args.template)
        try:
            _sfz_header = open(template, "r", encoding="utf8")
        except:
            print(f"ERROR: TEMPLATE '{args.template}' NOT FOUND")
            sys.exit(0)
        sfz_header = _sfz_header.read()
    else:
        sfz_header = ""

    if args.dictionary != None:
        vel_dict_txt = args.dictionary + ".txt"

    if args.list is None:
        print(f"ERROR: NO SEPARATOR SPECIFIED")
        sys.exit(0)
    
    parse_data = re.split(" ", args.list)

    if len(parse_data) == 0:
        print(f"ERROR: YOU MUST SPECIFY A LIST OF ARGUMENTS")
        sys.exit(0)
    
    # list all possible audio files for sfz
    for file in os.listdir(p_in):
        if file.endswith(formats):
            # check the parse data is correct
            check_name = re.split(sep, file)
            if (len(parse_data)) != len(check_name):
                #print(f"SKIPPING {file}")
                #print(f"ERROR: ARGUMENTS HAS NO EQUAL SIZE AS STRINGS TO PARSE.\nstrings: {check_name} -> {len(check_name)}\nargs: {parse_data} -> {len(parse_data)}")
                pass
            else:
                file_list.append(file)
    
    if len(file_list) == 0:
        print(f"ERROR: NO AUDIO SAMPLES FOUND IN '{p_in}'")
        sys.exit(0)

    # check spread arguments
    if args.spread is not None:
        spr = re.split(" ", args.spread)
    else:
        spr = []
    
    # parses spread args
    match len(spr):
        case 0:
            # for vel curve, it should be "lo"
            keyspr = "lo"
            velspr = "hi"
        case 1:
            keyspr = spr[0]
            velspr = "hi"
        case 2:
            keyspr = spr[0]
            velspr = spr[1]
        case _:
            print(f"ERROR: SPREAD ARGUMENTS MORE THAN TWO")
            sys.exit(0)
    
    # collects the argument list variables
    for i in range(len(parse_data)):
        match parse_data[i]:
            case "ign":
                # list which offsets will be ignored
                ign.append(i)
            case "name":
                if name == None:
                    name = [True, i] # state and offset
                    name_off_ls.append(i)
                else:
                    name_off_ls.append(i)
            case "velraw":
                veltype = ["velraw", i]
            case "veldict":
                veltype = ["veldict", i]
                vel_dict = open(os.path.normpath(str(pypath) + "\\dict\\" + vel_dict_txt), "r", encoding="utf8")
            case "veldyn":
                veltype = ["veldyn", i]
                #velspr = "lo"
            case "keyraw":
                keytype = ["keyraw", i]
            case "root":
                root = [None, i]
            case _:
                # non static arguments
                # note name
                _str = parse_data[i]
                if root == None:
                    if "c" in _str[0] or "C" in _str[0]:
                        root = [parse_data[i], i]
                    else:
                        print(f"ERROR: NO CENTER KEY SPECIFIED CORRECTLY -> {parse_data[i]}")
                        sys.exit(0)
                
                # round robin
                if _str == "rr":
                    if rr[0] == False:
                        rr = [True, i]
                        name_off_ls.append(rr[1])
    # curve options
    try:
        crv_ls = re.split(" ", args.curve)
        try:
            minamp = crv_ls[1]
        except:
            minamp = None
    except:
        crv_ls = [None, None]
        minamp = None
    
    # sfz options
    try:
        options_data = re.split(" ", args.options)
        if len(options_data) != 0:
            for i in range(len(options_data)):
                match options_data[i]:
                    case "metadata":
                        metadata = True
                    case "fix-endloop":
                        endlp = 1
                    case "byte-root":
                        byte_note = True
                        root = [None, None]
                    case "fix-tune":
                        fix_tune = True
                    case "ignore-root":
                        ign_root = True
                        root = [None, False]
                    case "key-verbose":
                        key_verbose = True
    except:
        pass
    
    veltype.append(crv_ls[0])
    veltype.append(minamp)

    # generating sfz, if there's name, the folder has multiple instruments, otherwise, the folder is for one instrument
    if veltype[0] == "veldict":
        vel_lines = vel_dict.readlines()
    num_name = 0
    group_sfz = ""
    rr_step = 0
    if name is not None:
        # reformat(file_list, sep, name[1], [0, 1, 3])
        # list_names = get_names_list(file_list, sep, name[1], name_off_ls) [:-1]
        if rr[0]:
            _name_off_ls = name_off_ls[:-1] # remove the rr offset for name
        else:
            _name_off_ls = name_off_ls
        list_names = get_names_list(file_list, sep, name[1], _name_off_ls)
        # print(list_names)
        # print(rr_len)
        # print(len(list_names))
        for name_idx in range(len(list_names)):
            current_grp = get_group_by_name(file_list, list_names[name_idx], sep, name[1], _name_off_ls)
            if rr[0]:
                rr_list = get_rr_list(current_grp, sep, rr[1])
                rr_len = len(rr_list)
                for rr_idx in range(rr_len):
                    rr_group = get_group_by_name(current_grp, rr_list[rr_idx], sep, rr[1], [rr[1]])
                    sorted_grp = sort_list_by_root(rr_group, sep, root[1], root[0])
                    # process region
                    _group_sfz = process_regions(sorted_grp, keyspr, root[1], root[0], [velspr, veltype[0]], veltype[1], veltype[2], veltype[3], rr)
                    group_sfz += _group_sfz
                sfz_name = reformat(current_grp[0], sep, name[1], _name_off_ls)[name[1]]
                rr_step = 0
                write_sfz(str(sfz_header), group_sfz, sfz_name, p_out)
                group_sfz = ""
            else:
                rr_idx = 0
                sorted_grp = sort_list_by_root(current_grp, sep, root[1], root[0])
                sfz_name = reformat(current_grp[0], sep, name[1], _name_off_ls)[name[1]]
                # process region
                _group_sfz = process_regions(sorted_grp, keyspr, root[1], root[0], [velspr, veltype[0]], veltype[1], veltype[2], veltype[3], rr)
                group_sfz = _group_sfz
                write_sfz(str(sfz_header), group_sfz, sfz_name, p_out)
    else:
        if rr[0]:
            _name_off_ls = name_off_ls[:-1]
        else:
            _name_off_ls = name_off_ls
        if rr[0]:
            rr_list = get_rr_list(file_list, sep, rr[1])
            rr_len = len(rr_list)

            for rr_idx in range(len(rr_list)):
                current_grp = get_group_by_name(file_list, rr_list[rr_idx], sep, rr[1], _name_off_ls)
                #print(current_grp)
                sorted_grp = sort_list_by_root(current_grp, sep, root[1], root[0]) # the entire folder is one instrument
                #print(sorted_grp)
                sfz_name = None
                # process region
                #print(len(sorted_grp))
                _group_sfz = process_regions(sorted_grp, keyspr, root[1], root[0], [velspr, veltype[0]], veltype[1], veltype[2], veltype[3], rr)
                group_sfz += _group_sfz
        else:
            rr_idx = 0
            sorted_grp = sort_list_by_root(file_list, sep, root[1], root[0]) # the entire folder is one instrument
            sfz_name = None
            # process region
            group_sfz = process_regions(sorted_grp, keyspr, root[1], root[0], [velspr, veltype[0]], veltype[1], veltype[2], veltype[3], rr)
        write_sfz(str(sfz_header), group_sfz, sfz_name, p_out)
