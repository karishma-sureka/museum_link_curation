# museum_link_curation

1. Setup Virtual Environment for python 2.7.X.

  ```
  pip install virtualenv
  virtualenv <env name>

  Unix/Mac OS : 
  source <env name>/bin/activate

  Windows:
  <env name>\scripts\activate
  ```
2. Install dependent python packages using following command
  ```
  pip install -r packages.txt
  ```

3. Install MongoDb and run the mongo server. (Ref: https://docs.mongodb.org/manual/installation/)
  ```
  mongod --dbpath <path to data directory>
  ```
  
4. Run the application using following command
  ```
  python app.py
  ```
