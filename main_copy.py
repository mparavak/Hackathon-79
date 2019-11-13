import os
import sys

import toml
import yaml


input_toml = sys.argv[1]
input_yaml = sys.argv[2]


dct_toml = toml.load(input_toml)

with open(input_yaml) as f :
    dct_yaml = yaml.safe_load(f)

#print dct_toml

{u'pools': [
            {u'name': u'pushnotification-bk-prod.gsuiteidstream',
             u'firewall': {u'in': [{u'firewall': u'pushnotification-fw-prod.gsuiteidstream', u'mode': u'allow'}]},
             u'healthcheck': {u'protocol': u'http', u'rise': 3, u'timeout': 2, u'fall': 3,
                              u'path': u'/identity/v1/status', u'port': 80},
             u'image': u'gsuiteidstream/pushnotification-app', u'memory': 5120, u'kill_timeout': 3600,
             u'save_empty_deploys': 2, u'instances': 1, u'tag': u'prod', u'host_tag': u'default',
             u'datacenters': [u'${DATACENTER}'], u'cpu': 2.0, u'deploy_step_size': 1},
            {u'name': u'pushnotification-lb-prod.gsuiteidstream',
             u'firewall': {u'in': [{u'firewall': u'pushnotification-fw-prod.gsuiteidstream', u'mode': u'allow'}]},
             u'healthcheck': {u'protocol': u'https', u'rise': 3, u'timeout': 2, u'fall': 3, u'path': u'/backend_status',
                              u'port': 443}, u'image': u'quadra/http-lb', u'save_empty_deploys': 1, u'environment': {
                u'SSL_CIPHERS': u'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-DSS-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES256-GCM-SHA384:AES256-SHA256:AES256-SHA:SRP-DSS-AES-256-CBC-SHA:SRP-RSA-AES-256-CBC-SHA:SRP-AES-256-CBC-SHA:DHE-DSS-AES256-SHA256:DHE-RSA-CAMELLIA256-SHA:DHE-DSS-CAMELLIA256-SHA:CAMELLIA256-SHA:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:AES128-GCM-SHA256:AES128-SHA256:AES128-SHA:SRP-DSS-AES-128-CBC-SHA:SRP-RSA-AES-128-CBC-SHA:SRP-AES-128-CBC-SHA:DHE-DSS-AES128-SHA:DHE-RSA-CAMELLIA128-SHA:DHE-DSS-CAMELLIA128-SHA:CAMELLIA128-SHA:DES-CBC3-SHA:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305',
                u'VINZ_CERT_ID': u'${REQUEST_ID_PROD}', u'SSL_PROTOCOLS': u'TLSv1 TLSv1.1 TLSv1.2',
                u'BACKEND_CHECK_URL': u'/identity/v1/status', u'SSL_PORT': 443,
                u'VINZ_API': u'https://api.vinz.opendns.com/v1', u'SECRET_VINZ_DEPLOY_KEY': u'${DEPLOYKEY_PROD}',
                u'REDIRECT_TO_SSL': True, u'BACKEND_POOL': u'pushnotification-bk-prod.gsuiteidstream',
                u'BACKEND_PORT': 80}, u'instances': 1, u'tag': u'latest', u'ipv4': u'${IP}', u'memory': 4096,
             u'datacenters': [u'${DATACENTER}'], u'cpu': 2.0, u'deploy_step_size': 1}
            ],
 u'ips': [
    {u'comment': u'gsuiteidstream/pushnotification-app - This is the reserved IP for pushnotification service',
     u'ip': u'${IP}', u'project': u'gsuiteidstream', u'datacenters': [u'${DATACENTER}']}],
 u'firewalls': [

                {u'rules': [
                                {u'protocols': [u'tcp'], u'ports': [443], u'resources': [u'0.0.0.0/0']},
                                {u'protocols': [u'tcp'], u'ports': [80], u'resources': [u'0.0.0.0/0']}
                           ],
                 u'datacenters': [u'${DATACENTER}'],
                                                                                                           u'name': u'pushnotification-fw-prod.gsuiteidstream'}
            ]
 }


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


toml_obj = Toml(**dct_toml)
yaml_obj = Yaml(**dct_yaml)

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


def generate_yaml_file(output_obj,output_yaml_file):
    with open(output_yaml_file, 'w') as yaml_file:
        yaml_file.write(yaml.dump( vars(output_obj), default_flow_style=False,sort_keys=True))


if yaml_obj.kind == "Service":
    name = get_app_name(toml_obj.pools,"http-lb")
    yaml_obj.spec["selector"]["app"] = name
    yaml_obj.metadata["name"] = name
elif yaml_obj.kind == "Deployment":
    name = get_app_name(toml_obj.pools, "http-lb",found=False)
    yaml_obj.metadata["name"] = name
    yaml_obj.spec["selector"]["matchLabels"]["app"] = name
    yaml_obj.spec["template"]["spec"]["containers"][0]["image"] = get_image_name(toml_obj.pools, "http-lb",found=False)
else:
    raise UnknownFormat("Unknown Yaml File type")




generate_yaml_file(yaml_obj,"generated_"+input_yaml)






"""
class Node :
    def __init__(self):
        self.image = "image"
        self.path = "/h/ki"

class Yaml:
    def __init__(self):
        self.pool = ""
        self.firewall = ""
        self.node = Node()


    def __dct__(self):
        self.node = self.node.__dict__()
        return self.__dict__


print Yaml().__dict__

print vars(Yaml())


"""





