CREATE DATABASE prueba1;

USE prueba1;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fname VARCHAR(50) NOT NULL,
    lastname VARCHAR(50),
    email VARCHAR(50) NOT NULL unique,
    password varchar(255) NOT NULL 
);

INSERT INTO usuarios (nombre, email) VALUES ('Juan','juan@mail.mx'), ('Ana', 'ana@mail.mx');

INSERT INTO users (fname, lastname, email, password) values ('Juan','Gomez','juan@gmail.com', '12345'), ('Ana','Cedillo','ana@mail.com', '12345');

SELECT * FROM users;

delete from users;

drop table users;

SET SQL_SAFE_UPDATES = 0;


ALTER TABLE usuarios
ADD lastname varchar(50) not null,
ADD password varchar(50) not null;

ALTER TABLE users
MODIFY email VARCHAR(50) NOT NULL UNIQUE,
MODIFY password VARCHAR(255) NOT NULL;

INSERT INTO usuarios (nombre, email) VALUES ('oscar','oscar@mail.mx');

-- contacto--
CREATE TABLE contacto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL,
    mensaje TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);