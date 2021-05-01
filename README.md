# press-graphs
Press analytics Flask based API and Flask-Dash based GUI

# Data and ETL process
Pressgraphs relyes on a remote mysql database which is updated every day by a bot.
This repository consists only of the API and GUI part of the application. The Database and the ETP process are to be described in another repository (#todo)

# Architecture
 Pressgraphs implements an [Model View Control (MVC)](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller) Architecture with its main components; 
 * Remote Database (not included and not described in this repository)
 * WebAPI 
 * WebGUI 
Both the API and GUI use Flask, however the GUI uses Dash GUI extension on top of the Flask environment.

### WebAPI 
The API is a RESTful Flask based application. 
Currently it is hosted on [PythonAnywhere](https://www.pythonanywhere.com/)

#### Description of Endpoints:

#### REGISTER
You can register your own API key here:

> http://pressgraphs.pythonanywhere.com/create/{user}  
> example: http://pressgraphs.pythonanywhere.com/create/test_user

#### RETURN LIST

> Pattern:  
> http://pressgraphs.pythonanywhere.com/date/list/{api_key}/{search_word}/{switch_value}/{start_date}/{end_date}/{site} 

> *parameter variations*:
> * **fix date (start_date=end_date) & fix site**  
    exapmle:  
    http://pressgraphs.pythonanywhere.com/date/list/API-KEY/korona/1/2020-03-31/2020-03-31/hvg  
    
> * ***fix date (start_date=end_date) & all site (site="all")**  
    example:  
    http://pressgraphs.pythonanywhere.com/date/list/API-KEY/korona/1/2020-03-31/2020-03-31/all
    
> * **date interval & fix site**  
    example:  
    http://pressgraphs.pythonanywhere.com/date/list/API-KEY/korona/1/2020-08-31/2020-10-03/origo
    
> * **date interval & all site (site="all")**  
    example:  
    http://pressgraphs.pythonanywhere.com/date/list/API-KEY/korona/1/2020-08-31/2020-10-03/all
    

#### RETURN COUNT
> http://pressgraphs.pythonanywhere.com/date/count/{api_key}/{search_word}/{switch_value}/{start_date}/{end_date}/{site}  

> *parameter variations*:
> * **fix date (start_date=end_date) & fix site**  
    example:  
    http://pressgraphs.pythonanywhere.com/date/count/API-KEY/korona/1/2020-05-31/2020-05-31/hvg
    
> * **fix date (start_date=end_date) & all site**  
    example:  
    http://pressgraphs.pythonanywhere.com/date/count/API-KEY/korona/1/2020-05-31/2020-05-31/all
    
> * **date interval & fix site**  
    example:  
    http://pressgraphs.pythonanywhere.com/date/count/API-KEY/korona/1/2020-10-01/2020-10-15/hvg
    
> * **date interval & all site (site="all")**  
    example:  
    http://pressgraphs.pythonanywhere.com/date/count/API-KEY/korona/1/2020-10-01/2020-10-15/all
    

#### INFO
> * **available sites**  
> http://pressgraphs.pythonanywhere.com/{api_key}/info/sites/all  
  example:  
  http://pressgraphs.pythonanywhere.com/API-KEY/info/sites/all

> * **first date available**  
> http://pressgraphs.pythonanywhere.com/{api_key}/info/dates/first  
  example:  
  http://pressgraphs.pythonanywhere.com/API-KEY/info/dates/first


> * **last date available**  
> http://pressgraphs.pythonanywhere.com/{api_key}/info/dates/last  
  example:  
  http://pressgraphs.pythonanywhere.com/API-KEY/info/dates/last  
    
> * **does the site exist in the database?**  
> http://pressgraphs.pythonanywhere.com/{api_key}/info/sites/exists/{site}  
  example:  
  http://pressgraphs.pythonanywhere.com/API-KEY/info/sites/exists/index  

### WebGUI 

The web application is hosted on [heroku.com](https://www.heroku.com/):  
http://pressgraphs.herokuapp.com/  
(Please be patient, the app might be running on a free tier heroku dyno so it eventually requires a few sec until it boots up..)

For source code click [here](https://github.com/xngst/press-graphs/tree/main/GUI%20src)  
The app needed a few CSS tweaks, the custom.css file is included in the assets directory.

The GUI itself is based on [Dash](https://dash.plotly.com/installation)  
Dash is a productive Python framework for building web analytic applications.
Written on top of Flask, Plotly.js, and React.js, Dash is ideal for building data visualization apps with highly custom user interfaces in pure Python. It's particularly suited for anyone who works with data in Python.
Through a couple of simple patterns, Dash abstracts away all of the technologies and protocols that are required to build an interactive web-based application. Dash is simple enough that you can bind a user interface around your Python code in an afternoon.
Dash apps are rendered in the web browser. You can deploy your apps to servers and then share them through URLs. Since Dash apps are viewed in the web browser, Dash is inherently cross-platform and mobile ready.
