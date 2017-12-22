import re
import datetime
import configparser
import redis
import pickle
from pony.orm import *

config = configparser.ConfigParser()
config.read('C://Users//Zerbs//accounts.sec')
redis_key_delimiter = "_"
prefix = "sql"
time_prefix = "timesql"

redis_connection = redis.StrictRedis(host=config['redis']['host'], port=int(config['redis']['port']), db=0)

def get_date(string_date):
    if (isinstance(string_date,datetime.datetime)):
        return string_date
    return datetime.datetime.strptime(string_date, '%d.%m.%Y')

def get_date_time(string_date):
    if (isinstance(string_date,datetime.datetime)):
        return string_date
    return datetime.datetime.strptime(string_date, '%d.%m.%Y %H:%M')

def get_bytes(path):
    if path == None:
        return None
    in_file = open(path, "rb")
    data = in_file.read()
    in_file.close()
    return data

def write_time_to_redis(key):
    str_key = str(key)
    if (str_key[:2] == "b'"):
        str_key = str_key[2:-1]
    print(str_key)
    redis_connection.set(time_prefix + redis_key_delimiter + str_key, pickle.dumps(datetime.datetime.now()))

def get(value):
    return value

def get_str(value):
    return "'"+str(value)+"'"

def get_list(value):
    return value.replace(" ","").split(",")

def get_float(value):
    if value == None:
        return None
    return float(value)

def get_worker_date_state_list(value):
    #value = '12.12.2017,e88 ; 12.11.2017, e89 '
    #print(">>>>" + value)
    result = []
    pre_result = value.replace(" ","").split(";")
    for item in pre_result:
        pair = item.split(",")
        result.append([get_date(pair[0]), pair[1]])
    return result

def get_holdings_list(value):
    #value = 'e88, 100 ;e89, 200 '
    #print(">>>>" + value)
    result = []
    pre_result = value.replace(" ","").split(";")
    for item in pre_result:
        pair = item.split(",")
        result.append([pair[0], get_float(pair[1])])
    return result


##
def find_next_flag(begin_index, command):
    #print(command)
    for i in range(begin_index, len(command)):
        if (command[i][0] == "-") and (re.match("[a-z/-]",command[i][1])):
            print("---%s" % command[i])
            return i
    return len(command)

def get_parameter_cmd(command, code):
    try:
        index = command.index(code) + 1
        value = command[index]
        if (value[0] != "-") or (re.match("[0-9]",value[1])):
            return command[index : find_next_flag(index + 1, command)]
        return None
    except ValueError:
        return None

def get_params(result, shorts):
    returned = []
    for short in shorts:
        returned.append(get_joined_value(result, short, " "))
    return returned

def parse(command, parameters_list):
    result = []
    for parameter in parameters_list:
        values = get_parameter_cmd(command, parameter)
        if values != None:
            result.append([parameter, values])
    return result

def get_stre(widths):
    stre = ""
    for width in widths:
        stre += "%-"+str(width)+"s "
    return stre

def get_joined_value(parameters, code, delimiter):
    for parameter in parameters:
        if code == parameter[0]:
            return delimiter.join(parameter[1])

def get_full_set(base_class):
    return base_class.query.find().all()

def get_properties_tuple(item, field_widths, field_names):
    #print(item)
    #print(field_widths)
    #print(field_names)
    result = []
    for i in range(len(field_widths)):
        if len(str(getattr(item, field_names[i]))) > field_widths[i]:
            result.append(str(getattr(item, field_names[i]))[:field_widths[i]-5] + "...")
        else:
            result.append(str(getattr(item, field_names[i])))
    return tuple(result)

def get_full_properties_tuple(item, field_names):
    result = []
    for i in range(len(field_names)):
        result.append(str(getattr(item, field_names[i])))
    return tuple(result)

def get_id(item, field_name):
    return getattr(item, field_name)



def get_filter(params, field_names):
    filter = ""
    for i in range(len(params)):
        if (params[i] == None):
            continue
        if filter != "":
            filter += " AND "
        filter += field_names[i] + " = " + get_str(params[i])
    return filter

