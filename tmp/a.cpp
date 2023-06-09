#include <arpa/inet.h>
#include <fcntl.h>
#include <netdb.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <semaphore.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/shm.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#include <algorithm>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <thread>
#include <vector>

#include "json.hpp"
using namespace std;
using json = nlohmann::json;
#define RECEIVER_ADDRESS "127.0.0.1"  // 目的地址
#define INT_MAX 99999999
//#define RECEIVER_ADDRESS "172.17.0.55" // 目的地址

struct my_package {
  uint32_t tunnel_id;
  uint32_t source_module_id;
  uint16_t source_user_id;
  uint16_t dest_user_id;
  uint32_t flow_id;
  uint32_t service_id;
  uint32_t qos_id;
  uint32_t packet_id;
  timespec timestamp;
  uint32_t ext_flag;
};

struct control_message {
  uint32_t  total_loss=1;
  uint32_t  recent_loss=2;
  uint32_t  max_delay=3;
  uint32_t  min_delay=4;
  uint32_t  avg_delay=5;
  uint32_t  unused1=234;
  uint32_t  unused2=1234;
  uint32_t  unused3=1234;
};

int recv_thread(int port, int package_size);
void client_init();
void report_delay(uint32_t max_delay,uint32_t min_delay,uint32_t avg_delay);
int package_size = 2048, package_speed, delay;
long package_num;
int control_port, client_port,server_port;//client:接入网 server：本pod接收程序 control；控制程序
string control_address;  // 初始发送参数，在程序开始时指定
char datagram[2048];
my_package pack;

int main(int argc, char *argv[]) {
  // 127.0.0.1
  client_init();
  control_address = argv[1];
  cout << control_address << endl;
  struct hostent *host;
  host = gethostbyname(control_address.c_str());
  if (host == NULL) {
    cout << "gethostbyname error" << endl;
    return 0;
  }
  control_address = inet_ntoa(*(struct in_addr *)host->h_addr_list[0]);
  cout << control_address << endl;
  sleep(1);
  cout << "接收开始" << endl;
  std::thread receive_t(recv_thread,server_port,package_size);
  while (1) {
    sleep(1);
  }
}

void client_init() {
  ifstream srcFile("./init.json", ios::binary);
  if (!srcFile.is_open()) {
    cout << "Fail to open src.json" << endl;
    return;
  }
  json j;
  srcFile >> j;
  pack.source_user_id = j["source_id"];
  pack.dest_user_id = j["dest_id"];
  package_num = j["package_num"];
  package_speed = j["package_speed"];
  control_port = j["control_port"];
  server_port = j["server_port"];
  srcFile.close();
  return;
}

int recv_thread(int port, int package_size) {
  int num = 0;
  // socket初始化
  int recv_socket;
  sockaddr_in recv_addr, sender_addr;
  recv_socket = socket(AF_INET, SOCK_DGRAM, 0);
  recv_addr.sin_family = AF_INET;
  recv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
  recv_addr.sin_port = htons(server_port);
  bind(recv_socket, (sockaddr *)&recv_addr, sizeof(recv_addr));
  // 接收准备
  socklen_t sender_addrLen = sizeof(sender_addr);
  char buffer[package_size];
  int readLen = 0;
  uint32_t cnt_package = 0,recent_package=0;
  uint32_t total_delay;
  timespec delay_a, delay_b,delay_c;
  uint32_t max_delay=0,min_delay=INT_MAX,avg_delay=0, recent_delay=0;
  delay_a = {0, 0};
  delay_b = {0, 0};
  delay_c = {0, 0};
  clock_gettime(CLOCK_MONOTONIC, &delay_c);
  while (true) {    
    // readLen = recvfrom(recv_socket, buffer, package_size, 0,
                      //  (sockaddr *)&sender_addr, &sender_addrLen);
    clock_gettime(CLOCK_MONOTONIC, &delay_a);
    my_package *temp=(my_package *)buffer;
    delay_b=temp->timestamp;
    recent_delay=(delay_a.tv_sec-delay_b.tv_sec)*(1000000000)+(delay_a.tv_nsec-delay_b.tv_nsec);
    if(recent_delay>max_delay)
      max_delay=recent_delay;
    else if(recent_delay<min_delay)
      min_delay=recent_delay;
    total_delay=total_delay+recent_delay;
    cnt_package++;recent_package++;
    //每隔1s汇报
    if((delay_a.tv_sec-delay_c.tv_sec)*(1000000000)+(delay_a.tv_nsec-delay_c.tv_nsec)>=1000000000)
    {
        avg_delay=total_delay/recent_package;
        report_delay(max_delay,min_delay,avg_delay);
        avg_delay=0;min_delay=INT_MAX;
        max_delay=0;recent_package=0;total_delay=0;
        delay_c=delay_a;
    }
  }
  return 0;
}

void report_delay(uint32_t max_delay,uint32_t min_delay,uint32_t avg_delay)
{
  //消息准备
  char data[32];
  memset(data,0,sizeof(data));
  control_message* temp=(control_message*)data;
  temp->max_delay=max_delay;temp->min_delay=min_delay;temp->avg_delay=avg_delay;
  //发送准备
  int my_socket;
  sockaddr_in target_addr, my_addr;
  my_socket = socket(AF_INET, SOCK_DGRAM, 0);
  my_addr.sin_family = AF_INET;
  my_addr.sin_port = htons(2222);
  my_addr.sin_addr.s_addr = inet_addr("0.0.0.0");
  // 绑定端口
  bind(my_socket, (sockaddr *)&my_addr, sizeof(my_addr));
  // 指定目标
  target_addr.sin_family = AF_INET;
  target_addr.sin_port = htons(control_port);
  target_addr.sin_addr.s_addr = inet_addr(control_address.c_str());

  sendto(my_socket, data, sizeof(data), 0,
                   (sockaddr *)&target_addr, sizeof(target_addr));
}

