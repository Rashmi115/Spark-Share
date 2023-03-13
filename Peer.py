import sys, socket, pickle
from threading import *

MAX_CHUNK = 8*1024

class Peer:
    def __init__(self,serv_host,serv_port,max_conn):
        self.SERV=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.SERV.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.serv_host=serv_host
        self.serv_port=serv_port
        print(self.serv_host,self.serv_port)
        self.max_connection=max_conn
        try:
            self.SERV.connect((self.serv_host,self.serv_port))
        except(ConnectionRefusedError):
            print("\nFailed to establish connection with central server\n")
            sys.exit()
        except(TimeoutError):
            print("\nPeer not responding connection failed")
            sys.exit()
        else:
            msg=self.SERV.recv(MAX_CHUNK)
            msg=pickle.loads(msg)
            print("\nConnection Established\nPeer ID: ",msg[0],"\n")
            self.PORT=msg[1]            

    def download(self,addr,fileName):
        try:                
            self.soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.soc.connect(addr)
            self.soc.send(pickle.dumps(fileName))
            msg= pickle.loads(self.soc.recv(MAX_CHUNK))
            var = False
            if msg == "FILEFOUND":
                self.soc.send(pickle.dumps("SND"))
                file = open('D:\\download\\'+fileName,'wb')
                data = self.soc.recv(MAX_CHUNK)
                while True:
                    file.write(data)
                    data = self.soc.recv(MAX_CHUNK)
                    if not data:
                        break
                file.close()               
                self.soc.send(pickle.dumps("RCVD"))
                var = True
            elif msg == "FILENOTFOUND":
                var = False
                self.soc.close()
        except(ConnectionRefusedError):
            print("\nFailed to establish connection with central server\n")
            var = False
        except(TimeoutError):
            print("\nPeer not responding connection failed")
            var = False
        return var

    
    def sendFile(self,conn,addr):
        try:
            fileName = conn.recv(MAX_CHUNK)
            fileName = pickle.loads(fileName)
            file = open(fileName, 'rb')
            msg= "FILEFOUND"
            conn.send(pickle.dumps(msg))
            ack = pickle.loads(conn.recv(MAX_CHUNK))
            if ack == "SND":
                x=file.read(MAX_CHUNK)
                while (x):
                    conn.send(x)
                    # print(x)
                    x=file.read(MAX_CHUNK)
                file.close()
                data = pickle.loads(conn.recv(MAX_CHUNK))
                if(data == "RCVD"):
                    print(fileName+" sent")
        except(FileNotFoundError):
            msg= "FILENOTFOUND"
            conn.send(pickle.dumps(msg))
            return False
        except:
            print("File transfer failed")
            return False            
        else:
            return True

    def seed(self):
        try:
            self.soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.soc.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            self.HOST=socket.gethostbyname(socket.gethostname())
            self.soc.bind((self.HOST,self.PORT))
            self.soc.listen(self.max_connection)
    
            while True:
                conn,addr = self.soc.accept()
                print("Connected with "+str(addr[0])+" Port: "+str(addr[1]))
        
                try:                
                    Thread(target=self.sendFile,args=(conn,addr)).start()  
                except:
                    print("Thread did not start")
                    traceback.print_exc()
        except(KeyboardInterrupt):
            print("Stopping Seeding")
        return
        


    def register(self,filename):
        self.SERV.send(pickle.dumps("REG"))
        data = pickle.loads(self.SERV.recv(MAX_CHUNK))
        if (data == "OK"):
            self.SERV.send(pickle.dumps(filename))
            data=pickle.loads(self.SERV.recv(MAX_CHUNK))
            if (data == "SUCCESS"):
                proc=input("\nFile registered.\nProceed to Seed (Y/N)\n")
                if (proc.upper() == 'Y'):
                    print("Enabling Seeder mode:")
                    self.seed()
                else:
                    return True
            else:
                return False
        else:
            return False

    def search_file(self,fileName):
        self.SERV.send(pickle.dumps("SEARCH"))
        var=False
        data = self.SERV.recv(MAX_CHUNK)
        if (pickle.loads(data) == "OK"):
            self.SERV.send(pickle.dumps(fileName))
            data=self.SERV.recv(MAX_CHUNK)
            if (pickle.loads(data) == "FOUND"):
                proc=input("\nFile Found\nProceed to download (Y/N)\n")
                if (proc.upper() == 'Y'):
                    self.SERV.send(pickle.dumps("SEND"))
                    data=self.SERV.recv(MAX_CHUNK)
                    data=pickle.loads(data)
                    if len(data) == 1:
                        self.SERV.send(pickle.dumps(data[0]))
                    else:
                        for i in range(len(data)):
                            print(i+1," ",data[i])
                        choice=int(input("Enter choice of peer:"))
                        self.SERV.send(pickle.dumps(data[choice-1]))
                    addr=pickle.loads(self.SERV.recv(MAX_CHUNK))
                    var = self.download(addr,fileName)
                elif (proc.upper() == 'N'):
                    self.SERV.send(pickle.dumps("N"))
                    var = False
            elif (pickle.loads(data) == "NOT FOUND") :
                print("File not found with any peer")
                var = False
        return var


    def quit_all(self):
        self.SERV.send(pickle.dumps("BYE"))
        if (pickle.loads(self.SERV.recv(MAX_CHUNK)) == "OK"):
                self.SERV.close()
                sys.exit(0)
    
            


addr=input("\nEnter the ip and port of server:\n")
addr=addr.split(" ")
print(addr)
myPeer = Peer(addr[0],int(addr[1]),5)
while True:
        choice= int(input("\nEnter your choice:\n1. Register and Seed\n2. Search and Download\n3. Quit\n"))
        if choice == 1:
            fileName=input("Enter the name of your file:\n")
            try:
                file = open(fileName,'r')
            except(FileNotFoundError):
                print("File does not exist in the given directory\n")
            else:
                file.close()
                var = myPeer.register(fileName)
                if var:
                    print("Registration Successful")
                else:
                    print("Registration Failed")

        elif choice == 2:
                fileName=input("Enter the file name to search:")
                result=myPeer.search_file(fileName)
                if result:
                    print("Search and Download Successful")
                else:
                    print("Search and Download Failed")

        elif choice == 3:
                myPeer.quit_all()