def get_ids_set(base_class, field_names, field_modifiers, params):
    filter = get_filter(params, field_names)
    with db_session:
        if filter == "":
            return select(item.id for item in base_class if True)[:]
        else:
            return select(item.id for item in base_class if True).filter(raw_sql(filter))[:]
    #print(base_class.query.get(**args))
    #return [str(item._id) for item in base_class.query.find(args).all()]

def get_entities(command, base_class, field_shorts, field_names, field_modifiers):
    global prefix
    global redis_connection

    collection_name = prefix + redis_key_delimiter + str(base_class).split("'")[1].split(".")[0]
    result = parse(command, field_shorts)
    params = get_params(result, field_shorts)
    redis_key = collection_name + redis_key_delimiter + redis_key_delimiter.join([str(param) for param in params])

    got_from_redis = redis_connection.get(redis_key)
    get_ids_set(base_class, field_names, field_modifiers, params)

    if (got_from_redis != None):
        result = [];
        print("got from redis")
        with db_session:
            unpacked = pickle.loads(got_from_redis)
    else:
        unpacked = get_ids_set(base_class, field_names, field_modifiers, params)
        redis_connection.set(redis_key, pickle.dumps(unpacked))
        write_time_to_redis(redis_key)
    pipe = redis_connection.pipeline()
    item_keys = []
    for item_id in unpacked:
        item_key = collection_name + redis_key_delimiter + str(item_id)
        item_keys.append(item_key)
        pipe.get(item_key)
        write_time_to_redis(item_key)
    item_params_set = pipe.execute()
    result = []
    with db_session:
        for i in range(len(unpacked)):
            item = item_params_set[i]
            item_id = unpacked[i]
            if (item != None):
                print("got item from redis")
                result.append(pickle.loads(item))
            else:
                right_item = base_class.select(lambda obj: obj.id == item_id)[:][0]
                print(right_item)
                result.append(right_item)
                redis_connection.set(item_keys[i], pickle.dumps(right_item))
                write_time_to_redis(item_keys[i])
    return result

def show_entities(command, base_class, field_shorts, field_names, field_widths, field_modifiers):
    stre = get_stre(field_widths)
    print(stre % field_names)
    for item in get_entities(command, base_class, field_shorts, field_names, field_modifiers):
        print(stre % get_properties_tuple(item, field_widths, field_names))

def mark_redis_invalid(base_class):
    global redis_connection
    global prefix
    collection_name = prefix + redis_key_delimiter + str(base_class).split("'")[1].split(".")[0]
    #for key in redis_connection.scan_iter(collection_name+'_*valid'):
    #    redis_connection.delete(key)
    for key in redis_connection.scan_iter(collection_name+"*"):
        print(key)
        redis_connection.delete(key)

def check_universal(params):
    for param in params:
        if param != "None":
            return False
    return True

def mark_redis_invalid_after_update(base_class, modified_key_params, entities, collection_name, field_names):
    global redis_connection
    global prefix

    if not check_universal(modified_key_params):
        item_keys = []
        pipe = redis_connection.pipeline()
        for item in entities:
            item_id = get_properties_tuple(item, [10 for i in range(len(field_names))], field_names)[0]
            item_key = collection_name + redis_key_delimiter + item_id
            item_keys.append(item_key)
            pipe.get(item_key)
            write_time_to_redis(item_key)
        item_set = pipe.execute()
        for i in range(len(entities)):
            if (item_set[i] != None):
                redis_connection.set(item_keys[i], pickle.dumps(entities[i]))
                write_time_to_redis(item_keys[i])
        #redis_connection.delete(item_key)

    for key in redis_connection.scan_iter(collection_name+"*" + redis_key_delimiter + "*" + redis_key_delimiter + "*"):
        current_key_params = str(key)[2:-1].split(redis_key_delimiter)[2:]
        #if check_universal(current_key_params) and not check_universal(modified_key_params):
        #    redis_connection.delete(key)
        #    continue
        for i in range(len(modified_key_params)):
            if (modified_key_params[i] != "None") and (current_key_params[i+1] != "None"):
                redis_connection.delete(key)
                break

