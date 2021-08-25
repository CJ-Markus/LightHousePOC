# LightHouse POC
This repo is to keep LH initiative alive. Since all our customers like to measure, gather and compare performance numbers and different UI metrics, using LH tool, I decided it will be useful to have some kind of POC. There are no any packages in this PR or fancy code. One thing that changes is python script, where you can:
* add/remove sites you want to test. Change following section in script
``` 
if __name__ == "__main__":
    main(["https://cowab.se", "https://cowab.no"])  //here you can add or remove test sites
    
```  
    
* run with or without headless mode
* use different options to start test with throatling, or emulate mobile device
```
  for url in urls:
        print(f"__________________________")
        print(f"Collecting stats for {url}")
        p = Popen(
            f"lighthouse {url} --output json --chrome-flags=--headless",  //that is how you start light house. More options are available, just google
            shell=True,
            stdout=PIPE,
            stderr=PIPE
        )
```
 
 //Here we define metrics that we collect, based on generated json files.

```
        stdout, stderr = p.communicate()
        report = json.loads(stdout.decode("UTF-8"))

        categories = report["categories"]
        performance = categories["performance"]["score"]
        accessibility = categories["accessibility"]["score"]
        bestPractices=categories["best-practices"]["score"]
        seo = categories["seo"]["score"]
        pwa = categories["pwa"]["score"]
        .....
```

 //Here we split URL into 2 parts and throw away everything with "htttps://" just to display url in a more readable way: cowab.se, instead of https://cowab.se
       
```
               site = url.split("://")[-1]
```

//Here we print out to console for visibility

```
        print(f"Site: {site}")
        print(f"performance: {performance}")
        print(f"accessibility: {accessibility}")
        print(f"bestPractices: {bestPractices}")
        print(f"seo: {seo}")
        print(f"pwa: {pwa}")
        .....
 ```       
        
//Linking metric names and metric values together
```
      metrics={
            "performance": performance,
            "accessibility": accessibility,
            "bestPractices": bestPractices,
            "seo":seo,
            "pwa":pwa,
            "firstContentfulPaint":firstContentfulPaint,
            "largestContentfulPaint":largestContentfulPaint,
            "speedIndex":speedIndex,
            "estimatedInputLatency":estimatedInputLatency,
            ......
            "totalByteWeight":totalByteWeight,
            "totalTaskTime":totalTaskTime
        }
 ```
        
       
  //Inserting values into Data Base       
 ```
       for name, value in metrics.items():
            cursor.execute(
                f"INSERT INTO mysql.lh_reports_1 (site, metric_name, metric_value)"
                f"VALUES ('{site}', '{name}', {value})"
            )
        cursor.execute("COMMIT")

```  
    

To make it complex and fancy, build it into continues integration. Just read instructions here: https://github.com/GoogleChrome/lighthouse-ci/blob/main/docs/getting-started.md

I decided to keep it simple for a POC and created instructions on how to run it locally. Same steps may be done on a remote server with shared environment


# Prerequesits
1. Docker
2. DB, I used MySQL
3. Python
4. Graphana
5. LightHouse

# How to run 
Easy to run on MAC, may take some time to fix issues on Windows. Just be carefull if you are using UNIX clients on Windows. Better to use CMD command line


0) Install Lighthouse:

```
npm i -g lighthouse
```

1) Using Docker, create LightHouse network. It will include local DB, local Graphana.

```
docker network create lh-network
```

2) Create data base. Specify user, password and port. In our case that is: root, password, 3306

```
docker run --network lh-network --name lh-mysql -v /Users/innale/Workspaces/lighthouse/mysql_store:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=password -d -p 3306:3306 mysql:latest
```

3) Run DB.

```
docker run -it --network lh-network --rm mysql mysql -hlh-mysql -uroot -ppassword
```

4) Create table to store results 

```
create table mysql.lh_reports_1 (time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, site VARCHAR(255) NOT NULL, metric_name VARCHAR(255) NOT NULL, metric_value FLOAT NOT NULL);
```

5) Just try to insert smth to newly created table


```
insert into mysql.lh_reports (site, metric_name, metric_value) VALUES ('google.com', performance, 0.12); 
```


