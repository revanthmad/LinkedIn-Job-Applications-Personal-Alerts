import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

st.title("🤖 Personal_LinkedIn_Job_Alerts app")
st.info("⚡ This is an app for the Data Analyst job alerts posted in the past few hours, scraped from LinkedIn.")

st.badge("New")
st.badge("Success", icon=":material/check:", color="green")

st.markdown(":red-badge[⚡⚡⚡ HURRY UP!!!! ⚡⚡⚡]")

count = ("span", {"class": "results-context-header__job-count"})

st.divider()

data_analyst:str = "Data Analyst"
title2:str = "Tech Support Engineer"

def title_encode(job_title: str) -> str:
  """This function replaces the spaces in a title string with '%2B' and returns the modified string as the encoded title."""
  return job_title.replace(" ", "%2B")

with st.sidebar:
  st.header('Filter Inputs')
  tat = st.selectbox('TAT', (past_hour, past_4_hours, past_8_hours, past_24_hours))
  job_title = st.selectbox('Job',('Data Analyst','Technical Support Engineer'))

list_url = "https://www.linkedin.com/jobs/search?keywords=Data%20Analyst&location=India&geoId=102713980&f_TPR=r14400"

st.write(f"**Web Scrape Link**: {list_url}")

st.divider()

response = requests.get(list_url)

if response.status_code == 200:
  list_data = response.text
  list_soup = BeautifulSoup(list_data, "html.parser")
  page_jobs = list_soup("li")

  list_job_IDs = []
  
  for job in page_jobs:
      base_card_div = job.find("div", {"class": "base-card"})
      job_id = base_card_div.get("data-entity-urn").split(":")[-1]
      list_job_IDs.append(job_id)
  
  jobs_collection = {}    
  
  for job_id in list_job_IDs:
      job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
      response = requests.get(job_url)
      job_soup = BeautifulSoup(response.text, "html.parser")
      job_post = {}
      job_post["job_url"] = job_url
      try:
        job_post['location'] = job_soup.find("span", {"class": "topcard__flavor topcard__flavor--bullet"}).get_text(strip=True)
      except:
        job_post['location'] = None
      try:
        job_post["tat"] = job_soup.find("span", {"class": "posted-time-ago__text posted-time-ago__text--new topcard__flavor--metadata"}).get_text(strip=True)
      except:
        job_post["tat"] = None
      try:
        job_post["num_applicants_caption"] = job_soup.find("figcaption", {"class": "num-applicants__caption"}).get_text(strip=True)
      except:
        job_post["num_applicants_caption"] = None
      try:
        job_post["company_url"] = job_soup.find("a", {"class": "topcard__org-name-link topcard__flavor--black-link"}).get("href")
      except:
        job_post["company_url"] = None
      try:
        job_post["company_name"] = job_soup.find("a", {"class": "topcard__org-name-link"}).get_text(strip=True)
      except:
        job_post["company_name"] = None
      try:
        job_post['job_title'] = job_soup.find("h2", {"class": "topcard__title"}).get_text(strip=True)
      except:
        job_post['job_title'] = None
      try:
        job_post['job_description'] = job_soup.find("div", {"class": "show-more-less-html__markup"}).get_text(strip=True)
      except:
        job_post['job_description'] = None
      try:
        job_criteria_keys = [e.get_text(strip=True) for e in job_soup("h3", {"class": "description__job-criteria-subheader"})]
        job_criteria_vals = [e.get_text(strip=True) for e in job_soup("span", {"class": "description__job-criteria-text description__job-criteria-text--criteria"})]
        if len(job_criteria_keys) == len(job_criteria_vals):
          job_criteria = dict(zip(job_criteria_keys, job_criteria_vals))
          job_post = {**job_post, **job_criteria}
      except:
        continue  
        
  jobs_collection[job_id] = job_post
  
  jobs_df = pd.DataFrame.from_dict(jobs_collection, orient='index')
  jobs_df.index.name = 'job_id'
  jobs_df.reset_index(inplace=True)
  
  @st.cache_data
  def get_data():
      df = pd.read_csv(jobs_df)
      return df
  
  with st.expander('Jobs Scraped'):
    st.write('**Jobs Dataset of the Past Hour**')
    get_data()
  
  @st.cache_data
  def convert_for_download(df):
    return df.to_csv().encode("utf-8")
  
  st.download_button(
      label="Download CSV",
      data=convert_for_download(df),
      now_ist = datetime.now(ZoneInfo('Asia/Kolkata')).strftime("DAjobs_%d%m%Y_%H%M%SIST")
      file_name=f"{now_ist}.csv",
      mime="text/csv",
      icon=":material/download:",
    )
except:
  print("Request failed, please try again.")