def revise_redis_keys_update(redis_keys, modified_key_params_before, modified_key_params_after, item_id):
    for key in redis_keys:
        current_key_params = str(key)[2:-1].split(redis_key_delimiter)[2:]

        contained = True
        for i in range(len(modified_key_params_before)):
            if (current_key_params[i+1] != "None") and (current_key_params[i+1] != modified_key_params_before[i]):
                contained = False
                break

        contains = True
        for i in range(len(modified_key_params_after)):
            if (current_key_params[i+1] != "None") and (current_key_params[i+1] != modified_key_params_after[i]):
                contains = False
                break

        if contained and not contains:
            old_list = pickle.loads(redis_connection.get(key))
            old_list.remove(item_id)
            redis_connection.set(key, pickle.dumps(old_list))
            write_time_to_redis(key)
        elif not contained and contains:
            redis_connection.set(key, pickle.dumps(pickle.loads(redis_connection.get(key)) + [item_id]))
            write_time_to_redis(key)


def revise_redis_keys(redis_keys, modified_key_params, append, item_id):
    for key in redis_keys:
        current_key_params = str(key)[2:-1].split(redis_key_delimiter)[2:]
        #if check_universal(current_key_params):
        #    redis_connection.delete(key)
        #    continue
        broken = False

        for i in range(len(modified_key_params)):
            print(modified_key_params," === ",current_key_params)
            if (current_key_params[i+1] != "None") and (current_key_params[i+1] != modified_key_params[i]):
                broken = True
                break
        if not broken:
            if append:
                redis_connection.set(key, pickle.dumps(pickle.loads(redis_connection.get(key)) + [item_id]))
                write_time_to_redis(key)
            else:
                old_list = pickle.loads(redis_connection.get(key))
                old_list.remove(item_id)
                redis_connection.set(key, pickle.dumps(old_list))
                write_time_to_redis(key)

            #redis_connection.delete(key)

def mark_redis_invalid_after_create(base_class, modified_key_params, collection_name, field_names, item_id):
    global redis_connection
    global prefix

    redis_keys = redis_connection.scan_iter(collection_name+"*" + redis_key_delimiter + "*" + redis_key_delimiter + "*")
    revise_redis_keys(redis_keys, modified_key_params, True, item_id)

def mark_redis_invalid_after_delete(base_class, deleted_items, collection_name, field_names):
    global redis_connection
    global prefix

    redis_keys = redis_connection.scan_iter(collection_name+"*" + redis_key_delimiter + "*" + redis_key_delimiter + "*")

    for item in deleted_items:
        redis_connection.delete(collection_name + redis_key_delimiter + str(get_id(item, field_names[0])))
        modified_key_params = get_full_properties_tuple(item, field_names)[1:]
        revise_redis_keys(redis_keys, modified_key_params, False, get_id(item, field_names[0]))

def mark_redis_invalid_after_update_enhanced(base_class, modified_key_params_before_set, modified_key_params_after_set, identifiers, collection_name, field_names):
    global redis_connection
    global prefix

    redis_keys = redis_connection.scan_iter(collection_name+"*" + redis_key_delimiter + "*" + redis_key_delimiter + "*")

    for i in range(len(modified_key_params_after_set)):
        revise_redis_keys_update(redis_keys, modified_key_params_before_set[i], modified_key_params_after_set[i], identifiers[i])

    #for item in deleted_items:
    #    redis_connection.delete(collection_name + redis_key_delimiter + str(get_id(item, field_names[0])))
    #    modified_key_params = get_full_properties_tuple(item, field_names)[1:]
    #    revise_redis_keys(redis_keys, modified_key_params, False, get_id(item, field_names[0]))

##

def delete(command, base_class, field_shorts, field_names, field_modifiers):
    collection_name = prefix + redis_key_delimiter + str(base_class).split("'")[1].split(".")[0]
    with db_session:
        entities = get_entities(command, base_class, field_shorts, field_names, field_modifiers)
        for item in entities:
            item.delete()
        mark_redis_invalid_after_delete(base_class, entities, collection_name, field_names)

