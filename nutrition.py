import streamlit as st

import pandas as pd

import pymysql

st.set_page_config(page_title="NUTRITION PARADOX")


st.title("Global Health Data Explorer")

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        database="nutrition"
    )

obesity_queries = {
    "1. Top 5 regions with highest avg obesity (2022)": """
    SELECT Region, AVG(Mean_Estimate) AS Avg_Obesity
    FROM obesity
    WHERE Year = 2022
    GROUP BY Region
    ORDER BY Avg_Obesity DESC
    LIMIT 5;""",

     "2. Top 5 countries with highest obesity estimates": """
    SELECT Country, MAX(Mean_Estimate) AS Max_Obesity
    FROM obesity
    GROUP BY Country
    ORDER BY Max_Obesity DESC
    LIMIT 5;""",

      "3. Obesity trend in India over the years": """
    SELECT Year, AVG(Mean_Estimate) AS Avg_Obesity
    FROM obesity
    WHERE Country = 'India'
    GROUP BY Year
    ORDER BY Year;""",

    "4. Average Obesity by gender": """
    SELECT Gender, AVG(Mean_Estimate) AS Avg_Obesity
    FROM obesity
    GROUP BY Gender;""",

     "5. Country count by obesity level category and age group": """
    SELECT Obesity_level, Age_Group, COUNT(DISTINCT Country) AS Country_Count
    FROM obesity
    GROUP BY Obesity_level, Age_Group;""",

     "6. Top 5 least and most reliable countries by CI_Width": """
    SELECT Country, AVG(CI_Width) AS Avg_CI, 'Least reliable' As Type
    FROM obesity
    GROUP BY Country
    ORDER BY Avg_CI DESC
    LIMIT 5

    UNION ALL

    SELECT Country, AVG(CI_Width) AS Avg_CI, 'Most reliable' As Type
    FROM obesity
    GROUP BY Country
    ORDER BY Avg_CI ASC
    LIMIT 5; """,

     "7. Average obesity by age group": """
    SELECT Age_Group, AVG(Mean_Estimate) AS Avg_Obesity
    FROM obesity
    GROUP BY Age_Group;""",

     "8. Top 10 countries with consistent low obesity": """
    SELECT Country, AVG(Mean_Estimate) AS Avg_Obesity, AVG(CI_Width) AS Avg_CI
    FROM obesity
    GROUP BY Country
    HAVING Avg_Obesity < 15 AND Avg_CI < 2
    ORDER BY Avg_Obesity ASC
    LIMIT 10;""",

     "9. Countries where female obesity exceeds male by large margin":"""
    SELECT o1.Country, o1.Mean_Estimate AS Female_Obesity, o2.Mean_Estimate AS Male_Obesity,
    (o1.Mean_Estimate - o2.Mean_Estimate) AS Gap
    FROM obesity o1
    JOIN obesity o2
    ON o1.Country = o2.Country AND o1.Year = o2.Year AND o1.Age_Group = o2.Age_Group
    WHERE o1.Sex = 'SEX_FMLE' AND o2.Sex = 'SEX_MLE'
    AND (o1.Mean_Estimate - o2.Mean_Estimate) > 5;""",

     "10. Global avg obesity % per year": """
    SELECT Year, AVG(Mean_Estimate) AS Global_Avg_Obesity
    FROM obesity
    GROUP BY Year
    ORDER BY Year;"""
}


malnutrition_queries = {
"1. Avg. malnutrition by age group": """
SELECT Age_Group, AVG(Mean_Estimate) AS Avg_Malnutrition
FROM malnutrition
GROUP BY Age_Group;
""",
"2. Top 5 countries with highest malnutrition" : """
SELECT Country, MAX(Mean_Estimate) AS Max_Malnutrition
FROM malnutrition
GROUP BY Country
ORDER BY Max_Malnutrition DESC
LIMIT 5;""",

"3. Malnutrition trend in African region": """
SELECT Year, AVG(Mean_Estimate) AS Avg_Malnutrition
FROM malnutrition
WHERE Region = 'Africa'
GROUP BY Year
ORDER BY Year;""",

"4. Gender-based average malnutrition": """
SELECT Sex, AVG(Mean_Estimate) AS Avg_Malnutrition
FROM malnutrition
GROUP BY Sex;""",

"5. Malnutrition level-wise average CI width by age group": """
SELECT Malnutrition_Level, Age_Group, AVG(CI_Width) AS Avg_CI
FROM malnutrition
GROUP BY Malnutrition_Level, Age_Group;
""",

"6. Yearly malnutrition change in India, Nigeria, Brazil": """
SELECT Country, Year, AVG(Mean_Estimate) AS Avg_Malnutrition
FROM malnutrition
WHERE Country IN ('India', 'Nigeria', 'Brazil')
GROUP BY Country, Year
ORDER BY Country, Year;
""",

"7. Regions with lowest malnutrition averages": """
SELECT Region, AVG(Mean_Estimate) AS Avg_Malnutrition
FROM malnutrition
GROUP BY Region
ORDER BY Avg_Malnutrition ASC
LIMIT 5;
""",

"8. Countries with increasing malnutrition": """
SELECT Country, MIN(Mean_Estimate) AS Min_Estimate, MAX(Mean_Estimate) AS Max_Estimate
FROM malnutrition
GROUP BY Country
HAVING MAX(Mean_Estimate) - MIN(Mean_Estimate) > 5;
""",

"9. Min/Max malnutrition levels year-wise": """
SELECT Year, MIN(Mean_Estimate) AS Min_Malnutrition, MAX(Mean_Estimate) AS Max_Malnutrition
FROM malnutrition
GROUP BY Year
ORDER BY Year;
""",

"10. High CI_Width flags (CI_Width > 5)": """
SELECT * FROM malnutrition
WHERE CI_Width > 5;"""
}

