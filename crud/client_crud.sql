create or replace package CLIENTS_tapi
is

type CLIENTS_tapi_rec is record (
SURNAME  CLIENTS.SURNAME%type
,PATRONYMIC  CLIENTS.PATRONYMIC%type
,SEX  CLIENTS.SEX%type
,ADDRESS  CLIENTS.ADDRESS%type
,ID  CLIENTS.ID%type
,NAME  CLIENTS.NAME%type
);
type CLIENTS_tapi_tab is table of CLIENTS_tapi_rec;

-- insert
procedure ins (
p_SURNAME in CLIENTS.SURNAME%type
,p_PATRONYMIC in CLIENTS.PATRONYMIC%type default null 
,p_SEX in CLIENTS.SEX%type
,p_ADDRESS in CLIENTS.ADDRESS%type
,p_ID out CLIENTS.ID%type
,p_NAME in CLIENTS.NAME%type
,p_LOGIN in CLIENTS.LOGIN%type
,p_PASSWD in CLIENTS.PASSWD%type
,p_contact in CONTACTS.CONTACT%type
);
-- update
procedure upd (
p_SURNAME in CLIENTS.SURNAME%type
,p_PATRONYMIC in CLIENTS.PATRONYMIC%type default null 
,p_SEX in CLIENTS.SEX%type
,p_ADDRESS in CLIENTS.ADDRESS%type
,p_ID in CLIENTS.ID%type
,p_NAME in CLIENTS.NAME%type
,p_LOGIN in CLIENTS.LOGIN%type
,p_PASSWD in CLIENTS.PASSWD%type
);
-- delete
procedure del (
p_ID in CLIENTS.ID%type
);
end CLIENTS_tapi;

/
create or replace package body CLIENTS_tapi
is
-- insert
procedure ins (
p_SURNAME in CLIENTS.SURNAME%type
,p_PATRONYMIC in CLIENTS.PATRONYMIC%type default null 
,p_SEX in CLIENTS.SEX%type
,p_ADDRESS in CLIENTS.ADDRESS%type
,p_ID out CLIENTS.ID%type
,p_NAME in CLIENTS.NAME%type
,p_LOGIN in CLIENTS.LOGIN%type
,p_PASSWD in CLIENTS.PASSWD%type
,p_contact in CONTACTS.CONTACT%type
) is
begin
insert into CLIENTS(SURNAME,PATRONYMIC,SEX,ADDRESS,NAME,LOGIN,PASSWD) values (p_SURNAME, p_PATRONYMIC, p_SEX, p_ADDRESS, p_NAME, p_LOGIN, p_PASSWD)returning ID into p_ID;
insert into contacts(person_id, person_status, type, contact) values (p_ID,'client','phone',p_contact);
end;
-- update
procedure upd (
p_SURNAME in CLIENTS.SURNAME%type
,p_PATRONYMIC in CLIENTS.PATRONYMIC%type default null 
,p_SEX in CLIENTS.SEX%type
,p_ADDRESS in CLIENTS.ADDRESS%type
,p_ID in CLIENTS.ID%type
,p_NAME in CLIENTS.NAME%type
,p_LOGIN in CLIENTS.LOGIN%type
,p_PASSWD in CLIENTS.PASSWD%type
) is
begin
update CLIENTS set
SURNAME = p_SURNAME
,PATRONYMIC = p_PATRONYMIC
,SEX = p_SEX
,ADDRESS = p_ADDRESS
,NAME = p_NAME
,LOGIN = p_LOGIN
,PASSWD = p_PASSWD
where ID = p_ID;
end;
-- del
procedure del (
p_ID in CLIENTS.ID%type
) is
begin
delete from CLIENTS
where ID = p_ID;
end;
end CLIENTS_tapi;

-----------------------------------