@db_session
def update(command, base_class, field_shorts, field_names, field_modifiers):
    entities = get_entities(command, base_class, field_shorts, field_names, field_modifiers)
    result = parse(command, ["-"+field_short for field_short in field_shorts[1:]])
    params = get_params(result,["-"+field_short for field_short in field_shorts[1:]])

    collection_name = prefix + redis_key_delimiter + str(base_class).split("'")[1].split(".")[0]
    modified_key_params_before_set = []
    modified_key_params_after_set = []
    identifiers = []

    for item in entities:
        modified_key_params_before_set.append(get_full_properties_tuple(item, field_names)[1:])

    print(entities)
    for i in range(len(params)):
        if (params[i] != None):
            for item in entities:
                setattr(item, field_names[i + 1], field_modifiers[ i + 1 ](params[i]))
    commit()

    for item in entities:
        identifiers.append(get_id(item, field_names[0]))
        modified_key_params_after_set.append(get_full_properties_tuple(item, field_names)[1:])

    if not check_universal([str(param) for param in params]):
        item_keys = []
        pipe = redis_connection.pipeline()
        for item in entities:
            item_id = get_properties_tuple(item, [10 for i in range(len(field_names))], field_names)[0]
            item_key = collection_name + redis_key_delimiter + item_id
            item_keys.append(item_key)
            pipe.get(item_key)
            write_time_to_redis(item_key)
        item_set = pipe.execute()
        for i in range(len(entities)):
            if (item_set[i] != None):
                redis_connection.set(item_keys[i], pickle.dumps(entities[i]))
                write_time_to_redis(item_keys[i])

    mark_redis_invalid_after_update_enhanced(base_class, modified_key_params_before_set, modified_key_params_after_set, identifiers, collection_name, field_names)
    return [item.id for item in entities]

@db_session
def update_old(command, base_class, field_shorts, field_names, field_modifiers):
    entities = get_entities(command, base_class, field_shorts, field_names, field_modifiers)
    result = parse(command, ["-"+field_short for field_short in field_shorts[1:]])
    params = get_params(result,["-"+field_short for field_short in field_shorts[1:]])

    collection_name = prefix + redis_key_delimiter + str(base_class).split("'")[1].split(".")[0]

    print(entities)
    for i in range(len(params)):
        if (params[i] != None):
            for item in entities:
                setattr(item, field_names[i + 1], field_modifiers[ i + 1 ](params[i]))
    commit()
    mark_redis_invalid_after_update(base_class, [str(param) for param in params], entities, collection_name, field_names)
    return [item.id for item in entities]

def create(command, base_class, field_shorts, field_names, field_modifiers):
    result = parse(command, field_shorts)
    args = {}
    collection_name = prefix + redis_key_delimiter + str(base_class).split("'")[1].split(".")[0]
    params = []

    for i in range(len(field_names) - 1):
        params.append(str(get_joined_value(result, field_shorts[ i + 1], " ")))
        if field_modifiers[ i + 1](get_joined_value(result, field_shorts[ i + 1], " ")) == None:
            continue;
        args[field_names[i + 1]] = field_modifiers[ i + 1](get_joined_value(result, field_shorts[ i + 1], " "))

    with db_session:
        new_object = base_class(**args)

    mark_redis_invalid_after_create(base_class, params, collection_name, field_names, get_id(new_object, field_names[0]))
    return new_object

##

def get_create_rules(cmd, field_status, field_shorts, field_names, field_descriptions):
    cmd = ""
    for i in range(len(field_status)):
        if field_status[i] == 1:
            opening_brace = " [ "
            closing_brace = " ] "
        elif field_status[i] == 2:
            opening_brace = " "
            closing_brace = " "
        else:
            continue
        cmd += "\n\t"
        cmd += opening_brace + field_shorts[i] + " " + field_names[i] + " " + field_descriptions[i] + closing_brace
    return cmd

def get_read_delete_rules(cmd, field_status, field_shorts, field_names, field_descriptions):
    cmd = ""
    for i in range(len(field_status)):
        cmd += "\n\t"
        cmd += " [ " + field_shorts[i] + " " + field_names[i] + " " + field_descriptions[i] + " ] "
    return cmd

def get_update_rules(cmd, field_status, field_shorts, field_names, field_descriptions):
    cmd = ""
    for i in range(len(field_shorts)):
        if field_status[i] == 0:
            continue
        cmd += "\n\t"
        cmd += " [ " + field_shorts[i] + " " + field_names[i] + " " + field_descriptions[i] + " ] "
        cmd += "\n\t"
        cmd += " [ " + "-" + field_shorts[i] + " " + field_names[i] + " " + "new value" + " ] "
    return cmd