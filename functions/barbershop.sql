
drop package barbershop;
CREATE or replace PACKAGE barbershop AS
   function get_clients_list(master_id int, date_ date) return clients_table__;
   function get_clients_list_as_strings(master_id int, date_ date) return string_clients_table__;
END;
/

CREATE or replace PACKAGE BODY barbershop AS
   FUNCTION get_clients_list(master_id int, date_ date) return clients_table__ IS
   clients clients_table__;
   cc client__;
   cnt int;
   cursor clients_ is select name, patronymic, contact, cast(visit_date_time as date) vdate from (requests r join clients c on r.client_id = c.id) join 
        (
            select * from contacts where id in 
            (
                select min(id) from contacts group by person_id, person_status
            ) 
            and person_status = 'client' and type = 'phone'
        ) 
        on person_id = client_id
        where trunc(cast(visit_date_time as date)) = date_ and worker_id = master_id
        order by visit_date_time;
   BEGIN
        cnt := 0;
        clients := clients_table__(null);
        FOR client_ IN clients_ LOOP
            if cnt <> 0 then
                clients.extend();
            else
                cnt := 1;
            end if;
            clients(clients.count) := client__(client_.name, client_.patronymic, client_.contact, client_.vdate);
        END LOOP;
        return clients;
   END;
   
   FUNCTION get_clients_list_as_strings(master_id int, date_ date) return string_clients_table__ IS
   clients string_clients_table__;
   client string_client__;
   cnt int;
   cursor clients_ is select name, patronymic, contact, cast(visit_date_time as date) vdate from (requests r join clients c on r.client_id = c.id) join 
        (
            select * from contacts where id in 
            (
                select min(id) from contacts group by person_id, person_status
            ) 
            and person_status = 'client' and type = 'phone'
        ) 
        on person_id = client_id
        where trunc(cast(visit_date_time as date)) = date_ and worker_id = master_id
        order by visit_date_time;
   BEGIN
        cnt := 0;
        clients := string_clients_table__(null);
        FOR client_ IN clients_ LOOP
            if cnt <> 0 then
                clients.extend();
            else
                cnt := 1;
            end if;
            clients(clients.count) := string_client__(client_.name, client_.patronymic, client_.contact, to_char(client_.vdate,'HH24:MI'));
        END LOOP;
        return clients;
   END;
END;
/
select min(id) from contacts group by person_id, person_status;
select * from contacts where id in (select min(id) from contacts group by person_id) and person_status = 'client' and type = 'phone';
select * from contacts where id in (select min(id) from contacts group by person_id);

--to_char(visit_date_time,'HH24:MI')1

create table strings_tmp(
    val varchar(200)
);
drop table opop;
select * from opop;
set serveroutput on;
declare
vv boolean;
clients clients_table__;
client client__;
ind int;
ide int;
begin
    --clients := clients_table__(null);
    --clients.extend(100);
    --declare local temporary table opop of client__;
    --delete from opop;
    --insert into opop values (client__('a', 'a', 'a', TO_DATE('2002/11/10', 'yyyy/mm/dd')));
    clients := barbershop.get_clients_list(2, TO_DATE('2002/11/10', 'yyyy/mm/dd'));
    --WORKERS_STATES_TAPI.del(3);
    --WORKERS_STATES_TAPI.ins(NULL, ide, '������');
    ide := WORKERS_STATES_TAPI.ins_f(null, '������������');
    for ind in clients.first .. clients.last loop
      client := clients(ind);
      dbms_output.put_line(client.name || ' ' || client.patronymic || ' ������ �� ' || to_char(client.date_,'HH24:MI') || '. ����� �������� : ' || client.phone);
    end loop;
    --dbms_output.put_line('-----------' || clients(1).phone);
end;
select * from clients;

select * from opop;
select * from requests;