6) Run graphana

```
docker run --network lh-network --name grafana -d -p 3000:3000 grafana/grafana
```

To open graphana locally: http://localhost:3000/d/yfcBDAinz/site-reports?orgId=1 
Use admin/admin as a login and password


7) Now true fun begins. LH can generate HTML or/and json file with the results. I have created python script to get results from json file.
In this script I gathered different FE and BE metrics. Not all of them, but if needed, we can always add more 

8) To run this script you need to install python. Then just type in a CLI: 
```
python report.py
```

Script will print out all gathered metrics and add them to DB

![image](https://user-images.githubusercontent.com/54897268/125449877-28f545b8-70b2-44cc-9a5b-06ba5a39e7a0.png)

Then in Graphana you can create dashboard with reports and have historical data
![image](https://user-images.githubusercontent.com/54897268/125450027-a4571ca1-b6c0-441c-bc11-7850cbe75052.png)

# Examples for graphana SQL:
1) To get table view for BE metrics per site, last not null:


```
SELECT
  distinct site as s,
  (select metric_value from mysql.lh_reports_1 m where m.site=s and metric_name='totalBlockingTime' order by time desc limit 1) as "totalBlockingTime",
  (select metric_value from mysql.lh_reports_1 m where m.site=s and metric_name='maxRtt' order by time desc limit 1) as "Max RTT",
  (select metric_value from mysql.lh_reports_1 m where m.site=s and metric_name='estimatedInputLatency' order by time desc limit 1) as "estimatedInputLatency",
  (select metric_value from mysql.lh_reports_1 m where m.site=s and metric_name='serverResponseTime' order by time desc limit 1) as "serverResponseTime",
  (select metric_value from mysql.lh_reports_1 m where m.site=s and metric_name='numRequests' order by time desc limit 1) as "numRequests",
  (select metric_value from mysql.lh_reports_1 m where m.site=s and metric_name='numScripts' order by time desc limit 1) as "numScripts",
  (select metric_value from mysql.lh_reports_1 m where m.site=s and metric_name='numTasksOver10ms' order by time desc limit 1) as "numTasksOver10ms",
  (select metric_value from mysql.lh_reports_1 m where m.site=s and metric_name='numTasksOver25ms' order by time desc limit 1) as "numTasksOver25ms",
  (select metric_value from mysql.lh_reports_1 m where m.site=s and metric_name='numTasksOver50ms' order by time desc limit 1) as "numTasksOver50ms",
  (select metric_value from mysql.lh_reports_1 m where m.site=s and metric_name='numTasksOver100ms' order by time desc limit 1) as "numTasksOver100ms",
  (select metric_value from mysql.lh_reports_1 m where m.site=s and metric_name='numTasksOver500ms' order by time desc limit 1) as "numTasksOver500ms",
  (select metric_value from mysql.lh_reports_1 m where m.site=s and metric_name='maxServerLatency' order by time desc limit 1) as "maxServerLatency"
FROM mysql.lh_reports_1
order by site
```

![image](https://user-images.githubusercontent.com/54897268/125470674-c49751f8-68ef-4817-9986-ac1ea93eda4e.png)


2) To display historical data per metric:
```
SELECT
  time AS "time",
  site AS metric,
  metric_value/1000  // almost all results are in mseconds. To display seconds we have to divide by 1000
FROM mysql.lh_reports_1
where metric_name="speedIndex"
ORDER BY time
```
![image](https://user-images.githubusercontent.com/54897268/125469684-e3179bc0-949f-4850-8498-e7cb44028cbb.png)

![image](https://user-images.githubusercontent.com/54897268/125470898-3c7312e1-b404-4305-b227-441988189f8c.png)

# Another way to display all these graphs in Graphana is to import configuration json file
Open settings in the Graphana Dashboard
![image](https://user-images.githubusercontent.com/54897268/125501170-9849b176-aa12-4494-97bb-c0e9719efbad.png)


Open JSON model window
![image](https://user-images.githubusercontent.com/54897268/125501311-d5ab302b-893b-4630-b627-f1804e226742.png)

Copypaste data from GraphanaJSONmodel.txt file
