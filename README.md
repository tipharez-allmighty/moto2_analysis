Title: Factors Influencing Promotion from Moto2 to MotoGP: A Data-Driven Analysis

Introduction:
The main question is: What factors influence the decision to promote a Moto2 rider to MotoGP? Based on our data, we can create a binary classification with the dependent variable 'got_promoted' and independent variables such as the number of first, second, and third places; overall podium finishes; median position during the season; median time difference to the leader over all races; number of races completed in Moto2; and, of course, the amount of points earned during the season. The key question here is whether the amount of points, i.e., victory in the Moto2 championship, is the defining factor that determines whether a rider will move to the MotoGP category, or if factors such as the number of first places and overall consistency of results during the season are more important.

Repository Inclusions:

    FILTERED_ROWS.csv: Data sourced from https://www.kaggle.com/datasets/amalsalilan/motogpresultdataset/code, providing Moto2 race results.
    Utility Module motogp_module.py: Includes functions necessary for data exploration, joining tables, and other essential tasks.
    Notebook motogp_analysis.ipynb: Contains data exploration, feature importance analysis, and development of two ML models, Random Forest and Gaussian NB.
