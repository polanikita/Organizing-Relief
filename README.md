# Organizing-Relief

Instructions for Setting Up Dependencies:

1. Framework: The framework used is TurboGears2, to install dependencies:

```
pip install TurboGears2
pip install kajiki
pip install sqlalchemy
pip install beaker
pip install json
pip install python3

python3 main.py

```

3. Database Setup:

Requires a Postgres database URL which can be added in line 87 of the setUp/myTables.py file

```
db_url = 'postgres://yourDBUsername:yourDBpassword@localhost:yourPort/yourDBname'
```

File Composition:

1. main.py: File to run to start the website
2. pages directory: All the XHTML files that are rendered for the website
3. setup directory: Basic setup for the TurboGears website

   a. muncipalities.py: list of all the Puertorrican municipalities

   b. myTables.py: the tables that make up the database used for the website

   c. rootController.py: python code for the root controller of the website

   d. urgencyRatingWeights.py: the weights used for the algorithm to generate the urgency rating of each municipality based on the emergency calls of the municipality

When you run main.py: 

1. Setting up municipality urgency rating for all the municipalities

   a. If the "munUrgency_table" is empty it fills out the urgency rating for all the municipalities, setting all their urgencies to 0.

   b. If the "munUrgency_table" is not empty, it will update the urgency rating for all the municipalities depending on the number of emergency calls. 
