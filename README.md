
#### 1 Purpose
I've had the Fitbit Aria 2 Smart Scale for a few years now, and I've always felt the stock charts looked good, but were not showing me what I wanted to see.
So in this project I: 
* create Charts that show the data in the way I want 
* can download the data into Excel

#### 2 Setup

##### 2.1 Register your App
First you will need to register a new app on the fitbit website: https://dev.fitbit.com/apps/new

I found the folowing article really helpful in setting up the initial connection if you are having difficulties:  https://towardsdatascience.com/collect-your-own-fitbit-data-with-python-ff145fa10873

##### 2.2 Prerequisites
There are a couple of non-standard libraries you'll need to install if you don't already have them installed on your current instance.
You can find further details on gather_keys_oauth2.py here: https://raw.githubusercontent.com/orcasgit/python-fitbit/

```python
!pip install fitbit
!pip install wget

#there's no pip for gather_keys_oauth2.. but we can download from the github user
url = 'https://raw.githubusercontent.com/orcasgit/python-fitbit/master/gather_keys_oauth2.py'
wget.download(url,'<install path>/gather_keys_oauth2.py')

#gather_keys_oauth2 needs cherrypy.. so we install that
!pip install cherrypy
```

##### 2.3 Create settings file
In your project root folder you will need to create a file called 'settings' with the folowing string:
```
{'client_id': 'client if from step 1', 'client_secret': 'client secret from steop 1', 'initialdate': '2017-09-20'}
```

The initialdate can be whatever date you want to start your data analysis or download from.  Note, the data clensing process interpolates missing data, so you might want to pick a date to start your download from that is after any long stretches of missing data.

#### 3 Files in this Github page

##### 3.1 ![fitbit_aria_analysis.ipynb](fitbit_aria_analysis.ipynb)
This is my initial notebook I created, it walks thru all of the connection code, data cleaning logic, different options for viewing and analysing the data etc.

##### 3.2 ![dashboard.ipynb](dashboard.ipynb)
This is the notebook I created that just shows the charts I want to see and allows me to download the data in Excel.  It hides alot of the code in two .py files (refresh.py, calcs.py)

###### 3.2.1 ![refresh.py](refresh.py)
Contains all of the connection/data cleaning code from the notebook in section 3.1

###### 3.2.2 ![calcs.py](calcs.py)
Contains the calculations specific to the analysis and charts that I want to see in section 3.2