combined_queries = {
"1. Obesity vs Malnutrition comparison (any 5 countries)": """
SELECT o.Country, AVG(o.Mean_Estimate) AS Avg_Obesity, AVG(m.Mean_Estimate) AS Avg_Malnutrition
FROM obesity o
JOIN malnutrition m
  ON o.Country = m.Country AND o.Year = m.Year
WHERE o.Country IN ('India', 'United States', 'Nigeria', 'Japan', 'Brazil')
GROUP BY o.Country;
""",

"2. Gender-based disparity in both obesity and malnutrition": """
SELECT o.Gender, AVG(o.Mean_Estimate) AS Avg_Obesity, AVG(m.Mean_Estimate) AS Avg_Malnutrition
FROM obesity o
JOIN malnutrition m
  ON o.Country = m.Country AND o.Year = m.Year AND o.Gender = m.Gender
GROUP BY o.Gender;
""",

"3. Region-wise average estimates (Africa, Americas)": """
SELECT o.Region, AVG(o.Mean_Estimate) AS Avg_Obesity, AVG(m.Mean_Estimate) AS Avg_Malnutrition
FROM obesity o
JOIN malnutrition m
  ON o.Country = m.Country AND o.Year = m.Year
WHERE o.Region IN ('Africa', 'Americas')
GROUP BY o.Region;
""",

"4. Countries where obesity is rising, malnutrition dropping": """
WITH trends AS (
  SELECT o.Country,
         MAX(o.Mean_Estimate) - MIN(o.Mean_Estimate) AS Obesity_Change,
         MIN(m.Mean_Estimate) - MAX(m.Mean_Estimate) AS Malnutrition_Change
  FROM obesity o
  JOIN malnutrition m
    ON o.Country = m.Country AND o.Year = m.Year
  GROUP BY o.Country
)
SELECT *
FROM trends;
""",

"5. Age-wise trend analysis (avg obesity & malnutrition over years)": """
SELECT o.Year, o.Age_Group, 
       AVG(o.Mean_Estimate) AS Avg_Obesity, 
       AVG(m.Mean_Estimate) AS Avg_Malnutrition
FROM obesity o
JOIN malnutrition m
  ON o.Country = m.Country AND o.Year = m.Year AND o.Age_Group = m.Age_Group
GROUP BY o.Year, o.Age_Group
ORDER BY o.Year;
"""
}

# Sidebar section headers
st.sidebar.header(" Query Categories")
query_category = st.sidebar.radio("Choose a category", ["Obesity", "Malnutrition", "Combined"])


# Load queries based on category
if query_category == "Obesity":
    selected_query_name = st.sidebar.selectbox("Obesity Queries", list(obesity_queries.keys()))
    selected_query = obesity_queries[selected_query_name]

elif query_category == "Malnutrition":
    selected_query_name = st.sidebar.selectbox("Malnutrition Queries", list(malnutrition_queries.keys()))
    selected_query = malnutrition_queries[selected_query_name]

else:  # Combined
    selected_query_name = st.sidebar.selectbox("Combined Queries", list(combined_queries.keys()))
    selected_query = combined_queries[selected_query_name]

# Show selected query and result
st.subheader(f"Query: {selected_query_name}")
# st.code(selected_query, language="sql")

# Execute query
try:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(selected_query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()

    df = pd.DataFrame(result,columns = [i[0] for i in cursor.description])
    df.drop_duplicates(inplace=True)
    if df.empty:
        st.warning("No data found.")
    else:
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Query execution failed: {e}")

