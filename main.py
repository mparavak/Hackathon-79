import time
import sys

import toml
import yaml


templates = {
                "service_template" : "template_service.yaml",
                "deployment_template":"template_deployment.yaml",
                "ingress_template" : "template_ingress.yaml",
                "secret_template"  : "template_secret.yaml"
            }

input_toml = sys.argv[1]

class UnknownFormat(Exception):
    pass

class Toml:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class Yaml:
    def __init__(self,**entries):
        self.__dict__.update(entries)

class Object:
    def __init__(self,**entries):
        self.__dict__.update(entries)

def get_app_name(pool,search,found = True):

    if not isinstance(pool,list):
        pools = pool
    else:
        pools = pool

    name = ""

    for dct_pool in pools:
        obj = Object(**dct_pool)
        name = str(obj.name)
        if found :
            if obj.image.find(search) != -1 :
                return str(obj.name)
        else:
            if obj.image.find(search) == -1:
                return name

    return name


def get_image_name(pool,search,found = False):
    if not isinstance(pool,list):
        pools = pool
    else:
        pools = pool

    name = ""

    for dct_pool in pools:
        obj = Object(**dct_pool)
        name = str(obj.image)
        if not found :
            if obj.image.find(search) == -1:
                return name

def get_environment(pool):
    if not isinstance(pool, list):
        pools = pool
    else:
        pools = pool

    name = ""

    for dct_pool in pools:
        if "environment" in dct_pool:
            d = dct_pool.get("environment","environment not found")
            return {str(k): str(v) for k, v in d.items()}
    pass

def get_template_object(input_yaml):
    with open(input_yaml) as f:
        return yaml.safe_load(f)
    pass

def generate_yaml_file(output_obj,output_yaml_file):
    with open(output_yaml_file, 'w') as yaml_file:
        yaml_file.write(yaml.dump( vars(output_obj), default_flow_style=False,sort_keys=True))


def generate_env_file(environ):
    with open("quadra.env", 'w') as env_file:
        env_file.writelines(environ)
    pass


dct_toml = toml.load(input_toml)
toml_obj = Toml(**dct_toml)

ports_name = "web"+str(int(time.time()))

for key,input_yaml in templates.items() :
    dct_yaml = get_template_object(input_yaml)
    yaml_obj = Yaml(**dct_yaml)

    if yaml_obj.kind == "Service":
        name = get_app_name(toml_obj.pools,"http-lb")
        yaml_obj.spec["selector"]["app"] = name.split(".")[0]
        yaml_obj.metadata["name"] = name.split(".")[0]
        yaml_obj.spec["ports"][0]["targetPort"] = ports_name

    elif yaml_obj.kind == "Deployment":
        name = get_app_name(toml_obj.pools, "http-lb",found=False)
        yaml_obj.metadata["name"] = name
        yaml_obj.spec["selector"]["matchLabels"]["app"] = name
        #yaml_obj.spec["template"]["spec"]["containers"][0]["image"] = get_image_name(toml_obj.pools, "http-lb",found=False)
        yaml_obj.spec["template"]["spec"]["containers"][0]["ports"][0]["name"] = ports_name
        yaml_obj.spec["template"]["metadata"]["labels"]["app"] = name

    elif yaml_obj.kind == "Ingress":
        name = toml_obj.firewalls[0]["name"]
        yaml_obj.metadata["name"] = str(name)

        protocol = toml_obj.firewalls[0]["rules"][0]["protocols"][0]
        yaml_obj.spec["ports"][0]["protocol"] = str(protocol).upper()

        port = toml_obj.firewalls[0]["rules"][0]["ports"][0]
        yaml_obj.spec["ports"][0]["port"] = port

        environ = get_environment(toml_obj.pools)
        yaml_obj.spec["rules"][0]["http"]["paths"][0]["path"] = environ.get('BACKEND_CHECK_URL','')

    elif yaml_obj.kind == "Secret":

        environ = get_environment(toml_obj.pools)
        yaml_obj.data = environ

    else:
        raise UnknownFormat("Unknown Yaml File type")

    generate_yaml_file(yaml_obj,"generated_"+input_yaml)
    pass





