import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

years = list(range(2000, 2025 + 1))

data = []

for year in years:
  url = "https://ndc.services.cdc.gov/search-results-year/"
  payload = {
      'notifiable_year': str(year),
      'search-type': 'years'
  }

  response = requests.post(url, data=payload)

  if response.status_code == 200:
      soup = BeautifulSoup(response.content, "html.parser")

      diseases_wrapper = soup.find("div", class_="list-of-notifiable-disease wrapper")
      if diseases_wrapper:
          diseases = diseases_wrapper.find_all("li")
          for disease in diseases:
              disease_name = disease.text.strip()
              disease_link = disease.find("a")["href"]
              data.append({"year": year, "disease": disease_name, "cdc_link": disease_link})
      else:
          print("Diseases wrapper not found")
  else:
      print(f"Failed to retrieve data ({year}): {response.status_code}")

  time.sleep(2)

cdc_reportable_diseases = pd.DataFrame(data)

cdc_reportable_diseases.to_csv("./cdc_reportable_diseases.csv")