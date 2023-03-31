# DecisionApp

## Step 1 initial installations

cd into ../../..DecisionApp-backend %

    pip install -r requirements.txt

    pip install django-cors-headers

    cd MyApp

## Step 2 fix migrations

    python3 manage.py makemigrations

        //should see no changes

    python3 manage.py migrate
    
        //list of items with a green OK..

## Step 3 run server

    python manage.py runserver

#### OUTPUT:

    Watching for file changes with StatReloader
    Performing system checks...

    System check identified no issues (0 silenced).
    March 27, 2023 - 19:47:38
    Django version 3.2.2, using settings 'MyApp.settings'
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.

#### Server should be up and running
