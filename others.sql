insert into workers_statuses (name) values ('�������');
insert into workers_statuses (name) values ('����������');
insert into workers_statuses (name) values ('������');
select * from workers_statuses;

select * from premiums_sizes;

set serveroutput on;
insert into contacts (person_id, person_status, type, contact) values (1,'client','phone','+7 (973) 122-3304');
select * from workers;

insert into premiums (premium_id, worker_id, earning_date, premium_size)
values(1, 2, to_date('10-03-02','DD-MM-RR'), 1000);
select * from premiums;
drop table premiums_sizes;
drop table holdings;
insert into clients (name, surname, patronymic, sex, address) values ('���������','�����������','�������������','m','���������� ���. 15/2 ������� 1306');
insert into workers (name, surname, sex, address, position, qualification) 
values ('�����','����','m','����-����� 13 ������ 6 �������� 666','�����-����������','���������');
insert into contacts (person_id, person_status, type, contact) values (1,'client','vk','do_odd');
insert into services (name, price) values ('������ ������',100);
insert into services (name, price) values ('����������� �������',300);
insert into requests (visit_date_time, worker_id, client_id, service_id) 
values (to_timestamp ('10-11-02 14:10', 'DD-MM-RR HH24:MI'), 2, 1, 2);
insert into holdings (name, price, quantity) values ('Refectocil ������ �.������ � ������ ��.-��������a� �3.1 15��', 331, 10);
drop table requests;
insert into premiums_sizes (name, min, max) values ('�� ������� �����', 500, 2000);
select * from premiums_sizes;
insert into salaries (worker_id, common, vacation, sick) values (2, 6666.66, 6666.66, 6666.66);

select * from workers;
select surname, c.name, patronymic, s.name, visit_date_time 
from (requests r join clients c on r.client_id = c.id) join services s on s.id = r.service_id;

SELECT TO_TIMESTAMP ('10-09-02 14:10:10.123000', 'DD-MM-RR HH24:MI:SS.FF')
   FROM DUAL;

drop table clients;
select * from clients;
select * from workers;