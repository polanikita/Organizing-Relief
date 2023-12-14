# OrganizingReliefMVP
MVP for our Senior Design Class

Intructions for Setting Up Dependencies:

1. Framework: The frame work used is TurboGears2, hence to see the website in your terminal write the below:

<img width="261" alt="Screenshot 2023-09-28 at 6 21 55 PM" src="https://github.com/nmf4262/OrganizingReliefMVP/assets/70984821/a07c9b6f-5b43-45d1-acb1-6c37fa21213f">

instead of myapp.py write main.py

2. Other Dependencies (pip install all):
kajiki, sqlalchemy, json, python3, and beaker

3. Database Setup:

Required a postgres database url which can be added in line 87 of the setUp/myTables.py file

![Screenshot 2023-12-10 at 9 06 49 PM](https://github.com/nmf4262/OrganizingReliefMVP/assets/70984821/a256f8dc-990b-42f6-9b7f-1fde1a437d52)

File Composition:

1. main.py: File to run to start the website
2. pages dirctory: All the xhtml files that are rendered for the website
3. setUp directory: Basic setup for the Turbogears website

   a. muncipalities.py: list of all the Puertorrican municipalities

   b. myTables.py: the tables that make up the database used for the website

   c. rootController.py: python code for the rootcontroller of the website

   d. urgencyRatingWeights.py: the weights used for the algorithm to generate the urgency rating of each municipality based on the emergency calls of the municipality

When you run main.py: 

1. Setting up municipality urgency rating for all the municipalities

   a. If the "munUrgency_table" is empty it fills out the urgency rating for all the munipalities, setting all their urgencies to 0.

   b. If the "munUrgency_table" is not empty, it will update the urgency rating for all the municipalities depending on the amount of emergency calls. 
