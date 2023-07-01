from typing import Optional
from dataclasses import dataclass
from docker.client import DockerClient
from docker.models.containers import Container as DockerContainer
import docker
import time

@dataclass
class Node:
    id: str
    ip: str
    obj: Optional[DockerClient]

@dataclass
class Contianer:
    id: str
    ip: str
    obj: Optional[DockerContainer]

def is_manager(client):
    sinfo = client.info()['Swarm']
    if sinfo['NodeID'] in [s['NodeID'] for s in sinfo['RemoteManagers']]:
        return True
    else:
        return False

def get_base_url(ip: str, port: int = 2375):
    return f"tcp://{ip}:{str(port)}"

def get_ip_address(client):
    return client.info()['Swarm']['NodeAddr']


class DockerSwarmHandler:
    def __init__(self, num_containers=None):
        self.manager = docker.from_env()
        self.update_nodes()
        self.set_num_containers(num_containers)
        self.service = None

    def set_num_containers(self, num_containers):
        if num_containers:
            self.mode = docker.types.ServiceMode('replicated', replicas=num_containers)
        else:
            self.mode = None
            
    def update_nodes(self):
        self.nodes = []
        for node in self.manager.nodes.list():
            nid = node.attrs['ID']
            node_status = node.attrs['Status']
            node_ip = node_status['Addr']
            node_state = node_status['State']
            
            if node_state == "ready":
                if node_ip == get_ip_address(self.manager):
                    n = self.manager
                else:
                    n = docker.DockerClient(base_url=get_base_url(node_ip))
            else:    
                n = None
            self.nodes.append(Node(id=nid, ip=node_ip, obj=n))
            
    def create_service(self, image, name):
        # remove existing service
        self.remove_service()

        # create new service
        self.service = self.manager.services.create(image, name=name, tty=True, mode=self.mode)
        self.containers = []

        # wait until node id appears
        tasks = self.service.tasks()
        holder = [t for t in tasks if 'NodeID' in t.keys()]
        while len(holder) == 0:
            time.sleep(0.1)
            tasks = self.service.tasks()
            holder = [t for t in tasks if 'NodeID' in t.keys()]

        # wait until all container active
        running = [t for t in tasks if 'ContainerStatus' in t['Status'].keys()]
        print('Waiting until all container active', end='')
        while len(running) < len(tasks):
            time.sleep(2)
            tasks = self.service.tasks()
            running = [t for t in tasks if 'ContainerStatus' in t['Status'].keys()]
            print('.', end='')
        print('ready!')
        
        for t in self.service.tasks():
            node_id = t['NodeID']
            node = self.manager.nodes.get(node_id)
            node_ip = node.attrs['Status']['Addr']
            cont_id = t['Status']['ContainerStatus']['ContainerID']
            node = [n for n in self.nodes if n.id == node_id]
            if len(node):
                client = node[0].obj
                if client:
                    container = client.containers.get(cont_id)
                    self.containers.append(Contianer(id=cont_id, ip=node_ip, obj=container))

    def remove_service(self):
        if self.service:
            self.service.remove()