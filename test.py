from src.cpp_process import server
import threading

def ff():
    print('ff')
    server.start('234234')
    pass

def gg():
    print('gg')
    server.start('1111')
    server.read_output()

if __name__ == "__main__":

    # t1 = threading.Thread(target=worker, args=(1,))
    t1 = threading.Thread(target=gg)
    # t1 = threading.Thread(target=check_cpp_output)
    t2 = threading.Thread(target=ff)

    t1.start()
    t2.start()


    t1.join()
    t2.join()
