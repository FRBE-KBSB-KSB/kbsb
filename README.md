FRBE-KBSB
=========

This is the repository for the development of the website https://www.frbe-kbsb.be

Prerequisites
-------------

 * have a working installation of Python 3.6
 * have a working installation of Postgres 10 
 * have a working installation of node.js (>= v6.0) with yarn
 * on Windows have the Window subsystem for Linux installed (on Windows store choose Ubuntu)
 * have a working github account, with registered ssh keys for your development machine 
 
Setting up source
-----------------

 * open bash terminal and go to the the directory where you want to store the project
   (for Windows users, run the Ubuntu command, and the c: drive is available at /mnt/c )
 * run: ```git clone git@github.com:cropr/kbsb.git```
 * go to the kbsb directory: ```cd kbsb```
 * run the setup script: ```source setup```

Setting up backend (python)
--------------------------

 * create in Postgres a user and the kbsb database for that user
 * modify database parameters in the backend/local_settings.py file to match the created user 
 and password.
 * go to the backend directory
 * set the variable:  ```KBSB_ENV=dev``` 
 * run: ```python manage.py makemigrations```
 * run: ```python manage.py migrate```
 * run: ```python manage.py createsuperuser```

Setting up frontend (javascript)
--------------------------------
 * go to the frontend directory
 * run: ```yarn``` 

Running the app
---------------

 * in the frontend duirectory run: ```yarn run dev``` .  This will open a browser window with an error message but this 
 can be ignored
 * in the backend run: ```python manage.py runserver``` 
 * open a browser at http://localhost:8000

