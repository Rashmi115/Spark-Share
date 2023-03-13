import socket
import pickle
import ipaddress
import uuid
import threading
PORT=12345
MAX_CHUNK = 8* 1024


class CentralServer:


    def __init__(self,port,max_connections):

        self.port = port                                            #this machine
        self.host = socket.gethostbyname(socket.gethostname())      #this machine
        self.max_connections = max_connections
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )

        x=True
        while x:
            try:
                self.sock.bind((self.host,self.port))   
            except OverflowError:
                input("Enter new port(0 to 65535): ")
            else:
                x=False

        self.file_list={} #List of Files registered
        self.peer_list={} #List of Peers connected

        print("Listen through (",self.host,":",self.port,")")


    def client_thread(self,conn,addr):

        uniq_id = uuid.uuid4().int>>115 #Generates unique ID for each peer
        
        self.peer_list[uniq_id]=addr #Append to List of Peers
        conn.send(pickle.dumps((uniq_id,addr[1]))) #Send unique (peer_id,port) to peer

        
        cmd = pickle.loads(conn.recv(MAX_CHUNK))
        print(cmd)
        
        if (cmd == "SEARCH") :    #Searching file in Central Index Server
            conn.send(pickle.dumps("OK"))
            file_name = pickle.loads(conn.recv(MAX_CHUNK))

            if file_name not in self.file_list:
                conn.send(pickle.dumps("NOT FOUND"))
                
            else:
                conn.send(pickle.dumps("FOUND"))
                reply=pickle.loads(conn.recv(MAX_CHUNK))

                if (reply =="SEND"):
                    list = pickle.dumps(self.file_list[file_name])
                    conn.send(list)
                    
                    c_peer = pickle.loads(conn.recv(MAX_CHUNK))
                    conn.send(pickle.dumps(self.peer_list[c_peer]))
                       
                else:
                    """Do Nothing for Search and not downloading"""
        
        elif (cmd == "REG"):   #Registering/Seeding a File
            conn.send(pickle.dumps("OK"))
            file_name = pickle.loads(conn.recv(MAX_CHUNK))
            print(file_name)

            if file_name in self.file_list:
                self.file_list[file_name].append(uniq_id)                
            else:
                self.file_list[file_name] = []
                self.file_list[file_name].append(uniq_id)
            conn.send(pickle.dumps("SUCCESS"))
        
        elif (cmd=="BYE"):

            conn.send(pickle.dumps("OK"))

            a=[]    #list of files with no peers 
            #to delete peer from the list
            for i in self.file_list:
                try:
                    self.file_list[i].remove(uniq_id)
                    if self.file_fist[i]==[]:
                        a.append(i)
                except ValueError:
                    continue
            for i in a:
                self.file_list.pop(i)

            del peer_list[uniq_id]

            
    def listen(self):
        threadId=[]
        self.sock.listen(self.max_connections)
        print("Listening...")

        while True:
            
            conn,addr = self.sock.accept()      #accept connections
            print("Connected with ",addr)

           
            
            try:               # thread creation for each peer
                t1=threading.Thread(target=self.client_thread,args=(conn,addr))
                t1.start()
                print("Thread started")

            except:
               print("Thread did not start")
                
        
        self.sock.close()

    

if __name__=="__main__":
    S=CentralServer(PORT,5)
    S.listen()

