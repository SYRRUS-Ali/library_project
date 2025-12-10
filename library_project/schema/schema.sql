BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "auth_group" (
	"id"	integer NOT NULL,
	"name"	varchar(150) NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "auth_group_permissions" (
	"id"	integer NOT NULL,
	"group_id"	integer NOT NULL,
	"permission_id"	integer NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("group_id") REFERENCES "auth_group"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("permission_id") REFERENCES "auth_permission"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "auth_permission" (
	"id"	integer NOT NULL,
	"content_type_id"	integer NOT NULL,
	"codename"	varchar(100) NOT NULL,
	"name"	varchar(255) NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("content_type_id") REFERENCES "django_content_type"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "auth_user" (
	"id"	integer NOT NULL,
	"password"	varchar(128) NOT NULL,
	"last_login"	datetime,
	"is_superuser"	bool NOT NULL,
	"username"	varchar(150) NOT NULL UNIQUE,
	"last_name"	varchar(150) NOT NULL,
	"email"	varchar(254) NOT NULL,
	"is_staff"	bool NOT NULL,
	"is_active"	bool NOT NULL,
	"date_joined"	datetime NOT NULL,
	"first_name"	varchar(150) NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "auth_user_groups" (
	"id"	integer NOT NULL,
	"user_id"	integer NOT NULL,
	"group_id"	integer NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("group_id") REFERENCES "auth_group"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("user_id") REFERENCES "auth_user"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "auth_user_user_permissions" (
	"id"	integer NOT NULL,
	"user_id"	integer NOT NULL,
	"permission_id"	integer NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("permission_id") REFERENCES "auth_permission"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("user_id") REFERENCES "auth_user"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "django_admin_log" (
	"id"	integer NOT NULL,
	"object_id"	text,
	"object_repr"	varchar(200) NOT NULL,
	"action_flag"	smallint unsigned NOT NULL CHECK("action_flag" >= 0),
	"change_message"	text NOT NULL,
	"content_type_id"	integer,
	"user_id"	integer NOT NULL,
	"action_time"	datetime NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("content_type_id") REFERENCES "django_content_type"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("user_id") REFERENCES "auth_user"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "django_content_type" (
	"id"	integer NOT NULL,
	"app_label"	varchar(100) NOT NULL,
	"model"	varchar(100) NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "django_migrations" (
	"id"	integer NOT NULL,
	"app"	varchar(255) NOT NULL,
	"name"	varchar(255) NOT NULL,
	"applied"	datetime NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "django_session" (
	"session_key"	varchar(40) NOT NULL,
	"session_data"	text NOT NULL,
	"expire_date"	datetime NOT NULL,
	PRIMARY KEY("session_key")
);
CREATE TABLE IF NOT EXISTS "library_app_author" (
	"id"	integer NOT NULL,
	"last_name"	varchar(100) NOT NULL,
	"first_name"	varchar(100) NOT NULL,
	"middle_name"	varchar(100),
	"nickname"	varchar(100),
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "library_app_book" (
	"id"	integer NOT NULL,
	"title"	varchar(300) NOT NULL,
	"publication_year"	integer unsigned CHECK("publication_year" >= 0),
	"page_count"	integer unsigned NOT NULL CHECK("page_count" >= 0),
	"illustration_count"	integer unsigned NOT NULL CHECK("illustration_count" >= 0),
	"price"	decimal NOT NULL,
	"created_at"	datetime NOT NULL,
	"updated_at"	datetime NOT NULL,
	"publisher_id"	bigint,
	"isbn"	varchar(20),
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("publisher_id") REFERENCES "library_app_publisher"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "library_app_book_authors" (
	"id"	integer NOT NULL,
	"book_id"	bigint NOT NULL,
	"author_id"	bigint NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("author_id") REFERENCES "library_app_author"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("book_id") REFERENCES "library_app_book"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "library_app_bookfacultyusage" (
	"id"	integer NOT NULL,
	"created_at"	datetime NOT NULL,
	"book_id"	bigint NOT NULL,
	"branch_id"	bigint NOT NULL,
	"faculty_id"	bigint NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("book_id") REFERENCES "library_app_book"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("branch_id") REFERENCES "library_app_branch"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("faculty_id") REFERENCES "library_app_faculty"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "library_app_bookinventory" (
	"id"	integer NOT NULL,
	"total_copies"	integer unsigned NOT NULL CHECK("total_copies" >= 0),
	"available_copies"	integer unsigned NOT NULL CHECK("available_copies" >= 0),
	"last_updated"	datetime NOT NULL,
	"book_id"	bigint NOT NULL,
	"branch_id"	bigint NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("book_id") REFERENCES "library_app_book"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("branch_id") REFERENCES "library_app_branch"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "library_app_branch" (
	"id"	integer NOT NULL,
	"name"	varchar(200) NOT NULL UNIQUE,
	"address"	text,
	"created_at"	datetime NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "library_app_faculty" (
	"id"	integer NOT NULL,
	"name"	varchar(200) NOT NULL UNIQUE,
	"description"	text,
	"created_at"	datetime NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "library_app_loan" (
	"id"	integer NOT NULL,
	"issue_date"	datetime NOT NULL,
	"return_date"	datetime,
	"is_returned"	bool NOT NULL,
	"book_id"	bigint NOT NULL,
	"branch_id"	bigint NOT NULL,
	"created_by_id"	integer,
	"student_id"	bigint NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("book_id") REFERENCES "library_app_book"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("branch_id") REFERENCES "library_app_branch"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("created_by_id") REFERENCES "auth_user"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("student_id") REFERENCES "library_app_student"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "library_app_publisher" (
	"id"	integer NOT NULL,
	"name"	varchar(200) NOT NULL UNIQUE,
	"address"	text,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "library_app_readingroom" (
	"id"	integer NOT NULL,
	"name"	varchar(200) NOT NULL,
	"capacity"	integer unsigned NOT NULL CHECK("capacity" >= 0),
	"has_computers"	bool NOT NULL,
	"opening_time"	time NOT NULL,
	"closing_time"	time NOT NULL,
	"is_active"	bool NOT NULL,
	"created_at"	datetime NOT NULL,
	"branch_id"	bigint NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("branch_id") REFERENCES "library_app_branch"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "library_app_student" (
	"id"	integer NOT NULL,
	"last_name"	varchar(100) NOT NULL,
	"first_name"	varchar(100) NOT NULL,
	"student_id"	varchar(20) NOT NULL UNIQUE,
	"created_at"	datetime NOT NULL,
	"faculty_id"	bigint NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("faculty_id") REFERENCES "library_app_faculty"("id") DEFERRABLE INITIALLY DEFERRED
);
INSERT INTO "auth_permission" VALUES (1,1,'add_logentry','Can add log entry');
INSERT INTO "auth_permission" VALUES (2,1,'change_logentry','Can change log entry');
INSERT INTO "auth_permission" VALUES (3,1,'delete_logentry','Can delete log entry');
INSERT INTO "auth_permission" VALUES (4,1,'view_logentry','Can view log entry');
INSERT INTO "auth_permission" VALUES (5,2,'add_permission','Can add permission');
INSERT INTO "auth_permission" VALUES (6,2,'change_permission','Can change permission');
INSERT INTO "auth_permission" VALUES (7,2,'delete_permission','Can delete permission');
INSERT INTO "auth_permission" VALUES (8,2,'view_permission','Can view permission');
INSERT INTO "auth_permission" VALUES (9,3,'add_group','Can add group');
INSERT INTO "auth_permission" VALUES (10,3,'change_group','Can change group');
INSERT INTO "auth_permission" VALUES (11,3,'delete_group','Can delete group');
INSERT INTO "auth_permission" VALUES (12,3,'view_group','Can view group');
INSERT INTO "auth_permission" VALUES (13,4,'add_user','Can add user');
INSERT INTO "auth_permission" VALUES (14,4,'change_user','Can change user');
INSERT INTO "auth_permission" VALUES (15,4,'delete_user','Can delete user');
INSERT INTO "auth_permission" VALUES (16,4,'view_user','Can view user');
INSERT INTO "auth_permission" VALUES (17,5,'add_contenttype','Can add content type');
INSERT INTO "auth_permission" VALUES (18,5,'change_contenttype','Can change content type');
INSERT INTO "auth_permission" VALUES (19,5,'delete_contenttype','Can delete content type');
INSERT INTO "auth_permission" VALUES (20,5,'view_contenttype','Can view content type');
INSERT INTO "auth_permission" VALUES (21,6,'add_session','Can add session');
INSERT INTO "auth_permission" VALUES (22,6,'change_session','Can change session');
INSERT INTO "auth_permission" VALUES (23,6,'delete_session','Can delete session');
INSERT INTO "auth_permission" VALUES (24,6,'view_session','Can view session');
INSERT INTO "auth_permission" VALUES (25,7,'add_author','Can add автор');
INSERT INTO "auth_permission" VALUES (26,7,'change_author','Can change автор');
INSERT INTO "auth_permission" VALUES (27,7,'delete_author','Can delete автор');
INSERT INTO "auth_permission" VALUES (28,7,'view_author','Can view автор');
INSERT INTO "auth_permission" VALUES (29,8,'add_book','Can add книга');
INSERT INTO "auth_permission" VALUES (30,8,'change_book','Can change книга');
INSERT INTO "auth_permission" VALUES (31,8,'delete_book','Can delete книга');
INSERT INTO "auth_permission" VALUES (32,8,'view_book','Can view книга');
INSERT INTO "auth_permission" VALUES (33,9,'add_branch','Can add филиал');
INSERT INTO "auth_permission" VALUES (34,9,'change_branch','Can change филиал');
INSERT INTO "auth_permission" VALUES (35,9,'delete_branch','Can delete филиал');
INSERT INTO "auth_permission" VALUES (36,9,'view_branch','Can view филиал');
INSERT INTO "auth_permission" VALUES (37,10,'add_faculty','Can add факультет');
INSERT INTO "auth_permission" VALUES (38,10,'change_faculty','Can change факультет');
INSERT INTO "auth_permission" VALUES (39,10,'delete_faculty','Can delete факультет');
INSERT INTO "auth_permission" VALUES (40,10,'view_faculty','Can view факультет');
INSERT INTO "auth_permission" VALUES (41,11,'add_publisher','Can add издательство');
INSERT INTO "auth_permission" VALUES (42,11,'change_publisher','Can change издательство');
INSERT INTO "auth_permission" VALUES (43,11,'delete_publisher','Can delete издательство');
INSERT INTO "auth_permission" VALUES (44,11,'view_publisher','Can view издательство');
INSERT INTO "auth_permission" VALUES (45,12,'add_student','Can add студент');
INSERT INTO "auth_permission" VALUES (46,12,'change_student','Can change студент');
INSERT INTO "auth_permission" VALUES (47,12,'delete_student','Can delete студент');
INSERT INTO "auth_permission" VALUES (48,12,'view_student','Can view студент');
INSERT INTO "auth_permission" VALUES (49,13,'add_loan','Can add выдача');
INSERT INTO "auth_permission" VALUES (50,13,'change_loan','Can change выдача');
INSERT INTO "auth_permission" VALUES (51,13,'delete_loan','Can delete выдача');
INSERT INTO "auth_permission" VALUES (52,13,'view_loan','Can view выдача');
INSERT INTO "auth_permission" VALUES (53,14,'add_bookinventory','Can add инвентаризация');
INSERT INTO "auth_permission" VALUES (54,14,'change_bookinventory','Can change инвентаризация');
INSERT INTO "auth_permission" VALUES (55,14,'delete_bookinventory','Can delete инвентаризация');
INSERT INTO "auth_permission" VALUES (56,14,'view_bookinventory','Can view инвентаризация');
INSERT INTO "auth_permission" VALUES (57,15,'add_bookfacultyusage','Can add использование книги факультетом');
INSERT INTO "auth_permission" VALUES (58,15,'change_bookfacultyusage','Can change использование книги факультетом');
INSERT INTO "auth_permission" VALUES (59,15,'delete_bookfacultyusage','Can delete использование книги факультетом');
INSERT INTO "auth_permission" VALUES (60,15,'view_bookfacultyusage','Can view использование книги факультетом');
INSERT INTO "auth_permission" VALUES (61,16,'add_readingroom','Can add читальный зал');
INSERT INTO "auth_permission" VALUES (62,16,'change_readingroom','Can change читальный зал');
INSERT INTO "auth_permission" VALUES (63,16,'delete_readingroom','Can delete читальный зал');
INSERT INTO "auth_permission" VALUES (64,16,'view_readingroom','Can view читальный зал');
INSERT INTO "auth_user" VALUES (1,'pbkdf2_sha256$600000$y0AR83FlETjesv9M10d8aZ$qoHJ24M50/cppTSrJlAsDdHqSDvy+EG5CCrMpuhkcCU=','2025-12-10 18:37:53.513313',1,'admin','','',1,1,'2025-09-26 12:43:39.521917','');
INSERT INTO "django_admin_log" VALUES (1,'1','FIT',1,'[{"added": {}}]',10,1,'2025-09-26 13:20:28.492943');
INSERT INTO "django_admin_log" VALUES (2,'1','Mehrez Mohammad (St215145)',1,'[{"added": {}}]',12,1,'2025-09-26 13:20:30.716406');
INSERT INTO "django_admin_log" VALUES (3,'1','The heart of the sea в F1: 2/2',1,'[{"added": {}}]',14,1,'2025-09-26 13:58:38.711245');
INSERT INTO "django_content_type" VALUES (1,'admin','logentry');
INSERT INTO "django_content_type" VALUES (2,'auth','permission');
INSERT INTO "django_content_type" VALUES (3,'auth','group');
INSERT INTO "django_content_type" VALUES (4,'auth','user');
INSERT INTO "django_content_type" VALUES (5,'contenttypes','contenttype');
INSERT INTO "django_content_type" VALUES (6,'sessions','session');
INSERT INTO "django_content_type" VALUES (7,'library_app','author');
INSERT INTO "django_content_type" VALUES (8,'library_app','book');
INSERT INTO "django_content_type" VALUES (9,'library_app','branch');
INSERT INTO "django_content_type" VALUES (10,'library_app','faculty');
INSERT INTO "django_content_type" VALUES (11,'library_app','publisher');
INSERT INTO "django_content_type" VALUES (12,'library_app','student');
INSERT INTO "django_content_type" VALUES (13,'library_app','loan');
INSERT INTO "django_content_type" VALUES (14,'library_app','bookinventory');
INSERT INTO "django_content_type" VALUES (15,'library_app','bookfacultyusage');
INSERT INTO "django_content_type" VALUES (16,'library_app','readingroom');
INSERT INTO "django_migrations" VALUES (1,'contenttypes','0001_initial','2025-09-26 12:42:40.961537');
INSERT INTO "django_migrations" VALUES (2,'auth','0001_initial','2025-09-26 12:42:40.980831');
INSERT INTO "django_migrations" VALUES (3,'admin','0001_initial','2025-09-26 12:42:40.996407');
INSERT INTO "django_migrations" VALUES (4,'admin','0002_logentry_remove_auto_add','2025-09-26 12:42:41.008271');
INSERT INTO "django_migrations" VALUES (5,'admin','0003_logentry_add_action_flag_choices','2025-09-26 12:42:41.017797');
INSERT INTO "django_migrations" VALUES (6,'contenttypes','0002_remove_content_type_name','2025-09-26 12:42:41.031941');
INSERT INTO "django_migrations" VALUES (7,'auth','0002_alter_permission_name_max_length','2025-09-26 12:42:41.042811');
INSERT INTO "django_migrations" VALUES (8,'auth','0003_alter_user_email_max_length','2025-09-26 12:42:41.054284');
INSERT INTO "django_migrations" VALUES (9,'auth','0004_alter_user_username_opts','2025-09-26 12:42:41.062770');
INSERT INTO "django_migrations" VALUES (10,'auth','0005_alter_user_last_login_null','2025-09-26 12:42:41.068711');
INSERT INTO "django_migrations" VALUES (11,'auth','0006_require_contenttypes_0002','2025-09-26 12:42:41.077790');
INSERT INTO "django_migrations" VALUES (12,'auth','0007_alter_validators_add_error_messages','2025-09-26 12:42:41.086401');
INSERT INTO "django_migrations" VALUES (13,'auth','0008_alter_user_username_max_length','2025-09-26 12:42:41.098148');
INSERT INTO "django_migrations" VALUES (14,'auth','0009_alter_user_last_name_max_length','2025-09-26 12:42:41.108060');
INSERT INTO "django_migrations" VALUES (15,'auth','0010_alter_group_name_max_length','2025-09-26 12:42:41.119250');
INSERT INTO "django_migrations" VALUES (16,'auth','0011_update_proxy_permissions','2025-09-26 12:42:41.123784');
INSERT INTO "django_migrations" VALUES (17,'auth','0012_alter_user_first_name_max_length','2025-09-26 12:42:41.135500');
INSERT INTO "django_migrations" VALUES (18,'sessions','0001_initial','2025-09-26 12:42:41.147963');
INSERT INTO "django_migrations" VALUES (19,'library_app','0001_initial','2025-09-26 12:43:06.418234');
INSERT INTO "django_migrations" VALUES (20,'library_app','0002_book_isbn','2025-12-10 18:10:58.337977');
INSERT INTO "django_migrations" VALUES (21,'library_app','0003_remove_book_isbn_book_description','2025-12-10 18:10:58.349924');
INSERT INTO "django_migrations" VALUES (22,'library_app','0004_add_readingroom','2025-12-10 18:47:37.384242');
INSERT INTO "django_migrations" VALUES (23,'library_app','0005_remove_book_description_author_nickname_book_isbn_and_more','2025-12-10 18:54:44.828747');
INSERT INTO "django_session" VALUES ('inugwyj1g0gt6huhwind2s0usrqsakyz','.eJxVjE0OwiAYBe_C2hD4wAIu3XsG8viTqqFJaVfGu9smXej2zcx7M491qX7tefZjYhcm2el3C4jP3HaQHmj3icepLfMY-K7wg3Z-m1J-XQ_376Ci161GKcJREAZKU1LIDnJQxSJCumAsGRU12azlWQ2FkgW0IEebLawrYJ8v4_03ZA:1v291P:A4c9TGFoQSDrowGi3qbGwAR3SRFMWtiq8hLryFTN8ms','2025-10-10 14:02:03.973901');
INSERT INTO "django_session" VALUES ('3t9mvhnfmpsw0pifk00w26gk0dbg2nuk','.eJxVjE0OwiAYBe_C2hD4wAIu3XsG8viTqqFJaVfGu9smXej2zcx7M491qX7tefZjYhcm2el3C4jP3HaQHmj3icepLfMY-K7wg3Z-m1J-XQ_376Ci161GKcJREAZKU1LIDnJQxSJCumAsGRU12azlWQ2FkgW0IEebLawrYJ8v4_03ZA:1vTP4T:E9JYS-Aj3fYKpS9dOJoFfoDcbyi7tQ5Lmd7tXqgwIGw','2025-12-24 18:37:53.522311');
INSERT INTO "library_app_author" VALUES (2,'Alfredo','Mark',NULL,NULL);
INSERT INTO "library_app_book" VALUES (1,'The heart of the sea',1987,550,100,1300,'2025-09-26 13:46:17.059894','2025-09-26 13:46:53.599327',1,NULL);
INSERT INTO "library_app_book_authors" VALUES (1,1,2);
INSERT INTO "library_app_bookinventory" VALUES (1,4,3,'2025-09-26 14:02:03.945269',1,1);
INSERT INTO "library_app_branch" VALUES (1,'F1','','2025-09-26 13:48:17.634888');
INSERT INTO "library_app_faculty" VALUES (1,'FIT','','2025-09-26 13:20:28.490946');
INSERT INTO "library_app_publisher" VALUES (1,'publisher test','');
INSERT INTO "library_app_student" VALUES (1,'Mehrez','Mohammad','St215145','2025-09-26 13:20:30.714357',1);
CREATE INDEX IF NOT EXISTS "auth_group_permissions_group_id_b120cbf9" ON "auth_group_permissions" (
	"group_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" ON "auth_group_permissions" (
	"group_id",
	"permission_id"
);
CREATE INDEX IF NOT EXISTS "auth_group_permissions_permission_id_84c5c92e" ON "auth_group_permissions" (
	"permission_id"
);
CREATE INDEX IF NOT EXISTS "auth_permission_content_type_id_2f476e4b" ON "auth_permission" (
	"content_type_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "auth_permission_content_type_id_codename_01ab375a_uniq" ON "auth_permission" (
	"content_type_id",
	"codename"
);
CREATE INDEX IF NOT EXISTS "auth_user_groups_group_id_97559544" ON "auth_user_groups" (
	"group_id"
);
CREATE INDEX IF NOT EXISTS "auth_user_groups_user_id_6a12ed8b" ON "auth_user_groups" (
	"user_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "auth_user_groups_user_id_group_id_94350c0c_uniq" ON "auth_user_groups" (
	"user_id",
	"group_id"
);
CREATE INDEX IF NOT EXISTS "auth_user_user_permissions_permission_id_1fbb5f2c" ON "auth_user_user_permissions" (
	"permission_id"
);
CREATE INDEX IF NOT EXISTS "auth_user_user_permissions_user_id_a95ead1b" ON "auth_user_user_permissions" (
	"user_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "auth_user_user_permissions_user_id_permission_id_14a6b632_uniq" ON "auth_user_user_permissions" (
	"user_id",
	"permission_id"
);
CREATE INDEX IF NOT EXISTS "django_admin_log_content_type_id_c4bce8eb" ON "django_admin_log" (
	"content_type_id"
);
CREATE INDEX IF NOT EXISTS "django_admin_log_user_id_c564eba6" ON "django_admin_log" (
	"user_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "django_content_type_app_label_model_76bd3d3b_uniq" ON "django_content_type" (
	"app_label",
	"model"
);
CREATE INDEX IF NOT EXISTS "django_session_expire_date_a5c62663" ON "django_session" (
	"expire_date"
);
CREATE UNIQUE INDEX IF NOT EXISTS "library_app_author_last_name_first_name_middle_name_83e9f1b8_uniq" ON "library_app_author" (
	"last_name",
	"first_name",
	"middle_name"
);
CREATE INDEX IF NOT EXISTS "library_app_book_authors_author_id_b9065aec" ON "library_app_book_authors" (
	"author_id"
);
CREATE INDEX IF NOT EXISTS "library_app_book_authors_book_id_882939bb" ON "library_app_book_authors" (
	"book_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "library_app_book_authors_book_id_author_id_207d38e6_uniq" ON "library_app_book_authors" (
	"book_id",
	"author_id"
);
CREATE INDEX IF NOT EXISTS "library_app_book_publisher_id_140c2820" ON "library_app_book" (
	"publisher_id"
);
CREATE INDEX IF NOT EXISTS "library_app_bookfacultyusage_book_id_1ee85f8f" ON "library_app_bookfacultyusage" (
	"book_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "library_app_bookfacultyusage_book_id_branch_id_faculty_id_ee807929_uniq" ON "library_app_bookfacultyusage" (
	"book_id",
	"branch_id",
	"faculty_id"
);
CREATE INDEX IF NOT EXISTS "library_app_bookfacultyusage_branch_id_e34de4ab" ON "library_app_bookfacultyusage" (
	"branch_id"
);
CREATE INDEX IF NOT EXISTS "library_app_bookfacultyusage_faculty_id_687f66c5" ON "library_app_bookfacultyusage" (
	"faculty_id"
);
CREATE INDEX IF NOT EXISTS "library_app_bookinventory_book_id_2fb41e12" ON "library_app_bookinventory" (
	"book_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "library_app_bookinventory_book_id_branch_id_83e07e5f_uniq" ON "library_app_bookinventory" (
	"book_id",
	"branch_id"
);
CREATE INDEX IF NOT EXISTS "library_app_bookinventory_branch_id_6319b50f" ON "library_app_bookinventory" (
	"branch_id"
);
CREATE INDEX IF NOT EXISTS "library_app_is_retu_f295fe_idx" ON "library_app_loan" (
	"is_returned"
);
CREATE INDEX IF NOT EXISTS "library_app_issue_d_ab8064_idx" ON "library_app_loan" (
	"issue_date"
);
CREATE INDEX IF NOT EXISTS "library_app_last_na_e17743_idx" ON "library_app_student" (
	"last_name",
	"first_name"
);
CREATE INDEX IF NOT EXISTS "library_app_loan_book_id_c1c7caae" ON "library_app_loan" (
	"book_id"
);
CREATE INDEX IF NOT EXISTS "library_app_loan_branch_id_e84bee9a" ON "library_app_loan" (
	"branch_id"
);
CREATE INDEX IF NOT EXISTS "library_app_loan_created_by_id_740bc4d8" ON "library_app_loan" (
	"created_by_id"
);
CREATE INDEX IF NOT EXISTS "library_app_loan_student_id_f91b666e" ON "library_app_loan" (
	"student_id"
);
CREATE INDEX IF NOT EXISTS "library_app_publica_a46121_idx" ON "library_app_book" (
	"publication_year"
);
CREATE INDEX IF NOT EXISTS "library_app_readingroom_branch_id_c52dc1da" ON "library_app_readingroom" (
	"branch_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "library_app_readingroom_name_branch_id_91358927_uniq" ON "library_app_readingroom" (
	"name",
	"branch_id"
);
CREATE INDEX IF NOT EXISTS "library_app_student_447a47_idx" ON "library_app_student" (
	"student_id"
);
CREATE INDEX IF NOT EXISTS "library_app_student_faculty_id_c3f659cd" ON "library_app_student" (
	"faculty_id"
);
CREATE INDEX IF NOT EXISTS "library_app_title_ec677d_idx" ON "library_app_book" (
	"title"
);
COMMIT;
