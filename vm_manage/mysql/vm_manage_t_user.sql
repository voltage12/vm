create table t_department
(
	id int auto_increment
		primary key,
	name varchar(20) not null,
	constraint t_department_name_uindex
		unique (name)
)
;

create table t_permission
(
	id int auto_increment
		primary key,
	u_id int not null,
	d_id int not null,
	permission varchar(50) not null
)
;

create table t_staff
(
	id int auto_increment
		primary key,
	name varchar(20) not null,
	d_id int not null
)
;

create table t_user
(
	id int auto_increment
		primary key,
	username varchar(20) not null,
	password char(50) not null,
	constraint t_user_username_uindex
		unique (username)
)
;

create table t_vm
(
	id int auto_increment
		primary key,
	host_ip char(20) not null,
	name varchar(50) not null,
	d_id int not null,
	s_id int default '-1' not null
)
;


INSERT INTO vm_manage.t_user (username, password) VALUES ('root', 'e10adc3949ba59abbe56e057f20f883e');
